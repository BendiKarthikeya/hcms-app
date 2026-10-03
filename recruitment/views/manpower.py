"""
recruitment/views/manpower.py

Manpower Request CRUD + submit/withdraw + approval inbox + approve/reject.
"""

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from fits.decorators import login_required
from recruitment.approvals.engine import advance, route_request
from recruitment.decorators import manager_can_enter
from recruitment.models import (
    ApprovalRule,
    ApprovalStep,
    ManpowerApproval,
    ManpowerRequest,
    ManpowerRequestStatusLog,
)


def _get_employee(user):
    return getattr(user, "employee_get", None)


@login_required
def manpower_list(request):
    emp = _get_employee(request.user)
    qs = ManpowerRequest.objects.all().select_related(
        "department", "job_position", "requested_by"
    )
    if not request.user.is_superuser:
        qs = qs.filter(requested_by=emp)

    status_filter = request.GET.get("status")
    if status_filter:
        qs = qs.filter(status=status_filter)

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "recruitment/manpower/list.html",
        {
            "requests_page": page,
            "status_choices": ManpowerRequest.STATUS_CHOICES,
            "current_status": status_filter,
        },
    )


@login_required
def manpower_create(request):
    from base.models import Department, JobPosition

    if request.method == "POST":
        data = request.POST
        emp = _get_employee(request.user)
        company = getattr(emp, "company_id", None) if emp else None
        if not company and request.user.is_superuser:
            from base.models import Company
            company = Company.objects.first()

        req = ManpowerRequest(
            company_id=company,
            grade=data.get("grade", ""),
            positions_count=int(data.get("positions_count") or 1),
            justification=data.get("justification", ""),
            budget_code=data.get("budget_code", ""),
            employment_type=data.get("employment_type", "full_time"),
            nationality_preference=data.get("nationality_preference", "any"),
            requested_by=emp,
        )
        dept_id = data.get("department")
        if dept_id:
            req.department = Department.objects.filter(id=dept_id).first()
        jp_id = data.get("job_position")
        if jp_id:
            req.job_position = JobPosition.objects.filter(id=jp_id).first()
        expected = data.get("expected_join_date")
        if expected:
            req.expected_join_date = expected
        req.save()
        ManpowerRequestStatusLog.objects.create(
            request=req, from_status="", to_status=req.status, changed_by=emp
        )
        messages.success(request, _("Manpower request %(no)s saved as draft.") % {"no": req.requisition_no})
        return redirect(reverse("manpower-detail", args=[req.id]))

    from base.models import Department, JobPosition
    return render(
        request,
        "recruitment/manpower/form.html",
        {
            "departments": Department.objects.all(),
            "job_positions": JobPosition.objects.all(),
            "employment_choices": ManpowerRequest.EMPLOYMENT_CHOICES,
            "nationality_choices": ManpowerRequest.NATIONALITY_CHOICES,
        },
    )


def _hr_friendly_label(approver):
    """Friendly labels for the demo flow accounts; everyone else keeps their name."""
    if not approver:
        return "—"
    user = getattr(approver, "employee_user_id", None)
    email = (getattr(user, "email", "") or getattr(approver, "email", "") or "").lower()
    DEMO_LABELS = {
        "hr@fits.com":      "HR",
        "cfo@fits.com":     "CFO",
        "ceo@fits.com":     "CEO",
        "divhead@fits.com": "Division Head",
    }
    return DEMO_LABELS.get(email, str(approver))


