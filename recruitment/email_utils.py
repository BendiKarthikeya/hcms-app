"""
recruitment/email_utils.py

Central email utility for the recruitment module.
Uses Brevo SMTP directly — bypasses the custom logging backend
that breaks on null from_email.

Usage:
    from recruitment.email_utils import send_recruitment_email
    send_recruitment_email(
        subject="...",
        body="...",
        to=["candidate@example.com"],
    )
"""

import os
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import EmailMultiAlternatives
from email.mime.base import MIMEBase
from email import encoders


def _get_backend():
    return EmailBackend(
        host=getattr(settings, "EMAIL_HOST", os.environ.get("EMAIL_HOST", "smtp-relay.brevo.com")),
        port=int(getattr(settings, "EMAIL_PORT", os.environ.get("EMAIL_PORT", 587))),
        username=getattr(settings, "EMAIL_HOST_USER", os.environ.get("EMAIL_HOST_USER", "")),
        password=getattr(settings, "EMAIL_HOST_PASSWORD", os.environ.get("EMAIL_HOST_PASSWORD", "")),
        use_tls=getattr(settings, "EMAIL_USE_TLS", True),
        fail_silently=True,
    )


def _from_email():
    return getattr(settings, "DEFAULT_FROM_EMAIL", os.environ.get("DEFAULT_FROM_EMAIL", "contractor1@fits.one"))


def _get_global_gmail():
    """Return the admin-connected Gmail integration (first active one), or None."""
    try:
        from base.models_integrations import MailboxIntegration
        return MailboxIntegration.objects.filter(provider="gmail", is_active=True).first()
    except Exception:
        return None


def _try_send_via_global_gmail(subject: str, body: str, to: list) -> bool:
    """Send through the globally connected Gmail. Returns True on success."""
    try:
        from base.integrations import gmail as gmail_api
        integ = _get_global_gmail()
        if not integ:
            return False
        html = body.replace("\n", "<br>") if body else ""
        ok_any = False
        for recipient in to:
            if gmail_api.send_via_gmail(integ, to=recipient, subject=subject, html=html, text=body):
                ok_any = True
        return ok_any
    except Exception:
        return False


def send_recruitment_email(subject: str, body: str, to: list, ics_bytes: bytes = None, user=None) -> bool:
    """Send a plain-text email, optionally with .ics attachment.

    Tries the globally connected Gmail first (admin sets this in Profile →
    Integrations). Falls back to Brevo SMTP if no Gmail is connected or send
    fails. Note: ics_bytes is only attached on the SMTP path.
    """
    if not to:
        return False
    if not ics_bytes:
        if _try_send_via_global_gmail(subject, body, to):
            return True
    try:
        backend = _get_backend()
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=_from_email(),
            to=to,
            connection=backend,
        )
        if ics_bytes:
            attachment = MIMEBase("text", "calendar", method="REQUEST", name="invite.ics")
            attachment.set_payload(ics_bytes)
            encoders.encode_base64(attachment)
            attachment.add_header("Content-Disposition", 'attachment; filename="invite.ics"')
            msg.attach(attachment)
        msg.send()
        return True
    except Exception:
        return False


# ── Pre-built email templates ─────────────────────────────────────────────────

def email_application_confirmation(candidate, recruitment):
    """Email to candidate confirming their application was received."""
    if not candidate.email or "careers.local" in candidate.email:
        return
    send_recruitment_email(
        subject=f"Application Received – {recruitment.title or str(recruitment.job_position_id)}",
        body=(
            f"Dear {candidate.name},\n\n"
            f"Thank you for applying for the position of "
            f"{recruitment.title or str(recruitment.job_position_id)}.\n\n"
            f"We have received your application and CV. Our HR team will review it "
            f"and get back to you within 5–7 working days.\n\n"
            f"Regards,\nHR Team\n{recruitment.company_id or ''}"
        ),
        to=[candidate.email],
    )


def email_hr_new_application(candidate, recruitment, hr_emails: list):
    """Alert HR managers about a new career page application."""
    if not hr_emails:
        return
    send_recruitment_email(
        subject=f"[FITS] New Application: {candidate.name} → {recruitment.title or str(recruitment.job_position_id)}",
        body=(
            f"A new application has been submitted via the Careers page.\n\n"
            f"Candidate : {candidate.name}\n"
            f"Email     : {candidate.email}\n"
            f"Mobile    : {candidate.mobile or '—'}\n"
            f"Applied for: {recruitment.title or str(recruitment.job_position_id)}\n\n"
            f"Review: {_site_url()}/recruitment/candidates/dashboard/"
        ),
        to=hr_emails,
    )


