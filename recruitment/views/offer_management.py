"""
recruitment/views/offer_management.py

Full offer letter lifecycle:
  create → send (with candidate e-sign link) → accept/reject → offer-tracking

Also manages:
  - OfferLetterTemplate CRUD
  - Candidate self-sign endpoint (public, token-based)
"""

import io
import threading

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from django.contrib.auth.decorators import permission_required

from fits.decorators import login_required
from recruitment.models import Candidate, OfferLetter, OfferLetterTemplate
from recruitment.decorators import manager_can_enter
from recruitment.models import Candidate, OfferLetter


def _get_employee(user):
    return getattr(user, "employee_get", None)


_SITE_URL = "https://hcmspro.net"


def _build_sign_url(request, offer):
    """Return the absolute URL the candidate clicks to e-sign the offer."""
    path = reverse("offer-candidate-sign", args=[str(offer.candidate_signature_token)])
    # Use the configured site URL so the link is correct even when called from
    # a background thread (where request.get_host() may differ).
    try:
        return request.build_absolute_uri(path)
    except Exception:
        return f"{_SITE_URL}{path}"


# ── LIST ─────────────────────────────────────────────────────────────────────

@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
def offer_list(request):
    offers = OfferLetter.objects.select_related("candidate_id").order_by("-created_on")
    return render(request, "recruitment/offer/list.html", {"offers": offers})


# ── CREATE ────────────────────────────────────────────────────────────────────

@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
def offer_create(request, cand_id):
    candidate = get_object_or_404(Candidate, id=cand_id)

    existing = OfferLetter.objects.filter(candidate_id=candidate).first()
    if existing:
        messages.info(request, _("Offer letter already exists for this candidate."))
        return redirect(reverse("offer-detail", args=[existing.id]))

    templates = OfferLetterTemplate.objects.all()
    default_tpl = templates.filter(is_active=True).first()

    if request.method == "POST":
        data = request.POST
        emp = _get_employee(request.user)
        joining_date = data.get("joining_date")
        if not joining_date:
            messages.error(request, _("Joining date is required."))
            return render(request, "recruitment/offer/create.html", {
                "candidate": candidate, "templates": templates,
            })

        letter_template = data.get("letter_template", "").strip()
        # If a saved template was selected, load its content
        tpl_id = data.get("template_id")
        if tpl_id:
            try:
                tpl_obj = OfferLetterTemplate.objects.get(pk=tpl_id)
                letter_template = letter_template or tpl_obj.content
            except OfferLetterTemplate.DoesNotExist:
                pass

        offer = OfferLetter.objects.create(
            candidate_id=candidate,
            position=data.get("position", str(candidate.job_position_id or "Position")),
            department=data.get("department", ""),
            basic_salary=data.get("basic_salary") or 0,
            gross_salary=data.get("gross_salary") or None,
            currency=data.get("currency", "OMR"),
            joining_date=joining_date,
            contract_duration=data.get("contract_duration") or None,
            probation_period=int(data.get("probation_period") or 3),
            job_description=data.get("job_description", ""),
            terms_conditions=data.get("terms_conditions", ""),
            letter_template=letter_template,
            status="draft",
            created_by=emp,
        )
        # Auto-route for e-sign chain immediately after creation
        from recruitment.approvals.engine import route_offer
        chain = route_offer(offer)
        if chain:
            offer.status = "pending_approval"
            offer.approval_submitted_at = timezone.now()
            offer.save()
            messages.success(request, _(f"Offer letter created for {candidate.name} and sent for e-sign."))
        else:
            messages.success(request, _(f"Offer letter created for {candidate.name}."))
        return redirect(reverse("offer-detail", args=[offer.id]))

    dept = ""
    try:
        dept = str(candidate.job_position_id.department_id.department)
    except AttributeError:
        pass

    return render(request, "recruitment/offer/create.html", {
        "candidate": candidate,
        "templates": templates,
        "default_tpl": default_tpl,
        "dept": dept,
    })


# ── DETAIL ────────────────────────────────────────────────────────────────────

