import json
import os

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from recruitment.cv_screening_ai import CVScreeningAI
from recruitment.cv_screening_fallback import mock_analyze_cv
from recruitment.models import Candidate, Recruitment


@login_required
def job_board_settings(request):
    return render(request, "recruitment/job_board_settings.html")


@login_required
def cv_screening(request):
    from recruitment.models_cv_screening import CandidateRankingScore

    ai_enabled = bool(os.getenv("OPENROUTER_API_KEY") or os.getenv("CV_SCREENING_AI_ENABLED"))

    ranked = (
        CandidateRankingScore.objects.select_related("candidate", "recruitment")
        .order_by("-overall_ranking_score")
    )

    recruitment_id = request.GET.get("recruitment")
    selected_recruitment = None
    if recruitment_id:
        selected_recruitment = Recruitment.objects.filter(pk=recruitment_id).first()
        if selected_recruitment:
            ranked = ranked.filter(recruitment=selected_recruitment)

    screened_ids = CandidateRankingScore.objects.values_list("candidate_id", flat=True)
    unscreened = Candidate.objects.exclude(resume="").exclude(resume=None).exclude(id__in=screened_ids)
    recruitments = Recruitment.objects.filter(closed=False).order_by("-id")[:20]

    return render(request, "recruitment/cv_screening_dashboard.html", {
        "ranked": ranked,
        "unscreened": unscreened,
        "recruitments": recruitments,
        "selected_recruitment": selected_recruitment,
        "ai_enabled": ai_enabled,
        "total_screened": ranked.count(),
        "total_unscreened": unscreened.count(),
    })


@login_required
@csrf_exempt
def cv_screening_upload(request):
    """API endpoint: upload a CV file and get AI analysis back as JSON."""
    if request.method == "POST":
        try:
            cv_file = request.FILES.get("cv_file")
            job_requirements = request.POST.get("job_requirements", "")

            if not cv_file:
                return JsonResponse({"error": "No CV file provided"}, status=400)
            if not job_requirements:
                return JsonResponse({"error": "Job requirements are required"}, status=400)

            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{cv_file.name}") as tmp:
                for chunk in cv_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            try:
                ai = CVScreeningAI()
                cv_content = ai.extract_cv_content(tmp_path)
                analysis = ai.analyze_cv_with_deepseek(cv_content, job_requirements)
                if not analysis:
                    analysis = mock_analyze_cv(cv_content, job_requirements)

                if analysis:
                    return JsonResponse({
                        "candidate_name": analysis.get("candidate_name", "Unknown"),
                        "skills": analysis.get("skills", []),
                        "years_experience": analysis.get("years_experience", 0),
                        "education": analysis.get("education", []),
                        "matching_score": analysis.get("matching_score", 0),
                        "matching_skills": analysis.get("matching_skills", []),
                        "missing_skills": analysis.get("missing_skills", []),
                        "summary": analysis.get("summary", ""),
                        "recommendation": analysis.get("recommendation", "interview"),
                    })
                return JsonResponse({"error": "AI analysis failed"}, status=500)
            finally:
                os.unlink(tmp_path)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST required"}, status=405)


@login_required
@require_POST
def cv_screening_trigger(request, candidate_id):
    if not os.getenv("OPENROUTER_API_KEY"):
        return JsonResponse({"error": "OPENROUTER_API_KEY not set. Add it to your .env to enable AI screening."}, status=400)

    candidate = get_object_or_404(Candidate, pk=candidate_id)
    if not candidate.resume:
        return JsonResponse({"error": "Candidate has no resume attached."}, status=400)

    recruitment_id = request.POST.get("recruitment_id")
    job_req = ""
    if recruitment_id:
        rec = Recruitment.objects.filter(pk=recruitment_id).first()
        if rec:
            job_req = f"{rec.job_position_id or ''} {rec.description or ''}"

    try:
        import threading
        def _run():
            from recruitment.cv_screening_ai import screen_candidate_cv
            screen_candidate_cv(candidate.id, job_req)
        threading.Thread(target=_run, daemon=True).start()
        return JsonResponse({"status": "queued", "candidate": candidate.name})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def candidate_evaluation(request):
    return render(request, "recruitment/candidate_evaluation.html")


@login_required
@require_POST
def bulk_send_rejection_emails(request, rec_id):
    """Send rejection emails to all weak-match candidates for a recruitment."""
    from recruitment.models_cv_screening import CandidateRankingScore
    from recruitment.views.views import _send_candidate_rejection_email

    recruitment = get_object_or_404(Recruitment, pk=rec_id)
    job_title = str(recruitment.job_position_id or recruitment.title or "the position")

    rejects = CandidateRankingScore.objects.filter(
        recruitment=recruitment,
        ranking_category="weak",
    ).select_related("candidate")

    sent = 0
    for score in rejects:
        cand = score.candidate
        if cand.email:
            try:
                _send_candidate_rejection_email(cand.email, cand.name, job_title)
                sent += 1
            except Exception:
                pass

    from django.contrib import messages
    messages.success(request, f"Rejection emails sent to {sent} candidate(s).")
    return redirect(f"{request.META.get('HTTP_REFERER', '/recruitment/cv-screening/')}?recruitment={rec_id}")