def email_interview_invite(interview, recipient_emails: list):
    """Send interview invite + .ics to panelists and candidate."""
    from recruitment.interview_utils import _make_ics
    if not recipient_emails:
        return
    candidate = interview.candidate_id
    ics = _make_ics(interview)
    body = (
        f"Dear Interviewer,\n\n"
        f"You are invited to interview {candidate.name}.\n\n"
        f"Date  : {interview.interview_date}\n"
        f"Time  : {interview.interview_time}\n"
    )
    if interview.online_meeting_link:
        body += f"Link  : {interview.online_meeting_link}\n"
    if interview.description:
        body += f"\nNotes : {interview.description}\n"
    body += "\nPlease find the calendar invite attached.\n\nRegards,\nHR Team"
    send_recruitment_email(
        subject=f"Interview Scheduled – {candidate.name}",
        body=body,
        to=recipient_emails,
        ics_bytes=ics,
    )


def email_candidate_interview_invite(interview):
    """Send interview invite to the candidate themselves."""
    candidate = interview.candidate_id
    if not candidate.email or "careers.local" in candidate.email:
        return
    from recruitment.interview_utils import _make_ics
    ics = _make_ics(interview)
    body = (
        f"Dear {candidate.name},\n\n"
        f"We are pleased to invite you for an interview.\n\n"
        f"Date  : {interview.interview_date}\n"
        f"Time  : {interview.interview_time}\n"
    )
    if interview.online_meeting_link:
        body += f"Link  : {interview.online_meeting_link}\n"
    body += (
        f"\nPlease confirm your attendance by replying to this email.\n\n"
        f"Regards,\nHR Team"
    )
    send_recruitment_email(
        subject=f"Interview Invitation – {interview.candidate_id.job_position_id or 'Position'}",
        body=body,
        to=[candidate.email],
        ics_bytes=ics,
    )


def email_offer_letter(offer):
    """Send offer letter notification to candidate."""
    candidate = offer.candidate_id
    if not candidate.email or "careers.local" in candidate.email:
        return
    send_recruitment_email(
        subject=f"Offer Letter – {offer.position}",
        body=(
            f"Dear {candidate.name},\n\n"
            f"We are pleased to offer you the position of {offer.position}.\n\n"
            f"Basic Salary : {offer.currency} {offer.basic_salary}\n"
            f"Joining Date : {offer.joining_date}\n"
            f"Probation    : {offer.probation_period} months\n"
            + (f"Contract     : {offer.contract_duration} months\n" if offer.contract_duration else "")
            + (f"\nJob Description:\n{offer.job_description}\n" if offer.job_description else "")
            + (f"\nTerms & Conditions:\n{offer.terms_conditions}\n" if offer.terms_conditions else "")
            + f"\nKindly confirm your acceptance at your earliest convenience.\n\nRegards,\nHR Team"
        ),
        to=[candidate.email],
    )


def email_offer_accepted(offer):
    """Notify HR when a candidate accepts the offer."""
    try:
        from django.contrib.auth.models import User
        hr_users = User.objects.filter(is_superuser=True, is_active=True)
        emails = [u.email for u in hr_users if u.email]
        if not emails:
            return
        send_recruitment_email(
            subject=f"[FITS] Offer Accepted: {offer.candidate_id.name}",
            body=(
                f"{offer.candidate_id.name} has accepted the offer for {offer.position}.\n"
                f"Joining Date: {offer.joining_date}\n\n"
                f"Update clearance status: {_site_url()}/recruitment/offer-tracking/"
            ),
            to=emails,
        )
    except Exception:
        pass


def email_offer_rejected(offer):
    """Send rejection email to candidate."""
    candidate = offer.candidate_id
    if not candidate.email or "careers.local" in candidate.email:
        return
    send_recruitment_email(
        subject=f"Application Update – {offer.position}",
        body=(
            f"Dear {candidate.name},\n\n"
            f"Thank you for your time and interest in the position of {offer.position}.\n"
            f"After careful consideration, we have decided to move forward with other candidates.\n\n"
            + (f"Feedback: {offer.rejection_reason}\n\n" if offer.rejection_reason else "")
            + f"We appreciate your interest and wish you all the best.\n\nRegards,\nHR Team"
        ),
        to=[candidate.email],
    )