@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
def offer_detail(request, offer_id):
    offer = get_object_or_404(OfferLetter, id=offer_id)
    approvals = offer.approvals.select_related("step", "approver", "acted_by").order_by("id")
    employee = _get_employee(request.user)
    pending_approval = None
    if employee:
        pending_approval = offer.approvals.filter(action="pending", approver=employee).first()
    sign_url = None
    try:
        sign_url = reverse("offer-candidate-sign", args=[str(offer.candidate_signature_token)])
    except Exception:
        pass
    # Show visa button when all signatories have approved (status advances to sent/accepted/joined)
    show_visa_btn = offer.status in ("sent", "accepted", "joined")
    return render(request, "recruitment/offer/detail.html", {
        "offer": offer,
        "approvals": approvals,
        "pending_approval": pending_approval,
        "employee": employee,
        "sign_url": sign_url,
        "show_visa_btn": show_visa_btn,
    })


# ── REQUEST VISA ──────────────────────────────────────────────────────────────

@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
@require_POST
def offer_request_visa(request, offer_id):
    offer = get_object_or_404(OfferLetter, id=offer_id)

    from recruitment.onboarding_docs import all_documents_approved
    if offer.sign_documents.exists() and not all_documents_approved(offer):
        messages.warning(request, _("All onboarding documents must be approved before sending to the Visa Department."))
        return redirect(request.META.get("HTTP_REFERER", reverse("offer-detail", args=[offer_id])))

    offer.visa_status = "in_progress"
    offer.save(update_fields=["visa_status"])
    try:
        from recruitment.email_utils import email_visa_team
        threading.Thread(target=email_visa_team, args=(offer,), daemon=True).start()
    except Exception:
        pass
    messages.success(request, "Request sent to the Visa Department to process the candidate's visa.")
    return redirect(request.META.get("HTTP_REFERER", reverse("offer-detail", args=[offer_id])))


# ── ONBOARDING DOCUMENT HR REVIEW ──────────────────────────────────────────────

@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
@require_POST
def onboarding_doc_approve(request, doc_id):
    from recruitment.models import OnboardingDocument
    from recruitment.onboarding_docs import on_hr_approve
    doc = get_object_or_404(OnboardingDocument, id=doc_id)
    if doc.status != OnboardingDocument.STATUS_SIGNED:
        messages.warning(request, _("Only signed documents can be approved."))
    else:
        on_hr_approve(doc, _get_employee(request.user))
        messages.success(request, _(f"'{doc.title}' approved."))
    return redirect(request.META.get("HTTP_REFERER", reverse("offer-detail", args=[doc.offer_id])))


@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
@require_POST
def onboarding_doc_resign(request, doc_id):
    from recruitment.models import OnboardingDocument
    from recruitment.onboarding_docs import on_hr_resign
    doc = get_object_or_404(OnboardingDocument, id=doc_id)
    note = request.POST.get("note", "").strip()
    on_hr_resign(doc, _get_employee(request.user), note)
    messages.info(request, _(f"'{doc.title}' sent back to the candidate to re-sign."))
    return redirect(request.META.get("HTTP_REFERER", reverse("offer-detail", args=[doc.offer_id])))


# ── SEND ──────────────────────────────────────────────────────────────────────

