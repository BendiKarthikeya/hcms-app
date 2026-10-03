import sys
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

today = datetime.now()


def recruitment_close():
    """
    Closes recruitment campaigns that have reached their end date.

    """
    from recruitment.models import Recruitment

    today_date = today.date()

    recruitments = Recruitment.objects.filter(closed=False)

    for rec in recruitments:
        if rec.end_date:
            if rec.end_date == today_date:
                rec.closed = True
                rec.is_published = False
                rec.save()


def candidate_convert():
    """
    Converts candidates to a "converted" state if they already exist as users.
    """
    from django.contrib.auth.models import User

    from recruitment.models import Candidate

    candidates = Candidate.objects.filter(is_active=True)
    mails = list(Candidate.objects.values_list("email", flat=True))
    existing_emails = list(
        User.objects.filter(username__in=mails).values_list("email", flat=True)
    )
    for cand in candidates:
        if cand.email in existing_emails:
            cand.converted = True
            cand.save()


def escalate_overdue_approvals():
    """
    Check ManpowerApproval and OfferApproval records where the approver has not
    acted within the configured SLA hours. Send a single digest email to HR/superusers
    listing all overdue items.
    """
    try:
        from recruitment.models_approvals import ManpowerApproval, OfferApproval
        from recruitment.email_utils import email_sla_escalation

        now = timezone.now()
        overdue = []

        # Manpower approvals
        for ap in ManpowerApproval.objects.filter(
            action=ManpowerApproval.ACTION_PENDING,
            due_at__lt=now,
        ).select_related("approver", "manpower_request"):
            hours_over = (now - ap.due_at).total_seconds() / 3600
            ref = getattr(ap.manpower_request, "requisition_no", f"MR-{ap.manpower_request_id}")
            approver_name = str(ap.approver) if ap.approver else "Unknown"
            overdue.append({
                "doc_type": "Manpower Request",
                "ref": ref,
                "approver_name": approver_name,
                "due_at": ap.due_at.strftime("%d %b %Y %H:%M"),
                "hours_overdue": hours_over,
            })

        # Offer approvals
        for ap in OfferApproval.objects.filter(
            action=OfferApproval.ACTION_PENDING,
            due_at__lt=now,
        ).select_related("approver", "offer"):
            hours_over = (now - ap.due_at).total_seconds() / 3600
            ref = getattr(ap.offer, "offer_no", f"OL-{ap.offer_id}")
            approver_name = str(ap.approver) if ap.approver else "Unknown"
            overdue.append({
                "doc_type": "Offer Letter",
                "ref": ref,
                "approver_name": approver_name,
                "due_at": ap.due_at.strftime("%d %b %Y %H:%M"),
                "hours_overdue": hours_over,
            })

        if overdue:
            email_sla_escalation(overdue)
    except Exception:
        pass


if not any(
    cmd in sys.argv
    for cmd in ["makemigrations", "migrate", "compilemessages", "flush", "shell"]
):
    """
    Initializes and starts background tasks using APScheduler when the server is running.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(candidate_convert, "interval", minutes=5)
    scheduler.add_job(recruitment_close, "interval", hours=1)
    scheduler.add_job(escalate_overdue_approvals, "interval", hours=1)

    scheduler.start()