def email_approval_assigned(approver_employee, document_obj, doc_type: str):
    """Notify an approver that a document is waiting for their action."""
    user = getattr(approver_employee, "employee_user_id", None)
    if not user or not user.email:
        return
    ref = getattr(document_obj, "offer_no", None) or getattr(document_obj, "requisition_no", str(document_obj.pk))
    send_recruitment_email(
        subject=f"[FITS] Action Required: {doc_type} {ref} awaiting your approval",
        body=(
            f"Dear {approver_employee.get_full_name()},\n\n"
            f"A {doc_type} requires your approval.\n\n"
            f"Reference : {ref}\n"
            + (f"Position  : {document_obj.position}\n" if hasattr(document_obj, 'position') else "")
            + (f"Candidate : {document_obj.candidate_id.name}\n" if hasattr(document_obj, 'candidate_id') else "")
            + (f"Requested : {document_obj.job_position}\n" if hasattr(document_obj, 'job_position') else "")
            + f"\nPlease log in to FITS HRMS to take action.\n\nRegards,\nHR Team"
        ),
        to=[user.email],
    )


def email_offer_approval_approved(offer):
    """Notify HR when an offer letter clears all approval steps."""
    try:
        from django.contrib.auth.models import User
        hr_users = User.objects.filter(is_superuser=True, is_active=True)
        emails = [u.email for u in hr_users if u.email]
        if not emails:
            return
        send_recruitment_email(
            subject=f"[FITS] Offer Letter Approved – {offer.offer_no}",
            body=(
                f"Offer letter {offer.offer_no} for {offer.candidate_id.name} ({offer.position}) "
                f"has been fully approved and is ready to be sent to the candidate.\n\n"
                f"Joining Date: {offer.joining_date}\n\n"
                f"Regards,\nFITS System"
            ),
            to=emails,
        )
    except Exception:
        pass


def email_offer_approval_rejected(offer, reason=""):
    """Notify HR when an offer letter is rejected during approval."""
    try:
        from django.contrib.auth.models import User
        hr_users = User.objects.filter(is_superuser=True, is_active=True)
        emails = [u.email for u in hr_users if u.email]
        if not emails:
            return
        send_recruitment_email(
            subject=f"[FITS] Offer Letter Rejected – {offer.offer_no}",
            body=(
                f"Offer letter {offer.offer_no} for {offer.candidate_id.name} ({offer.position}) "
                f"was rejected during the approval process.\n\n"
                + (f"Reason: {reason}\n\n" if reason else "")
                + f"The offer has been returned to Draft status.\n\nRegards,\nFITS System"
            ),
            to=emails,
        )
    except Exception:
        pass


def email_manpower_approved(mr):
    """Notify requester when their manpower request is approved."""
    emp = mr.requested_by
    if not emp:
        return
    user = getattr(emp, "employee_user_id", None)
    if not user or not user.email:
        return
    send_recruitment_email(
        subject=f"[FITS] Manpower Request Approved – {mr.requisition_no}",
        body=(
            f"Dear {emp.get_full_name()},\n\n"
            f"Your manpower request {mr.requisition_no} for the position of "
            f"{mr.job_position or 'the requested role'} has been approved.\n\n"
            f"A recruitment campaign has been created automatically.\n"
            f"View: {_site_url()}/recruitment/manpower/{mr.id}/\n\n"
            f"Regards,\nHR Team"
        ),
        to=[user.email],
    )


def email_manpower_rejected(mr, reason=""):
    """Notify requester when their manpower request is rejected."""
    emp = mr.requested_by
    if not emp:
        return
    user = getattr(emp, "employee_user_id", None)
    if not user or not user.email:
        return
    send_recruitment_email(
        subject=f"[FITS] Manpower Request Rejected – {mr.requisition_no}",
        body=(
            f"Dear {emp.get_full_name()},\n\n"
            f"Your manpower request {mr.requisition_no} has been rejected.\n"
            + (f"Reason: {reason}\n" if reason else "")
            + f"\nPlease contact HR for further details.\n\nRegards,\nHR Team"
        ),
        to=[user.email],
    )


def send_rejection_email(candidate):
    """Send a rejection email to a candidate (used by the manual reject button)."""
    if not candidate.email or "careers.local" in candidate.email:
        return
    job_title = ""
    try:
        job_title = str(candidate.job_position_id) if candidate.job_position_id else ""
    except Exception:
        pass
    send_recruitment_email(
        subject=f"Application Update{(' – ' + job_title) if job_title else ''}",
        body=(
            f"Dear {candidate.name},\n\n"
            f"Thank you for your interest"
            + (f" in the position of {job_title}" if job_title else "")
            + ".\n"
            f"After careful consideration, we have decided to move forward with other candidates.\n\n"
            f"We appreciate your time and wish you the very best in your career.\n\n"
            f"Regards,\nHR Team"
        ),
        to=[candidate.email],
    )


