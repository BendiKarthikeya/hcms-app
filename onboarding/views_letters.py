"""
onboarding/views_letters.py

Letters section: Offer Letter, Medical Letter, Visa Letter tabs.
Shows candidates promoted to onboarding, allows creating and managing offer letters
with a multi-step approval chain before sending to the candidate.

Module 9 — Document Tracking & Audit Trail:
  - Every state change is written to the relevant StatusLog table (actor + timestamp).
  - Search by document number (offer_no / doc_no) is supported via ?q= on the listing.
"""

import re
import uuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from recruitment.models import (
    Candidate, OfferLetter, OfferLetterApproval, OfferLetterTemplate,
    MedicalLetter, MedicalLetterTemplate, VisaLetter, VisaLetterTemplate,
    OfferLetterStatusLog, MedicalLetterStatusLog, VisaLetterStatusLog,
)
from employee.models import Employee


# ── Template processing helper ───────────────────────────────────────────────

def _process_template_body(body_html, context):
    """
    Process simple {% if varname %}...{% endif %} blocks stored in offer letter
    template body_html strings. Strips the blocks when the variable is falsy.
    """
    def _replace_if(m):
        var_name = m.group(1).strip()
        inner = m.group(2)
        return inner if context.get(var_name) else ""

    result = re.sub(
        r"\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}",
        _replace_if,
        body_html,
        flags=re.DOTALL,
    )
    # Clean up any leftover stray {% %} tags
    result = re.sub(r"\{%[^%]*%\}", "", result)
    return result.strip()


# ── Audit helpers ────────────────────────────────────────────────────────────

def _log_offer(offer, from_status, to_status, actor, note=""):
    OfferLetterStatusLog.objects.create(
        offer_letter=offer,
        from_status=from_status,
        to_status=to_status,
        actor=actor,
        note=note,
    )


def _log_medical(letter, from_status, to_status, actor, note=""):
    MedicalLetterStatusLog.objects.create(
        medical_letter=letter,
        from_status=from_status,
        to_status=to_status,
        actor=actor,
        note=note,
    )


def _log_visa(letter, from_status, to_status, actor, note=""):
    VisaLetterStatusLog.objects.create(
        visa_letter=letter,
        from_status=from_status,
        to_status=to_status,
        actor=actor,
        note=note,
    )


# ── Approval chain helpers ───────────────────────────────────────────────────

def _get_approval_chain(offer_letter):
    """Return ordered approval steps for an offer letter."""
    return offer_letter.approvals.all().order_by("sequence")


def _create_approval_chain(offer_letter, request):
    """
    Build the approval chain for an offer letter:
    HR (step 1) → Raiser/raised_by (step 2) → Raiser's reporting manager (step 3) → First active superuser (step 4)
    """
    from django.contrib.auth.models import User

    seen = set()
    steps = []

    def _add(emp):
        if emp and emp.id not in seen:
            seen.add(emp.id)
            steps.append(emp)

    candidate = offer_letter.candidate_id
    recruitment = candidate.recruitment_id

    hr_emp = getattr(request.user, "employee_get", None)
    _add(hr_emp)

    raiser = recruitment.raised_by if recruitment else None
    if raiser:
        _add(raiser)
        try:
            mgr = raiser.get_reporting_manager()
            if mgr:
                _add(mgr)
        except Exception:
            pass

    su_user = User.objects.filter(is_superuser=True, is_active=True).order_by("pk").first()
    if su_user:
        su_emp = getattr(su_user, "employee_get", None)
        if su_emp:
            _add(su_emp)

    for seq, approver in enumerate(steps, start=1):
        OfferLetterApproval.objects.create(
            offer_letter=offer_letter,
            approver=approver,
            sequence=seq,
        )

    _notify_all_approvers(offer_letter, steps, request)

    if steps:
        _notify_approver(offer_letter, steps[0], request)


def _ensure_superusers_in_chain(offer_letter, request):
    """Append any active superuser employees missing from this offer's chain as
    pending final steps. Safe to call repeatedly; only adds steps that are not
    already present. Notifies the first newly-added step if the rest of the
    chain is already fully signed."""
    from django.contrib.auth.models import User

    existing_approver_ids = set(
        offer_letter.approvals.values_list("approver_id", flat=True)
    )
    superuser_emps = []
    for su_user in User.objects.filter(is_superuser=True, is_active=True).order_by("pk"):
        emp = getattr(su_user, "employee_get", None)
        if emp and emp.id not in existing_approver_ids:
            superuser_emps.append(emp)

    if not superuser_emps:
        return

    last_seq = offer_letter.approvals.aggregate(
        m=Max("sequence")
    ).get("m") or 0
    new_steps = []
    for offset, emp in enumerate(superuser_emps, start=1):
        new_steps.append(
            OfferLetterApproval.objects.create(
                offer_letter=offer_letter,
                approver=emp,
                sequence=last_seq + offset,
            )
        )

    # If everyone before the newly-added step has acted, ping the first new step.
    earlier_pending = offer_letter.approvals.filter(
        status="pending", sequence__lte=last_seq
    ).exists()
    if not earlier_pending and new_steps:
        _notify_approver(offer_letter, new_steps[0].approver, request)