@login_required
def manpower_detail(request, req_id):
    mr = get_object_or_404(ManpowerRequest, id=req_id)
    logs = mr.status_logs.select_related("changed_by").all()
    approvals = list(mr.approvals.select_related("approver", "step").all())
    for a in approvals:
        a.display_approver = _hr_friendly_label(a.approver)
    details = [
        (_("Requisition No"), mr.requisition_no),
        (_("Department"), mr.department),
        (_("Job Position"), mr.job_position),
        (_("Grade"), mr.grade or "—"),
        (_("Positions Required"), mr.positions_count),
        (_("Employment Type"), mr.get_employment_type_display()),
        (_("Nationality Preference"), mr.get_nationality_preference_display()),
        (_("Budget Code"), mr.budget_code or "—"),
        (_("Expected Join Date"), mr.expected_join_date or "—"),
        (_("Requested By"), mr.requested_by),
        (_("Requested On"), mr.requested_on.strftime("%d %b %Y %H:%M") if mr.requested_on else "—"),
    ]
    return render(
        request,
        "recruitment/manpower/detail.html",
        {"mr": mr, "logs": logs, "approvals": approvals, "details": details},
    )


@login_required
def manpower_submit(request, req_id):
    mr = get_object_or_404(ManpowerRequest, id=req_id)
    emp = _get_employee(request.user)
    if mr.status != ManpowerRequest.STATUS_DRAFT:
        messages.error(request, _("Only draft requests can be submitted."))
        return redirect(reverse("manpower-detail", args=[req_id]))

    old = mr.status
    rule = route_request(mr)
    if rule:
        mr.status = ManpowerRequest.STATUS_UNDER_APPROVAL
        msg = _("Request submitted — pending approval.")
    else:
        # No rule configured: keep as submitted so HR can manually assign/approve
        mr.status = ManpowerRequest.STATUS_SUBMITTED
        msg = _("Request submitted. No approval rule found — HR will review manually.")
    mr.save()
    ManpowerRequestStatusLog.objects.create(
        request=mr, from_status=old, to_status=mr.status, changed_by=emp, note="Submitted"
    )
    messages.success(request, msg)
    return redirect(reverse("manpower-detail", args=[req_id]))


@login_required
def approval_inbox(request):
    emp = _get_employee(request.user)
    is_hr = request.user.is_superuser or request.user.has_perm("recruitment.view_recruitment")

    if is_hr:
        pending = ManpowerApproval.objects.filter(
            action=ManpowerApproval.ACTION_PENDING
        ).select_related("request", "step", "approver")
    else:
        pending = ManpowerApproval.objects.filter(
            approver=emp, action=ManpowerApproval.ACTION_PENDING
        ).select_related("request", "step", "approver")

    # Also include requests stuck in 'submitted' with no approval records (no rule matched)
    submitted_no_rule = ManpowerRequest.objects.filter(
        status=ManpowerRequest.STATUS_SUBMITTED
    ).exclude(
        id__in=ManpowerApproval.objects.values_list("request_id", flat=True)
    ).select_related("department", "job_position", "requested_by")

    return render(request, "recruitment/manpower/inbox.html", {
        "pending": pending,
        "submitted_no_rule": submitted_no_rule,
        "is_hr": is_hr,
    })


@login_required
def manual_approve(request, req_id):
    """Directly approve or reject a submitted request that has no approval rule."""
    mr = get_object_or_404(ManpowerRequest, id=req_id)
    emp = _get_employee(request.user)
    action = request.POST.get("action")
    comment = request.POST.get("comment", "")
    old = mr.status

    if action == "approved":
        mr.status = ManpowerRequest.STATUS_APPROVED
        from recruitment.approvals.engine import _create_recruitment
        _create_recruitment(mr)
        try:
            import threading
            from recruitment.email_utils import email_manpower_approved
            threading.Thread(target=email_manpower_approved, args=(mr,), daemon=True).start()
        except Exception:
            pass
        messages.success(request, _(f"{mr.requisition_no} approved."))
    elif action == "rejected":
        mr.status = ManpowerRequest.STATUS_REJECTED
        try:
            import threading
            from recruitment.email_utils import email_manpower_rejected
            threading.Thread(target=email_manpower_rejected, args=(mr, comment), daemon=True).start()
        except Exception:
            pass
        messages.warning(request, _(f"{mr.requisition_no} rejected."))
    else:
        messages.error(request, _("Invalid action."))
        return redirect(reverse("approval-inbox"))

    mr.save()
    ManpowerRequestStatusLog.objects.create(
        request=mr, from_status=old, to_status=mr.status,
        changed_by=emp, note=comment or "Manual HR decision (no rule matched)"
    )
    return redirect(reverse("approval-inbox"))


