"""
recruitment/views/integrations.py

Integration stubs: Tawteen platform, email templates (interview invite, offer, rejection).
"""

from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from fits.decorators import login_required
from recruitment.decorators import manager_can_enter
from recruitment.models import Candidate, InterviewSchedule, OfferLetter


# ── Tawteen Platform Stub ─────────────────────────────────────────────────────

@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def tawteen_dashboard(request):
    """Tawteen integration dashboard — stub ready for API wiring."""
    import os
    api_endpoint = os.getenv("TAWTEEN_API_ENDPOINT", "") or getattr(settings, "TAWTEEN_API_ENDPOINT", "")
    api_key = os.getenv("TAWTEEN_API_KEY", "") or getattr(settings, "TAWTEEN_API_KEY", "")
    connected = bool(api_endpoint and api_key)

    test_result = None
    if request.method == "POST" and connected:
        try:
            import requests as req
            resp = req.get(
                api_endpoint.rstrip("/") + "/ping",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5,
            )
            test_result = "success" if resp.status_code < 400 else f"error_{resp.status_code}"
        except Exception as e:
            test_result = f"error: {e}"

    return render(request, "recruitment/integrations/tawteen.html", {
        "connected": connected,
        "api_endpoint": api_endpoint,
        "test_result": test_result,
    })


# ── Email Templates ───────────────────────────────────────────────────────────

def _send(subject, body, to_email):
    try:
        send_mail(
            subject, body,
            getattr(settings, "DEFAULT_FROM_EMAIL", "hr@company.com"),
            [to_email], fail_silently=True,
        )
    except Exception:
        pass


@login_required
@manager_can_enter(perm="recruitment.change_candidate")
def send_interview_email(request, cand_id):
    """Send a personalised interview invitation email to a candidate."""
    candidate = get_object_or_404(Candidate, id=cand_id)
    if request.method == "POST":
        date = request.POST.get("interview_date", "TBD")
        time = request.POST.get("interview_time", "TBD")
        link = request.POST.get("meeting_link", "")
        body = (
            f"Dear {candidate.name},\n\n"
            f"We are pleased to invite you for an interview.\n\n"
            f"Date: {date}\nTime: {time}\n"
        )
        if link:
            body += f"Meeting Link: {link}\n"
        body += "\nPlease confirm your attendance by replying to this email.\n\nRegards,\nHR Team"
        _send(f"Interview Invitation — {candidate.job_position_id or 'Position'}", body, candidate.email)
        messages.success(request, _(f"Interview invitation sent to {candidate.email}."))
        return redirect("candidate-view-individual", obj_id=cand_id)

    return render(request, "recruitment/integrations/interview_email_form.html", {
        "candidate": candidate
    })


@login_required
@manager_can_enter(perm="recruitment.change_candidate")
def send_offer_email(request, cand_id):
    """Send offer letter notification email to candidate."""
    candidate = get_object_or_404(Candidate, id=cand_id)
    offer = getattr(candidate, "offer_letter", None)
    if request.method == "POST":
        body = (
            f"Dear {candidate.name},\n\n"
            f"We are pleased to extend an offer for the position of "
            f"{offer.position if offer else 'the role'}.\n\n"
        )
        if offer:
            body += (
                f"Basic Salary: {offer.currency} {offer.basic_salary}\n"
                f"Joining Date: {offer.joining_date}\n"
            )
        body += "\nKindly confirm your acceptance at your earliest convenience.\n\nRegards,\nHR Team"
        _send(f"Offer Letter — {candidate.name}", body, candidate.email)
        messages.success(request, _(f"Offer email sent to {candidate.email}."))
        return redirect("candidate-view-individual", obj_id=cand_id)

    return render(request, "recruitment/integrations/offer_email_form.html", {
        "candidate": candidate, "offer": offer
    })


@login_required
@manager_can_enter(perm="recruitment.change_candidate")
def send_interview_reminder(request, interview_id):
    """Send a reminder email to the candidate about their scheduled interview."""
    interview = get_object_or_404(InterviewSchedule, id=interview_id)
    candidate = interview.candidate_id
    if request.method == "POST":
        note = request.POST.get("note", "").strip()
        body = (
            f"Dear {candidate.name},\n\n"
            f"This is a reminder for your upcoming interview.\n\n"
            f"Date: {interview.interview_date}\n"
        )
        if interview.interview_time:
            body += f"Time: {interview.interview_time}\n"
        if interview.online_meeting_link:
            body += f"Meeting Link: {interview.online_meeting_link}\n"
        if note:
            body += f"\n{note}\n"
        body += "\nPlease be prepared and confirm your attendance.\n\nRegards,\nHR Team"
        _send(f"Interview Reminder — {candidate.name}", body, candidate.email)
        messages.success(request, _(f"Reminder sent to {candidate.email}."))
        return redirect("interview-view")

    return render(request, "recruitment/integrations/interview_reminder_form.html", {
        "interview": interview,
        "candidate": candidate,
    })


@login_required
@manager_can_enter(perm="recruitment.change_candidate")
def send_rejection_email(request, cand_id):
    """Send a professional rejection email to a candidate."""
    candidate = get_object_or_404(Candidate, id=cand_id)
    if request.method == "POST":
        reason = request.POST.get("reason", "")
        body = (
            f"Dear {candidate.name},\n\n"
            f"Thank you for taking the time to interview with us. After careful consideration, "
            f"we have decided to move forward with other candidates.\n"
        )
        if reason:
            body += f"\n{reason}\n"
        body += "\nWe appreciate your interest and wish you success in your career.\n\nRegards,\nHR Team"
        _send("Application Update", body, candidate.email)
        messages.success(request, _(f"Rejection email sent to {candidate.email}."))
        return redirect("candidate-view-individual", obj_id=cand_id)

    return render(request, "recruitment/integrations/rejection_email_form.html", {
        "candidate": candidate
    })