def _notify_all_approvers(offer_letter, approver_list, request):
    """Email all approvers that a new offer letter needs their e-signature."""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        candidate_name = offer_letter.candidate_id.name
        letters_url = request.build_absolute_uri(reverse("onboarding-letters") + "?tab=offer")
        for approver in approver_list:
            emp_user = getattr(approver, "employee_user_id", None)
            if not emp_user:
                continue
            email = getattr(emp_user, "email", None) or getattr(approver, "email", None)
            if not email:
                continue
            body = (
                f"Dear {approver},\n\n"
                f"An offer letter has been created for candidate {candidate_name} "
                f"for the position of {offer_letter.position}.\n\n"
                f"Your e-signature is required as part of the approval chain.\n"
                f"Please check your notifications or visit the Letters page:\n{letters_url}\n\n"
                f"Best Regards,\nHuman Resources"
            )
            send_mail(
                subject=f"E-Signature Required — Offer Letter for {candidate_name}",
                message=body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "hr@company.com"),
                recipient_list=[email],
                fail_silently=True,
            )
    except Exception:
        pass


def _notify_approver(offer_letter, approver, request):
    """Send in-app notification to the next approver."""
    try:
        from notifications.signals import notify
        recipient_user = approver.employee_user_id
        if recipient_user:
            notify.send(
                request.user,
                recipient=recipient_user,
                verb=f"Offer letter for {offer_letter.candidate_id.name} requires your e-signature.",
                icon="document-text",
                redirect="/onboarding/letters/",
            )
    except Exception:
        pass


def _email_candidate_offer(offer_letter, request):
    """Email the candidate once all approvals are complete."""
    from django.core.signing import TimestampSigner
    candidate = offer_letter.candidate_id
    accept_token = TimestampSigner(salt="offer-accept").sign(str(offer_letter.id))

    accept_url = request.build_absolute_uri(
        reverse("candidate-accept-offer", kwargs={"token": accept_token})
    )
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        body = (
            f"Dear {candidate.name},\n\n"
            f"We are pleased to inform you that your offer letter for the position of "
            f"{offer_letter.position} has been fully approved and signed.\n\n"
            f"{offer_letter.generated_letter or offer_letter.letter_template or ''}\n\n"
            f"To accept this offer, please click the link below:\n{accept_url}\n\n"
            f"We look forward to welcoming you to our team.\n\nBest Regards,\nHuman Resources"
        )
        send_mail(
            subject=f"Your Offer Letter — {offer_letter.position}",
            message=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "hr@company.com"),
            recipient_list=[candidate.email],
            fail_silently=True,
        )
    except Exception:
        pass


# ── Main letters view ────────────────────────────────────────────────────────