@login_required
def approval_action(request, approval_id):
    approval = get_object_or_404(ManpowerApproval, id=approval_id)
    action = request.POST.get("action")
    comment = request.POST.get("comment", "")
    allowed = (
        ManpowerApproval.ACTION_APPROVED,
        ManpowerApproval.ACTION_REJECTED,
        ManpowerApproval.ACTION_QUERIED,
    )
    if action not in allowed:
        messages.error(request, _("Invalid action."))
        return redirect(reverse("approval-inbox"))
    if action == ManpowerApproval.ACTION_QUERIED and not comment.strip():
        messages.error(request, _("Please include the query before sending the request back."))
        return redirect(reverse("manpower-detail", args=[approval.request_id]))
    advance(approval.request, action, request.user, comment)
    if action == ManpowerApproval.ACTION_QUERIED:
        messages.success(request, _(f"Request {approval.request.requisition_no} returned to requester."))
    else:
        messages.success(request, _(f"Request {approval.request.requisition_no} {action}."))
    return redirect(reverse("approval-inbox"))


@login_required
def manpower_resubmit(request, req_id):
    """Requester responds to a query — attach clarification doc + resume the chain."""
    from recruitment.approvals.engine import resubmit_after_query

    mr = get_object_or_404(ManpowerRequest, id=req_id)
    emp = _get_employee(request.user)
    if mr.requested_by_id != getattr(emp, "id", None) and not request.user.is_superuser:
        messages.error(request, _("Only the requester can resubmit this request."))
        return redirect(reverse("manpower-detail", args=[req_id]))
    if mr.status != ManpowerRequest.STATUS_QUERIED:
        messages.error(request, _("This request is not in a queried state."))
        return redirect(reverse("manpower-detail", args=[req_id]))

    comment = request.POST.get("comment", "")
    attachment = request.FILES.get("clarification_document")
    if not attachment and not mr.clarification_document:
        messages.error(request, _("Please attach the clarification document."))
        return redirect(reverse("manpower-detail", args=[req_id]))

    resubmit_after_query(mr, request.user, comment=comment, attachment=attachment)
    messages.success(request, _("Request resubmitted — back in the approval chain."))
    return redirect(reverse("manpower-detail", args=[req_id]))


@login_required
def manpower_advance_stage(request, req_id):
    """Move an approved ManpowerRequest forward through the pipeline stages."""
    mr = get_object_or_404(ManpowerRequest, id=req_id)
    emp = _get_employee(request.user)

    PIPELINE = [
        ManpowerRequest.STATUS_APPROVED,
        ManpowerRequest.STATUS_SOURCING,
        ManpowerRequest.STATUS_INTERVIEWING,
        ManpowerRequest.STATUS_OFFER,
        ManpowerRequest.STATUS_JOINED,
        ManpowerRequest.STATUS_CLOSED,
    ]

    target = request.POST.get("status")
    if target and target in [s for s, _ in ManpowerRequest.STATUS_CHOICES]:
        old = mr.status
        mr.status = target
        mr.save()
        ManpowerRequestStatusLog.objects.create(
            request=mr, from_status=old, to_status=target,
            changed_by=emp, note=f"Stage advanced to {target}"
        )
        messages.success(request, _(f"Status updated to {mr.get_status_display()}."))
    return redirect(reverse("manpower-detail", args=[req_id]))


@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def approval_rules(request):
    rules = ApprovalRule.objects.prefetch_related("steps").all()
    return render(request, "recruitment/manpower/rule_list.html", {"rules": rules})


