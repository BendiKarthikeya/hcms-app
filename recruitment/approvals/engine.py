"""
recruitment/approvals/engine.py

Approval routing engine for ManpowerRequests and OfferLetters.
route_request() / route_offer()  — find the matching ApprovalRule and create approval records.
advance() / advance_offer()      — move the document forward or back based on approver action.
resolve_approver()               — maps step.approver_type to a concrete Employee.
"""

from django.utils import timezone

from recruitment.models_approvals import (
    ApprovalRule,
    ApprovalStep,
    ManpowerApproval,
    OfferApproval,
    RecruitmentApprovalDelegation,
)
from recruitment.models_manpower import ManpowerRequest, ManpowerRequestStatusLog


def resolve_approver(step: ApprovalStep, document):
    """
    Return the Employee who should action this step.
    `document` can be a ManpowerRequest or an OfferLetter.
    """
    from employee.models import Employee

    approver = None

    if step.approver_type == "user" and step.approver_user:
        approver = step.approver_user

    elif step.approver_type == "manager_of_requester":
        # ManpowerRequest → requested_by; OfferLetter → created_by
        emp = getattr(document, "requested_by", None) or getattr(document, "created_by", None)
        if emp:
            work_info = getattr(emp, "employee_work_info", None)
            if work_info:
                approver = getattr(work_info, "reporting_manager_id", None)

    elif step.approver_type == "department_head":
        dept = getattr(document, "department", None)
        if dept is None:
            pass
        elif hasattr(dept, "manager"):
            # ManpowerRequest.department is a FK with a .manager attribute
            approver = getattr(dept, "manager", None)
        elif isinstance(dept, str) and dept:
            # OfferLetter.department is a plain CharField — look up by name
            from base.models import Department
            dept_obj = Department.objects.filter(department__iexact=dept).first()
            if dept_obj:
                approver = getattr(dept_obj, "manager", None)

    elif step.approver_type in ("hr_manager", "finance"):
        from django.contrib.auth.models import Permission
        hr_perm = Permission.objects.filter(codename="view_recruitment").first()
        if hr_perm:
            hr_user = hr_perm.user_set.filter(is_active=True).first()
            if hr_user:
                approver = getattr(hr_user, "employee_get", None)
        if approver is None:
            approver = Employee.objects.filter(
                employee_user_id__is_superuser=True, is_active=True
            ).first()

    if approver is None:
        return None

    # Check delegation
    today = timezone.now().date()
    delegation = RecruitmentApprovalDelegation.objects.filter(
        delegator=approver, start_date__lte=today, end_date__gte=today
    ).first()
    return delegation.delegate if delegation else approver


def _match_rule(company_id, department=None):
    """Find the first matching ApprovalRule for a company + department."""
    rules = ApprovalRule.objects.filter(company_id=company_id, is_active=True)
    for rule in rules:
        if rule.department and rule.department != department:
            continue
        return rule
    return None


def _custom_manpower_approvers(request: ManpowerRequest):
    """
    If the requester matches CUSTOM_REQUESTER_FLOWS, return the ordered list of
    Employee approvers for the manpower request (the requester themselves is
    excluded — they raised it, they don't self-approve). Returns [] otherwise.
    """
    try:
        requested_by = request.requested_by
        if not requested_by:
            return []
        user = getattr(requested_by, "employee_user_id", None)
        email = (getattr(user, "email", "") or requested_by.email or "").lower()
    except Exception:
        return []

    if email not in CUSTOM_REQUESTER_FLOWS:
        return []

    chain = []
    seen = set()
    excluded_for_hr = {e for e in CUSTOM_REQUESTER_FLOWS[email] if e != "__HR__"}
    for entry in CUSTOM_REQUESTER_FLOWS[email]:
        if entry == email:
            continue  # skip self
        emp = _resolve_shared_hr(exclude_emails=excluded_for_hr) if entry == "__HR__" else _resolve_employee_by_email(entry)
        if emp and emp.id not in seen:
            seen.add(emp.id)
            chain.append(emp)
    return chain