@login_required
def letters_view(request):
    """Main Letters page with 3 tabs: Offer Letter, Medical Letter, Visa Letter."""
    from recruitment.models_interview import InterviewRound
    from recruitment.models import InterviewSchedule

    # Candidates whose interview is marked complete (interview.completed=True OR all rounds done)
    interviews_all_done = []
    for iv in InterviewSchedule.objects.select_related("candidate_id").prefetch_related("rounds"):
        rounds = iv.rounds.all()
        all_rounds_done = rounds.exists() and not rounds.filter(completed=False).exists()
        if iv.completed or all_rounds_done:
            interviews_all_done.append(iv.candidate_id_id)

    promoted_ids = set(
        Candidate.objects.filter(promoted_to_onboarding=True).values_list("id", flat=True)
    )
    all_ids = set(interviews_all_done) | promoted_ids

    # ── Search by document number ────────────────────────────────────────────
    q = request.GET.get("q", "").strip()
    active_tab = request.GET.get("tab", "offer")

    if q:
        offer_ids = set(
            OfferLetter.objects.filter(offer_no__icontains=q).values_list("candidate_id_id", flat=True)
        )
        medical_ids = set(
            MedicalLetter.objects.filter(doc_no__icontains=q).values_list("candidate_id_id", flat=True)
        )
        visa_ids = set(
            VisaLetter.objects.filter(doc_no__icontains=q).values_list("candidate_id_id", flat=True)
        )
        # Also search by candidate name
        name_ids = set(
            Candidate.objects.filter(name__icontains=q, id__in=all_ids).values_list("id", flat=True)
        )
        matched_ids = (offer_ids | medical_ids | visa_ids | name_ids) & all_ids
        filtered_ids = matched_ids
    else:
        filtered_ids = all_ids

    promoted_candidates = Candidate.objects.filter(id__in=filtered_ids).select_related(
        "recruitment_id", "stage_id"
    ).prefetch_related("offer_letter__approvals")

    # ── Offer Letter tab data ────────────────────────────────────────────────
    offer_data = []
    for cand in promoted_candidates:
        offer = getattr(cand, "offer_letter", None)
        if offer:
            if not offer.approvals.exists():
                _create_approval_chain(offer, request)
            chain = list(offer.approvals.select_related("approver").order_by("sequence"))
            active_found = False
            for step in chain:
                if step.status == "pending" and not active_found:
                    step.display_status = "active"
                    active_found = True
                elif step.status == "pending":
                    step.display_status = "waiting"
                else:
                    step.display_status = step.status
            current_step = next((s for s in chain if s.display_status == "active"), None)
            audit_logs = list(offer.status_logs.order_by("timestamp"))
            offer_data.append({
                "candidate": cand,
                "offer": offer,
                "chain": chain,
                "current_approver": current_step.approver if current_step else None,
                "all_approved": bool(chain) and not any(s.status == "pending" for s in chain),
                "signed_count": sum(1 for s in chain if s.signature_image),
                "audit_logs": audit_logs,
            })
        else:
            offer_data.append({
                "candidate": cand,
                "offer": None,
                "chain": [],
                "current_approver": None,
                "all_approved": False,
                "audit_logs": [],
            })

    # Only show approvals where THIS user is the ACTIVE (first pending) step
    current_employee = getattr(request.user, "employee_get", None)
    my_pending_approvals = []
    if current_employee:
        for appr in OfferLetterApproval.objects.filter(
            approver=current_employee, status="pending"
        ).select_related("offer_letter__candidate_id").order_by("offer_letter__candidate_id__name"):
            first_pending = appr.offer_letter.approvals.filter(
                status="pending"
            ).order_by("sequence").first()
            if first_pending and first_pending.id == appr.id:
                my_pending_approvals.append(appr)

    templates = OfferLetterTemplate.objects.filter(is_active=True)
    medical_templates = MedicalLetterTemplate.objects.filter(is_active=True)
    visa_templates = VisaLetterTemplate.objects.filter(is_active=True)

    all_candidates = Candidate.objects.filter(id__in=filtered_ids).select_related("recruitment_id", "stage_id")

    # ── Medical Letter tab data ──────────────────────────────────────────────
    medical_data = []
    for cand in all_candidates:
        letter = MedicalLetter.objects.filter(candidate_id=cand).first()
        audit_logs = list(letter.status_logs.order_by("timestamp")) if letter else []
        medical_data.append({"candidate": cand, "letter": letter, "audit_logs": audit_logs})

    # ── Visa Letter tab data ─────────────────────────────────────────────────
    visa_data = []
    for cand in all_candidates:
        letter = VisaLetter.objects.filter(candidate_id=cand).first()
        audit_logs = list(letter.status_logs.order_by("timestamp")) if letter else []
        visa_data.append({"candidate": cand, "letter": letter, "audit_logs": audit_logs})

    import os
    docuseal_api_key = os.environ.get("DOCUSEAL_API_KEY", "")

    return render(request, "onboarding/letters/letters.html", {
        "offer_data": offer_data,
        "my_pending_approvals": my_pending_approvals,
        "templates": templates,
        "medical_templates": medical_templates,
        "visa_templates": visa_templates,
        "medical_data": medical_data,
        "visa_data": visa_data,
        "active_tab": active_tab,
        "docuseal_enabled": bool(docuseal_api_key),
        "search_query": q,
        "total_count": len(all_ids),
        "filtered_count": len(filtered_ids),
    })


# ── Offer Letter views ───────────────────────────────────────────────────────