@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
def offer_send(request, offer_id):
    offer = get_object_or_404(OfferLetter, id=offer_id)
    if request.method == "POST":
        offer.status = "sent"
        offer.sent_date = timezone.now()
        offer.save()

        sign_url = _build_sign_url(request, offer)

        # Build portal URL (public document-upload page)
        try:
            portal_path = reverse("candidate-portal", args=[str(offer.portal_token)])
            portal_url = request.build_absolute_uri(portal_path)
        except Exception:
            portal_url = f"{_SITE_URL}{reverse('candidate-portal', args=[str(offer.portal_token)])}"

        def _send():
            try:
                from django.core.mail import send_mail
                from django.conf import settings

                generated = offer.generated_letter or ""
                if offer.letter_template and not generated:
                    try:
                        generated = offer.letter_template.format(
                            candidate_name=offer.candidate_id.name,
                            position=offer.position,
                            department=offer.department or "",
                            basic_salary=f"{offer.currency} {offer.basic_salary:,.2f}",
                            gross_salary=f"{offer.currency} {offer.gross_salary:,.2f}" if offer.gross_salary else "TBD",
                            joining_date=offer.joining_date.strftime("%d %b %Y"),
                            probation_period=offer.probation_period,
                            contract_duration=offer.contract_duration or "Permanent",
                            currency=offer.currency,
                        )
                    except (KeyError, AttributeError):
                        generated = ""

                body = (
                    f"Dear {offer.candidate_id.name},\n\n"
                    f"We are pleased to offer you the position of {offer.position}.\n\n"
                    f"Basic Salary : {offer.currency} {offer.basic_salary}\n"
                    f"Joining Date : {offer.joining_date}\n"
                    f"Probation    : {offer.probation_period} months\n"
                )
                if generated:
                    body += f"\n{generated}\n"
                body += (
                    f"\n─────────────────────────────\n"
                    f"Please review and digitally sign your offer letter by clicking the link below:\n\n"
                    f"  {sign_url}\n\n"
                    f"Clicking this link confirms your acceptance of the offer.\n\n"
                    f"─────────────────────────────\n"
                    f"CANDIDATE PORTAL — Upload Required Documents\n\n"
                    f"Please log in to your personal candidate portal to upload the required\n"
                    f"pre-joining documents (medical certificate, academic marksheets,\n"
                    f"experience certificates, passport copy, etc.):\n\n"
                    f"  {portal_url}\n\n"
                    f"No login is needed — the link above is unique to you.\n\n"
                    f"Regards,\nHR Team"
                )
                send_mail(
                    f"Offer Letter & Document Upload — {offer.position}",
                    body,
                    getattr(settings, "DEFAULT_FROM_EMAIL", "hr@company.com"),
                    [offer.candidate_id.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            try:
                from recruitment.email_utils import email_offer_letter
                email_offer_letter(offer)
            except Exception:
                pass

        threading.Thread(target=_send, daemon=True).start()
        messages.success(request, _(f"Offer sent to {offer.candidate_id.email}. Sign and portal links included."))
    return redirect(reverse("offer-detail", args=[offer_id]))


# ── CANDIDATE E-SIGN (public endpoint) ────────────────────────────────────────

def offer_candidate_sign(request, token):
    """
    Public URL (no login required) sent in the offer email.
    When the candidate clicks it their acceptance is recorded.
    """
    offer = get_object_or_404(OfferLetter, candidate_signature_token=token)

    if offer.candidate_signed_at:
        return render(request, "recruitment/offer/candidate_sign.html", {
            "offer": offer, "already_signed": True,
        })

    if request.method == "POST":
        offer.candidate_signed_at = timezone.now()
        if offer.status == "sent":
            offer.status = "accepted"
            offer.accepted_date = timezone.now()
            offer.candidate_id.hired = True
            offer.candidate_id.joining_date = offer.joining_date
            offer.candidate_id.save()
        offer.save()

        def _notify():
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                from django.contrib.auth.models import User
                hr_emails = [
                    u.email for u in
                    User.objects.filter(is_active=True).filter(
                        user_permissions__codename="view_offerletter"
                    ).union(User.objects.filter(is_superuser=True, is_active=True))
                    if u.email
                ]
                if hr_emails:
                    send_mail(
                        f"Offer Signed — {offer.candidate_id.name}",
                        f"{offer.candidate_id.name} has digitally signed the offer letter for {offer.position}.\n"
                        f"Signed at: {offer.candidate_signed_at.strftime('%d %b %Y %H:%M')} UTC\n\n"
                        f"View: {_SITE_URL}{reverse('offer-detail', args=[offer.id])}",
                        getattr(settings, "DEFAULT_FROM_EMAIL", "hr@company.com"),
                        hr_emails,
                        fail_silently=True,
                    )
            except Exception:
                pass

        threading.Thread(target=_notify, daemon=True).start()
        return render(request, "recruitment/offer/candidate_sign.html", {
            "offer": offer, "signed_now": True,
        })

    return render(request, "recruitment/offer/candidate_sign.html", {"offer": offer})


# ── ACCEPT / REJECT ───────────────────────────────────────────────────────────

@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
def offer_accept(request, offer_id):
    offer = get_object_or_404(OfferLetter, id=offer_id)
    if request.method == "POST":
        offer.status = "accepted"
        offer.accepted_date = timezone.now()
        offer.save()
        candidate = offer.candidate_id
        candidate.hired = True
        candidate.joining_date = offer.joining_date
        candidate.save()
        try:
            from recruitment.email_utils import email_offer_accepted
            threading.Thread(target=email_offer_accepted, args=(offer,), daemon=True).start()
        except Exception:
            pass
        messages.success(request, _(f"{candidate.name} marked as accepted."))
    return redirect(reverse("offer-tracking"))


@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
def offer_reject(request, offer_id):
    offer = get_object_or_404(OfferLetter, id=offer_id)
    if request.method == "POST":
        reason = request.POST.get("reason", "")
        offer.status = "rejected"
        offer.rejected_date = timezone.now()
        offer.rejection_reason = reason
        offer.save()
        try:
            from recruitment.email_utils import email_offer_rejected
            threading.Thread(target=email_offer_rejected, args=(offer,), daemon=True).start()
        except Exception:
            pass
        messages.warning(request, _("Offer rejected."))
    return redirect(reverse("offer-list"))


# ── APPROVAL WORKFLOW ─────────────────────────────────────────────────────────

@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
def offer_submit_approval(request, offer_id):
    offer = get_object_or_404(OfferLetter, id=offer_id)
    if request.method == "POST":
        if offer.status != "draft":
            messages.warning(request, _("Only draft offers can be submitted for approval."))
            return redirect(reverse("offer-detail", args=[offer_id]))

        # Delete any stale approval records from a previous rejected attempt
        offer.approvals.all().delete()

        from recruitment.approvals.engine import route_offer
        result = route_offer(offer)
        if not result:
            messages.error(request, _(
                "No approval chain found. Either configure an Approval Rule or raise the "
                "recruitment request through the employee workflow first."
            ))
            return redirect(reverse("offer-detail", args=[offer_id]))

        offer.status = "pending_approval"
        offer.approval_submitted_at = timezone.now()
        offer.save()

        chain_source = "recruitment request chain" if result == "recruitment_chain" else f"rule '{result}'"
        messages.success(request, _(f"Offer {offer.offer_no} submitted for approval using the {chain_source}."))
    return redirect(reverse("offer-detail", args=[offer_id]))


@login_required
def offer_approval_action(request, offer_id):
    """
    Any approver in the chain (not just HR) can approve/reject their step.
    The engine verifies they are the current pending approver.
    """
    offer = get_object_or_404(OfferLetter, id=offer_id)
    if request.method == "POST":
        action = request.POST.get("action")
        comment = request.POST.get("comment", "")
        signature_image = request.POST.get("signature_data", "")
        if action not in ("approved", "rejected", "esign", "feedback"):
            messages.error(request, _("Invalid action."))
            return redirect(reverse("offer-approval-inbox"))

        from recruitment.approvals.engine import advance_offer
        success = advance_offer(offer, action, request.user, comment, signature_image)
        if success:
            if action in ("approved", "esign"):
                messages.success(request, _("E-signed. Next person in chain notified."))
            else:
                messages.warning(request, _("Feedback submitted. Offer returned to HR."))
        else:
            messages.error(request, _("No pending approval found for this offer — you may not be the current approver."))
    return redirect(reverse("offer-approval-inbox"))


@login_required
def offer_approval_inbox(request):
    """
    Accessible to any logged-in user who is an approver in the chain —
    NOT restricted to HR. Each user only sees their own pending items.
    """
    from recruitment.models_approvals import OfferApproval
    employee = _get_employee(request.user)
    pending = []
    if employee:
        pending = OfferApproval.objects.filter(
            approver=employee, action="pending"
        ).select_related("offer", "offer__candidate_id", "step").order_by("due_at")
    return render(request, "recruitment/offer/approval_inbox.html", {"pending": pending})


# ── OFFER LETTER TEMPLATES ────────────────────────────────────────────────────

@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
def offer_template_list(request):
    """List, create, and delete offer letter templates."""
    templates = OfferLetterTemplate.objects.all()

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        content = request.POST.get("content", "").strip()
        is_default = request.POST.get("is_default") == "on"
        if name and content:
            OfferLetterTemplate.objects.create(name=name, content=content, is_default=is_default)
            messages.success(request, _(f"Template '{name}' saved."))
        else:
            messages.error(request, _("Name and content are required."))
        return redirect(reverse("offer-template-list"))

    return render(request, "recruitment/offer/templates.html", {"templates": templates})


@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
@require_POST
def offer_template_delete(request, tpl_id):
    tpl = get_object_or_404(OfferLetterTemplate, pk=tpl_id)
    tpl.delete()
    messages.success(request, _("Template deleted."))
    return redirect(reverse("offer-template-list"))


@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
def offer_template_preview(request, tpl_id):
    """Return template content as plain text for JS injection into the create form."""
    tpl = get_object_or_404(OfferLetterTemplate, pk=tpl_id)
    return HttpResponse(tpl.content, content_type="text/plain")


@login_required
@require_POST
def generate_offer_from_interview(request, interview_id):
    """
    Mark all interview rounds complete, auto-create a draft OfferLetter,
    route it for e-sign, and redirect to the letters page.
    """
    from datetime import timedelta
    from django.utils import timezone as tz
    from recruitment.models import InterviewSchedule
    from recruitment.models_interview import InterviewRound
    from recruitment.approvals.engine import route_offer

    interview = get_object_or_404(InterviewSchedule, id=interview_id)
    candidate = interview.candidate_id

    # Mark all rounds complete and interview itself as done
    now = tz.now()
    InterviewRound.objects.filter(interview=interview, completed=False).update(
        completed=True, completed_at=now
    )
    if not interview.completed:
        interview.completed = True
        interview.save(update_fields=["completed"])

    # Reuse existing offer if one already exists
    offer = OfferLetter.objects.filter(candidate_id=candidate).first()
    if not offer:
        joining_date = (now + timedelta(days=30)).date()
        job_pos = candidate.job_position_id
        if not job_pos and candidate.recruitment_id:
            job_pos = (
                candidate.recruitment_id.job_position_id
                or candidate.recruitment_id.open_positions.first()
            )
        position = job_pos.job_position if job_pos else "To be confirmed"
        dept = ""
        try:
            if job_pos and job_pos.department_id:
                dept = job_pos.department_id.department
        except Exception:
            pass

        offer = OfferLetter.objects.create(
            candidate_id=candidate,
            position=position,
            department=dept,
            basic_salary=0,
            joining_date=joining_date,
            status="draft",
        )
        try:
            chain = route_offer(offer)
            if chain:
                offer.status = "pending_approval"
                offer.approval_submitted_at = now
                offer.save()
        except Exception:
            pass

    return JsonResponse({"redirect": reverse("onboarding-letters")})


@login_required
@permission_required("recruitment.view_offerletter", raise_exception=True)
def offer_pdf(request, offer_id):
    """Generate and download the offer letter as a PDF."""
    try:
        from xhtml2pdf import pisa
    except ImportError:
        messages.error(request, _("PDF export is unavailable (xhtml2pdf not installed)."))
        return redirect(reverse("offer-detail", args=[offer_id]))

    offer = get_object_or_404(OfferLetter, id=offer_id)

    if not offer.generated_letter:
        offer.generate_offer_letter()
        offer.save(update_fields=["generated_letter"])

    html = render_to_string(
        "recruitment/offer/pdf.html",
        {"offer": offer},
        request=request,
    )

    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        messages.error(request, _("PDF generation failed. Please try again."))
        return redirect(reverse("offer-detail", args=[offer_id]))

    filename = f"Offer-{offer.offer_no}-{offer.candidate_id.name.replace(' ', '_')}.pdf"
    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