def route_request(request: ManpowerRequest):
    """
    Route a manpower request for approval.

    If the requester matches CUSTOM_REQUESTER_FLOWS, build pending ManpowerApproval
    rows directly from that fixed chain (step=None). Otherwise fall back to the
    ApprovalRule-based matching.
    """
    custom = _custom_manpower_approvers(request)
    if custom:
        for approver in custom:
            due_at = timezone.now() + timezone.timedelta(hours=48)
            ManpowerApproval.objects.create(
                request=request,
                step=None,
                approver=approver,
                action=ManpowerApproval.ACTION_PENDING,
                due_at=due_at,
            )
        _notify_approver(custom[0], request, "Manpower Request", True)
        return "custom_requester_flow"

    rules = ApprovalRule.objects.filter(
        company_id=request.company_id, is_active=True
    )

    matched_rule = None
    for rule in rules:
        # Department match (None = any)
        if rule.department and rule.department != request.department:
            continue
        matched_rule = rule
        break

    if not matched_rule:
        return None

    steps = list(matched_rule.steps.all())
    for step in steps:
        approver = resolve_approver(step, request)
        due_at = timezone.now() + timezone.timedelta(hours=step.sla_hours)
        ManpowerApproval.objects.create(
            request=request,
            step=step,
            approver=approver,
            action=ManpowerApproval.ACTION_PENDING,
            due_at=due_at,
        )
    # Notify first approver
    if steps:
        first_approver = resolve_approver(steps[0], request)
        _notify_approver(first_approver, request, "Manpower Request", True)

    return matched_rule


def advance(request: ManpowerRequest, action: str, by_user, comment: str = ""):
    """
    Process an approve/reject/queried action by by_user on the current pending approval.
    Updates request status accordingly.
    """
    from employee.models import Employee

    actor_employee = getattr(by_user, "employee_get", None)

    pending = ManpowerApproval.objects.filter(
        request=request, action=ManpowerApproval.ACTION_PENDING
    ).order_by("step__sequence", "id").first()

    if not pending:
        return False

    old_status = request.status

    # "queried" — bounce request back to requester WITHOUT consuming the step.
    if action == ManpowerApproval.ACTION_QUERIED:
        request.status = ManpowerRequest.STATUS_QUERIED
        request.last_query = comment
        request.query_count = (request.query_count or 0) + 1
        request.save()
        pending.action = ManpowerApproval.ACTION_QUERIED
        pending.comment = comment
        pending.acted_at = timezone.now()
        pending.acted_by = actor_employee if actor_employee != pending.approver else None
        pending.save(update_fields=["action", "comment", "acted_at", "acted_by"])
        _log(request, old_status, request.status, actor_employee, comment or "Sent back with query")
        # Bell-notify the requester that they need to attach a clarification.
        _in_app_notify(
            recipient=getattr(request.requested_by, "employee_user_id", None),
            actor=actor_employee,
            verb=f"{request.requisition_no} returned with query: {comment[:80]}",
            redirect_path=f"/recruitment/manpower/{request.id}/",
        )
        return True

    pending.action = action
    pending.acted_at = timezone.now()
    pending.acted_by = actor_employee if actor_employee != pending.approver else None
    pending.comment = comment
    pending.save()

    if action == ManpowerApproval.ACTION_REJECTED:
        request.status = ManpowerRequest.STATUS_REJECTED
        request.save()
        _log(request, old_status, request.status, actor_employee, comment)
        try:
            import threading
            from recruitment.email_utils import email_manpower_rejected
            threading.Thread(target=email_manpower_rejected, args=(request, comment), daemon=True).start()
        except Exception:
            pass
        _in_app_notify(
            recipient=getattr(request.requested_by, "employee_user_id", None),
            actor=actor_employee,
            verb=f"{request.requisition_no} was rejected.",
            redirect_path=f"/recruitment/manpower/{request.id}/",
        )
        return True

    # Check if more pending steps remain
    remaining = ManpowerApproval.objects.filter(
        request=request, action=ManpowerApproval.ACTION_PENDING
    ).exists()

    if remaining:
        request.status = ManpowerRequest.STATUS_UNDER_APPROVAL
        # Notify next approver in the chain
        next_pending = ManpowerApproval.objects.filter(
            request=request, action=ManpowerApproval.ACTION_PENDING
        ).order_by("step__sequence", "id").first()
        if next_pending and next_pending.approver:
            _notify_approver(next_pending.approver, request, "Manpower Request", False)
    else:
        request.status = ManpowerRequest.STATUS_APPROVED
        _create_recruitment(request)
        try:
            import threading
            from recruitment.email_utils import email_manpower_approved
            threading.Thread(target=email_manpower_approved, args=(request,), daemon=True).start()
        except Exception:
            pass
        _in_app_notify(
            recipient=getattr(request.requested_by, "employee_user_id", None),
            actor=actor_employee,
            verb=f"{request.requisition_no} fully approved 🎉",
            redirect_path=f"/recruitment/manpower/{request.id}/",
        )

    request.save()
    _log(request, old_status, request.status, actor_employee, comment)
    return True


