"""
dashboard.py

This module is used to write dashboard related views
"""

import datetime

from django.core import serializers
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from base.models import Department, JobPosition
from employee.models import EmployeeWorkInformation
from fits.decorators import login_required
from recruitment.decorators import manager_can_enter
from recruitment.models import Candidate, Recruitment, SkillZone, Stage


def _build_stage_count_map(recruitment_ids):
    """Return {(recruitment_id, stage_type): count} in a single query."""
    rows = (
        Candidate.objects.filter(
            is_active=True,
            recruitment_id__in=recruitment_ids,
            stage_id__stage_type__in=[t[0] for t in Stage.stage_types],
        )
        .values("recruitment_id", "stage_id__stage_type")
        .annotate(cnt=Count("id"))
    )
    return {(r["recruitment_id"], r["stage_id__stage_type"]): r["cnt"] for r in rows}


@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def dashboard(request):
    """
    This method is used to render dashboard for recruitment module
    """
    candidates = Candidate.objects.all()
    stage_chart_count = 0
    dep_vacancy = 1 if Recruitment.objects.filter(closed=False, is_event_based=False).exists() else 0
    joining = 1 if EmployeeWorkInformation.objects.filter(date_joining__isnull=False).exists() else 0

    # Single query for per-job-position stage counts
    jobs = list(JobPosition.objects.all())
    all_job = [job.job_position for job in jobs]
    job_ids = [job.id for job in jobs]

    stage_types = ["initial", "test", "interview", "hired", "cancelled"]
    per_job_counts = (
        Candidate.objects.filter(
            job_position_id__in=job_ids,
            stage_id__stage_type__in=stage_types,
        )
        .values("job_position_id", "stage_id__stage_type")
        .annotate(cnt=Count("id"))
    )
    job_stage_map = {(r["job_position_id"], r["stage_id__stage_type"]): r["cnt"] for r in per_job_counts}

    initial   = [job_stage_map.get((job.id, "initial"),   0) for job in jobs]
    test      = [job_stage_map.get((job.id, "test"),      0) for job in jobs]
    interview = [job_stage_map.get((job.id, "interview"), 0) for job in jobs]
    hired     = [job_stage_map.get((job.id, "hired"),     0) for job in jobs]
    cancelled = [job_stage_map.get((job.id, "cancelled"), 0) for job in jobs]

    job_data = list(zip(all_job, initial, test, interview, hired, cancelled))

    recruitment_obj = Recruitment.objects.filter(closed=False).prefetch_related("recruitment_managers")
    ongoing_recruitments = recruitment_obj.count()

    rec_ids = list(recruitment_obj.values_list("id", flat=True))
    stage_count_map = _build_stage_count_map(rec_ids)

    for rec in recruitment_obj:
        for stage_type, _ in Stage.stage_types:
            stage_chart_count += stage_count_map.get((rec.id, stage_type), 0)
        if stage_chart_count >= 1:
            stage_chart_count = 1
            break

    accepted_count = Candidate.objects.filter(offer_letter_status="accepted").count()

    recruitment_manager_mapping = {
        rec.title: [m.get_full_name() for m in rec.recruitment_managers.all()]
        for rec in recruitment_obj
    }

    total_vacancy = recruitment_obj.aggregate(total=Sum("vacancy"))["total"] or 0

    hired_candidates = candidates.filter(
        Q(hired=True) | Q(stage_id__stage_type="hired")
    ).distinct()
    total_candidates = candidates.count()
    total_hired_candidates = hired_candidates.count()
    conversion_ratio = 0
    hired_ratio = 0
    total_candidate_ratio = 0
    acceptance_ratio = 0
    if total_candidates != 0:
        conversion_ratio = f"{((total_hired_candidates / total_candidates) * 100):.1f}"
    if total_vacancy != 0:
        hired_ratio = f"{((total_hired_candidates / total_vacancy) * 100):.1f}"
        total_candidate_ratio = f"{((total_candidates / total_vacancy) * 100):.1f}"
    if total_hired_candidates != 0:
        acceptance_ratio = f"{((accepted_count / total_hired_candidates) * 100):.1f}"

    skill_zone = SkillZone.objects.filter(is_active=True)
    return render(
        request,
        "dashboard/dashboard.html",
        {
            "ongoing_recruitments": ongoing_recruitments,
            "total_candidate_ratio": total_candidate_ratio,
            "total_hired_candidates": total_hired_candidates,
            "conversion_ratio": conversion_ratio,
            "acceptance_ratio": acceptance_ratio,
            "onboard_candidates": hired_candidates.filter(
                onboarding_stage__isnull=False
            ),
            "job_data": job_data,
            "total_vacancy": total_vacancy,
            "recruitment_manager_mapping": recruitment_manager_mapping,
            "hired_ratio": hired_ratio,
            "joining": joining,
            "dep_vacancy": dep_vacancy,
            "stage_chart_count": stage_chart_count,
            "onboarding_count": hired_candidates.filter(
                onboarding_stage__isnull=False
            ).count(),
            "total_candidates": total_candidates,
            "skill_zone": skill_zone,
        },
    )


