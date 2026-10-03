"""
recruitment/views/interview_evaluation.py

Panel evaluation — submit scores, view aggregated results per candidate.
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from fits.decorators import login_required
from recruitment.models import (
    Candidate,
    EvaluationCriteria,
    EvaluationScore,
    InterviewEvaluation,
    InterviewSchedule,
    JobApplication,
)


def _get_employee(user):
    return getattr(user, "employee_get", None)


def _hr_override_justification(candidate):
    """Lookup the HR-override justification (if any) on the matching JobApplication."""
    if not candidate:
        return ""
    app = (
        JobApplication.objects
        .filter(email=candidate.email, recruitment_id=candidate.recruitment_id, hr_override=True)
        .exclude(hr_override_justification__isnull=True)
        .exclude(hr_override_justification__exact="")
        .order_by("-created_at")
        .first()
    )
    return app.hr_override_justification if app else ""


@login_required
def evaluation_form(request, interview_id):
    """Panelist submits their evaluation for a scheduled interview."""
    interview = get_object_or_404(InterviewSchedule, id=interview_id)
    candidate = interview.candidate_id
    emp = _get_employee(request.user)
    criteria = EvaluationCriteria.objects.filter(is_active=True)

    # Check if panelist already submitted
    existing = InterviewEvaluation.objects.filter(
        interview=interview, panelist=emp
    ).first()

    if request.method == "POST":
        overall = float(request.POST.get("overall_score") or 0)
        recommendation = request.POST.get("recommendation", "maybe")
        strengths = request.POST.get("strengths", "")
        weaknesses = request.POST.get("weaknesses", "")
        notes = request.POST.get("notes", "")

        if existing:
            ev = existing
            ev.overall_score = overall
            ev.recommendation = recommendation
            ev.strengths = strengths
            ev.weaknesses = weaknesses
            ev.notes = notes
            ev.save()
        else:
            ev = InterviewEvaluation.objects.create(
                interview=interview,
                candidate=candidate,
                panelist=emp,
                overall_score=overall,
                recommendation=recommendation,
                strengths=strengths,
                weaknesses=weaknesses,
                notes=notes,
            )

        # Per-criteria scores
        for c in criteria:
            score_val = int(request.POST.get(f"score_{c.id}") or 0)
            comment_val = request.POST.get(f"comment_{c.id}", "")
            EvaluationScore.objects.update_or_create(
                evaluation=ev,
                criteria=c,
                defaults={"score": score_val, "comment": comment_val},
            )

        messages.success(request, _("Evaluation submitted."))
        return redirect("interview-evaluation-summary", interview_id=interview_id)

    return render(request, "recruitment/interview/evaluation_form.html", {
        "interview": interview,
        "candidate": candidate,
        "criteria": criteria,
        "existing": existing,
        "recommendation_choices": InterviewEvaluation.RECOMMENDATION_CHOICES,
        "hr_override_justification": _hr_override_justification(candidate),
    })


@login_required
def evaluation_summary(request, interview_id):
    """Aggregated panel scores for an interview — HR/manager view."""
    interview = get_object_or_404(InterviewSchedule, id=interview_id)
    candidate = interview.candidate_id
    evaluations = (
        interview.evaluations
        .select_related("panelist")
        .prefetch_related("scores__criteria")
        .all()
    )

    # Aggregate per criteria
    criteria_agg = {}
    for ev in evaluations:
        for s in ev.scores.all():
            name = s.criteria.name
            if name not in criteria_agg:
                criteria_agg[name] = {"total": 0, "count": 0, "max": s.criteria.max_score}
            criteria_agg[name]["total"] += s.score
            criteria_agg[name]["count"] += 1

    criteria_avg = [
        {
            "name": name,
            "avg": round(v["total"] / v["count"], 1) if v["count"] else 0,
            "max": v["max"],
            "pct": round((v["total"] / (v["count"] * v["max"])) * 100) if v["count"] else 0,
        }
        for name, v in criteria_agg.items()
    ]

    overall_avg = (
        round(sum(e.overall_score for e in evaluations) / len(evaluations), 1)
        if evaluations else 0
    )

    rec_counts = {}
    for ev in evaluations:
        rec_counts[ev.recommendation] = rec_counts.get(ev.recommendation, 0) + 1

    return render(request, "recruitment/interview/evaluation_summary.html", {
        "interview": interview,
        "candidate": candidate,
        "evaluations": evaluations,
        "criteria_avg": criteria_avg,
        "overall_avg": overall_avg,
        "rec_counts": rec_counts,
        "recommendation_choices": dict(InterviewEvaluation.RECOMMENDATION_CHOICES),
        "hr_override_justification": _hr_override_justification(candidate),
    })