@login_required
def offer_letter_create(request, cand_id):
    """Create or update an offer letter for a promoted candidate."""
    candidate = get_object_or_404(Candidate, id=cand_id)

    existing = OfferLetter.objects.filter(candidate_id=candidate).first()
    if existing:
        messages.info(request, _("An offer letter already exists for this candidate."))
        return redirect(f"{reverse('onboarding-letters')}?tab=offer")

    templates = OfferLetterTemplate.objects.filter(is_active=True)

    if request.method == "POST":
        template_id = request.POST.get("template_id")
        custom_body = request.POST.get("custom_body", "").strip()
        position = request.POST.get("position", "").strip() or str(candidate.job_position_id or "")
        department = request.POST.get("department", "").strip()
        basic_salary = request.POST.get("basic_salary", 0)
        joining_date = request.POST.get("joining_date") or timezone.now().date().isoformat()

        body_html = custom_body
        if template_id:
            tmpl = OfferLetterTemplate.objects.filter(id=template_id).first()
            if tmpl:
                company_name = ""
                try:
                    company_name = candidate.recruitment_id.company_id.company
                except Exception:
                    pass
                ctx = {"department": department, "position": position, "company_name": company_name}
                raw = tmpl.body_html.replace("{{candidate_name}}", candidate.name or "").replace(
                    "{{position}}", position).replace("{{department}}", department).replace(
                    "{{joining_date}}", joining_date).replace(
                    "{{basic_salary}}", str(basic_salary)).replace(
                    "{{company_name}}", company_name)
                body_html = _process_template_body(raw, ctx)

        try:
            actor = getattr(request.user, "employee_get", None)
            offer = OfferLetter.objects.create(
                candidate_id=candidate,
                position=position or "TBD",
                department=department,
                basic_salary=basic_salary or 0,
                joining_date=joining_date,
                letter_template=body_html,
                generated_letter=body_html,
                created_by=actor,
                status="draft",
            )
            _log_offer(offer, "", "draft", actor, f"Created by {actor}")
            _create_approval_chain(offer, request)
            messages.success(request, _(f"Offer letter created for {candidate.name}. All approvers have been notified by email."))
        except Exception as e:
            messages.error(request, str(e))

        return redirect(f"{reverse('onboarding-letters')}?tab=offer")

    # Resolve applied position/department with fallbacks:
    # 1) candidate.job_position_id
    # 2) recruitment.job_position_id
    # 3) first of recruitment.open_positions
    # 4) recruitment.title (string only — no department available)
    applied_position = ""
    applied_department = ""
    jp = getattr(candidate, "job_position_id", None)
    rec = getattr(candidate, "recruitment_id", None)
    if jp is None and rec is not None:
        jp = getattr(rec, "job_position_id", None) or rec.open_positions.first()
    if jp is not None:
        applied_position = str(getattr(jp, "job_position", "") or "")
        dept = getattr(jp, "department_id", None)
        if dept is not None:
            applied_department = str(getattr(dept, "department", "") or "")
    if not applied_position and rec is not None:
        applied_position = str(getattr(rec, "title", "") or "")

    return render(request, "onboarding/letters/offer_create.html", {
        "candidate": candidate,
        "templates": templates,
        "applied_position": applied_position,
        "applied_department": applied_department,
    })


@login_required
def offer_letter_edit(request, letter_id):
    """Edit an existing draft offer letter."""
    offer = get_object_or_404(OfferLetter, id=letter_id, status="draft")
    candidate = offer.candidate_id
    templates = OfferLetterTemplate.objects.filter(is_active=True)

    # Auto-populate position/department from candidate's applied role if not yet set
    if not offer.position and candidate.job_position_id:
        offer.position = str(candidate.job_position_id.job_position)
    if not offer.department and candidate.job_position_id and candidate.job_position_id.department_id:
        offer.department = str(candidate.job_position_id.department_id.department)

    if request.method == "POST":
        position = request.POST.get("position", "").strip() or offer.position
        department = request.POST.get("department", "").strip()
        basic_salary = request.POST.get("basic_salary", offer.basic_salary)
        gross_salary = request.POST.get("gross_salary", "").strip() or None
        joining_date = request.POST.get("joining_date") or str(offer.joining_date or "")
        role_type = request.POST.get("role_type", "full_time")
        contract_duration = request.POST.get("contract_duration", "").strip() or None
        probation_period = request.POST.get("probation_period", "").strip()
        custom_body = request.POST.get("custom_body", "").strip()
        template_id = request.POST.get("template_id")

        body_html = custom_body
        if template_id:
            tmpl = OfferLetterTemplate.objects.filter(id=template_id).first()
            if tmpl:
                company_name = ""
                try:
                    company_name = candidate.recruitment_id.company_id.company
                except Exception:
                    pass
                ctx = {"department": department, "position": position, "company_name": company_name}
                raw = tmpl.body_html.replace("{{candidate_name}}", candidate.name or "").replace(
                    "{{position}}", position).replace("{{department}}", department).replace(
                    "{{joining_date}}", joining_date).replace(
                    "{{basic_salary}}", str(basic_salary)).replace(
                    "{{gross_salary}}", str(gross_salary or "")).replace(
                    "{{company_name}}", company_name)
                body_html = _process_template_body(raw, ctx)

        offer.position = position
        offer.department = department
        offer.basic_salary = basic_salary or 0
        offer.gross_salary = gross_salary
        offer.joining_date = joining_date or None
        offer.role_type = role_type
        offer.contract_duration = contract_duration
        if probation_period.isdigit():
            offer.probation_period = int(probation_period)
        offer.letter_template = body_html
        offer.generated_letter = body_html
        offer.save(update_fields=[
            "position", "department", "basic_salary", "gross_salary",
            "joining_date", "role_type", "contract_duration", "probation_period",
            "letter_template", "generated_letter",
        ])

        actor = getattr(request.user, "employee_get", None)
        _log_offer(offer, "draft", "draft", actor, "Letter content edited")

        messages.success(request, _("Offer letter updated."))
        return redirect(f"{reverse('onboarding-letters')}?tab=offer")

    return render(request, "onboarding/letters/offer_edit.html", {
        "offer": offer,
        "candidate": candidate,
        "templates": templates,
    })