def resubmit_after_query(request: ManpowerRequest, by_user, comment: str = "", attachment=None):
    """
    Requester answers a queried approval and pushes the request back into the chain.
    The previously-queried approval row is reset to pending (same approver), and the
    request moves back to UNDER_APPROVAL — no restart, no new approval rows.
    """
    if request.status != ManpowerRequest.STATUS_QUERIED:
        return False

    actor_employee = getattr(by_user, "employee_get", None)
    queried_row = ManpowerApproval.objects.filter(
        request=request, action=ManpowerApproval.ACTION_QUERIED
    ).order_by("step__sequence", "id").first()
    # Backward-compat: if the queried row was already reset, fall back to first pending row.
    if not queried_row:
        queried_row = ManpowerApproval.objects.filter(
            request=request, action=ManpowerApproval.ACTION_PENDING
        ).order_by("step__sequence", "id").first()

    if attachment is not None:
        request.clarification_document = attachment

    old_status = request.status
    request.status = ManpowerRequest.STATUS_UNDER_APPROVAL
    request.save()

    if queried_row and queried_row.action == ManpowerApproval.ACTION_QUERIED:
        queried_row.action = ManpowerApproval.ACTION_PENDING
        queried_row.acted_at = None
        queried_row.save(update_fields=["action", "acted_at"])

    note = f"Resubmitted after query"
    if comment:
        note += f": {comment}"
    _log(request, old_status, request.status, actor_employee, note)

    # Re-notify the approver who asked the question.
    if queried_row and queried_row.approver:
        _notify_approver(queried_row.approver, request, "Manpower Request", True)

    return True


CUSTOM_REQUESTER_FLOWS = {
    "fatma@fits.com":      ["fatma@fits.com",      "mohammad@fits.com", "__HR__"],
    "aisha@fits.com":      ["aisha@fits.com",      "wahlid@fits.com",   "__HR__"],
    "khalid@fits.com":     ["khalid@fits.com",     "divhead@fits.com",  "cfo@fits.com", "ceo@fits.com"],
    # Demo flow: karthikeya → aditya → HR
    "karthikeya@fits.one": ["karthikeya@fits.one", "aditya@fits.one",   "__HR__"],
}


def _resolve_employee_by_email(email):
    from employee.models import Employee
    return Employee.objects.filter(email__iexact=email).first()


def _resolve_shared_hr(exclude_emails=()):
    """
    Resolve the shared HR step. Prefer the dedicated `hr@fits.com` account so the
    Fatma/Aisha chains route to a human-friendly HR user instead of `superuser`.
    Falls back to any active user holding `view_offerletter` if hr@fits.com is
    missing or excluded by the caller.
    """
    from django.contrib.auth.models import User
    excluded = set(exclude_emails or ())
    if "hr@fits.com" not in excluded:
        hr_user = User.objects.filter(username="hr@fits.com", is_active=True).first()
        if hr_user:
            return getattr(hr_user, "employee_get", None)
    qs = (
        User.objects.filter(is_active=True, user_permissions__codename="view_offerletter")
        | User.objects.filter(is_active=True, groups__permissions__codename="view_offerletter")
    ).distinct()
    if excluded:
        qs = qs.exclude(email__in=excluded).exclude(username__in=excluded)
    hr_user = qs.first()
    return getattr(hr_user, "employee_get", None) if hr_user else None


