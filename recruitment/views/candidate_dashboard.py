"""
recruitment/views/candidate_dashboard.py

Candidate Dashboard — KPIs + advanced search + paginated table + CV upload.
Advanced search: position, nationality, experience, skills, project, availability, phase.
"""

from datetime import timedelta

from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef, Q
from django.shortcuts import render
from django.utils import timezone

from fits.decorators import login_required
from recruitment.decorators import manager_can_enter
from recruitment.models import Candidate, InterviewSchedule, OfferLetter, Recruitment, Skill, Stage
from recruitment.models_proposal import EmploymentProposal


def _annotate_phase(candidates):
    """Annotate each candidate with has_offer, has_proposal, has_interview flags."""
    return candidates.annotate(
        has_offer=Exists(
            OfferLetter.objects.filter(candidate_id=OuterRef("pk"))
        ),
        has_proposal=Exists(
            EmploymentProposal.objects.filter(candidate=OuterRef("pk"))
        ),
        has_interview=Exists(
            InterviewSchedule.objects.filter(candidate_id=OuterRef("pk"))
        ),
    )


@login_required
@manager_can_enter(perm="recruitment.view_candidate")
def candidate_dashboard(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    candidates = Candidate.objects.select_related(
        "stage_id", "job_position_id", "recruitment_id"
    ).order_by("-id")

    total = candidates.count()
    new_this_week = candidates.filter(created_at__gte=week_ago).count()
    in_pipeline = candidates.filter(hired=False, canceled=False).exclude(
        stage_id__stage_type="hired"
    ).count()
    hired_this_month = candidates.filter(
        Q(hired=True) | Q(stage_id__stage_type="hired"),
        joining_date__gte=month_start.date(),
    ).count()

    # ── Advanced filters ──────────────────────────────────────────────
    GET = request.GET

    # Text search
    q = GET.get("q", "").strip()
    if q:
        candidates = candidates.filter(
            Q(name__icontains=q) | Q(email__icontains=q) | Q(mobile__icontains=q)
        )

    # Position filter
    position_id = GET.get("position")
    if position_id:
        candidates = candidates.filter(job_position_id_id=position_id)

    # Nationality / country
    nationality = GET.get("nationality", "").strip()
    if nationality == "omani":
        candidates = candidates.filter(country__iexact="OM")
    elif nationality == "expat":
        candidates = candidates.exclude(country__iexact="OM").exclude(country="")
    elif nationality:
        candidates = candidates.filter(country__iexact=nationality)

    # Experience range
    exp_min = GET.get("exp_min")
    exp_max = GET.get("exp_max")
    if exp_min:
        candidates = candidates.filter(experience_years__gte=float(exp_min))
    if exp_max:
        candidates = candidates.filter(experience_years__lte=float(exp_max))

    # Availability date
    avail_before = GET.get("avail_before")
    if avail_before:
        candidates = candidates.filter(
            Q(availability_date__lte=avail_before) | Q(availability_date__isnull=True)
        )

    # Stage filter
    stage_id = GET.get("stage")
    if stage_id:
        candidates = candidates.filter(stage_id_id=stage_id)

    # Source filter
    source = GET.get("source", "").strip()
    if source:
        candidates = candidates.filter(source=source)

    # Recruitment / project filter
    recruitment_id = GET.get("recruitment")
    if recruitment_id:
        candidates = candidates.filter(recruitment_id_id=recruitment_id)

    # Phase filter — applied after annotating
    phase_filter = GET.get("phase", "").strip()

    # Annotate with phase flags before phase filtering & pagination
    candidates = _annotate_phase(candidates)

    if phase_filter == "offer_letter":
        candidates = candidates.filter(has_offer=True)
    elif phase_filter == "proposal":
        candidates = candidates.filter(has_proposal=True, has_offer=False)
    elif phase_filter == "interview":
        candidates = candidates.filter(has_interview=True, has_proposal=False, has_offer=False)
    elif phase_filter == "hired":
        candidates = candidates.filter(Q(hired=True) | Q(stage_id__stage_type="hired"))
    elif phase_filter == "cancelled":
        candidates = candidates.filter(Q(canceled=True) | Q(stage_id__stage_type="cancelled"))
    elif phase_filter == "application":
        candidates = candidates.filter(
            has_interview=False, has_proposal=False, has_offer=False,
            hired=False, canceled=False
        ).exclude(stage_id__stage_type="hired").exclude(stage_id__stage_type="cancelled")

    paginator = Paginator(candidates, 25)
    page = paginator.get_page(GET.get("page"))

    # Choices for filter dropdowns
    from base.models import JobPosition
    sources = Candidate.objects.values_list("source", flat=True).distinct().exclude(source="")

    context = {
        "kpi_total": total,
        "kpi_new_week": new_this_week,
        "kpi_in_pipeline": in_pipeline,
        "kpi_hired_month": hired_this_month,
        "candidates_page": page,
        "q": q,
        "open_recruitments": Recruitment.objects.filter(closed=False),
        "stages": Stage.objects.all(),
        "job_positions": JobPosition.objects.all(),
        "sources": sorted(set(sources)),
        "filters": {
            "position": position_id or "",
            "nationality": nationality,
            "exp_min": exp_min or "",
            "exp_max": exp_max or "",
            "avail_before": avail_before or "",
            "stage": stage_id or "",
            "source": source,
            "recruitment": recruitment_id or "",
            "phase": phase_filter,
        },
    }
    return render(request, "recruitment/candidate_dashboard/index.html", context)