@login_required
def offer_letter_approve(request, letter_id):
    """Approve current approval step for an offer letter."""
    if request.method != "POST":
        return HttpResponse(status=405)

    offer = get_object_or_404(OfferLetter, id=letter_id)
    current_employee = getattr(request.user, "employee_get", None)

    step = offer.approvals.filter(approver=current_employee, status="pending").order_by("sequence").first()
    if not step:
        messages.error(request, _("You don't have a pending approval step for this offer letter."))
        return redirect(f"{reverse('onboarding-letters')}?tab=offer")

    prev_status = offer.status
    step.status = "approved"
    step.acted_at = timezone.now()
    sig = request.POST.get("signature_data", "").strip()
    if sig:
        step.signature_image = sig
    step.save(update_fields=["status", "acted_at", "signature_image"])

    _log_offer(offer, prev_status, offer.status, current_employee,
               f"Step {step.sequence} e-signed by {current_employee}")

    next_step = offer.approvals.filter(status="pending").order_by("sequence").first()
    if next_step:
        _notify_approver(offer, next_step.approver, request)
        try:
            import threading
            from recruitment.email_utils import email_offer_approval_step
            threading.Thread(
                target=email_offer_approval_step,
                args=(next_step.approver, offer, request),
                daemon=True,
            ).start()
        except Exception:
            pass
        messages.success(request, _(f"Approved. Waiting for next approver: {next_step.approver}."))
    else:
        offer.status = "sent"
        offer.sent_date = timezone.now()
        offer.save(update_fields=["status", "sent_date"])
        offer.candidate_id.offer_letter_status = "sent"
        offer.candidate_id.save(update_fields=["offer_letter_status"])
        _log_offer(offer, prev_status, "sent", current_employee,
                   "All approvals complete — offer sent to candidate")
        _email_candidate_offer(offer, request)

        try:
            from notifications.signals import notify
            from django.contrib.auth.models import User
            hr_users = list(User.objects.filter(is_superuser=True, is_active=True))
            if offer.created_by and offer.created_by.employee_user_id:
                hr_users.append(offer.created_by.employee_user_id)
            if hr_users:
                notify.send(
                    request.user,
                    recipient=hr_users,
                    verb=f"All approvals complete for {offer.candidate_id.name}. Offer letter sent to candidate.",
                    icon="checkmark-circle",
                    redirect="/onboarding/letters/",
                )
        except Exception:
            pass

        messages.success(request, _("All approvals complete. Offer letter has been sent to the candidate."))

    return redirect(f"{reverse('onboarding-letters')}?tab=offer")


@login_required
def offer_letter_reject(request, letter_id):
    """Reject current approval step and notify HR with feedback."""
    if request.method != "POST":
        return HttpResponse(status=405)

    offer = get_object_or_404(OfferLetter, id=letter_id)
    current_employee = getattr(request.user, "employee_get", None)
    feedback = request.POST.get("feedback", "").strip()

    step = offer.approvals.filter(approver=current_employee, status="pending").order_by("sequence").first()
    if not step:
        messages.error(request, _("You don't have a pending approval step for this offer letter."))
        return redirect(f"{reverse('onboarding-letters')}?tab=offer")

    prev_status = offer.status
    step.status = "rejected"
    step.feedback = feedback
    step.acted_at = timezone.now()
    step.save(update_fields=["status", "feedback", "acted_at"])

    offer.approvals.filter(status="pending").update(status="rejected")
    offer.status = "rejected"
    offer.save(update_fields=["status"])

    _log_offer(offer, prev_status, "rejected", current_employee,
               f"Rejected by {current_employee}. Feedback: {feedback or 'None'}")

    try:
        from notifications.signals import notify
        from django.contrib.auth.models import User
        hr_users = list(User.objects.filter(is_superuser=True, is_active=True))
        if offer.created_by and offer.created_by.employee_user_id:
            hr_users.append(offer.created_by.employee_user_id)
        if hr_users:
            notify.send(
                request.user,
                recipient=hr_users,
                verb=f"Offer letter for {offer.candidate_id.name} was rejected by {current_employee}. Feedback: {feedback or 'No feedback provided.'}",
                icon="close-circle",
                redirect="/onboarding/letters/",
            )
    except Exception:
        pass

    try:
        import threading
        from recruitment.email_utils import email_offer_approval_rejected_hr
        threading.Thread(
            target=email_offer_approval_rejected_hr,
            args=(offer, current_employee, feedback, request),
            daemon=True,
        ).start()
    except Exception:
        pass

    messages.warning(request, _("Offer letter rejected. HR has been notified."))
    return redirect(f"{reverse('onboarding-letters')}?tab=offer")