@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def dashboard_pipeline(request):
    """
    This method is used generate recruitment dataset for the dashboard
    """
    recruitment_obj = list(Recruitment.objects.filter(closed=False))
    rec_ids = [r.id for r in recruitment_obj]
    stage_count_map = _build_stage_count_map(rec_ids)
    has_candidates = set(
        Candidate.objects.filter(recruitment_id__in=rec_ids, is_active=True)
        .values_list("recruitment_id", flat=True)
        .distinct()
    )

    data_set = []
    labels = [type[1] for type in Stage.stage_types]
    for rec in recruitment_obj:
        if rec.id not in has_candidates:
            continue
        data = [stage_count_map.get((rec.id, t[0]), 0) for t in Stage.stage_types]
        data_set.append(
            {
                "label": rec.title if rec.title is not None else f"{rec.job_position_id} {rec.start_date}",
                "data": data,
            }
        )
    return JsonResponse(
        {
            "dataSet": data_set,
            "labels": labels,
            "message": _("No records available at the moment."),
        }
    )


@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def dashboard_hiring(request):
    """
    This method is used generate employee joining status for the dashboard
    """

    selected_year = request.GET.get("id")

    employee_info = EmployeeWorkInformation.objects.filter(
        date_joining__year=selected_year
    )

    # Create a list to store the count of employees for each month
    employee_count_per_month = [0] * 12  # Initialize with zeros for all months

    # Count the number of employees who joined in each month for the selected year
    for info in employee_info:
        if isinstance(info.date_joining, datetime.date):
            month_index = info.date_joining.month - 1  # Month index is zero-based
            employee_count_per_month[month_index] += (
                1  # Increment the count for the corresponding month
            )

    labels = [
        _("January"),
        _("February"),
        _("March"),
        _("April"),
        _("May"),
        _("June"),
        _("July"),
        _("August"),
        _("September"),
        _("October"),
        _("November"),
        _("December"),
    ]

    data_set = [
        {
            "label": _("Employees joined in %(year)s") % {"year": selected_year},
            "data": employee_count_per_month,
            "backgroundColor": "rgba(236, 131, 25)",
        }
    ]

    return JsonResponse({"dataSet": data_set, "labels": labels})


@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def dashboard_vacancy(_request):
    """
    This method is used to generate a recruitment vacancy chart for the dashboard
    """

    recruitment_obj = Recruitment.objects.filter(closed=False, is_event_based=False)
    department = Department.objects.all()
    label = []
    data_set = [{"label": _("Openings"), "data": []}]

    for dep in department:
        vacancies_for_department = recruitment_obj.filter(
            job_position_id__department_id=dep
        )
        for rec in vacancies_for_department:
            if rec.vacancy is not None:
                label.append(dep.department)

        vacancies = [
            int(rec.vacancy) if rec.vacancy is not None else 0
            for rec in vacancies_for_department
        ]

        data_set[0]["data"].append([sum(vacancies)])

    return JsonResponse({"dataSet": data_set, "labels": label})


def get_open_position(request):
    """
    This is an ajax method to render the open position to the recruitment

    Returns:
        obj: it returns the list of job positions
    """
    rec_id = request.GET["recId"]
    recruitment_obj = Recruitment.objects.get(id=rec_id)
    queryset = recruitment_obj.open_positions.all()
    job_info = serializers.serialize("json", queryset)
    rec_info = serializers.serialize("json", [recruitment_obj])
    return JsonResponse({"openPositions": job_info, "recruitmentInfo": rec_info})


@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def candidate_status(_request):
    """
    This method is used to generate a CAndidate status chart for the dashboard
    """

    not_sent_candidates = Candidate.objects.filter(
        offer_letter_status="not_sent"
    ).count()
    sent_candidates = Candidate.objects.filter(offer_letter_status="sent").count()
    accepted_candidates = Candidate.objects.filter(
        offer_letter_status="accepted"
    ).count()
    rejected_candidates = Candidate.objects.filter(
        offer_letter_status="rejected"
    ).count()
    joined_candidates = Candidate.objects.filter(offer_letter_status="joined").count()

    data_set = []
    labels = ["Not Sent", "Sent", "Accepted", "Rejected", "Joined"]
    data = [
        not_sent_candidates,
        sent_candidates,
        accepted_candidates,
        rejected_candidates,
        joined_candidates,
    ]

    for i in range(len(data)):
        data_set.append({"label": labels[i], "data": data[i]})

    # for i in range(len(data)):
    #     if data[i] != 0:
    #         data_set.append({
    #             "label": labels[i],
    #             "data": data[i]
    #         })

    # # Remove labels corresponding to data points with value 0
    # labels = [label for label, d in zip(labels, data) if d != 0]

    return JsonResponse({"dataSet": data_set, "labels": labels})
