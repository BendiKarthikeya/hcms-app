"""
recruitment/views/careers.py — Public careers page + application submission.

On submission:
  1. Candidate record created
  2. Confirmation email → candidate
  3. In-app notification + email → HR managers
  4. AI CV screening triggered (background)
"""

import threading
import uuid

from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse

from recruitment.models import Candidate, Recruitment, Stage


def _get_hr_emails(recruitment):
    from django.contrib.auth.models import User, Permission
    emails = set()
    for emp in recruitment.recruitment_managers.select_related("employee_user_id").all():
        if emp.employee_user_id and emp.employee_user_id.email:
            emails.add(emp.employee_user_id.email)
    perm = Permission.objects.filter(codename="view_candidate").first()
    if perm:
        for u in perm.user_set.filter(is_active=True):
            if u.email:
                emails.add(u.email)
    if not emails:
        for u in User.objects.filter(is_superuser=True, is_active=True):
            if u.email:
                emails.add(u.email)
    return list(emails)


def _notify_hr_inapp(candidate, recruitment):
    try:
        from notifications.signals import notify
        from django.contrib.auth.models import User
        sender = User.objects.filter(is_superuser=True, is_active=True).first()
        if not sender:
            return
        from django.contrib.auth.models import Permission
        perm = Permission.objects.filter(codename="view_candidate").first()
        recipients = list(perm.user_set.filter(is_active=True)) if perm else []
        if not recipients:
            recipients = list(User.objects.filter(is_superuser=True, is_active=True))
        for user in recipients:
            notify.send(
                sender,
                recipient=user,
                verb=f"New application: {candidate.name} applied for {recruitment.title or str(recruitment.job_position_id)}.",
                icon="person-add",
                redirect="/recruitment/candidates/dashboard/",
            )
    except Exception:
        pass


def _post_submit_actions(candidate, recruitment):
    def _run():
        from recruitment.email_utils import email_application_confirmation, email_hr_new_application
        # 1. Confirmation to candidate
        email_application_confirmation(candidate, recruitment)
        # 2. Alert to HR
        hr_emails = _get_hr_emails(recruitment)
        email_hr_new_application(candidate, recruitment, hr_emails)
        # 3. In-app notification
        _notify_hr_inapp(candidate, recruitment)
        # 4. AI CV screening (Groq → OpenRouter → regex fallback; no key needed)
        try:
            job_req = (
                f"{recruitment.job_position_id or ''} {recruitment.title or ''} "
                f"{getattr(recruitment, 'description', '') or ''}"
            )
            from recruitment.cv_screening_ai import screen_candidate_cv
            screen_candidate_cv(candidate.id, job_req)
        except Exception:
            pass

    threading.Thread(target=_run, daemon=True).start()


def careers_index(request):
    jobs = Recruitment.objects.filter(closed=False, is_public=True).select_related(
        "job_position_id", "company_id"
    )
    return render(request, "public/careers/index.html", {"jobs": jobs})


def careers_detail(request, slug):
    job = get_object_or_404(Recruitment, public_slug=slug, closed=False, is_public=True)
    return render(request, "public/careers/detail.html", {"job": job})


def careers_apply(request, slug):
    job = get_object_or_404(Recruitment, public_slug=slug, closed=False, is_public=True)

    if request.method == "POST":
        stage = (
            Stage.objects.filter(recruitment_id=job, stage_type="initial").first()
            or Stage.objects.filter(stage_type="initial").first()
        )
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip() or f"applicant-{uuid.uuid4().hex[:8]}@careers.local"
        mobile = request.POST.get("mobile", "").strip()
        resume = request.FILES.get("resume")

        cover_letter = request.FILES.get("cover_letter")
        graduation_certificate = request.FILES.get("graduation_certificate")
        transcripts = request.FILES.get("transcripts")

        if name and resume:
            candidate = Candidate.objects.create(
                name=name, email=email, mobile=mobile,
                resume=resume, recruitment_id=job, stage_id=stage, source="application",
                cover_letter=cover_letter,
                graduation_certificate=graduation_certificate,
                transcripts=transcripts,
            )
            _post_submit_actions(candidate, job)
            return render(request, "public/careers/apply_thanks.html", {
                "job": job, "candidate_name": name,
            })

    return render(request, "public/careers/apply.html", {"job": job})


def careers_feed(request):
    jobs = Recruitment.objects.filter(closed=False, is_public=True).values(
        "id", "title", "public_slug", "start_date",
        "job_position_id__job_position", "company_id__company",
    )
    data = [{"id": j["id"], "title": j["title"], "position": j["job_position_id__job_position"],
              "company": j["company_id__company"], "slug": j["public_slug"], "posted": str(j["start_date"])}
            for j in jobs]
    return JsonResponse({"vacancies": data})