@login_required
def offer_letter_send(request, letter_id):
    """Manually send a fully-approved offer letter to the candidate."""
    if request.method != "POST":
        return HttpResponse(status=405)

    offer = get_object_or_404(OfferLetter, id=letter_id)

    if offer.approvals.filter(status="pending").exists():
        messages.error(request, _("Cannot send — the offer letter still has pending approvals."))
        return redirect(f"{reverse('onboarding-letters')}?tab=offer")

    if offer.approvals.filter(status="rejected").exists():
        messages.error(request, _("Cannot send — the offer letter was rejected."))
        return redirect(f"{reverse('onboarding-letters')}?tab=offer")

    prev_status = offer.status
    _email_candidate_offer(offer, request)
    offer.status = "sent"
    offer.sent_date = timezone.now()
    offer.save(update_fields=["status", "sent_date"])
    offer.candidate_id.offer_letter_status = "sent"
    offer.candidate_id.save(update_fields=["offer_letter_status"])

    actor = getattr(request.user, "employee_get", None)
    _log_offer(offer, prev_status, "sent", actor, "Manually sent to candidate")

    messages.success(request, _(f"Offer letter sent to {offer.candidate_id.email}."))
    return redirect(f"{reverse('onboarding-letters')}?tab=offer")


# ── Audit trail view (HTMX / JSON) ──────────────────────────────────────────

def _format_audit_logs(qs):
    logs = list(qs.select_related("actor").order_by("timestamp").values(
        "from_status", "to_status", "note", "timestamp",
        "actor__employee_first_name", "actor__employee_last_name",
    ))
    for entry in logs:
        fn = entry.pop("actor__employee_first_name") or ""
        ln = entry.pop("actor__employee_last_name") or ""
        entry["actor"] = f"{fn} {ln}".strip() or "System"
        entry["timestamp"] = entry["timestamp"].strftime("%d %b %Y %H:%M")
    return logs


@login_required
def offer_letter_audit(request, letter_id):
    """Return the audit trail for an offer letter as JSON (for the modal)."""
    offer = get_object_or_404(OfferLetter, id=letter_id)
    return JsonResponse({"logs": _format_audit_logs(offer.status_logs), "offer_no": offer.offer_no})


@login_required
def medical_letter_audit(request, letter_id):
    """Return the audit trail for a medical letter as JSON."""
    letter = get_object_or_404(MedicalLetter, id=letter_id)
    return JsonResponse({"logs": _format_audit_logs(letter.status_logs), "doc_no": letter.doc_no})


@login_required
def visa_letter_audit(request, letter_id):
    """Return the audit trail for a visa letter as JSON."""
    letter = get_object_or_404(VisaLetter, id=letter_id)
    return JsonResponse({"logs": _format_audit_logs(letter.status_logs), "doc_no": letter.doc_no})


# ── Medical Letter views ─────────────────────────────────────────────────────

@login_required
def medical_letter_create(request, cand_id):
    """Create a medical letter for a candidate."""
    candidate = get_object_or_404(Candidate, id=cand_id)

    if MedicalLetter.objects.filter(candidate_id=candidate).exists():
        messages.info(request, _("A medical letter already exists for this candidate."))
        return redirect(f"{reverse('onboarding-letters')}?tab=medical")

    if request.method == "POST":
        template_id = request.POST.get("template_id")
        custom_body = request.POST.get("custom_body", "").strip()

        content = custom_body
        if template_id:
            tmpl = MedicalLetterTemplate.objects.filter(id=template_id).first()
            if tmpl:
                company_name = ""
                try:
                    company_name = candidate.recruitment_id.company_id.company
                except Exception:
                    pass
                position = str(candidate.job_position_id or "")
                content = tmpl.body_html.replace("{{candidate_name}}", candidate.name or "").replace(
                    "{{position}}", position).replace("{{company_name}}", company_name)

        actor = getattr(request.user, "employee_get", None)
        letter = MedicalLetter.objects.create(
            candidate_id=candidate,
            content=content,
            created_by=actor,
        )
        _log_medical(letter, "", "draft", actor, f"Created by {actor}")

        try:
            from notifications.signals import notify
            from django.contrib.auth.models import User
            hr_users = list(User.objects.filter(is_superuser=True, is_active=True))
            if hr_users:
                notify.send(
                    request.user,
                    recipient=hr_users,
                    verb=f"Medical letter created for {candidate.name}. Awaiting HR e-signature.",
                    icon="medical-outline",
                    redirect="/onboarding/letters/?tab=medical",
                )
        except Exception:
            pass

        messages.success(request, _(f"Medical letter created for {candidate.name}."))
        return redirect(f"{reverse('onboarding-letters')}?tab=medical")

    templates = MedicalLetterTemplate.objects.filter(is_active=True)
    return render(request, "onboarding/letters/medical_create.html", {
        "candidate": candidate,
        "templates": templates,
    })


@login_required
def medical_letter_sign(request, letter_id):
    """HR signs the medical letter."""
    if request.method != "POST":
        return HttpResponse(status=405)

    letter = get_object_or_404(MedicalLetter, id=letter_id)
    sig = request.POST.get("signature_data", "").strip()
    actor = getattr(request.user, "employee_get", None)

    prev_status = letter.status
    letter.hr_signed = True
    letter.hr_signature = sig
    letter.hr_signed_by = actor
    letter.hr_signed_at = timezone.now()
    letter.status = "signed"
    letter.save(update_fields=["hr_signed", "hr_signature", "hr_signed_by", "hr_signed_at", "status"])

    _log_medical(letter, prev_status, "signed", actor, f"HR e-signed by {actor}")

    messages.success(request, _("Medical letter signed."))
    return redirect(f"{reverse('onboarding-letters')}?tab=medical")