def email_offer_approval_step(approver_employee, offer_letter, request_obj=None):
    """Notify the next approver in the chain that it is now their turn to e-sign."""
    user = getattr(approver_employee, "employee_user_id", None)
    email = getattr(user, "email", None) if user else getattr(approver_employee, "email", None)
    if not email:
        return
    candidate_name = offer_letter.candidate_id.name if hasattr(offer_letter, "candidate_id") else ""
    position = getattr(offer_letter, "position", "")
    offer_ref = getattr(offer_letter, "offer_no", str(offer_letter.pk))
    letters_url = "/onboarding/letters/"
    if request_obj:
        try:
            letters_url = request_obj.build_absolute_uri(letters_url)
        except Exception:
            pass
    send_recruitment_email(
        subject=f"[FITS] Action Required: E-Sign Offer Letter {offer_ref}",
        body=(
            f"Dear {approver_employee},\n\n"
            f"It is now your turn to e-sign the offer letter for "
            f"{candidate_name}{(' (' + position + ')') if position else ''}.\n\n"
            f"Reference: {offer_ref}\n"
            f"Please visit the Letters page to review and sign:\n{letters_url}\n\n"
            f"Regards,\nHR Team"
        ),
        to=[email],
    )


def email_offer_approval_rejected_hr(offer_letter, rejector, feedback="", request_obj=None):
    """Email HR/superusers when an offer letter approval step is rejected."""
    try:
        from django.contrib.auth.models import User
        hr_users = User.objects.filter(is_superuser=True, is_active=True)
        emails = [u.email for u in hr_users if u.email]
        if not emails:
            return
        candidate_name = offer_letter.candidate_id.name if hasattr(offer_letter, "candidate_id") else ""
        offer_ref = getattr(offer_letter, "offer_no", str(offer_letter.pk))
        send_recruitment_email(
            subject=f"[FITS] Offer Letter Rejected – {offer_ref}",
            body=(
                f"The offer letter {offer_ref} for {candidate_name} was rejected by {rejector}.\n\n"
                + (f"Feedback: {feedback}\n\n" if feedback else "")
                + f"Please log in to FITS to review and take action.\n\nRegards,\nFITS System"
            ),
            to=emails,
        )
    except Exception:
        pass


def email_proposal_for_signature(proposal, approver_employee, request_obj=None):
    """Notify the next approver in the proposal e-sign chain."""
    user = getattr(approver_employee, "employee_user_id", None)
    email = getattr(user, "email", None) if user else getattr(approver_employee, "email", None)
    if not email:
        return
    list_url = "/recruitment/proposals/"
    if request_obj:
        try:
            list_url = request_obj.build_absolute_uri(list_url)
        except Exception:
            pass
    send_recruitment_email(
        subject=f"[FITS] Action Required: E-Sign Employment Proposal {proposal.proposal_no}",
        body=(
            f"Dear {approver_employee},\n\n"
            f"You have a pending signature on the Employment Proposal for "
            f"{proposal.applicant_name or proposal.candidate.name}.\n\n"
            f"Reference: {proposal.proposal_no}\n"
            f"Template: {proposal.get_template_type_display()}\n\n"
            f"Open the proposal here:\n{list_url}\n\n"
            f"Regards,\nHR Team"
        ),
        to=[email],
    )


def email_proposal_approved(proposal, request_obj=None):
    """Email HR / requester once a proposal is fully approved."""
    try:
        from django.contrib.auth.models import User
        hr_users = User.objects.filter(is_superuser=True, is_active=True)
        emails = [u.email for u in hr_users if u.email]
        if proposal.created_by and proposal.created_by.email:
            emails.append(proposal.created_by.email)
        emails = list({e for e in emails if e})
        if not emails:
            return
        send_recruitment_email(
            subject=f"[FITS] Proposal Approved: {proposal.proposal_no}",
            body=(
                f"Employment Proposal {proposal.proposal_no} for "
                f"{proposal.applicant_name or proposal.candidate.name} has been "
                f"approved by all signatories. You may now proceed to create the "
                f"Offer Letter.\n\nRegards,\nFITS"
            ),
            to=emails,
        )
    except Exception:
        pass


def email_proposal_rejected(proposal, feedback=""):
    """Email the proposal submitter when their proposal is rejected in the chain."""
    try:
        submitter = getattr(proposal, "created_by", None)
        email = getattr(submitter, "email", None)
        if not email:
            return
        cand_name = proposal.applicant_name or proposal.candidate.name
        send_recruitment_email(
            subject=f"[FITS] Employment Proposal Rejected – {proposal.proposal_no}",
            body=(
                f"Dear {submitter},\n\n"
                f"The Employment Proposal {proposal.proposal_no} for {cand_name} "
                f"was rejected during the approval process.\n"
                + (f"Feedback: {feedback}\n" if feedback else "")
                + f"\nPlease review at /recruitment/proposals/.\n\nRegards,\nFITS"
            ),
            to=[email],
        )
    except Exception:
        pass