def _build_custom_chain(requester_email):
    chain = []
    seen = set()
    excluded_for_hr = {e for e in CUSTOM_REQUESTER_FLOWS[requester_email] if e != "__HR__"}
    for entry in CUSTOM_REQUESTER_FLOWS[requester_email]:
        emp = _resolve_shared_hr(exclude_emails=excluded_for_hr) if entry == "__HR__" else _resolve_employee_by_email(entry)
        if emp and emp.id not in seen:
            seen.add(emp.id)
            chain.append(emp)
    return chain


def _build_esign_chain(offer):
    """
    Build the explicit e-sign chain for an offer letter.

    If the manpower-request requester matches one of CUSTOM_REQUESTER_FLOWS,
    return that fixed sequence. Otherwise fall back to the default chain:
      1. HR (first user with view_offerletter permission)
      2. ManpowerRequest requester
      3. Requester's reporting manager
      4. First active superuser
    Returns a deduplicated ordered list of Employee objects.
    """
    from django.contrib.auth.models import User

    try:
        from recruitment.models_manpower import ManpowerRequest
        mp_early = ManpowerRequest.objects.filter(
            recruitment_id=offer.candidate_id.recruitment_id
        ).select_related("requested_by__employee_user_id").first()
        if mp_early and mp_early.requested_by:
            req_user = mp_early.requested_by.employee_user_id
            req_email = (getattr(req_user, "email", "") or mp_early.requested_by.email or "").lower()
            if req_email in CUSTOM_REQUESTER_FLOWS:
                custom = _build_custom_chain(req_email)
                if custom:
                    return custom
    except Exception:
        pass

    seen_ids = set()
    chain = []

    def _add(emp):
        if emp and emp.id not in seen_ids:
            seen_ids.add(emp.id)
            chain.append(emp)

    # 1. HR — first active user with view_offerletter permission
    try:
        hr_user = (
            User.objects.filter(is_active=True, user_permissions__codename="view_offerletter")
            | User.objects.filter(is_active=True, groups__permissions__codename="view_offerletter")
        ).distinct().first()
        if hr_user:
            _add(getattr(hr_user, "employee_get", None))
    except Exception:
        pass

    # 2. ManpowerRequest requester
    requester = None
    try:
        from recruitment.models_manpower import ManpowerRequest
        mp = ManpowerRequest.objects.filter(
            recruitment_id=offer.candidate_id.recruitment_id
        ).select_related("requested_by").first()
        if mp and mp.requested_by:
            requester = mp.requested_by
            _add(requester)
    except Exception:
        pass

    # 3. Requester's reporting manager
    if requester is not None:
        try:
            manager = requester.get_reporting_manager()
            if manager:
                _add(manager)
        except Exception:
            pass

    # 4. First active superuser
    try:
        su = User.objects.filter(is_superuser=True, is_active=True).first()
        if su:
            _add(getattr(su, "employee_get", None))
    except Exception:
        pass

    return chain


def route_offer(offer):
    """
    Build the offer e-sign chain:
      ManpowerRequest requester → ApprovalRule approvers → superusers → HR

    Returns "esign_chain" if a chain was built, None if no approvers found.
    """
    chain = _build_esign_chain(offer)
    if not chain:
        return None

    for seq, approver in enumerate(chain, start=1):
        due_at = timezone.now() + timezone.timedelta(hours=48)
        OfferApproval.objects.create(
            offer=offer,
            step=None,
            approver=approver,
            action=OfferApproval.ACTION_PENDING,
            due_at=due_at,
        )
        if seq == 1:
            _notify_approver(approver, offer, "Offer Letter E-Sign", True)

    return "esign_chain"


