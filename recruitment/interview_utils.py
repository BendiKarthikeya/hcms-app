"""
recruitment/interview_utils.py

Utility: send an interview invitation email with .ics calendar attachment.
Called after an InterviewSchedule is created/updated.
"""

import textwrap
from datetime import datetime, timedelta
from email.mime.base import MIMEBase
from email import encoders

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone


def _make_ics(interview) -> bytes:
    """Generate a minimal .ics (iCalendar) file for the interview."""
    dt_date = interview.interview_date
    dt_time = interview.interview_time

    dt_start = datetime(
        dt_date.year, dt_date.month, dt_date.day,
        dt_time.hour, dt_time.minute, dt_time.second
    )
    dt_end = dt_start + timedelta(hours=1)

    fmt = "%Y%m%dT%H%M%S"
    location = interview.online_meeting_link or "To be confirmed"
    description = interview.description or "Interview"
    candidate_name = interview.candidate_id.name

    ics = textwrap.dedent(f"""\
        BEGIN:VCALENDAR
        VERSION:2.0
        PRODID:-//FITS HRMS//Interview//EN
        BEGIN:VEVENT
        DTSTART:{dt_start.strftime(fmt)}
        DTEND:{dt_end.strftime(fmt)}
        SUMMARY:Interview – {candidate_name}
        DESCRIPTION:{description}
        LOCATION:{location}
        STATUS:CONFIRMED
        END:VEVENT
        END:VCALENDAR
    """)
    return ics.encode("utf-8")


def send_interview_invite(interview, recipients: list):
    """
    Send interview invite email with .ics attachment to a list of email addresses.
    recipients: list of email strings
    """
    if not recipients:
        return

    subject = f"Interview Invitation – {interview.candidate_id.name}"
    body = (
        f"Dear Team,\n\n"
        f"You are invited to interview {interview.candidate_id.name}.\n\n"
        f"Date: {interview.interview_date}\n"
        f"Time: {interview.interview_time}\n"
    )
    if interview.online_meeting_link:
        body += f"Meeting Link: {interview.online_meeting_link}\n"
    body += f"\n{interview.description or ''}\n\nRegards,\nHR Team"

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "hr@company.com")
    msg = EmailMultiAlternatives(subject, body, from_email, recipients)

    # Attach .ics
    ics_bytes = _make_ics(interview)
    attachment = MIMEBase("text", "calendar", method="REQUEST", name="invite.ics")
    attachment.set_payload(ics_bytes)
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", 'attachment; filename="invite.ics"')
    msg.attach(attachment)

    try:
        msg.send()
        interview.invite_sent_at = timezone.now()
        interview.save(update_fields=["invite_sent_at"])
    except Exception:
        pass  # Don't crash the request if email fails


def send_interview_invite_to_panelists(interview):
    """Gather panelist + candidate emails and send invite."""
    emails = []
    for emp in interview.employee_id.all():
        user = getattr(emp, "employee_user_id", None)
        if user and user.email:
            emails.append(user.email)
    candidate_email = interview.candidate_id.email
    if candidate_email and "@" in candidate_email and "imported.local" not in candidate_email:
        emails.append(candidate_email)
    send_interview_invite(interview, emails)