# ── Visa Letter views ────────────────────────────────────────────────────────

@login_required
def visa_letter_create(request, cand_id):
    """Create a visa support letter for a candidate."""
    candidate = get_object_or_404(Candidate, id=cand_id)

    if VisaLetter.objects.filter(candidate_id=candidate).exists():
        messages.info(request, _("A visa letter already exists for this candidate."))
        return redirect(f"{reverse('onboarding-letters')}?tab=visa")

    if request.method == "POST":
        template_id = request.POST.get("template_id")
        custom_body = request.POST.get("custom_body", "").strip()

        content = custom_body
        if template_id:
            tmpl = VisaLetterTemplate.objects.filter(id=template_id).first()
            if tmpl:
                company_name = ""
                try:
                    company_name = candidate.recruitment_id.company_id.company
                except Exception:
                    pass
                position = str(candidate.job_position_id or "")
                content = tmpl.body_html.replace("{{candidate_name}}", candidate.name or "").replace(
                    "{{position}}", position).replace("{{company_name}}", company_name)

        actor = getattr(request.user, "employee_get", None)
        letter = VisaLetter.objects.create(
            candidate_id=candidate,
            content=content,
            created_by=actor,
        )
        _log_visa(letter, "", "draft", actor, f"Created by {actor}")

        try:
            from notifications.signals import notify
            from django.contrib.auth.models import User
            hr_users = list(User.objects.filter(is_superuser=True, is_active=True))
            if hr_users:
                notify.send(
                    request.user,
                    recipient=hr_users,
                    verb=f"Visa letter created for {candidate.name}. Awaiting HR e-signature.",
                    icon="globe-outline",
                    redirect="/onboarding/letters/?tab=visa",
                )
        except Exception:
            pass

        messages.success(request, _(f"Visa letter created for {candidate.name}."))
        return redirect(f"{reverse('onboarding-letters')}?tab=visa")

    templates = VisaLetterTemplate.objects.filter(is_active=True)
    return render(request, "onboarding/letters/visa_create.html", {
        "candidate": candidate,
        "templates": templates,
    })


@login_required
def visa_letter_sign(request, letter_id):
    """HR signs the visa letter."""
    if request.method != "POST":
        return HttpResponse(status=405)

    letter = get_object_or_404(VisaLetter, id=letter_id)
    sig = request.POST.get("signature_data", "").strip()
    actor = getattr(request.user, "employee_get", None)

    prev_status = letter.status
    letter.hr_signed = True
    letter.hr_signature = sig
    letter.hr_signed_by = actor
    letter.hr_signed_at = timezone.now()
    letter.status = "signed"
    letter.save(update_fields=["hr_signed", "hr_signature", "hr_signed_by", "hr_signed_at", "status"])

    _log_visa(letter, prev_status, "signed", actor, f"HR e-signed by {actor}")

    messages.success(request, _("Visa letter signed."))
    return redirect(f"{reverse('onboarding-letters')}?tab=visa")


# ── Send Documents Email ─────────────────────────────────────────────────────

@login_required
def send_documents_email(request):
    """Send selected signed documents to a candidate by email."""
    if request.method != "POST":
        return HttpResponse(status=405)

    cand_id = request.POST.get("candidate_id")
    send_offer = request.POST.get("send_offer") == "on"
    send_medical = request.POST.get("send_medical") == "on"
    send_visa = request.POST.get("send_visa") == "on"

    candidate = get_object_or_404(Candidate, id=cand_id)
    actor = getattr(request.user, "employee_get", None)

    doc_lines = []
    if send_offer:
        offer = OfferLetter.objects.filter(candidate_id=candidate).first()
        if offer:
            doc_lines.append(f"• Offer Letter ({offer.position})")
    if send_medical:
        ml = MedicalLetter.objects.filter(candidate_id=candidate).first()
        if ml:
            doc_lines.append("• Medical Clearance Letter")
    if send_visa:
        vl = VisaLetter.objects.filter(candidate_id=candidate).first()
        if vl:
            doc_lines.append("• Visa Support Letter")

    if not doc_lines:
        messages.error(request, _("No documents selected or documents not yet created."))
        return redirect(reverse("onboarding-letters"))

    try:
        from django.core.mail import send_mail
        from django.conf import settings

        docs_text = "\n".join(doc_lines)
        body = (
            f"Dear {candidate.name},\n\n"
            f"Please find below the documents prepared for you as part of your onboarding process:\n\n"
            f"{docs_text}\n\n"
            f"All documents have been reviewed and signed. Please review them and contact HR if you have any questions.\n\n"
            f"Best Regards,\nHuman Resources"
        )
        send_mail(
            subject=f"Your Onboarding Documents — {candidate.name}",
            message=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "hr@company.com"),
            recipient_list=[candidate.email],
            fail_silently=False,
        )
        # Log the send event on each document
        if send_offer and offer:
            _log_offer(offer, offer.status, offer.status, actor, "Documents email sent to candidate")
        if send_medical and ml:
            _log_medical(ml, ml.status, ml.status, actor, "Documents email sent to candidate")
        if send_visa and vl:
            _log_visa(vl, vl.status, vl.status, actor, "Documents email sent to candidate")

        messages.success(request, _(f"Documents sent to {candidate.email}."))
    except Exception as e:
        messages.error(request, _(f"Failed to send email: {e}"))

    return redirect(reverse("onboarding-letters"))