@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def approval_rule_create(request):
    from base.models import Department

    if request.method == "POST":
        data = request.POST
        emp = _get_employee(request.user)
        company = getattr(emp, "company_id", None) if emp else None
        if not company and request.user.is_superuser:
            from base.models import Company
            company = Company.objects.first()

        rule = ApprovalRule.objects.create(
            company_id=company,
            name=data["name"],
            grade_min=data.get("grade_min", ""),
            grade_max=data.get("grade_max", ""),
            priority=int(data.get("priority") or 0),
        )
        dept_id = data.get("department")
        if dept_id:
            rule.department = Department.objects.filter(id=dept_id).first()
            rule.save()

        # Steps
        approver_types = data.getlist("approver_type")
        sla_hours = data.getlist("sla_hours")
        for seq, (atype, sla) in enumerate(zip(approver_types, sla_hours), start=1):
            ApprovalStep.objects.create(
                rule=rule, sequence=seq, approver_type=atype, sla_hours=int(sla or 48)
            )
        messages.success(request, _("Approval rule created."))
        return redirect(reverse("approval-rules"))

    from base.models import Department
    return render(
        request,
        "recruitment/manpower/rule_form.html",
        {
            "departments": Department.objects.all(),
            "approver_types": ApprovalStep.APPROVER_TYPES,
        },
    )


@login_required
def document_search(request):
    """Module 9 — search by document ref (MR-XXXX or OL-XXXX) to see real-time location."""
    from recruitment.models import OfferLetter, ManpowerRequest, ManpowerRequestStatusLog
    from recruitment.models_approvals import ManpowerApproval, OfferApproval

    query = request.GET.get("q", "").strip()
    result = None
    doc_type = None
    timeline = []
    current_approver = None
    error = None

    if query:
        if query.upper().startswith("OL-"):
            offer = OfferLetter.objects.filter(offer_no__iexact=query).select_related("candidate_id", "created_by").first()
            if offer:
                doc_type = "offer"
                result = offer
                approvals = offer.approvals.select_related("step", "approver", "acted_by").order_by("step__sequence")
                for appr in approvals:
                    timeline.append({
                        "label": f"Step {appr.step.sequence} — {appr.step.get_approver_type_display()}" if appr.step else "Approval",
                        "status": appr.action,
                        "actor": str(appr.acted_by or appr.approver or "—"),
                        "at": appr.acted_at,
                    })
                    if appr.action == "pending":
                        current_approver = str(appr.approver) if appr.approver else "Unassigned"
                if not current_approver and offer.status not in ("draft",):
                    current_approver = "HR / Completed"
            else:
                error = f"No offer letter found with ref: {query}"

        elif query.upper().startswith("MR-"):
            mr = ManpowerRequest.objects.filter(requisition_no__iexact=query).select_related("requested_by", "department").first()
            if mr:
                doc_type = "manpower"
                result = mr
                for log in ManpowerRequestStatusLog.objects.filter(request=mr).order_by("changed_at"):
                    timeline.append({
                        "label": log.get_new_status_display() if hasattr(log, "get_new_status_display") else log.new_status,
                        "status": log.new_status,
                        "actor": str(log.changed_by) if log.changed_by else "System",
                        "at": log.changed_at,
                    })
                pending_appr = ManpowerApproval.objects.filter(request=mr, action="pending").select_related("approver").first()
                current_approver = str(pending_appr.approver) if pending_appr and pending_appr.approver else ("HR" if mr.status != "draft" else None)
            else:
                error = f"No manpower request found with ref: {query}"
        else:
            error = "Enter a document ref starting with OL- (offer letter) or MR- (manpower request)."

    return render(request, "recruitment/document_search.html", {
        "query": query,
        "result": result,
        "doc_type": doc_type,
        "timeline": timeline,
        "current_approver": current_approver,
        "error": error,
    })