def _site_url():
    return getattr(settings, "SITE_URL", os.environ.get("SITE_URL", "https://hcmspro.net"))


def _portal_url(offer):
    """Absolute URL of the candidate document portal for this offer."""
    try:
        from django.urls import reverse
        return f"{_site_url()}{reverse('candidate-portal', args=[str(offer.portal_token)])}"
    except Exception:
        return f"{_site_url()}/recruitment/portal/{offer.portal_token}/"


def email_candidate_documents_ready(offer, batch=1):
    """Email the candidate that documents are ready for them to e-sign in the portal."""
    candidate = offer.candidate_id
    if not candidate.email or "careers.local" in candidate.email:
        return
    if batch == 1:
        intro = (
            "Congratulations! Your offer has been approved. Please review and "
            "e-sign your offer letter in your personal candidate portal."
        )
    else:
        intro = (
            "Thank you for signing your offer letter. Additional onboarding "
            "documents are now ready for your e-signature in your portal."
        )
    send_recruitment_email(
        subject=f"Action Required: Documents to E-Sign – {offer.position}",
        body=(
            f"Dear {candidate.name},\n\n"
            f"{intro}\n\n"
            f"Open your portal (no login needed — this link is unique to you):\n"
            f"  {_portal_url(offer)}\n\n"
            f"In the portal you can e-sign the documents and upload your "
            f"certificates (academic, experience, medical, passport, ID).\n\n"
            f"Regards,\nHR Team"
        ),
        to=[candidate.email],
    )


def email_candidate_resign_request(doc):
    """Email the candidate to re-sign a document HR sent back."""
    offer = doc.offer
    candidate = offer.candidate_id
    if not candidate.email or "careers.local" in candidate.email:
        return
    send_recruitment_email(
        subject=f"Action Required: Please Re-Sign '{doc.title}'",
        body=(
            f"Dear {candidate.name},\n\n"
            f"HR has requested that you re-sign the document '{doc.title}'.\n"
            + (f"Note from HR: {doc.hr_note}\n" if doc.hr_note else "")
            + f"\nPlease open your portal and e-sign it again:\n"
            f"  {_portal_url(offer)}\n\n"
            f"Regards,\nHR Team"
        ),
        to=[candidate.email],
    )


def email_visa_team(offer):
    """Notify the visa team that a candidate's onboarding documents are complete."""
    to = getattr(settings, "VISA_TEAM_EMAIL", os.environ.get("VISA_TEAM_EMAIL", ""))
    if not to:
        return
    candidate = offer.candidate_id
    send_recruitment_email(
        subject=f"Visa Processing Request – {candidate.name} ({offer.position})",
        body=(
            f"All onboarding documents for the following new hire have been "
            f"signed and approved. Please initiate visa processing.\n\n"
            f"Candidate : {candidate.name}\n"
            f"Email     : {candidate.email}\n"
            f"Position  : {offer.position}\n"
            f"Department: {offer.department or '—'}\n"
            f"Joining   : {offer.joining_date}\n"
            f"Offer Ref : {offer.offer_no}\n\n"
            f"Regards,\nHR Team"
        ),
        to=[to],
    )


def email_sla_escalation(overdue_items: list):
    """
    Alert HR/superusers about approval steps that have exceeded their SLA deadline.

    overdue_items: list of dicts with keys: doc_type, ref, approver_name, due_at, hours_overdue
    """
    if not overdue_items:
        return
    try:
        from django.contrib.auth.models import User
        hr_users = User.objects.filter(is_superuser=True, is_active=True)
        emails = [u.email for u in hr_users if u.email]
        if not emails:
            return

        lines = []
        for item in overdue_items:
            lines.append(
                f"  • [{item['doc_type']}] {item['ref']} — "
                f"Awaiting: {item['approver_name']} — "
                f"Overdue by {item['hours_overdue']:.0f}h (due {item['due_at']})"
            )

        body = (
            f"The following approvals have exceeded their SLA deadline and require immediate attention:\n\n"
            + "\n".join(lines)
            + "\n\nPlease log in to FITS and follow up with the relevant approvers.\n\nRegards,\nFITS System"
        )
        send_recruitment_email(
            subject=f"[FITS] ⚠ SLA Breach — {len(overdue_items)} approval(s) overdue",
            body=body,
            to=emails,
        )
    except Exception:
        pass