@login_required
def send_notification_all(request, cand_id):
    """Send in-app notification to all stakeholders."""
    if request.method != "POST":
        return HttpResponse(status=405)

    candidate = get_object_or_404(Candidate, id=cand_id)

    from django.contrib.auth.models import User
    stakeholder_users = list(User.objects.filter(is_active=True, is_superuser=True))
    if candidate.recruitment_id:
        for mgr in candidate.recruitment_id.recruitment_managers.all():
            if mgr.employee_user_id and mgr.employee_user_id not in stakeholder_users:
                stakeholder_users.append(mgr.employee_user_id)
        if candidate.recruitment_id.raised_by and candidate.recruitment_id.raised_by.employee_user_id:
            u = candidate.recruitment_id.raised_by.employee_user_id
            if u not in stakeholder_users:
                stakeholder_users.append(u)

    try:
        from notifications.signals import notify
        if stakeholder_users:
            notify.send(
                request.user,
                recipient=stakeholder_users,
                verb=f"Interview completed for {candidate.name}. Offer notification sent to candidate.",
                icon="checkmark-circle",
                redirect="/onboarding/letters/",
            )
    except Exception:
        pass

    messages.success(request, f"Notification sent to all stakeholders.")
    return redirect(f"{reverse('onboarding-letters')}?tab=offer")


@login_required
def offer_template_preview(request, tmpl_id):
    """Return template name + body as JSON for the preview modal."""
    tmpl = get_object_or_404(OfferLetterTemplate, id=tmpl_id)
    return JsonResponse({"id": tmpl.id, "name": tmpl.name, "body_html": tmpl.body_html})


@login_required
def offer_template_edit(request, tmpl_id):
    """Save updated name + body_html for an offer letter template."""
    if request.method != "POST":
        return HttpResponse(status=405)
    tmpl = get_object_or_404(OfferLetterTemplate, id=tmpl_id)
    name = request.POST.get("name", "").strip()
    body_html = request.POST.get("body_html", "").strip()
    if name:
        tmpl.name = name
    if body_html:
        tmpl.body_html = body_html
    tmpl.save(update_fields=["name", "body_html"])
    return JsonResponse({"ok": True, "name": tmpl.name, "body_html": tmpl.body_html})


def candidate_accept_offer(request, token):
    """Public page — candidate accepts the offer letter via emailed link."""
    from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
    try:
        offer_id = TimestampSigner(salt="offer-accept").unsign(token, max_age=60 * 60 * 24 * 30)
    except (BadSignature, SignatureExpired):
        return render(request, "onboarding/letters/accept_invalid.html", {}, status=404)

    offer = OfferLetter.objects.filter(id=offer_id).select_related("candidate_id").first()
    if not offer:
        return render(request, "onboarding/letters/accept_invalid.html", {}, status=404)
    candidate = offer.candidate_id

    if request.method == "POST":
        if offer and offer.status == "sent":
            prev_status = offer.status
            offer.status = "accepted"
            offer.accepted_date = timezone.now()
            offer.save(update_fields=["status", "accepted_date"])
            candidate.offer_letter_status = "accepted"
            candidate.hired = True
            candidate.save(update_fields=["offer_letter_status", "hired"])
            _log_offer(offer, prev_status, "accepted", None, "Candidate accepted the offer via email link")

            try:
                from notifications.signals import notify
                from django.contrib.auth.models import User
                recipients = list(User.objects.filter(is_superuser=True, is_active=True))
                if offer.created_by and offer.created_by.employee_user_id:
                    recipients.append(offer.created_by.employee_user_id)
                for appr in offer.approvals.all():
                    if appr.approver.employee_user_id:
                        recipients.append(appr.approver.employee_user_id)
                if recipients:
                    notify.send(
                        User.objects.filter(is_superuser=True).first(),
                        recipient=list(set(recipients)),
                        verb=f"{candidate.name} has accepted the offer letter for {offer.position}.",
                        icon="checkmark-circle",
                        redirect="/onboarding/letters/",
                    )
            except Exception:
                pass

        return render(request, "onboarding/letters/accept_success.html", {
            "candidate": candidate,
            "offer": offer,
        })

    return render(request, "onboarding/letters/accept_offer.html", {
        "candidate": candidate,
        "offer": offer,
    })