def advance_offer(offer, action: str, by_user, comment: str = "", signature_image: str = ""):
    """
    Process an e-sign / feedback action by by_user on the current pending OfferApproval.
    "esign" maps to approved; "feedback" maps to rejected.
    """
    from employee.models import Employee

    # Map UI action labels to internal values
    action = {"esign": OfferApproval.ACTION_APPROVED, "feedback": OfferApproval.ACTION_REJECTED}.get(action, action)

    actor_employee = getattr(by_user, "employee_get", None)

    pending = OfferApproval.objects.filter(
        offer=offer, action=OfferApproval.ACTION_PENDING
    ).order_by("step__sequence", "id").first()

    if not pending:
        return False

    pending.action = action
    pending.acted_at = timezone.now()
    pending.acted_by = actor_employee if actor_employee != pending.approver else None
    pending.comment = comment
    if action == OfferApproval.ACTION_APPROVED and signature_image:
        pending.signature_image = signature_image
    pending.save()

    old_status = offer.status

    if action == OfferApproval.ACTION_REJECTED:
        offer.status = "draft"
        offer.save()
        try:
            import threading
            from recruitment.email_utils import email_offer_approval_rejected
            threading.Thread(target=email_offer_approval_rejected, args=(offer, comment), daemon=True).start()
        except Exception:
            pass
        return True

    # Check if more pending steps remain
    remaining = OfferApproval.objects.filter(
        offer=offer, action=OfferApproval.ACTION_PENDING
    ).exclude(id=pending.id)

    if remaining.exists():
        # Notify the next approver in line
        next_pending = remaining.order_by("step__sequence").first()
        if next_pending and next_pending.approver:
            _notify_approver(next_pending.approver, offer, "Offer Letter", False)
    else:
        # Fully approved — auto-send to candidate
        offer.status = "sent"
        offer.sent_date = timezone.now()
        offer.save()
        try:
            import threading
            from recruitment.email_utils import email_offer_approval_approved
            threading.Thread(target=email_offer_approval_approved, args=(offer,), daemon=True).start()
        except Exception:
            pass
        # Offer fully approved internally → create the candidate sign-documents
        # and email the candidate their portal link (this replaces the plain
        # offer-letter email; the portal contains the offer letter to e-sign).
        try:
            from recruitment.onboarding_docs import create_onboarding_documents
            create_onboarding_documents(offer)
        except Exception:
            pass
    return True


def _notify_approver(approver, document, doc_type: str, is_first: bool):
    """Send both an email + an in-app bell notification when it's the approver's turn."""
    if not approver:
        return
    # Email (existing behaviour)
    try:
        import threading
        from recruitment.email_utils import email_approval_assigned
        threading.Thread(
            target=email_approval_assigned,
            args=(approver, document, doc_type),
            daemon=True,
        ).start()
    except Exception:
        pass
    # In-app notification (bell icon on dashboard)
    _in_app_notify(
        recipient=getattr(approver, "employee_user_id", None),
        actor=getattr(document, "requested_by", None) or getattr(document, "raised_by", None),
        verb=f"{doc_type} {getattr(document, 'requisition_no', '')} is waiting for your action.",
        redirect_path="/recruitment/approvals/inbox/",
    )


def _in_app_notify(recipient, actor=None, verb="", redirect_path="/"):
    """Best-effort dashboard notification using the notifications app, if available."""
    if not recipient:
        return
    try:
        from notifications.signals import notify
        actor_obj = getattr(actor, "employee_user_id", None) or actor or recipient
        notify.send(
            actor_obj,
            recipient=[recipient],
            verb=verb,
            icon="people-circle",
            redirect=redirect_path,
        )
    except Exception:
        pass


def _log(request, from_status, to_status, changed_by, note=""):
    ManpowerRequestStatusLog.objects.create(
        request=request,
        from_status=from_status,
        to_status=to_status,
        changed_by=changed_by,
        note=note,
    )


def _create_recruitment(request: ManpowerRequest):
    """Auto-create a Recruitment campaign when a request is fully approved."""
    from recruitment.models import Recruitment

    if hasattr(request, "recruitment_campaign"):
        return  # already linked

    from django.utils.text import slugify

    title = (
        str(request.job_position)
        if request.job_position
        else f"Vacancy – {request.requisition_no}"
    )
    rec = Recruitment.objects.create(
        title=title,
        job_position_id=request.job_position,
        vacancy=request.positions_count,
        company_id=request.company_id,
        manpower_request=request,
        is_public=True,
    )
    rec.public_slug = slugify(f"{title}-{rec.id}")
    rec.save(update_fields=["public_slug"])
