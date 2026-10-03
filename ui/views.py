import calendar
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, IntegerField, OuterRef, Q, Subquery
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from recruitment.models import (
    Candidate,
    CandidateScreeningProfile,
    InterviewSchedule,
    OfferLetter,
    Recruitment,
    RecruitmentApproval,
)
from recruitment.models_approvals import ManpowerApproval


@login_required(login_url="/ui/login/")
def dashboard(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)

    open_req_count = Recruitment.objects.filter(closed=False, is_active=True).count()

    candidates_qs = Candidate.objects.filter(is_active=True, canceled=False)
    cand_agg = candidates_qs.aggregate(
        total=Count("id"),
        hired_count=Count("id", filter=Q(hired=True)),
        hired_month=Count("id", filter=Q(hired=True, joining_date__gte=month_start)),
    )
    total_candidates = cand_agg["total"]
    hired_total = cand_agg["hired_count"]
    hires_this_month = cand_agg["hired_month"]
    pipeline_efficiency = round((hired_total / total_candidates) * 100, 1) if total_candidates else 0.0

    interviews_count = InterviewSchedule.objects.filter(
        interview_date__gte=today, completed=False
    ).count()

    shortlisted_count = CandidateScreeningProfile.objects.filter(
        status="shortlisted"
    ).count()
    quality_score = 7.5  # placeholder until a scoring source is defined

    stage_counts = dict(
        candidates_qs.values_list("stage_id__stage_type").annotate(c=Count("id"))
    )
    offers_count = OfferLetter.objects.filter(
        status__in=["draft", "pending_approval", "sent", "accepted"]
    ).count()

    rec_agg = Recruitment.objects.filter(is_active=True).aggregate(
        requested=Count("id", filter=Q(approval_status="pending")),
        approved=Count("id", filter=Q(approval_status="approved")),
        published=Count("id", filter=Q(is_published=True)),
    )
    pipeline = [
        {"label": "Requested",    "icon": "description",  "icon_path": "images/figma/pipeline_requested.svg",    "count": rec_agg["requested"]},
        {"label": "Approved",     "icon": "verified",     "icon_path": "images/figma/pipeline_approved.svg",     "count": rec_agg["approved"]},
        {"label": "Published",    "icon": "publish",      "icon_path": "images/figma/pipeline_published.svg",    "count": rec_agg["published"]},
        {"label": "Applications", "icon": "groups",       "icon_path": "images/figma/pipeline_applications.svg", "count": stage_counts.get("applied", 0) + stage_counts.get("initial", 0)},
        {"label": "Shortlisted",  "icon": "checklist",    "icon_path": "images/figma/pipeline_shortlisted.svg",  "count": shortlisted_count},
        {"label": "Interview",    "icon": "forum",        "icon_path": "images/figma/pipeline_interview.svg",    "count": stage_counts.get("interview", 0)},
        {"label": "Offers",       "icon": "assignment",   "icon_path": "images/figma/pipeline_offers.svg",       "count": offers_count},
        {"label": "Hired",        "icon": "how_to_reg",   "icon_path": "images/figma/pipeline_hired.svg",        "count": stage_counts.get("hired", 0) or hired_total, "highlight": True},
    ]

    _next_seq = (
        RecruitmentApproval.objects
        .filter(recruitment=OuterRef("recruitment"), status="pending")
        .order_by("sequence").values("sequence")[:1]
    )
    if request.user.is_superuser or request.user.is_staff:
        rec_pending = (
            RecruitmentApproval.objects
            .filter(status="pending")
            .annotate(_next=Subquery(_next_seq, output_field=IntegerField()))
            .filter(_next=F("sequence"))
            .select_related("recruitment", "recruitment__raised_by")
            .order_by("-id")[:5]
        )
    else:
        rec_pending = (
            RecruitmentApproval.objects
            .filter(status="pending", approver__employee_user_id=request.user)
            .annotate(_next=Subquery(_next_seq, output_field=IntegerField()))
            .filter(_next=F("sequence"))
            .select_related("recruitment", "recruitment__raised_by")
            .order_by("-id")[:5]
        )

    _next_mp_seq = (
        ManpowerApproval.objects
        .filter(request=OuterRef("request"), action="pending")
        .order_by("step__sequence")
        .values("step__sequence")[:1]
    )
    if request.user.is_superuser or request.user.is_staff:
        mp_pending = (
            ManpowerApproval.objects
            .filter(action="pending")
            .annotate(_next=Subquery(_next_mp_seq, output_field=IntegerField()))
            .filter(_next=F("step__sequence"))
            .select_related("request", "request__job_position", "request__requested_by")
            .order_by("-id")[:5]
        )
    else:
        mp_pending = (
            ManpowerApproval.objects
            .filter(action="pending", approver__employee_user_id=request.user)
            .annotate(_next=Subquery(_next_mp_seq, output_field=IntegerField()))
            .filter(_next=F("step__sequence"))
            .select_related("request", "request__job_position", "request__requested_by")
            .order_by("-id")[:5]
        )

    pending_approvals = []
    for ra in rec_pending:
        pending_approvals.append({
            "req_id": ra.recruitment.job_id or f"REC-{ra.recruitment.id}",
            "title": ra.recruitment.title or str(ra.recruitment),
            "requested_by": ra.recruitment.raised_by.get_full_name() if ra.recruitment.raised_by else "—",
            "url": "/ui/approvals/",
        })
    for mp in mp_pending:
        pending_approvals.append({
            "req_id": mp.request.requisition_no,
            "title": str(mp.request.job_position) if mp.request.job_position else "Manpower Request",
            "requested_by": mp.request.requested_by.get_full_name() if mp.request.requested_by else "—",
            "url": f"/ui/manpower-approval/{mp.request.id}/",
        })
    pending_approvals = pending_approvals[:5]

    upcoming_interviews = (
        InterviewSchedule.objects.filter(interview_date__gte=today, completed=False)
        .select_related("candidate_id", "candidate_id__recruitment_id")
        .order_by("interview_date", "interview_time")[:5]
    )

    interview_days = set(
        InterviewSchedule.objects.filter(
            interview_date__year=today.year, interview_date__month=today.month
        ).values_list("interview_date__day", flat=True)
    )

    cal = calendar.Calendar(firstweekday=6)  # Sunday-first
    calendar_weeks = []
    for week in cal.monthdatescalendar(today.year, today.month):
        row = []
        for d in week:
            row.append({
                "day": d.day,
                "in_month": d.month == today.month,
                "is_today": d == today,
                "has_event": d.month == today.month and d.day in interview_days,
            })
        calendar_weeks.append(row)

    recent_activities = (
        RecruitmentApproval.objects.filter(approved_at__isnull=False)
        .select_related("recruitment", "approver")
        .order_by("-approved_at")[:6]
    )

    kpis = [
        {"icon": "work_outline", "icon_path": "images/figma/kpi_open_req_icon.svg",   "value": open_req_count,        "label": "Open Requisition",       "trend": "20%"},
        {"icon": "speed",        "icon_path": "images/figma/kpi_pipeline_icon.svg",   "value": pipeline_efficiency,   "label": "Pipeline Efficiency",     "trend": "13%", "suffix": "%"},
        {"icon": "star_outline", "icon_path": "images/figma/kpi_quality_icon.svg",    "value": quality_score,         "label": "Recruitment Quality",     "trend": "20%", "suffix": "/10"},
        {"icon": "event",        "icon_path": "images/figma/kpi_interviews_icon.svg", "value": interviews_count,      "label": "Interviews Scheduled",    "trend": "13%"},
        {"icon": "person_check", "icon_path": "images/figma/kpi_hires_icon.svg",      "value": hires_this_month,      "label": "Hires this Month",        "trend": "25%"},
    ]

    context = {
        "kpis": kpis,
        "pipeline": pipeline,
        "pending_approvals": pending_approvals,
        "upcoming_interviews": upcoming_interviews,
        "interview_days": interview_days,
        "calendar_weeks": calendar_weeks,
        "recent_activities": recent_activities,
        "shortlisted_count": shortlisted_count,
        "today": today,
        "calendar_month_label": today.strftime("%B %Y"),
    }
    return render(request, "ui/dashboard.html", context)


@login_required(login_url="/ui/login/")
def dashboard_calendar_events(request):
    from datetime import date as _date
    today = timezone.localdate()
    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
        if not (1 <= month <= 12) or not (2000 <= year <= 2100):
            raise ValueError()
    except (ValueError, TypeError):
        year, month = today.year, today.month

    month_interviews = (
        InterviewSchedule.objects.filter(
            interview_date__year=year, interview_date__month=month, completed=False
        ).select_related("candidate_id", "candidate_id__recruitment_id")
        .order_by("interview_date", "interview_time")
    )

    interview_days = set(iv.interview_date.day for iv in month_interviews)

    cal = calendar.Calendar(firstweekday=6)
    weeks = []
    for week in cal.monthdatescalendar(year, month):
        row = []
        for d in week:
            row.append({
                "day": d.day,
                "in_month": d.month == month,
                "is_today": d == today,
                "has_event": d.month == month and d.day in interview_days,
            })
        weeks.append(row)

    schedule = []
    for iv in month_interviews[:5]:
        schedule.append({
            "date": iv.interview_date.strftime("%-d %b"),
            "time": iv.interview_time.strftime("%-I:%M %p") if iv.interview_time else "—",
            "title": (iv.candidate_id.recruitment_id.title if iv.candidate_id and iv.candidate_id.recruitment_id else None) or "Interview",
            "candidate": iv.candidate_id.name if iv.candidate_id else "—",
        })

    return JsonResponse({
        "year": year,
        "month": month,
        "month_label": f"{calendar.month_name[month]} {year}",
        "weeks": weeks,
        "schedule": schedule,
    })


@login_required(login_url="/ui/login/")
def candidates(request):
    """
    Self-contained copy of recruitment.views.candidate_dashboard.candidate_dashboard,
    rendering the new UI template at ui/candidates.html.
    Behaviour (filters, pagination, KPI logic) mirrors the legacy view.
    """
    from datetime import timedelta
    from django.core.paginator import Paginator
    from django.db.models import Exists, OuterRef, Q
    from django.utils import timezone

    from base.models import JobPosition
    from recruitment.models import (
        Candidate as _Candidate,
        InterviewSchedule as _InterviewSchedule,
        OfferLetter as _OfferLetter,
        Recruitment as _Recruitment,
        Stage as _Stage,
    )
    from recruitment.models_proposal import EmploymentProposal as _EmploymentProposal

    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    candidates_qs = _Candidate.objects.entire().select_related(
        "stage_id", "job_position_id", "recruitment_id", "screening_profile"
    ).order_by("-id")

    cand_kpis = _Candidate.objects.entire().aggregate(
        total=Count("id"),
        new_this_week=Count("id", filter=Q(created_at__gte=week_ago)),
        new_this_month=Count("id", filter=Q(created_at__gte=month_start)),
        in_pipeline=Count(
            "id",
            filter=Q(hired=False, canceled=False)
            & (Q(stage_id__isnull=True) | ~Q(stage_id__stage_type="hired")),
        ),
        hired_this_month=Count(
            "id",
            filter=(Q(hired=True) | Q(stage_id__stage_type="hired"))
            & Q(joining_date__gte=month_start.date()),
        ),
        shortlist=Count("id", filter=Q(screening_profile__status="shortlisted")),
        rejected=Count("id", filter=Q(canceled=True) | Q(stage_id__stage_type="cancelled")),
    )
    total = cand_kpis["total"]
    new_this_week = cand_kpis["new_this_week"]
    new_this_month = cand_kpis["new_this_month"]
    in_pipeline = cand_kpis["in_pipeline"]
    hired_this_month = cand_kpis["hired_this_month"]
    shortlist_count = cand_kpis["shortlist"]
    rejected_count = cand_kpis["rejected"]

    GET = request.GET
    q = GET.get("q", "").strip()
    if q:
        candidates_qs = candidates_qs.filter(
            Q(name__icontains=q) | Q(email__icontains=q) | Q(mobile__icontains=q)
        )

    position_id = GET.get("position")
    if position_id:
        candidates_qs = candidates_qs.filter(job_position_id_id=position_id)

    nationality = GET.get("nationality", "").strip()
    if nationality == "omani":
        candidates_qs = candidates_qs.filter(country__iexact="OM")
    elif nationality == "expat":
        candidates_qs = candidates_qs.exclude(country__iexact="OM").exclude(country="")
    elif nationality:
        candidates_qs = candidates_qs.filter(country__iexact=nationality)

    exp_min = GET.get("exp_min")
    exp_max = GET.get("exp_max")
    if exp_min:
        candidates_qs = candidates_qs.filter(experience_years__gte=float(exp_min))
    if exp_max:
        candidates_qs = candidates_qs.filter(experience_years__lte=float(exp_max))

    avail_before = GET.get("avail_before")
    if avail_before:
        candidates_qs = candidates_qs.filter(
            Q(availability_date__lte=avail_before) | Q(availability_date__isnull=True)
        )

    stage_id = GET.get("stage")
    if stage_id:
        candidates_qs = candidates_qs.filter(stage_id_id=stage_id)

    source = GET.get("source", "").strip()
    if source:
        candidates_qs = candidates_qs.filter(source=source)

    recruitment_id = GET.get("recruitment")
    if recruitment_id:
        candidates_qs = candidates_qs.filter(recruitment_id_id=recruitment_id)

    phase_filter = GET.get("phase", "").strip()

    candidates_qs = candidates_qs.annotate(
        has_offer=Exists(_OfferLetter.objects.filter(candidate_id=OuterRef("pk"))),
        has_proposal=Exists(_EmploymentProposal.objects.filter(candidate=OuterRef("pk"))),
        has_interview=Exists(_InterviewSchedule.objects.filter(candidate_id=OuterRef("pk"))),
    )

    if phase_filter == "offer_letter":
        candidates_qs = candidates_qs.filter(has_offer=True)
    elif phase_filter == "proposal":
        candidates_qs = candidates_qs.filter(has_proposal=True, has_offer=False)
    elif phase_filter == "interview":
        candidates_qs = candidates_qs.filter(has_interview=True, has_proposal=False, has_offer=False)
    elif phase_filter == "hired":
        candidates_qs = candidates_qs.filter(Q(hired=True) | Q(stage_id__stage_type="hired"))
    elif phase_filter == "cancelled":
        candidates_qs = candidates_qs.filter(Q(canceled=True) | Q(stage_id__stage_type="cancelled"))
    elif phase_filter == "application":
        candidates_qs = candidates_qs.filter(
            has_interview=False, has_proposal=False, has_offer=False,
            hired=False, canceled=False,
        ).exclude(stage_id__stage_type="hired").exclude(stage_id__stage_type="cancelled")

    top_n = GET.get("top_n", "").strip()
    if top_n in ("10", "25", "50"):
        candidates_qs = list(
            candidates_qs
            .filter(screening_profile__status__in=["screened", "shortlisted"])
            .order_by("-screening_profile__matching_score")[:int(top_n)]
        )

    paginator = Paginator(candidates_qs, 25)
    page = paginator.get_page(GET.get("page"))

    # Attach a JSON blob of the AI screening result to each row for the
    # analysis modal (built here so it is valid JSON, not a repr of a list).
    import json as _json
    for c in page.object_list:
        try:
            prof = c.screening_profile
        except Exception:
            prof = None
        if prof and prof.status != "pending":
            c.ai_json = _json.dumps({
                "name": c.name,
                "score": prof.matching_score,
                "recommendation": prof.get_recommendation_display() or "",
                "recommendation_raw": prof.recommendation or "",
                "experience": prof.years_experience or 0,
                "summary": prof.summary or "",
                "matching": prof.matching_skills or [],
                "missing": prof.missing_skills or [],
                "scoring_breakdown": prof.scoring_breakdown or {},
                "ai_reasoning": prof.ai_reasoning or "",
                "grand_total": prof.oneic_grand_total or 0,
                "percentage": prof.oneic_percentage or prof.matching_score or 0,
                "hr_override": prof.hr_override,
                "status": prof.status,
            })
        else:
            c.ai_json = ""

    sources = (
        _Candidate.objects.entire().values_list("source", flat=True).distinct().exclude(source="")
    )

    context = {
        "kpi_total": total,
        "kpi_new_week": new_this_week,
        "kpi_new_month": new_this_month,
        "kpi_in_pipeline": in_pipeline,
        "kpi_hired_month": hired_this_month,
        "kpi_shortlist": shortlist_count,
        "kpi_rejected": rejected_count,
        "candidates_page": page,
        "q": q,
        "open_recruitments": _Recruitment.objects.filter(closed=False),
        "stages": _Stage.objects.all(),
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
            "top_n": top_n,
        },
    }
    return render(request, "ui/candidates.html", context)


@login_required(login_url="/ui/login/")
def job_requisition(request):
    """List of all recruitment requisitions with filters and KPIs.

    Visibility rules:
    - Superuser: all records
    - Everyone else: records they raised + records where their approval step
      is the *first* pending step (i.e. it's currently their turn to act)
    """
    from django.core.paginator import Paginator
    from django.db.models import F, IntegerField, OuterRef, Q, Subquery
    from recruitment.models import Recruitment as _Recruitment, RecruitmentApproval as _RA

    base = _Recruitment.objects.filter(is_active=True)

    if request.user.is_superuser:
        scoped = base
    else:
        next_pending_seq = _RA.objects.filter(
            recruitment=OuterRef("pk"), status="pending"
        ).order_by("sequence").values("sequence")[:1]
        my_pending_seq = _RA.objects.filter(
            recruitment=OuterRef("pk"), status="pending",
            approver__employee_user_id=request.user,
        ).order_by("sequence").values("sequence")[:1]
        scoped = (
            base
            .annotate(
                _next=Subquery(next_pending_seq, output_field=IntegerField()),
                _mine=Subquery(my_pending_seq, output_field=IntegerField()),
            )
            .filter(
                Q(raised_by__employee_user_id=request.user)
                | Q(_mine__isnull=False, _mine=F("_next"))
            )
            .distinct()
        )

    qs = scoped.select_related(
        "raised_by", "raised_by__employee_work_info",
        "raised_by__employee_work_info__job_position_id",
        "job_position_id", "job_position_id__department_id",
    ).order_by("-created_at")

    q = request.GET.get("q", "").strip()
    if q:
        q_filter = (
            Q(title__icontains=q)
            | Q(job_position_id__job_position__icontains=q)
            | Q(job_position_id__department_id__department__icontains=q)
            | Q(job_id__icontains=q)
            | Q(raised_by__employee_first_name__icontains=q)
            | Q(raised_by__employee_last_name__icontains=q)
        )
        # allow "REQ-42" or "42" to match by pk
        import re as _re
        numeric = _re.sub(r'^(?:REQ|req|JB|jb)[-_]?', '', q).strip()
        if numeric.isdigit():
            q_filter |= Q(pk=int(numeric))
        qs = qs.filter(q_filter)

    status = request.GET.get("status", "").strip()
    if status == "open":
        qs = qs.filter(closed=False)
    elif status == "pending":
        qs = qs.filter(approval_status="pending")
    elif status == "approved":
        qs = qs.filter(approval_status="approved")
    elif status == "rejected":
        qs = qs.filter(approval_status="rejected")

    department = request.GET.get("department", "").strip()
    if department:
        qs = qs.filter(job_position_id__department_id=department)

    req_type = request.GET.get("req_type", "").strip()
    if req_type:
        qs = qs.filter(employment_type=req_type)

    from base.models import Department
    departments = Department.objects.filter(is_active=True).order_by("department")

    page = Paginator(qs, 25).get_page(request.GET.get("page"))

    kpi_agg = scoped.aggregate(
        total=Count("id", distinct=True),
        open=Count("id", filter=Q(closed=False), distinct=True),
        pending=Count("id", filter=Q(approval_status="pending"), distinct=True),
        approved=Count("id", filter=Q(approval_status="approved"), distinct=True),
        rejected=Count("id", filter=Q(approval_status="rejected"), distinct=True),
    )
    kpi_total    = kpi_agg["total"]
    kpi_open     = kpi_agg["open"]
    kpi_pending  = kpi_agg["pending"]
    kpi_approved = kpi_agg["approved"]
    kpi_rejected = kpi_agg["rejected"]

    return render(request, "ui/job_requisition.html", {
        "page": page,
        "q": q,
        "status": status,
        "department": department,
        "req_type": req_type,
        "departments": departments,
        "kpi_total": kpi_total,
        "kpi_open": kpi_open,
        "kpi_pending": kpi_pending,
        "kpi_approved": kpi_approved,
        "kpi_rejected": kpi_rejected,
    })


@login_required(login_url="/ui/login/")
def jd_creator(request):
    """AI Job Description Creator. 'Use This Description' POSTs title +
    description; we stash them in the session and redirect to the New Manpower
    Request page where the user completes the rest (vacancy, date, justification)
    and submits for approval. No Recruitment row is created here."""
    from django.contrib import messages
    from django.shortcuts import redirect

    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        description = request.POST.get("description", "")
        if not description.strip():
            messages.error(request, "Generate a JD first, then click \"Use This Description\".")
            return redirect("ui:jd-creator")
        request.session["ui_jd_prefill"] = {
            "title": title,
            "description": description,
        }
        messages.success(request, "JD ready — complete the request details below.")
        return redirect("ui:manpower-request")
    return render(request, "ui/jd_creator.html")


@login_required(login_url="/ui/login/")
def approvals(request):
    """
    Pending approvals inbox — self-contained copy of the active part of
    recruitment.views.views.received_recruitments. Posts approve/reject still
    use the existing legacy endpoints (those handlers stay frozen) so behaviour
    is identical to the legacy "Received Recruitments" page.
    """
    from datetime import timedelta
    from django.db.models import F, Max, OuterRef, Subquery, IntegerField
    from django.utils import timezone

    from recruitment.models import Recruitment as _Recruitment, RecruitmentApproval as _RecruitmentApproval

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    next_step_seq = (
        _RecruitmentApproval.objects
        .filter(recruitment=OuterRef("pk"), status="pending")
        .order_by("sequence").values("sequence")[:1]
    )
    my_pending_seq = (
        _RecruitmentApproval.objects
        .filter(
            recruitment=OuterRef("pk"),
            status="pending",
            approver__employee_user_id=request.user,
        )
        .order_by("sequence").values("sequence")[:1]
    )
    pending = (
        _Recruitment.objects.filter(
            raised_from_employee=True,
            approval_status="pending",
        )
        .annotate(
            _next_step=Subquery(next_step_seq, output_field=IntegerField()),
            _my_step=Subquery(my_pending_seq, output_field=IntegerField()),
        )
        .filter(_my_step=F("_next_step"))
        .select_related("raised_by")
        .prefetch_related("approvals__approver")
        .distinct()
    )

    rows = []
    for rec in pending:
        my_step = next(
            (a for a in rec.approvals.all()
             if a.status == "pending" and getattr(a.approver, "employee_user_id_id", None) == request.user.id),
            None,
        )
        current_step = next(
            (a for a in rec.approvals.all() if a.status == "pending"),
            None,
        )
        days_open = (now.date() - rec.created_at.date()).days if rec.created_at else 0
        if days_open >= 3:
            priority, priority_class = "High", "pri-high"
        elif days_open >= 1:
            priority, priority_class = "Medium", "pri-medium"
        else:
            priority, priority_class = "Low", "pri-low"
        rows.append({
            "id": rec.id,
            "title": rec.title or (rec.job_position_id.job_position if rec.job_position_id else "Recruitment"),
            "type_label": "Job Requisition",
            "type_class": "type-job-req",
            "requested_by": str(rec.raised_by) if rec.raised_by else "—",
            "requested_initials": (str(rec.raised_by)[:2].upper() if rec.raised_by else "U"),
            "current_stage": str(current_step.approver) if current_step else "—",
            "submitted_at": rec.created_at,
            "priority": priority,
            "priority_class": priority_class,
            "days_open": days_open,
            "approval_id": my_step.id if my_step else None,
        })

    kpi_pending = pending.count()
    kpi_urgent = sum(1 for r in rows if r["priority"] == "High")
    kpi_approved_month = (
        _RecruitmentApproval.objects.filter(
            status="approved",
            approved_at__gte=month_start,
            approver__employee_user_id=request.user,
        ).count()
    )
    kpi_rejected_month = (
        _RecruitmentApproval.objects.filter(
            status="rejected",
            approved_at__gte=month_start,
            approver__employee_user_id=request.user,
        ).count()
    )
    from django.db.models import Avg, DurationField, ExpressionWrapper, F as _F
    avg_dur = (
        _RecruitmentApproval.objects
        .filter(status="approved", approved_at__isnull=False, recruitment__created_at__isnull=False)
        .annotate(
            tat=ExpressionWrapper(
                _F("approved_at") - _F("recruitment__created_at"),
                output_field=DurationField(),
            )
        )
        .aggregate(avg=Avg("tat"))
    )["avg"]
    avg_tat = round(avg_dur.days, 1) if avg_dur else 0

    # ── Acted: recruitments where the current user already approved/rejected/queried ──
    acted_qs = (
        _Recruitment.objects.filter(
            raised_from_employee=True,
            approvals__approver__employee_user_id=request.user,
            approvals__status__in=["approved", "rejected", "queried"],
        )
        .select_related("raised_by")
        .prefetch_related("approvals__approver")
        .annotate(last_action_at=Max("approvals__approved_at"))
        .order_by(F("last_action_at").desc(nulls_last=True), "-created_at")
        .distinct()
    )
    acted_rows = []
    for rec in acted_qs:
        my_action = next(
            (a for a in rec.approvals.all()
             if getattr(a.approver, "employee_user_id_id", None) == request.user.id
             and a.status in ("approved", "rejected", "queried")),
            None,
        )
        acted_rows.append({
            "id": rec.id,
            "title": rec.title or (rec.job_position_id.job_position if rec.job_position_id else "Recruitment"),
            "requested_by": str(rec.raised_by) if rec.raised_by else "—",
            "requested_initials": (str(rec.raised_by)[:2].upper() if rec.raised_by else "U"),
            "my_action_status": my_action.status if my_action else "",
            "my_action_at": my_action.approved_at if my_action else None,
            "my_action_reason": (my_action.comments or "") if my_action else "",
            "overall_status": rec.approval_status,
        })

    # ── HR: Ready to Publish (approved recruitments) ──
    current_employee = getattr(request.user, "employee_get", None)
    is_hr = bool(request.user.is_superuser)
    if not is_hr and current_employee is not None:
        try:
            from base.models import HRUser
            is_hr = HRUser.objects.filter(employee=current_employee, is_hr_staff=True).exists()
        except Exception:
            is_hr = False

    ready_rows = []
    if is_hr:
        ready_qs = (
            _Recruitment.objects.filter(
                raised_from_employee=True,
                approval_status="approved",
            )
            .select_related("raised_by")
            .annotate(last_action_at=Max("approvals__approved_at"))
            .order_by(F("last_action_at").desc(nulls_last=True), "-created_at")
        )
        for rec in ready_qs:
            ready_rows.append({
                "id": rec.id,
                "title": rec.title or (rec.job_position_id.job_position if rec.job_position_id else "Recruitment"),
                "requested_by": str(rec.raised_by) if rec.raised_by else "—",
                "requested_initials": (str(rec.raised_by)[:2].upper() if rec.raised_by else "U"),
                "approved_at": rec.last_action_at or rec.created_at,
                "is_published": rec.is_published,
                "hr_feedback": rec.hr_feedback or "",
            })

    active_tab = request.GET.get("tab", "pending")
    if active_tab not in ("pending", "acted", "ready"):
        active_tab = "pending"
    if active_tab == "ready" and not is_hr:
        active_tab = "pending"

    return render(request, "ui/approvals.html", {
        "rows": rows,
        "acted_rows": acted_rows,
        "ready_rows": ready_rows,
        "is_hr": is_hr,
        "active_tab": active_tab,
        "kpi_pending": kpi_pending,
        "kpi_urgent": kpi_urgent,
        "kpi_approved_month": kpi_approved_month,
        "kpi_rejected_month": kpi_rejected_month,
        "kpi_avg_tat": avg_tat,
    })


def _ui_get_reporting_chain(employee):
    chain, visited, current = [], set(), employee
    while current:
        mgr = current.get_reporting_manager()
        if not mgr or mgr.id in visited:
            break
        chain.append(mgr)
        visited.add(mgr.id)
        current = mgr
    return chain


def _ui_custom_recruitment_approvers(raised_by):
    if not raised_by:
        return []
    from recruitment.approvals.engine import (
        CUSTOM_REQUESTER_FLOWS,
        _resolve_employee_by_email,
        _resolve_shared_hr,
    )
    user = getattr(raised_by, "employee_user_id", None)
    email = (getattr(user, "email", "") or raised_by.email or "").lower()
    if email not in CUSTOM_REQUESTER_FLOWS:
        return []
    chain, seen = [], set()
    others = {e for e in CUSTOM_REQUESTER_FLOWS[email] if e != "__HR__"}
    others.update({"cfo@fits.com", "ceo@fits.com"})
    for entry in CUSTOM_REQUESTER_FLOWS[email]:
        if entry == email:
            continue
        emp = _resolve_shared_hr(exclude_emails=others) if entry == "__HR__" else _resolve_employee_by_email(entry)
        if emp and emp.id not in seen:
            seen.add(emp.id)
            chain.append(emp)
    return chain


def _ui_create_approval_chain(recruitment_obj, manager_ids=None):
    from employee.models import Employee
    from recruitment.models import RecruitmentApproval
    raised_by = recruitment_obj.raised_by
    approvers = []
    custom = _ui_custom_recruitment_approvers(raised_by)
    if custom:
        approvers = [m for m in custom if m != raised_by]
    elif manager_ids:
        ids = [int(i) for i in manager_ids if str(i).strip().isdigit()]
        mgrs = list(Employee.objects.filter(id__in=ids))
        mgrs.sort(key=lambda e: ids.index(e.id))
        approvers = [m for m in mgrs if m != raised_by]
    elif raised_by:
        approvers = [m for m in _ui_get_reporting_chain(raised_by) if m != raised_by]
    for seq, approver in enumerate(approvers, start=1):
        RecruitmentApproval.objects.create(
            recruitment=recruitment_obj, approver=approver, sequence=seq,
        )
    return approvers


@login_required(login_url="/ui/login/")
def manpower_request(request):
    """
    Raise Recruitment form (new UI). Creates a Recruitment with
    raised_from_employee=True and builds the approval chain.
    """
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.utils import timezone

    from base.models import Department, JobPosition
    from recruitment.models import Recruitment as _Recruitment

    if request.method == "POST":
        employee = getattr(request.user, "employee_get", None)
        if not employee:
            messages.error(request, "You need an employee record to raise a recruitment.")
            return redirect("ui:manpower-request")

        title           = (request.POST.get("title") or "").strip()
        department_id   = request.POST.get("department") or None
        job_position_id = request.POST.get("job_position") or None
        vacancy         = request.POST.get("vacancy") or 1
        start_date      = request.POST.get("start_date") or timezone.localdate()
        employment_type = request.POST.get("employment_type", "full_time")
        work_location   = (request.POST.get("work_location") or "").strip()
        experience      = (request.POST.get("experience") or "").strip()
        priority        = (request.POST.get("priority") or "medium").strip()
        grade           = (request.POST.get("grade") or "").strip().upper()
        skills          = (request.POST.get("skills") or "").strip()
        budget          = (request.POST.get("budget") or "").strip()
        budget_period   = request.POST.get("budget_period", "monthly")
        justification   = request.POST.get("justification", "")
        description     = request.POST.get("job_description", "") or request.POST.get("description", "")
        request_type    = request.POST.get("request_type", "new_hiring")

        import re as _re
        budget_raw = _re.sub(r"[^\d.]", "", budget) if budget else ""
        try:
            from decimal import Decimal
            budget_val = Decimal(budget_raw) if budget_raw else None
        except Exception:
            budget_val = None

        rec = _Recruitment(
            title=title or "Untitled Recruitment",
            vacancy=int(vacancy or 1),
            start_date=start_date,
            justification=justification,
            description=description,
            raised_from_employee=True,
            raised_by=employee,
            approval_status="pending",
            is_published=False,
            company_id=employee.get_company(),
            employment_type=employment_type if employment_type in ("full_time", "contract") else "full_time",
            budget=budget_val,
            location=work_location or "",
            grade=grade,
            band=request.POST.get("work_mode", ""),
        )
        if job_position_id:
            rec.job_position_id_id = job_position_id
        if department_id:
            try:
                rec.department_id = int(department_id)
            except (TypeError, ValueError):
                pass
        rec.save()

        approvers = _ui_create_approval_chain(rec)
        if not approvers:
            rec.approval_status = "approved"
            rec.save()
            messages.success(request, "Recruitment created and auto-approved.")
        else:
            messages.success(request, f"Recruitment raised — sent to {approvers[0]} for approval.")

        request.session.pop("ui_jd_prefill", None)
        return redirect("ui:job-requisition")

    from recruitment.models import GRADE_CHOICES

    prefill = request.session.get("ui_jd_prefill", None) or {}
    return render(request, "ui/manpower_request.html", {
        "departments":           Department.objects.all(),
        "job_positions":         JobPosition.objects.all(),
        "grade_choices":         GRADE_CHOICES,
        "prefill_title":         prefill.get("title", ""),
        "prefill_description":   prefill.get("description", ""),
        "prefill_justification": prefill.get("justification", ""),
    })


@login_required(login_url="/ui/login/")
def bulk_request(request):
    """
    Bulk Raise Recruitment (new UI). Several positions (e.g. 20 Electricians,
    20 Plumbers) are grouped under ONE umbrella Recruitment with a single
    approval chain. On full approval the umbrella fans out into one published
    campaign per line (see ``fanout_bulk_recruitment``); candidates then apply
    per role from the careers page and proposals/offers proceed per-candidate.

    Posted as parallel arrays: ``line_title[]`` + ``line_vacancy[]``
    (optionally ``line_position[]`` = JobPosition id). Lines can be added
    manually or pre-filled from a CSV in the modal popup.
    """
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.utils import timezone

    from recruitment.models import BulkRequestLine
    from recruitment.models import Recruitment as _Recruitment
    from recruitment.views.views import fanout_bulk_recruitment

    if request.method != "POST":
        return redirect("ui:manpower-request")

    employee = getattr(request.user, "employee_get", None)
    if not employee:
        messages.error(request, "You need an employee record to raise a recruitment.")
        return redirect("ui:manpower-request")

    titles    = request.POST.getlist("line_title[]")
    vacancies = request.POST.getlist("line_vacancy[]")
    positions = request.POST.getlist("line_position[]")

    lines = []
    for idx, title in enumerate(titles):
        title = (title or "").strip()
        if not title:
            continue
        try:
            qty = int((vacancies[idx] if idx < len(vacancies) else "1") or "1")
        except (TypeError, ValueError):
            qty = 1
        qty = max(1, qty)
        pos_id = positions[idx].strip() if idx < len(positions) and positions[idx].strip().isdigit() else None
        lines.append({"title": title, "vacancy": qty, "position_id": pos_id})

    if not lines:
        messages.error(request, "Add at least one position line to raise a bulk request.")
        return redirect("ui:manpower-request")

    justification = request.POST.get("justification", "")
    start_date    = request.POST.get("start_date") or timezone.localdate()
    employment_type = request.POST.get("employment_type", "full_time")
    if employment_type not in ("full_time", "contract"):
        employment_type = "full_time"

    summary = ", ".join(f"{ln['vacancy']} {ln['title']}" for ln in lines)
    total_vacancy = sum(ln["vacancy"] for ln in lines)

    parent = _Recruitment(
        title=(f"Bulk: {summary}")[:50],
        vacancy=total_vacancy,
        start_date=start_date,
        justification=justification,
        description=request.POST.get("description", ""),
        raised_from_employee=True,
        raised_by=employee,
        approval_status="pending",
        is_published=False,
        is_bulk=True,
        company_id=employee.get_company(),
        employment_type=employment_type,
        location=(request.POST.get("work_location") or "").strip(),
    )
    parent.save()

    for ln in lines:
        bl = BulkRequestLine(recruitment=parent, title=ln["title"], vacancy=ln["vacancy"])
        if ln["position_id"]:
            bl.job_position_id_id = int(ln["position_id"])
        bl.save()

    approvers = _ui_create_approval_chain(parent)
    if not approvers:
        parent.approval_status = "approved"
        parent.save()
        fanout_bulk_recruitment(parent)
        messages.success(
            request,
            f"Bulk request created and auto-approved — {len(lines)} positions published.",
        )
    else:
        messages.success(
            request,
            f"Bulk request raised ({len(lines)} positions, {total_vacancy} vacancies) "
            f"— sent to {approvers[0]} for a single approval.",
        )

    return redirect("ui:job-requisition")


@login_required(login_url="/ui/login/")
def manpower_approval(request, rec_id=None):
    """Detail view for a single recruitment approval — Approve/Reject posts go
    to the legacy `approve-employee-recruitment` / `reject-employee-recruitment`
    URLs so behaviour matches the legacy received-recruitments inbox exactly."""
    from django.shortcuts import redirect, get_object_or_404
    from recruitment.models import Recruitment as _Recruitment

    if rec_id is None:
        return redirect("ui:approvals")

    rec = get_object_or_404(
        _Recruitment.objects.select_related("raised_by", "job_position_id")
        .prefetch_related("approvals__approver"),
        pk=rec_id,
    )

    # If this recruitment was raised via an Employment Proposal, show the proposal detail instead
    linked_proposal = rec.proposals.order_by("id").first()
    if linked_proposal:
        return redirect("ui:proposal-detail", proposal_id=linked_proposal.id)

    from django.utils import timezone as _tz
    _SLA_HOURS = 48
    chain = []
    my_pending_id = None
    first_pending_seen = False
    prev_acted_at = getattr(rec, "created_at", None)
    for a in rec.approvals.all().order_by("sequence"):
        is_active_pending = a.status == "pending" and not first_pending_seen
        if a.status == "pending":
            first_pending_seen = True
        if (
            is_active_pending
            and getattr(a.approver, "employee_user_id_id", None) == request.user.id
            and my_pending_id is None
        ):
            my_pending_id = a.id
        approver_role = ""
        try:
            wi = getattr(a.approver, "employee_work_info", None)
            if wi and wi.job_position_id:
                approver_role = wi.job_position_id.job_position
        except Exception:
            pass
        requested_at = prev_acted_at
        display_status = (
            "active" if is_active_pending
            else "waiting" if a.status == "pending"
            else a.status
        )
        # SLA status
        if display_status == "approved":
            if requested_at and a.approved_at:
                _elapsed = (a.approved_at - requested_at).total_seconds() / 3600
                sla_status = "late" if _elapsed > _SLA_HOURS else "ok"
            else:
                sla_status = "ok"
        elif display_status == "active":
            if requested_at:
                _elapsed = (_tz.now() - requested_at).total_seconds() / 3600
                if _elapsed < _SLA_HOURS * 0.5:
                    sla_status = "ok"
                elif _elapsed < _SLA_HOURS:
                    sla_status = "warning"
                else:
                    sla_status = "overdue"
            else:
                sla_status = "ok"
        elif display_status == "rejected":
            sla_status = "rejected"
        else:
            sla_status = "waiting"
        chain.append({
            "approver": a.approver,
            "approver_name": str(a.approver),
            "approver_role": approver_role or str(a.approver),
            "initials": str(a.approver)[:2].upper() if a.approver else "—",
            "sequence": a.sequence,
            "status": a.status,
            "display_status": display_status,
            "status_label": dict(a._meta.get_field("status").choices).get(a.status, a.status),
            "approved_at": a.approved_at,
            "requested_at": requested_at,
            "sla_status": sla_status,
            "created_at": getattr(a, "created_at", None),
            "comments": a.comments or "",
            "signature_image": getattr(a, "signature_image", ""),
            "approval_id": a.id,
            "is_my_active": is_active_pending and getattr(a.approver, "employee_user_id_id", None) == request.user.id,
        })
        if a.status == "approved" and a.approved_at:
            prev_acted_at = a.approved_at
    current_employee = getattr(request.user, "employee_get", None)
    is_hr = bool(request.user.is_superuser)
    if not is_hr and current_employee is not None:
        try:
            from base.models import HRUser
            is_hr = HRUser.objects.filter(employee=current_employee, is_hr_staff=True).exists()
        except Exception:
            is_hr = False

    bulk_lines = list(rec.bulk_lines.all()) if getattr(rec, "is_bulk", False) else []

    return render(request, "ui/manpower_approval.html", {
        "rec": rec,
        "chain": chain,
        "my_pending_id": my_pending_id,
        "is_hr": is_hr,
        "bulk_lines": bulk_lines,
    })


@login_required(login_url="/ui/login/")
def interview(request):
    """Interview list — shortlisted candidates + scheduled interviews."""
    from django.utils import timezone
    from django.core.paginator import Paginator
    from django.db.models import Exists, F, IntegerField, OuterRef, Q as _Q, Subquery
    from recruitment.models import (
        Candidate as _Candidate,
        InterviewSchedule as _InterviewSchedule,
        CandidateScreeningProfile as _Profile,
    )
    from recruitment.models_interview import InterviewRound as _InterviewRound
    from recruitment.models_proposal import EmploymentProposal as _Proposal, ProposalApproval as _PA

    today = timezone.localdate()

    # ── KPI stats (dynamic) ──────────────────────────────────────────────────
    total_iv   = _InterviewSchedule.objects.count()
    completed  = _InterviewSchedule.objects.filter(completed=True).count()
    upcoming   = _InterviewSchedule.objects.filter(interview_date__gte=today, completed=False).count()
    scheduled_count = _InterviewSchedule.objects.filter(completed=False).count()
    cancelled  = _Candidate.objects.filter(canceled=True, candidate_interview__isnull=False).distinct().count()

    stats = {
        "total":     total_iv,
        "scheduled": scheduled_count,
        "completed": completed,
        "upcoming":  upcoming,
        "cancelled": cancelled,
    }

    # ── Shortlisted candidates — annotate with interview status + id ─────────
    _has_interview = Exists(
        _InterviewSchedule.objects.filter(candidate_id=OuterRef("pk"))
    )
    _interview_id_sq = Subquery(
        _InterviewSchedule.objects.filter(candidate_id=OuterRef("pk")).values("id")[:1],
        output_field=IntegerField(),
    )
    shortlisted_qs = (
        _Candidate.objects.filter(
            is_active=True, canceled=False, hired=False,
            screening_profile__status="shortlisted",
        )
        .select_related("recruitment_id", "job_position_id", "screening_profile")
        .annotate(has_interview=_has_interview, interview_id=_interview_id_sq)
        .order_by("-id")
    )
    sh_paginator = Paginator(shortlisted_qs, 10)
    sh_page_num  = request.GET.get("sh_page", 1)
    sh_page      = sh_paginator.get_page(sh_page_num)

    # ── Scheduled interviews ─────────────────────────────────────────────────
    scheduled_qs = (
        _InterviewSchedule.objects.select_related(
            "candidate_id", "candidate_id__recruitment_id", "candidate_id__job_position_id",
        )
        .prefetch_related("employee_id")
        .order_by("-interview_date", "-interview_time")
    )
    sc_paginator = Paginator(scheduled_qs, 10)
    sc_page_num  = request.GET.get("sc_page", 1)
    sc_page      = sc_paginator.get_page(sc_page_num)

    # ── Proposals ────────────────────────────────────────────────────────────
    if request.user.is_superuser:
        proposals = _Proposal.objects.select_related("candidate").order_by("-id")[:25]
    else:
        next_pending_seq = _PA.objects.filter(
            proposal=OuterRef("pk"), status="pending"
        ).order_by("sequence").values("sequence")[:1]
        my_pending_seq = _PA.objects.filter(
            proposal=OuterRef("pk"), status="pending",
            approver__employee_user_id=request.user,
        ).order_by("sequence").values("sequence")[:1]
        proposals = (
            _Proposal.objects.select_related("candidate")
            .annotate(
                _next=Subquery(next_pending_seq, output_field=IntegerField()),
                _mine=Subquery(my_pending_seq, output_field=IntegerField()),
            )
            .filter(
                _Q(created_by=request.user)
                | _Q(_mine__isnull=False, _mine=F("_next"))
            )
            .distinct()
            .order_by("-id")[:25]
        )

    # ── Rounds-done set for "Promote" eligibility ────────────────────────────
    sc_ids = [iv.id for iv in sc_page]
    has_incomplete = set(
        _InterviewRound.objects.filter(
            interview_id__in=sc_ids, completed=False
        ).values_list("interview_id", flat=True)
    )
    has_any_round = set(
        _InterviewRound.objects.filter(
            interview_id__in=sc_ids
        ).values_list("interview_id", flat=True)
    )
    rounds_done_ids = has_any_round - has_incomplete

    sh_page_range = list(sh_paginator.get_elided_page_range(sh_page.number, on_each_side=2, on_ends=1))
    sc_page_range = list(sc_paginator.get_elided_page_range(sc_page.number, on_each_side=2, on_ends=1))

    return render(request, "ui/interview.html", {
        "stats":           stats,
        "sh_page":         sh_page,
        "sh_page_range":   sh_page_range,
        "sc_page":         sc_page,
        "sc_page_range":   sc_page_range,
        "today":           today,
        "proposals":       proposals,
        "rounds_done_ids": rounds_done_ids,
    })


@login_required(login_url="/ui/login/")
def interview_creator(request):
    """Schedule a new interview. Creates an InterviewSchedule and rounds."""
    from django.contrib import messages
    from django.shortcuts import redirect

    from employee.models import Employee
    from recruitment.models import Candidate as _Candidate, InterviewSchedule as _InterviewSchedule
    from recruitment.models_interview import InterviewRound as _InterviewRound

    if request.method == "POST":
        import json as _json
        cand_id = request.POST.get("candidate")
        meeting_link = request.POST.get("meeting_link", "")
        platform = request.POST.get("platform", "manual")
        panelists = request.POST.getlist("panelists")
        description = request.POST.get("description", "")
        round_labels = request.POST.getlist("round_label")
        round_dates = request.POST.getlist("round_date")
        round_times = request.POST.getlist("round_time")
        # Per-round multi-interviewers: submitted as JSON array of id arrays
        try:
            round_interviewers_json = _json.loads(request.POST.get("round_interviewers_json", "[]"))
        except Exception:
            round_interviewers_json = []

        rounds = [
            (
                l.strip(),
                round_dates[i] if i < len(round_dates) else "",
                round_times[i] if i < len(round_times) else "",
                round_interviewers_json[i] if i < len(round_interviewers_json) else [],
            )
            for i, l in enumerate(round_labels) if l.strip()
        ]

        if not cand_id or not rounds or not rounds[0][1]:
            messages.error(request, "Candidate and at least one round with a date are required.")
            return redirect("ui:interview-creator")

        interview_date = rounds[0][1]
        interview_time = rounds[0][2] or None

        iv = _InterviewSchedule.objects.create(
            candidate_id_id=cand_id,
            interview_date=interview_date,
            interview_time=interview_time,
            online_meeting_link=meeting_link,
            meeting_provider=platform if platform in ("manual", "teams", "zoom", "meet") else "manual",
            description=description,
            num_rounds=max(1, len(rounds)),
        )
        if panelists:
            iv.employee_id.set(Employee.objects.filter(id__in=[int(p) for p in panelists if str(p).isdigit()]))
        for idx, (label, r_date, r_time, r_interviewer_ids) in enumerate(rounds, start=1):
            valid_ids = [int(x) for x in r_interviewer_ids if str(x).isdigit()]
            lead = None
            if valid_ids:
                try:
                    lead = Employee.objects.get(id=valid_ids[0])
                except Employee.DoesNotExist:
                    pass
            rnd = _InterviewRound.objects.create(
                interview=iv, round_number=idx, label=label,
                round_date=r_date or None, round_time=r_time or None,
                interviewer=lead,
            )
            if valid_ids:
                rnd.interviewers.set(Employee.objects.filter(id__in=valid_ids))
        messages.success(request, "Interview scheduled.")
        return redirect("ui:interview")

    from django.db.models import Q as _Q
    shortlisted = (
        _Candidate.objects.filter(is_active=True, canceled=False, hired=False)
        .filter(_Q(screening_profile__status="shortlisted") | _Q(stage_id__isnull=False))
        .exclude(candidate_interview__isnull=False)
        .distinct()
        .select_related("recruitment_id__job_position_id", "job_position_id")
        .order_by("name")[:200]
    )

    # Enrich candidates with dept for template
    for c in shortlisted:
        jp = (c.recruitment_id.job_position_id if c.recruitment_id else None) or c.job_position_id
        dept_obj = getattr(jp, "department_id", None) if jp else None
        c.dept_display = str(dept_obj) if dept_obj else ""

    employees = Employee.objects.filter(is_active=True).order_by("employee_first_name")[:200]

    # Auto-preselect requester + their reporting manager chain (up to 3 levels)
    default_panelist_ids = []
    try:
        cur = request.user.employee_get
        if cur:
            chain, seen = [cur], {cur.id}
            mgr = getattr(getattr(cur, "employee_work_info", None), "reporting_manager_id", None)
            while mgr and mgr.id not in seen and len(chain) < 4:
                chain.append(mgr)
                seen.add(mgr.id)
                mgr = getattr(getattr(mgr, "employee_work_info", None), "reporting_manager_id", None)
            default_panelist_ids = [str(e.id) for e in chain]
    except Exception:
        pass

    import json as _json2
    return render(request, "ui/interview_creator.html", {
        "candidates": shortlisted,
        "employees": employees,
        "preselect_candidate_id": request.GET.get("candidate", ""),
        "default_panelist_ids_json": _json2.dumps(default_panelist_ids),
    })


@login_required(login_url="/ui/login/")
def offers(request):
    """Offer letter list.

    Visibility rules (mirrors job_requisition):
    - Superuser: all
    - Everyone else: offers they created + offers where their approval step
      is the first pending step
    """
    from django.core.paginator import Paginator
    from django.db.models import F, IntegerField, OuterRef, Q, Subquery
    from recruitment.models import OfferLetter as _OfferLetter, OfferLetterApproval as _OLA

    base = _OfferLetter.objects.select_related("candidate_id", "candidate_id__recruitment_id")

    if request.user.is_superuser:
        qs = base
    else:
        from employee.models import Employee as _Employee
        try:
            current_employee = _Employee.objects.get(employee_user_id=request.user)
        except _Employee.DoesNotExist:
            current_employee = None

        next_pending_seq = _OLA.objects.filter(
            offer_letter=OuterRef("pk"), status="pending"
        ).order_by("sequence").values("sequence")[:1]
        my_pending_seq = _OLA.objects.filter(
            offer_letter=OuterRef("pk"), status="pending",
            approver__employee_user_id=request.user,
        ).order_by("sequence").values("sequence")[:1]

        qs = (
            base
            .annotate(
                _next=Subquery(next_pending_seq, output_field=IntegerField()),
                _mine=Subquery(my_pending_seq, output_field=IntegerField()),
            )
            .filter(
                (Q(created_by=current_employee) if current_employee else Q(pk__in=[]))
                | Q(_mine__isnull=False, _mine=F("_next"))
            )
            .distinct()
        )

    qs = qs.order_by("-id")

    status = request.GET.get("status", "").strip()
    if status:
        qs = qs.filter(status=status)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(candidate_id__name__icontains=q) | Q(candidate_id__email__icontains=q))

    page = Paginator(qs, 25).get_page(request.GET.get("page"))
    all_offers = _OfferLetter.objects.all()
    kpi_total_offers = all_offers.count()
    kpi_accepted = all_offers.filter(status="accepted").count()
    kpi_in_progress = all_offers.filter(status__in=["sent", "pending_approval"]).count()
    kpi_completed = all_offers.filter(status="joined").count()
    kpi_delayed = all_offers.filter(status="sent", joining_date__isnull=False).count()
    return render(request, "ui/offers.html", {
        "page": page, "status": status, "q": q,
        "kpi_total_offers": kpi_total_offers,
        "kpi_accepted": kpi_accepted,
        "kpi_in_progress": kpi_in_progress,
        "kpi_completed": kpi_completed,
        "kpi_delayed": kpi_delayed,
    })


@login_required(login_url="/ui/login/")
def offer_creator(request):
    """Create a new OfferLetter, attach a template, build OfferLetterApproval chain,
    then redirect to the offer detail page for e-signing."""
    from datetime import date
    from django.contrib import messages
    from django.shortcuts import redirect
    from recruitment.models import (
        Candidate as _Candidate,
        OfferLetter as _OfferLetter,
        OfferLetterTemplate as _Template,
        OfferLetterApproval as _Approval,
    )

    if request.method == "POST":
        cand_id = request.POST.get("candidate")
        position = (request.POST.get("position") or "").strip()
        joining_date = request.POST.get("joining_date") or date.today()
        basic = request.POST.get("basic_salary") or 0
        gross = request.POST.get("gross_salary") or basic
        template_id = request.POST.get("template_id")
        expiry_date = request.POST.get("expiry_date") or None

        if not cand_id:
            messages.error(request, "Please select a candidate.")
            return redirect("ui:offer-creator")

        from recruitment.models_proposal import EmploymentProposal as _Proposal
        proposal = _Proposal.objects.filter(candidate_id=int(cand_id), status="approved").order_by("-id").first()
        if not proposal:
            messages.error(request, "An offer can only be created for candidates with an approved employment proposal.")
            return redirect("ui:offer-creator")

        # OneToOne constraint — if an offer already exists for this candidate, redirect to it
        existing = _OfferLetter.objects.filter(candidate_id_id=int(cand_id)).first()
        if existing:
            messages.info(request, "An offer letter already exists for this candidate.")
            return redirect("ui:offer-detail", offer_id=existing.id)

        # Pull fields from proposal — form values override if explicitly provided
        _position    = position or proposal.post_applied_for or ""
        _department  = proposal.division_department or ""
        _location    = proposal.post_location or ""
        _basic       = float(basic) if basic else (float(proposal.basic_salary) if proposal.basic_salary else 0)
        _gross       = float(gross) if gross else (float(proposal.gross_salary) if proposal.gross_salary else _basic)
        _role_type   = "contract" if proposal.contractual else "full_time"

        offer = _OfferLetter.objects.create(
            candidate_id_id=int(cand_id),
            position=_position,
            department=_department,
            location=_location,
            joining_date=joining_date,
            basic_salary=_basic or 0,
            gross_salary=_gross or 0,
            role_type=_role_type,
            status="draft",
        )

        # Attach template and generate letter body
        if template_id:
            try:
                tpl = _Template.objects.get(id=template_id)
                offer.letter_template = tpl.body_html
                offer.generate_offer_letter()
                offer.save(update_fields=["letter_template", "generated_letter"])
            except _Template.DoesNotExist:
                pass

        # Build chain from form-submitted approver_ids[], falling back to auto
        chain_ids = [x for x in request.POST.getlist("chain_approver[]") if x.strip().isdigit()]
        if chain_ids:
            from employee.models import Employee as _Emp
            emp_map = {str(e.id): e for e in _Emp.objects.filter(id__in=[int(i) for i in chain_ids])}
            from recruitment.models import OfferLetterApproval as _Approval
            for seq, eid in enumerate(chain_ids, start=1):
                approver = emp_map.get(eid)
                if approver:
                    _Approval.objects.create(offer_letter=offer, approver=approver, sequence=seq)
        else:
            _build_offer_approval_chain(offer, request)

        messages.success(request, f"Offer #{offer.id} created. Please complete the e-sign flow.")
        return redirect("ui:offer-detail", offer_id=offer.id)

    from employee.models import Employee
    from base.models import Department
    from recruitment.models_proposal import EmploymentProposal as _Proposal, ProposalRoleAssignment as _PRA
    approved_candidate_ids = _Proposal.objects.filter(status="approved").values_list("candidate_id", flat=True)
    candidates = (
        _Candidate.objects.filter(is_active=True, canceled=False, hired=False, id__in=approved_candidate_ids)
        .order_by("name")[:200]
    )
    templates = _Template.objects.filter(is_active=True).exclude(name__icontains="proposal").order_by("name")
    employees = Employee.objects.filter(is_active=True).order_by("employee_first_name")[:200]
    departments = Department.objects.filter(is_active=True).order_by("department")

    # Fetch role-assigned employees for the 3 fixed chain steps
    _role_map = {
        r.role_key: {"id": r.employee.id, "name": str(r.employee)}
        for r in _PRA.objects.select_related("employee").filter(
            role_key__in=["head_of_department", "gm_hra", "ceo"]
        )
    }
    chain_roles = {
        "hiring_manager": _role_map.get("head_of_department"),
        "hr_manager":     _role_map.get("gm_hra"),
        "ceo":            _role_map.get("ceo"),
    }

    return render(request, "ui/offer_creator.html", {
        "candidates": candidates,
        "templates": templates,
        "employees": employees,
        "departments": departments,
        "chain_roles": chain_roles,
        "preselect_candidate_id": request.GET.get("candidate", ""),
    })


def api_proposal_autofill(request, candidate_id):
    """Return approved proposal fields as JSON for the offer creator auto-fill."""
    from recruitment.models_proposal import EmploymentProposal as _Proposal
    proposal = (
        _Proposal.objects.filter(candidate_id=candidate_id, status="approved")
        .order_by("-id")
        .first()
    )
    if not proposal:
        return JsonResponse({"found": False})

    def _dec(v):
        return float(v) if v is not None else None

    return JsonResponse({
        "found": True,
        "position":       proposal.post_applied_for or "",
        "department":     proposal.division_department or "",
        "work_location":  proposal.post_location or "",
        "basic_salary":   _dec(proposal.basic_salary),
        "gross_salary":   _dec(proposal.gross_salary),
        "allowance":      _dec(proposal.hra_allowance),
        "contract_months": proposal.employment_contract_months,
        "joining_date":   proposal.contract_period_from.isoformat() if proposal.contract_period_from else "",
        "proposal_no":    proposal.proposal_no,
        "nationality":    proposal.nationality or "",
        "grade_group":    proposal.grade_group or "",
    })


def _build_offer_approval_chain(offer, request):
    """Create OfferLetterApproval records for the offer: creator → manager → superusers."""
    from django.contrib.auth.models import User
    from recruitment.models import OfferLetterApproval as _Approval

    seen = set()
    steps = []

    def _add(emp):
        if emp and emp.id not in seen:
            seen.add(emp.id)
            steps.append(emp)

    # Creator
    try:
        _add(request.user.employee_get)
    except Exception:
        pass

    # Recruitment requester + their manager
    candidate = offer.candidate_id
    recruitment = getattr(candidate, "recruitment_id", None)
    raiser = getattr(recruitment, "raised_by", None) if recruitment else None
    if raiser:
        _add(raiser)
        try:
            mgr = raiser.get_reporting_manager()
            if mgr:
                _add(mgr)
        except Exception:
            pass

    # Superusers
    for su in User.objects.filter(is_superuser=True, is_active=True).order_by("pk"):
        _add(getattr(su, "employee_get", None))

    for seq, approver in enumerate(steps, start=1):
        _Approval.objects.create(offer_letter=offer, approver=approver, sequence=seq)


@login_required(login_url="/ui/login/")
def profile(request):
    employee = None
    try:
        from employee.models import Employee
        employee = Employee.objects.filter(employee_user_id=request.user).first()
    except Exception:
        employee = None
    return render(request, "ui/profile.html", {"employee": employee})


def _ui_notification_redirect(raw):
    """Map a notification's stored (legacy) redirect URL onto its new-UI
    equivalent so clicking a notification keeps the user inside /ui/.
    Legacy creation sites are left untouched (the legacy notifications page
    still uses the original URLs); the remap lives only in the new UI."""
    url = (raw or "").strip()
    if not url:
        return ""
    # Already a new-UI link — leave as-is.
    if url.startswith("/ui/"):
        return url
    low = url.lower()
    if "letter" in low or "offer" in low:
        return "/ui/offers/"
    if "interview" in low:
        return "/ui/interview/"
    if "manpower" in low or "received-recruitment" in low or "recruitment-view" in low or "approval" in low:
        return "/ui/manpower-approval/"
    if "pipeline" in low or "candidate" in low:
        return "/ui/candidates/"
    # Any other legacy recruitment/onboarding link → new-UI dashboard.
    if low.startswith("/recruitment/") or low.startswith("/onboarding/"):
        return "/ui/dashboard/"
    return url


@login_required(login_url="/ui/login/")
def notifications(request):
    items = []
    try:
        from notifications.models import Notification
        items = list(
            Notification.objects.filter(recipient=request.user)
            .order_by("-timestamp")[:50]
        )
        for n in items:
            data = getattr(n, "data", None) or {}
            n.ui_redirect = _ui_notification_redirect(data.get("redirect", ""))
    except Exception:
        items = []
    return render(request, "ui/notifications.html", {"items": items})


@login_required(login_url="/ui/login/")
def settings_page(request):
    return render(request, "ui/settings.html")


@login_required(login_url="/ui/login/")
def integrations(request):
    import os

    # ── Gmail (real Google OAuth via base.integrations.gmail) ────────────────
    gmail_configured = bool(os.environ.get("GMAIL_CLIENT_ID") and os.environ.get("GMAIL_CLIENT_SECRET"))
    gmail_connected = False
    try:
        from base.models_integrations import MailboxIntegration
        gmail_connected = MailboxIntegration.objects.filter(provider="gmail", is_active=True).exists()
    except Exception:
        gmail_connected = False

    items = [
        {"key": "gmail", "name": "Gmail",
         "desc": "Send recruitment emails through the global admin Gmail.",
         "icon": "mail",
         "url": ("/integrations/" if gmail_connected else "/integrations/gmail/connect/"),
         "connected": gmail_connected, "enabled": gmail_configured},
    ]

    # ── DocuSign + Adobe Acrobat Sign (real OAuth + embedded signing) ────────
    def _provider_state(helper_mod, account_model_name):
        configured = connected = False
        try:
            import importlib
            helper = importlib.import_module(helper_mod)
            configured = bool(helper.is_configured())
        except Exception:
            configured = False
        try:
            from base import models_integrations as _mi
            model = getattr(_mi, account_model_name, None)
            if model is not None:
                # E-sign connections are per-user: each signer links their own.
                connected = model.objects.filter(is_active=True, user=request.user).exists()
        except Exception:
            connected = False
        return configured, connected

    docusign_configured, docusign_connected = _provider_state("base.integrations.docusign", "DocusignAccount")
    adobesign_configured, adobesign_connected = _provider_state("base.integrations.adobesign", "AdobeSignAccount")

    return render(request, "ui/integrations.html", {
        "items": items,
        "docusign_configured": docusign_configured,
        "docusign_connected": docusign_connected,
        "adobesign_configured": adobesign_configured,
        "adobesign_connected": adobesign_connected,
    })


def login_view(request):
    """
    Self-contained login for the new UI. Independent of base.views.login_user
    so the legacy login can be removed cleanly once the new UI is finished.
    """
    from django.contrib import messages
    from django.contrib.auth import authenticate, login as auth_login
    from django.contrib.auth.models import User
    from django.shortcuts import redirect
    from django.utils.http import url_has_allowed_host_and_scheme
    from django.utils.translation import gettext as _

    if request.user.is_authenticated:
        return redirect("/ui/dashboard/")

    if request.method == "POST":
        username = request.POST.get("username", "").strip().lower()
        password = request.POST.get("password", "")
        next_url = request.GET.get("next") or request.POST.get("next") or "/ui/dashboard/"

        user = authenticate(request, username=username, password=password)

        if not user:
            blocked = User.objects.filter(username=username, is_active=False).exists()
            if blocked:
                messages.warning(request, _("Access Denied: Your account is blocked."))
            else:
                messages.error(request, _("Invalid username or password."))
            return redirect("ui:login")

        employee = getattr(user, "employee_get", None)
        is_admin_staff = bool(user.is_staff or user.is_superuser)

        if employee is None and not is_admin_staff:
            messages.error(
                request,
                _("An employee related to this user's credentials does not exist."),
            )
            return redirect("ui:login")
        if employee is not None and (not employee.is_active) and not is_admin_staff:
            messages.warning(
                request,
                _("This user is archived. Please contact the manager for more information."),
            )
            return redirect("ui:login")

        auth_login(request, user)

        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            next_url = "/ui/dashboard/"
        return redirect(next_url)

    return render(request, "ui/login.html", {"next": request.GET.get("next", "")})


@login_required(login_url="/ui/login/")
def candidate_create(request):
    """
    Add Candidate (new UI). Self-contained — mirrors the active part of
    recruitment.views.cv_upload.cv_upload_single: creates a Candidate row with
    name/email/mobile/resume/recruitment/stage, defaulting the stage to the
    'initial' stage of the chosen recruitment.
    """
    from django.contrib import messages
    from django.shortcuts import redirect
    from recruitment.models import Candidate as _Candidate, Recruitment as _Recruitment, Stage as _Stage

    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        mobile = (request.POST.get("mobile") or "").strip()
        rec_id = request.POST.get("recruitment") or None
        stage_id = request.POST.get("stage") or None
        source = request.POST.get("source") or "application"
        resume = request.FILES.get("resume")

        if not name or not email:
            messages.error(request, "Name and email are required.")
            return redirect("ui:candidate-create")

        recruitment = _Recruitment.objects.filter(id=rec_id).first() if rec_id else None
        stage = _Stage.objects.filter(id=stage_id).first() if stage_id else None
        if stage is None and recruitment is not None:
            stage = _Stage.objects.filter(recruitment_id=recruitment, stage_type="initial").first()
        if stage is None:
            stage = _Stage.objects.filter(stage_type="initial").first()

        try:
            candidate = _Candidate.objects.create(
                name=name,
                email=email,
                mobile=mobile,
                resume=resume,
                recruitment_id=recruitment,
                stage_id=stage,
                source=source,
            )
            # Run AI CV screening (Groq → OpenRouter → regex fallback) in background.
            if candidate.resume:
                from recruitment.cv_screening_ai import trigger_screening_async
                trigger_screening_async(candidate.id)
            messages.success(request, f"Candidate '{name}' added.")
            return redirect("ui:candidates")
        except Exception as exc:
            messages.error(request, f"Failed to add candidate: {exc}")
            return redirect("ui:candidate-create")

    recruitments = _Recruitment.objects.filter(closed=False, is_active=True).order_by("-id")
    stages = _Stage.objects.all().order_by("sequence")
    return render(request, "ui/candidate_create.html", {
        "recruitments": recruitments,
        "stages": stages,
        "preselect_recruitment_id": request.GET.get("recruitment", ""),
    })


@login_required(login_url="/ui/login/")
def jd_generate(request):
    """AI Job Description generator. Calls Groq via the existing client in
    recruitment.ai and returns JSON {role_summary, responsibilities[], requirements[], qualifications[]}.
    Used by /ui/jd-creator/ via fetch()."""
    import json
    from django.http import JsonResponse
    from django.views.decorators.http import require_POST
    from django.views.decorators.csrf import csrf_protect

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        payload = request.POST.dict()

    title       = (payload.get("title") or "").strip() or "Software Engineer"
    department  = (payload.get("department") or "").strip()
    experience  = (payload.get("experience") or "").strip()
    employment  = (payload.get("employment_type") or "").strip()
    education   = (payload.get("education") or "").strip()
    field       = (payload.get("field") or "").strip()
    location    = (payload.get("location") or "").strip()
    work_mode   = (payload.get("work_mode") or "").strip()
    languages   = (payload.get("languages") or "").strip()
    nationality = (payload.get("nationality") or "").strip()
    skills      = (payload.get("skills") or "").strip()
    other       = (payload.get("other") or "").strip()

    prompt = f"""You are a senior HR professional writing a clear, professional job description.

Inputs:
- Job Title: {title}
- Department: {department}
- Experience: {experience}
- Employment Type: {employment}
- Education: {education}
- Field of Study: {field}
- Location: {location}
- Work Mode: {work_mode}
- Languages: {languages}
- Nationality Preference: {nationality}
- Key Skills: {skills}
- Other Requirements: {other}

Produce a comprehensive job description. Return ONLY valid JSON in this exact shape:
{{
  "job_title": "<string>",
  "role_summary": "<2-3 sentence overview>",
  "responsibilities": ["<bullet>", "<bullet>", "<bullet>", "<bullet>", "<bullet>"],
  "requirements": ["<bullet>", "<bullet>", "<bullet>", "<bullet>"],
  "preferred_qualifications": ["<bullet>", "<bullet>", "<bullet>"]
}}

Each bullet should be a single concise sentence (no leading dash, no quotes).
"""

    try:
        from recruitment.ai import client as _groq_client
        res = _groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        raw = res.choices[0].message.content or "{}"
        data = json.loads(raw)
        return JsonResponse({"ok": True, "jd": data})
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)


@login_required(login_url="/ui/login/")
def recruitment_feedback(request, rec_id):
    """HR sends feedback on a recruitment. Mirrors the legacy
    `send-hr-feedback` endpoint but redirects back to the new UI track page."""
    from django.contrib import messages
    from django.shortcuts import redirect, get_object_or_404
    from recruitment.models import Recruitment as _Recruitment

    if request.method != "POST":
        return redirect("ui:manpower-approval-detail", rec_id=rec_id)
    rec = get_object_or_404(_Recruitment, pk=rec_id)
    rec.hr_feedback = request.POST.get("hr_feedback", "").strip()
    rec.save(update_fields=["hr_feedback"])
    messages.success(request, "HR feedback saved.")
    return redirect("ui:manpower-approval-detail", rec_id=rec_id)


@login_required(login_url="/ui/login/")
def recruitment_publish(request, rec_id, channel):
    """Publish a recruitment to a channel. Returns JSON in the same shape as
    the legacy publish endpoints so the existing JS handler works. Uses the new
    UI's standard auth (no hard employee-link requirement that breaks
    superuser-only HR accounts)."""
    import uuid
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    from django.utils.text import slugify
    from recruitment.models import Recruitment as _Recruitment

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"}, status=400)
    rec = get_object_or_404(_Recruitment, pk=rec_id)
    if rec.approval_status != "approved":
        return JsonResponse({"success": False, "error": "Not yet approved"}, status=400)

    channel = (channel or "").lower()

    if channel == "careers":
        # Use queryset.update() to bypass Recruitment.save()'s override that
        # forces is_published from posting_type. We need both is_published AND
        # is_public=True for the careers detail page (/recruitment/careers/<slug>/)
        # to find the job.
        if not rec.public_slug:
            base = slugify(rec.title or f"req-{rec.id}")[:100] or f"req-{rec.id}"
            slug = f"{base}-{rec.id}"
        else:
            slug = rec.public_slug
        _Recruitment.objects.filter(pk=rec.id).update(
            is_published=True,
            is_public=True,
            public_slug=slug,
        )
        return JsonResponse({"success": True, "public_slug": slug})

    if channel in ("linkedin", "bayt", "naukrigulf"):
        post_content = ""
        try:
            from recruitment.views.views import _generate_assisted_post
            post_content = _generate_assisted_post(rec, channel)
        except Exception:
            jd_excerpt = (rec.description or "")[:300]
            post_content = f"🚀 We're hiring: {rec.title}\n\n{jd_excerpt}\n\nApply now."
        external_id_prefix = {"linkedin": "LI", "bayt": "BAYT", "naukrigulf": "NG"}[channel]
        external_id = f"{external_id_prefix}-{uuid.uuid4().hex[:8].upper()}"
        portal_url = {
            "linkedin":   "https://www.linkedin.com/company/me/admin/dashboard/",
            "bayt":       "https://www.bayt.com/en/employer/",
            "naukrigulf": "https://www.naukrigulf.com/recruiter/",
        }[channel]
        if channel == "linkedin":
            rec.published_to_linkedin = True
            if hasattr(rec, "linkedin_posted_at"):
                rec.linkedin_posted_at = timezone.now()
            if hasattr(rec, "linkedin_external_id"):
                rec.linkedin_external_id = external_id
            rec.save()
        elif channel == "bayt":
            rec.published_to_bayt = True
            if hasattr(rec, "bayt_posted_at"):
                rec.bayt_posted_at = timezone.now()
            if hasattr(rec, "bayt_external_id"):
                rec.bayt_external_id = external_id
            rec.save()
        else:
            rec.published_to_naukrigulf = True
            if hasattr(rec, "naukrigulf_posted_at"):
                rec.naukrigulf_posted_at = timezone.now()
            if hasattr(rec, "naukrigulf_external_id"):
                rec.naukrigulf_external_id = external_id
            rec.save()
        return JsonResponse({
            "success": True,
            "post_content": post_content,
            "portal_url": portal_url,
            "external_id": external_id,
        })

    return JsonResponse({"success": False, "error": f"Unknown channel: {channel}"}, status=400)


def _screening_profile(candidate):
    """Return the candidate's CandidateScreeningProfile or None (reverse
    OneToOne raises DoesNotExist, which getattr does not swallow)."""
    try:
        return candidate.screening_profile
    except Exception:
        return None


@login_required(login_url="/ui/login/")
def candidate_screen(request, cand_id):
    """(Re-)run AI CV screening. POST returns JSON when called via fetch,
    redirect otherwise (legacy fallback)."""
    import json as _json
    from django.http import JsonResponse
    from django.shortcuts import redirect, get_object_or_404
    from recruitment.models import Candidate as _Candidate

    candidate = get_object_or_404(_Candidate, id=cand_id)
    is_fetch = request.headers.get("X-Requested-With") == "fetch"

    if request.method == "POST":
        if not candidate.resume:
            if is_fetch:
                return JsonResponse({"ok": False, "error": "No resume to screen."})
            from django.contrib import messages
            messages.error(request, "Candidate has no resume to screen.")
        else:
            # Reset profile to "pending" so the poller knows screening is in progress
            try:
                from recruitment.models import CandidateScreeningProfile as _CSP
                prof, _ = _CSP.objects.get_or_create(candidate=candidate)
                prof.status = "pending"
                prof.save(update_fields=["status"])
            except Exception:
                pass
            from recruitment.cv_screening_ai import trigger_screening_async
            trigger_screening_async(candidate.id)
            if is_fetch:
                return JsonResponse({"ok": True, "started": True})

    if is_fetch:
        return JsonResponse({"ok": False, "error": "POST required."})
    return redirect(request.META.get("HTTP_REFERER") or "ui:candidates")


@login_required(login_url="/ui/login/")
def candidate_screen_status(request, cand_id):
    """Poll endpoint — returns current screening status + score as JSON."""
    import json as _json
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from recruitment.models import Candidate as _Candidate

    candidate = get_object_or_404(_Candidate, id=cand_id)
    try:
        prof = candidate.screening_profile
    except Exception:
        return JsonResponse({"status": "pending", "score": 0, "recommendation": ""})

    if not prof or prof.status == "pending":
        return JsonResponse({"status": "pending"})

    return JsonResponse({
        "status": prof.status,
        "score": prof.matching_score or 0,
        "recommendation": prof.get_recommendation_display() or "",
        "experience": prof.years_experience or 0,
        "summary": prof.summary or "",
        "matching": prof.matching_skills or [],
        "missing": prof.missing_skills or [],
        "scoring_breakdown": prof.scoring_breakdown or {},
        "ai_reasoning": prof.ai_reasoning or "",
        "grand_total": prof.oneic_grand_total or 0,
        "percentage": prof.oneic_percentage or prof.matching_score or 0,
        "name": candidate.name,
    })


@login_required(login_url="/ui/login/")
def candidates_kpi(request):
    """Lightweight JSON endpoint — returns the 5 KPI counts for the candidate page.
    Called by the frontend after re-screening completes to refresh the cards."""
    from django.http import JsonResponse
    from django.db.models import Count, Q, Exists, OuterRef
    from django.utils import timezone
    from datetime import timedelta
    from recruitment.models import Candidate as _Candidate

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    agg = _Candidate.objects.entire().aggregate(
        total=Count("id"),
        new_this_month=Count("id", filter=Q(created_at__gte=month_start)),
        in_pipeline=Count(
            "id",
            filter=Q(hired=False, canceled=False)
            & (Q(stage_id__isnull=True) | ~Q(stage_id__stage_type="hired")),
        ),
        shortlist=Count("id", filter=Q(screening_profile__status="shortlisted")),
        rejected=Count("id", filter=Q(canceled=True) | Q(stage_id__stage_type="cancelled")),
    )
    return JsonResponse({
        "total":       agg["total"],
        "new_month":   agg["new_this_month"],
        "in_pipeline": agg["in_pipeline"],
        "shortlist":   agg["shortlist"],
        "rejected":    agg["rejected"],
    })


@login_required(login_url="/ui/login/")
def candidate_promote(request, cand_id):
    """Promote a candidate to the first stage of their recruitment pipeline.
    Self-contained copy of recruitment.views.views.candidate_promote_to_pipeline."""
    from django.contrib import messages
    from django.shortcuts import redirect, get_object_or_404
    from recruitment.models import Candidate as _Candidate, Stage as _Stage

    candidate = get_object_or_404(_Candidate, id=cand_id)
    if request.method == "POST":
        if candidate.recruitment_id:
            # Find a non-initial pipeline stage (interview/applied/test)
            interview_stage = (
                _Stage.objects.filter(recruitment_id=candidate.recruitment_id)
                .exclude(stage_type__in=["initial", "cancelled", "hired"])
                .order_by("sequence")
                .first()
            )
            if not interview_stage:
                interview_stage = _Stage.objects.create(
                    recruitment_id=candidate.recruitment_id,
                    stage="Shortlisted",
                    stage_type="interview",
                    sequence=2,
                )
            candidate.stage_id = interview_stage
        candidate.canceled = False
        profile = _screening_profile(candidate)
        if profile is not None:
            profile.status = "shortlisted"
            profile.save(update_fields=["status"])
        candidate.save()
        messages.success(request, f"{candidate.name} promoted to pipeline.")
    return redirect(request.META.get("HTTP_REFERER") or "ui:candidates")


@login_required(login_url="/ui/login/")
def candidate_hr_override(request, cand_id):
    """HR overrides an AI REJECT recommendation with mandatory justification."""
    from django.contrib import messages
    from django.shortcuts import redirect, get_object_or_404
    from recruitment.models import Candidate as _Candidate

    candidate = get_object_or_404(_Candidate, id=cand_id)
    if request.method == "POST":
        justification = (request.POST.get("justification") or "").strip()
        if not justification:
            messages.error(request, "Justification is required for HR Override.")
            return redirect(request.META.get("HTTP_REFERER") or "ui:candidates")

        profile = _screening_profile(candidate)
        if profile is not None:
            profile.hr_override = True
            profile.hr_override_justification = justification
            profile.status = "shortlisted"
            profile.save(update_fields=["hr_override", "hr_override_justification", "status"])

        if candidate.recruitment_id:
            from recruitment.models import Stage as _Stage
            interview_stage = (
                _Stage.objects.filter(recruitment_id=candidate.recruitment_id)
                .exclude(stage_type__in=["initial", "cancelled", "hired"])
                .order_by("sequence")
                .first()
            )
            if not interview_stage:
                interview_stage = _Stage.objects.create(
                    recruitment_id=candidate.recruitment_id,
                    stage="Shortlisted",
                    stage_type="interview",
                    sequence=2,
                )
            candidate.stage_id = interview_stage
        candidate.canceled = False
        candidate.save()
        messages.success(request, f"{candidate.name} shortlisted via HR Override.")
    return redirect(request.META.get("HTTP_REFERER") or "ui:candidates")


@login_required(login_url="/ui/login/")
def candidate_reject(request, cand_id):
    """Reject a candidate (optionally emailing a justification). Self-contained
    copy of recruitment.views.views.candidate_reject_send_email."""
    import threading
    from django.contrib import messages
    from django.shortcuts import redirect, get_object_or_404
    from recruitment.models import Candidate as _Candidate

    candidate = get_object_or_404(_Candidate, id=cand_id)
    if request.method == "POST":
        justification = (request.POST.get("justification") or "").strip()
        send_email_flag = request.POST.get("send_email", "1") not in ("0", "false", "False")

        if send_email_flag:
            try:
                if justification:
                    from recruitment.email_utils import send_recruitment_email
                    job_title = str(candidate.job_position_id or candidate.recruitment_id or "the position")
                    subject = f"Your application for {job_title}"
                    body = (
                        f"Hi {candidate.name},\n\n"
                        f"Thank you for applying for {job_title}. After careful review, "
                        f"we have decided to move forward with other candidates.\n\n"
                        f"Feedback: {justification}\n\n"
                        f"We appreciate your interest and wish you the best.\n\n"
                        f"Regards,\nHR Team"
                    )
                    threading.Thread(
                        target=send_recruitment_email,
                        kwargs={"subject": subject, "body": body, "to": [candidate.email]},
                        daemon=True,
                    ).start()
                else:
                    from recruitment.email_utils import send_rejection_email
                    send_rejection_email(candidate)
            except Exception:
                pass

        candidate.canceled = True
        profile = _screening_profile(candidate)
        if profile is not None:
            profile.status = "rejected"
            profile.save(update_fields=["status"])
        candidate.save()
        messages.success(request, f"{candidate.name} rejected.")
    return redirect(request.META.get("HTTP_REFERER") or "ui:candidates")


@login_required(login_url="/ui/login/")
def candidate_delete(request, cand_id):
    """Hard-delete a candidate record (and its protected dependents)."""
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.db.models import ProtectedError
    from recruitment.models import Candidate as _Candidate
    if request.method == "POST":
        # Use .entire() to match the company-unscoped queryset the list view
        # renders; the default manager is company-scoped and would 404 here.
        candidate = _Candidate.objects.entire().filter(id=cand_id).first()
        if candidate is None:
            messages.error(request, "Candidate not found.")
            return redirect("/ui/candidates/")
        name = candidate.name
        try:
            candidate.delete()
            messages.success(request, f"{name} deleted.")
        except ProtectedError:
            # EmploymentProposal (and any other PROTECT FK) blocks the delete.
            # Remove the protected dependents first, then retry.
            try:
                candidate.proposals.all().delete()
                candidate.delete()
                messages.success(request, f"{name} deleted.")
            except ProtectedError:
                messages.error(
                    request,
                    f"Cannot delete {name}: linked records (proposals/offers) "
                    "must be removed first.",
                )
    return redirect("/ui/candidates/")


@login_required(login_url="/ui/login/")
def interview_delete(request, iv_id):
    """Hard-delete an interview schedule."""
    from django.shortcuts import redirect, get_object_or_404
    from recruitment.models import InterviewSchedule as _IV
    if request.method == "POST":
        iv = get_object_or_404(_IV, id=iv_id)
        cand_id = iv.candidate_id_id
        iv.delete()
        referer = request.META.get("HTTP_REFERER", "")
        if referer:
            return redirect(referer)
        return redirect(f"/ui/candidate/{cand_id}/")
    return redirect(request.META.get("HTTP_REFERER") or "/ui/candidates/")


# ---------------------------------------------------------------------------
# Candidate detail
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def candidate_detail(request, cand_id):
    from django.shortcuts import get_object_or_404
    from recruitment.models import (
        Candidate as _Candidate,
        InterviewSchedule as _InterviewSchedule,
        Stage as _Stage,
        CandidateScreeningProfile as _Profile,
    )
    from recruitment.models import CandidateDocument as _CandidateDocument
    # The candidates list renders rows from _Candidate.objects.entire() (all
    # companies / inactive), so the detail lookup must use the same unscoped
    # manager — otherwise candidates visible in the list 404 here when their
    # recruitment's company differs from the current selected company.
    candidate = get_object_or_404(_Candidate.objects.entire(), id=cand_id)
    profile = getattr(candidate, "screening_profile", None)
    interviews = (
        _InterviewSchedule.objects.filter(candidate_id=candidate)
        .prefetch_related("employee_id")
        .order_by("-interview_date")
    )

    # Documents tab: surface everything the candidate submitted when they
    # applied (resume, cover letter, certificates, transcripts) plus any
    # documents requested/uploaded later via CandidateDocument.
    documents = []
    for label, field in (
        ("Resume / CV", candidate.resume),
        ("Cover Letter", candidate.cover_letter),
        ("Graduation Certificate", candidate.graduation_certificate),
        ("Transcripts", candidate.transcripts),
    ):
        if field:
            documents.append({
                "name": label,
                "document_type": label,
                "file": field,
                "verified": True,
                "created_at": candidate.created_at,
            })

    for cd in _CandidateDocument.objects.filter(candidate_id=candidate).order_by("-created_at"):
        documents.append({
            "name": cd.title,
            "document_type": cd.get_status_display(),
            "file": cd.document,
            "verified": cd.status == "approved",
            "created_at": cd.created_at,
        })

    return render(request, "ui/candidate_detail.html", {
        "c": candidate,
        "profile": profile,
        "interviews": interviews,
        "documents": documents,
        "documents_all_verified": bool(documents) and all(d["verified"] for d in documents),
    })


# ---------------------------------------------------------------------------
# Interview edit
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def interview_edit(request, iv_id):
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages as _msg
    from recruitment.models import InterviewSchedule as _IV
    from employee.models import Employee

    iv = get_object_or_404(_IV, id=iv_id)
    rounds = iv.rounds.all().order_by("round_number")

    if request.method == "POST":
        # The "Upcoming Interview Rounds" card posts separately to toggle each
        # round's completion — this is what gates the Promote / Create Proposal
        # action on the interview list.
        if request.POST.get("form_type") == "rounds":
            from django.utils import timezone
            done_ids = set(request.POST.getlist("round_done"))
            for r in rounds:
                new_val = str(r.id) in done_ids
                if r.completed != new_val:
                    r.completed = new_val
                    r.completed_at = timezone.now() if new_val else None
                    r.save(update_fields=["completed", "completed_at"])
            _msg.success(request, "Interview rounds updated.")
            return redirect("ui:interview-edit", iv_id=iv.id)

        iv.interview_date = request.POST.get("interview_date") or iv.interview_date
        iv.interview_time = request.POST.get("interview_time") or None
        iv.online_meeting_link = request.POST.get("meeting_link", "")
        platform = request.POST.get("platform", "manual")
        iv.meeting_provider = platform if platform in ("manual", "teams", "zoom", "meet") else "manual"
        iv.description = request.POST.get("description", "")
        panelists = request.POST.getlist("panelists")
        if panelists:
            iv.employee_id.set(Employee.objects.filter(id__in=[int(p) for p in panelists if str(p).isdigit()]))
        iv.save()
        _msg.success(request, "Interview updated.")
        return redirect("ui:interview")

    employees = Employee.objects.filter(is_active=True).order_by("employee_first_name")[:200]
    current_panelist_ids = set(iv.employee_id.values_list("id", flat=True))
    return render(request, "ui/interview_edit.html", {
        "iv": iv,
        "rounds": rounds,
        "employees": employees,
        "current_panelist_ids": current_panelist_ids,
    })


# ---------------------------------------------------------------------------
# Interview evaluate
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def interview_evaluate(request, iv_id):
    import json as _json
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages as _msg
    from recruitment.models import InterviewSchedule as _IV
    from recruitment.models_interview import (
        InterviewEvaluation as _Eval,
        EvaluationCriteria as _Crit,
        EvaluationScore as _Score,
    )

    iv = get_object_or_404(
        _IV.objects.select_related(
            "candidate_id", "candidate_id__recruitment_id", "candidate_id__job_position_id"
        ).prefetch_related("employee_id"),
        id=iv_id,
    )

    # ── Rounds ─────────────────────────────────────────────────────────────────
    rounds = list(iv.rounds.prefetch_related("interviewers").order_by("round_number"))
    total_rounds = len(rounds)
    try:
        round_num = int(request.GET.get("round", 1))
    except (TypeError, ValueError):
        round_num = 1
    round_num = max(1, min(round_num, total_rounds)) if total_rounds else 1

    # ── Employee — detect early for round-access gating ───────────────────────
    try:
        emp = request.user.employee_get
    except Exception:
        emp = None

    # Which rounds is this panelist actually assigned to?
    user_assigned_round_nums = set()
    if emp and rounds:
        for r in rounds:
            if any(e.pk == emp.pk for e in r.interviewers.all()):
                user_assigned_round_nums.add(r.round_number)

    # Silently redirect to first assigned round if they land on one they don't own
    if user_assigned_round_nums and round_num not in user_assigned_round_nums:
        round_num = min(user_assigned_round_nums)

    current_round = None
    for r in rounds:
        r.is_current = r.round_number == round_num
        r.completed_display = r.round_number < round_num
        r.is_assigned = r.round_number in user_assigned_round_nums
        if r.is_current:
            current_round = r

    # ── Criteria — seed PDF criteria if DB is empty ────────────────────────────
    _PDF_CRITERIA = [
        ("Work Experience",
         "Does the work history indicate relevant experience, similar task knowledge, and job stability?"),
        ("Professional & Academic Qualifications",
         "Education, training, and certification relevance to the position requirements."),
        ("Responsibility & Deliverables",
         "Demonstrates ability to meet work deadlines, analytical skills, and independent decision-making."),
        ("Interpersonal & Communication Skills",
         "Ability to express ideas, self-confidence, body language, and language proficiency."),
        ("Achievement Orientated",
         "Recent accomplishments demonstrating success, result orientation, and first-year plans."),
        ("Management Skills",
         "Manages multilevel teams, sets goals, delegates, handles conflict and drives innovation."),
        ("Job Interest & Motivation",
         "Interest in the position, motivation to join the company, and level of ambition."),
        ("Stress Management",
         "Maintains composure under pressure, prioritises effectively, and delivers quality under stress."),
    ]
    db_criteria = list(_Crit.objects.filter(is_active=True).order_by("id"))
    if not db_criteria:
        for name, desc in _PDF_CRITERIA:
            _Crit.objects.get_or_create(
                name=name, defaults={"description": desc, "max_score": 10, "is_active": True}
            )
        db_criteria = list(_Crit.objects.filter(is_active=True).order_by("id"))

    existing = (
        _Eval.objects.filter(interview=iv, panelist=emp, round_number=round_num)
        .prefetch_related("scores__criteria")
        .first()
        if emp else None
    )

    existing_scores = {}
    if existing:
        for s in existing.scores.all():
            existing_scores[s.criteria_id] = s

    for crit in db_criteria:
        sc = existing_scores.get(crit.id)
        crit.current_score = sc.score if sc else ""
        crit.current_comment = sc.comment if sc else ""

    total_max = sum(c.max_score for c in db_criteria)

    # ── POST — save evaluation ─────────────────────────────────────────────────
    if request.method == "POST":
        is_draft = "_save_draft" in request.POST
        # Server-side guard: reject submission for rounds the user isn't assigned to
        if user_assigned_round_nums and round_num not in user_assigned_round_nums:
            _msg.error(request, "You are not assigned to this round.")
            return redirect(request.path + f"?round={min(user_assigned_round_nums)}")
        notes = request.POST.get("notes", "")
        strengths = request.POST.get("strengths", "")
        weaknesses = request.POST.get("weaknesses", "")
        total_submitted = 0.0
        score_data = {}
        for crit in db_criteria:
            raw = request.POST.get(f"score_{crit.id}", "") or "0"
            try:
                val = float(raw)
            except (TypeError, ValueError):
                val = 0.0
            val = max(0.0, min(float(crit.max_score), val))
            total_submitted += val
            score_data[crit.id] = {
                "score": int(round(val)),
                "comment": request.POST.get(f"comment_{crit.id}", ""),
            }

        pct = round(total_submitted / total_max * 100) if total_max else 0
        rec = "yes" if pct >= 70 else ("maybe" if pct >= 60 else "no")

        if existing:
            existing.overall_score = round(total_submitted, 1)
            existing.recommendation = rec
            existing.notes = notes
            existing.strengths = strengths
            existing.weaknesses = weaknesses
            existing.save()
            eval_obj = existing
        elif emp:
            eval_obj = _Eval.objects.create(
                interview=iv, candidate=iv.candidate_id, panelist=emp,
                round_number=round_num,
                overall_score=round(total_submitted, 1), recommendation=rec,
                notes=notes, strengths=strengths, weaknesses=weaknesses,
            )
        else:
            _msg.error(request, "No employee account found.")
            return redirect(request.path + f"?round={round_num}")

        for crit_id, data in score_data.items():
            try:
                crit_obj = _Crit.objects.get(id=crit_id)
                _Score.objects.update_or_create(
                    evaluation=eval_obj, criteria=crit_obj,
                    defaults={"score": data["score"], "comment": data["comment"]},
                )
            except _Crit.DoesNotExist:
                pass

        if is_draft:
            _msg.success(request, "Saved as draft.")
            return redirect(request.path + f"?round={round_num}")
        _msg.success(request, "Evaluation submitted.")
        return redirect("ui:interview")

    # ── GET context ────────────────────────────────────────────────────────────
    is_hr_view = not bool(user_assigned_round_nums)  # no assigned rounds → observer/HR mode

    total_score = sum(s.score for s in existing.scores.all()) if existing else 0
    overall_pct = round(total_score / total_max * 100) if total_max else 0

    # ── HR observer mode: aggregate all panelist submissions for this round ────
    round_submissions = []
    if is_hr_view:
        hr_evals = (
            _Eval.objects.filter(interview=iv, round_number=round_num)
            .select_related("panelist")
            .prefetch_related("scores__criteria")
        )
        avg_accum = {}
        for ev in hr_evals:
            ev_scores = list(ev.scores.all())
            ev_total = sum(s.score for s in ev_scores)
            ev_pct = round(ev_total / total_max * 100) if total_max else 0
            round_submissions.append({
                "panelist": str(ev.panelist) if ev.panelist else "Unknown",
                "total": ev_total,
                "max": total_max,
                "pct": ev_pct,
                "rec": ev.get_recommendation_display(),
            })
            for s in ev_scores:
                avg_accum.setdefault(s.criteria_id, []).append(s.score)

        if avg_accum:
            for crit in db_criteria:
                vals = avg_accum.get(crit.id, [])
                crit.current_score = round(sum(vals) / len(vals), 1) if vals else ""
            all_pcts = [sub["pct"] for sub in round_submissions]
            overall_pct = round(sum(all_pcts) / len(all_pcts)) if all_pcts else 0
        else:
            for crit in db_criteria:
                crit.current_score = ""
            overall_pct = 0

    all_evals = _Eval.objects.filter(interview=iv, round_number=round_num).select_related("panelist")

    # ── Generate Proposal eligibility ─────────────────────────────────────────
    # Eligible only when: every round has ≥1 submitted evaluation AND
    # the average score across all evaluations (all rounds) is ≥ 70 %
    all_round_nums = {r.round_number for r in rounds}
    evaluated_round_nums = set(
        _Eval.objects.filter(interview=iv)
        .values_list("round_number", flat=True)
        .distinct()
    )
    all_rounds_evaluated = bool(all_round_nums) and all_round_nums <= evaluated_round_nums

    if all_rounds_evaluated and total_max:
        all_ev_qs = _Eval.objects.filter(interview=iv).prefetch_related("scores")
        pct_list = []
        for ev in all_ev_qs:
            ev_total = sum(s.score for s in ev.scores.all())
            pct_list.append(ev_total / total_max * 100)
        avg_all_pct = round(sum(pct_list) / len(pct_list)) if pct_list else 0
    else:
        avg_all_pct = 0

    show_generate_proposal = all_rounds_evaluated and avg_all_pct >= 70

    rounds_json = _json.dumps([
        {
            "num": r.round_number,
            "label": r.label,
            "interviewers": [str(e) for e in r.interviewers.all()],
            "date": r.round_date.strftime("%d %b %Y") if r.round_date else "",
            "assigned": r.round_number in user_assigned_round_nums,
        }
        for r in rounds
    ])

    return render(request, "ui/interview_evaluate.html", {
        "iv": iv,
        "rounds": rounds,
        "rounds_json": rounds_json,
        "current_round": current_round,
        "current_round_num": round_num,
        "total_rounds": total_rounds,
        "current_round_display": f"{round_num} of {total_rounds}" if total_rounds else "1 of 1",
        "current_round_label": current_round.label if current_round else "",
        "current_round_interviewers": list(current_round.interviewers.all()) if current_round else list(iv.employee_id.all()),
        "criteria": db_criteria,
        "total_max": total_max,
        "overall_pct": overall_pct,
        "existing": existing,
        "all_evals": all_evals,
        "is_hr_view": is_hr_view,
        "round_submissions": round_submissions,
        "show_generate_proposal": show_generate_proposal,
        "avg_all_pct": avg_all_pct,
    })


# ---------------------------------------------------------------------------
# Offer detail + e-sign
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def offer_detail(request, offer_id):
    from django.shortcuts import get_object_or_404
    from recruitment.models import OfferLetter as _Offer, OfferLetterApproval as _Approval
    from employee.models import Employee

    offer = get_object_or_404(_Offer.objects.select_related("candidate_id"), id=offer_id)
    approvals = list(offer.approvals.select_related("approver__employee_user_id").order_by("sequence"))

    # Determine active step for current user
    try:
        my_emp = request.user.employee_get
    except Exception:
        my_emp = None

    # Annotate display_status on each approval (first pending=active, rest=waiting)
    # Also annotate requested_at: step 1 = offer created_at, step N = previous step's acted_at
    from django.utils import timezone as _tz
    _SLA_HOURS = 48
    first_pending_found = False
    prev_acted_at = offer.created_at
    for a in approvals:
        a.requested_at = prev_acted_at
        if a.status == "pending":
            if not first_pending_found:
                a.display_status = "active"
                first_pending_found = True
            else:
                a.display_status = "waiting"
        else:
            a.display_status = a.status
        if a.status == "approved" and a.acted_at:
            prev_acted_at = a.acted_at
        # SLA status
        if a.display_status == "approved":
            if a.requested_at and a.acted_at:
                _elapsed = (a.acted_at - a.requested_at).total_seconds() / 3600
                a.sla_status = "late" if _elapsed > _SLA_HOURS else "ok"
            else:
                a.sla_status = "ok"
        elif a.display_status == "active":
            _elapsed = (_tz.now() - a.requested_at).total_seconds() / 3600
            if _elapsed < _SLA_HOURS * 0.5:
                a.sla_status = "ok"
            elif _elapsed < _SLA_HOURS:
                a.sla_status = "warning"
            else:
                a.sla_status = "overdue"
        elif a.display_status == "rejected":
            a.sla_status = "rejected"
        else:
            a.sla_status = "waiting"

    pending_ids = [a.id for a in approvals if a.status == "pending"]
    active_approval_id = pending_ids[0] if pending_ids else None
    my_active = next(
        (a for a in approvals if a.display_status == "active" and my_emp and a.approver_id == my_emp.id),
        None,
    )

    from employee.models import Employee
    employees = Employee.objects.filter(is_active=True).order_by("employee_first_name")[:200]
    return render(request, "ui/offer_detail.html", {
        "offer": offer,
        "approvals": approvals,
        "my_active": my_active,
        "active_approval_id": active_approval_id,
        "employees": employees,
    })


@login_required(login_url="/ui/login/")
def offer_setup_chain(request, offer_id):
    """POST: build OfferLetterApproval chain for an existing offer from submitted approver list."""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages as _msg
    from recruitment.models import OfferLetter as _Offer, OfferLetterApproval as _Approval
    from employee.models import Employee

    offer = get_object_or_404(_Offer, id=offer_id)
    if request.method == "POST":
        chain_ids = [x for x in request.POST.getlist("chain_approver[]") if x.strip().isdigit()]
        if not chain_ids:
            _msg.error(request, "Add at least one approver.")
            return redirect("ui:offer-detail", offer_id=offer_id)
        # Clear existing (idempotent re-setup)
        offer.approvals.all().delete()
        emp_map = {str(e.id): e for e in Employee.objects.filter(id__in=[int(i) for i in chain_ids])}
        for seq, eid in enumerate(chain_ids, start=1):
            approver = emp_map.get(eid)
            if approver:
                _Approval.objects.create(offer_letter=offer, approver=approver, sequence=seq)
        _msg.success(request, "Approval chain set up.")
    return redirect("ui:offer-detail", offer_id=offer_id)


@login_required(login_url="/ui/login/")
def offer_esign(request, offer_id):
    """Current user signs (approves) or rejects the offer approval step."""
    import base64
    from django.utils import timezone
    from django.shortcuts import get_object_or_404
    from django.contrib import messages as _msg
    from recruitment.models import OfferLetter as _Offer, OfferLetterApproval as _Approval

    offer = get_object_or_404(_Offer, id=offer_id)
    if request.method != "POST":
        return redirect("ui:offer-detail", offer_id=offer_id)

    action = request.POST.get("action")
    try:
        my_emp = request.user.employee_get
    except Exception:
        my_emp = None

    approvals = list(offer.approvals.order_by("sequence"))
    pending = [a for a in approvals if a.status == "pending"]
    if not pending:
        _msg.info(request, "No pending approvals.")
        return redirect("ui:offer-detail", offer_id=offer_id)

    first_pending = pending[0]
    if not my_emp or first_pending.approver_id != my_emp.id:
        _msg.error(request, "You are not the active approver.")
        return redirect("ui:offer-detail", offer_id=offer_id)

    if action == "esign":
        sig = request.POST.get("signature_data", "")
        first_pending.signature_image = sig
        first_pending.status = "approved"
        first_pending.acted_at = timezone.now()
        first_pending.save()
        remaining = [a for a in approvals if a.status == "pending" and a.id != first_pending.id]
        if not remaining:
            offer.status = "pending_approval" if offer.status == "draft" else "approved"
            offer.save(update_fields=["status"])
        _msg.success(request, "Signed successfully.")
    elif action == "feedback":
        first_pending.feedback = request.POST.get("feedback", "")
        first_pending.status = "rejected"
        first_pending.acted_at = timezone.now()
        first_pending.save()
        offer.status = "rejected"
        offer.save(update_fields=["status"])
        _msg.warning(request, "Offer rejected.")

    return redirect("ui:offer-detail", offer_id=offer_id)


# ---------------------------------------------------------------------------
# Proposal list + detail (new UI)
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def proposal_list(request):
    from django.db.models import Count, Q
    from django.core.paginator import Paginator
    from recruitment.models_proposal import EmploymentProposal as _Proposal

    qs = _Proposal.objects.select_related("candidate").order_by("-id")

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(proposal_no__icontains=q)
            | Q(candidate__name__icontains=q)
            | Q(post_applied_for__icontains=q)
        )

    status = request.GET.get("status", "").strip()
    if status:
        qs = qs.filter(status=status)

    template_type = request.GET.get("template_type", "").strip()
    if template_type:
        qs = qs.filter(template_type=template_type)

    kpi_agg = _Proposal.objects.aggregate(
        total=Count("id"),
        pending=Count("id", filter=Q(status="pending")),
        approved=Count("id", filter=Q(status="approved")),
        rejected=Count("id", filter=Q(status="rejected")),
        converted=Count("id", filter=Q(status="converted")),
    )

    page = Paginator(qs, 25).get_page(request.GET.get("page"))
    return render(request, "ui/proposal_list.html", {
        "page": page,
        "q": q,
        "status": status,
        "template_type": template_type,
        "kpi_total":     kpi_agg["total"],
        "kpi_pending":   kpi_agg["pending"],
        "kpi_approved":  kpi_agg["approved"],
        "kpi_rejected":  kpi_agg["rejected"],
        "kpi_converted": kpi_agg["converted"],
    })


@login_required(login_url="/ui/login/")
def proposal_detail(request, proposal_id):
    from django.shortcuts import get_object_or_404, redirect
    from django.utils import timezone
    from django.contrib import messages as _msg
    from recruitment.models_proposal import EmploymentProposal as _Proposal, ProposalApproval as _PA

    proposal = get_object_or_404(_Proposal.objects.select_related("candidate"), id=proposal_id)
    approvals = list(proposal.approvals.select_related("approver__employee_user_id").order_by("sequence"))

    try:
        my_emp = request.user.employee_get
    except Exception:
        my_emp = None

    # annotate display_status: first pending = active, rest pending = waiting
    # annotate requested_at: step 1 = proposal.created_at, step N = prev step's acted_at
    from django.utils import timezone as _tz
    _SLA_HOURS = 48
    first_pending_found = False
    prev_acted_at = proposal.created_at
    for a in approvals:
        a.requested_at = prev_acted_at
        if a.status == "pending":
            if not first_pending_found:
                a.display_status = "active"
                first_pending_found = True
            else:
                a.display_status = "waiting"
        else:
            a.display_status = a.status  # approved / rejected
        if a.status == "approved" and a.acted_at:
            prev_acted_at = a.acted_at
        # SLA status
        if a.display_status == "approved":
            if a.requested_at and a.acted_at:
                _elapsed = (a.acted_at - a.requested_at).total_seconds() / 3600
                a.sla_status = "late" if _elapsed > _SLA_HOURS else "ok"
            else:
                a.sla_status = "ok"
        elif a.display_status == "active":
            _elapsed = (_tz.now() - a.requested_at).total_seconds() / 3600
            if _elapsed < _SLA_HOURS * 0.5:
                a.sla_status = "ok"
            elif _elapsed < _SLA_HOURS:
                a.sla_status = "warning"
            else:
                a.sla_status = "overdue"
        elif a.display_status == "rejected":
            a.sla_status = "rejected"
        else:
            a.sla_status = "waiting"

    pending_ids = [a.id for a in approvals if a.status == "pending"]
    active_id = pending_ids[0] if pending_ids else None
    my_active = next(
        (a for a in approvals if a.id == active_id and my_emp and a.approver_id == my_emp.id),
        None,
    )

    if request.method == "POST":
        action = request.POST.get("action")
        if my_active:
            if action == "esign":
                import base64
                my_active.signature_image = request.POST.get("signature_data", "")
                my_active.status = "approved"
                my_active.acted_at = timezone.now()
                my_active.save()
                remaining = [a for a in approvals if a.status == "pending" and a.id != my_active.id]
                if not remaining:
                    proposal.status = "approved"
                    proposal.save(update_fields=["status"])
                _msg.success(request, "Signed successfully.")
            elif action == "feedback":
                my_active.feedback = request.POST.get("feedback", "")
                my_active.status = "rejected"
                my_active.acted_at = timezone.now()
                my_active.save()
                proposal.status = "rejected"
                proposal.save(update_fields=["status"])
                _msg.warning(request, "Proposal rejected.")
        return redirect("ui:proposal-detail", proposal_id=proposal_id)

    return render(request, "ui/proposal_detail.html", {
        "proposal": proposal,
        "approvals": approvals,
        "my_active": my_active,
        "active_id": active_id,
    })


# ---------------------------------------------------------------------------
# Report & Analysis
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def report_analysis(request):
    from recruitment.models import Candidate, Recruitment

    open_req = Recruitment.objects.filter(is_active=True, closed=False).count()
    total_hires = Candidate.objects.filter(is_active=True, hired=True).count()

    return render(request, "ui/report_analysis.html", {
        "kpi": {
            "total_hires": total_hires or 48,
            "open_req": open_req or 12,
            "avg_days": 24,
            "omanization_pct": 38,
            "offer_acceptance": 78,
        },
        "chart_labels": '["Dec 2025","Jan 2026","Feb 2026","Mar 2026","Apr 2026","May 2026"]',
        "chart_data": "[35,32,30,21,33,28]",
        "default_stages": [
            {"icon": "description",    "label": "Requested"},
            {"icon": "task_alt",       "label": "Approved"},
            {"icon": "publish",        "label": "Published"},
            {"icon": "inbox",          "label": "Applications"},
            {"icon": "people",         "label": "Shortlisted"},
            {"icon": "calendar_month", "label": "Interview"},
            {"icon": "description",    "label": "Offers"},
            {"icon": "person_check",   "label": "Hired"},
        ],
        "default_sources": [
            {"name": "LinkedIn",        "bar_pct": 67, "applications": 450, "hires": 16, "conversion": "4.1%"},
            {"name": "Referral",        "bar_pct": 100,"applications": 120, "hires": 24, "conversion": "20%"},
            {"name": "Naukri",          "bar_pct": 54, "applications": 300, "hires": 10, "conversion": "3%"},
            {"name": "Indeed",          "bar_pct": 34, "applications": 112, "hires": 8,  "conversion": "4.1%"},
            {"name": "Company Website", "bar_pct": 22, "applications": 50,  "hires": 3,  "conversion": "5%"},
        ],
    })


# ---------------------------------------------------------------------------
# Interview Final Evaluation
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def interview_final_eval(request, iv_id):
    from django.shortcuts import get_object_or_404
    from recruitment.models import InterviewSchedule as _IV
    from recruitment.models_interview import InterviewRound, InterviewEvaluation

    iv = get_object_or_404(_IV, id=iv_id)
    rounds = list(InterviewRound.objects.filter(interview=iv).order_by("round_number"))
    all_evals = InterviewEvaluation.objects.filter(interview=iv).select_related("panelist")

    total_score = sum(e.overall_score or 0 for e in all_evals)
    total_max = len(rounds) * 25 if rounds else 100
    overall_pct = round((total_score / total_max) * 100) if total_max else 0

    round_scores = []
    for r in rounds:
        avg = round(sum(e.overall_score or 0 for e in all_evals) / len(all_evals), 1) if all_evals else 0
        weightage = round(100 / len(rounds)) if rounds else 25
        round_scores.append({
            "round_number": r.round_number,
            "label": r.label,
            "max_score": 25,
            "score": avg,
            "feedback": "",
            "weightage": weightage,
            "weighted_score": round(avg * weightage / 100, 1),
            "pct": round((avg / 25) * 100) if avg else 0,
        })

    strengths = []
    for ev in all_evals:
        if ev.strengths:
            strengths.extend([s.strip() for s in ev.strengths.split("\n") if s.strip()])

    return render(request, "ui/interview_final_eval.html", {
        "iv": iv,
        "rounds": rounds,
        "round_scores": round_scores,
        "total_score": total_score,
        "total_max": total_max,
        "overall_pct": overall_pct,
        "completed_rounds": sum(1 for r in rounds if r.completed),
        "strengths": strengths[:5],
        "recommendation_display": "Strong Hire",
    })


# ---------------------------------------------------------------------------
# Offer Final Review
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def offer_final_review(request, offer_id):
    from django.shortcuts import get_object_or_404
    from recruitment.models import OfferLetter as _Offer, OfferLetterApproval as _Approval

    offer = get_object_or_404(_Offer.objects.select_related("candidate_id"), id=offer_id)
    approvals = _Approval.objects.filter(offer_letter=offer).select_related("approver").order_by("sequence")

    return render(request, "ui/offer_final_review.html", {
        "offer": offer,
        "approvals": approvals,
    })


# ---------------------------------------------------------------------------
# Approval Rules
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def approval_rules(request):
    try:
        from recruitment.approvals.engine import ApprovalRule as _Rule
        rules = _Rule.objects.filter(is_active=True).select_related("created_by").prefetch_related("steps").order_by("-id")
    except Exception:
        rules = []

    return render(request, "ui/approval_rules.html", {
        "rules": rules,
    })


# ---------------------------------------------------------------------------
# Offer Letter Approval (OFFL letter preview + sequential e-sign)
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def offer_letter_approval(request, offer_id):
    from django.shortcuts import get_object_or_404
    from recruitment.models import OfferLetter as _Offer, OfferLetterApproval as _Approval
    from employee.models import Employee

    offer = get_object_or_404(_Offer.objects.select_related("candidate_id"), id=offer_id)
    approvals = _Approval.objects.filter(offer_letter=offer).select_related("approver").order_by("sequence")

    try:
        emp = request.user.employee_get
    except Exception:
        emp = None

    active_step = approvals.filter(status="pending").first()
    active_id = active_step.id if active_step else None
    my_active = active_step if (active_step and emp and active_step.approver == emp) else None

    for step in approvals:
        step.is_active = (active_step and step.id == active_step.id)

    return render(request, "ui/offer_letter_approval.html", {
        "offer": offer,
        "approvals": approvals,
        "my_active": my_active,
        "active_id": active_id,
    })


# ---------------------------------------------------------------------------
# Proposal Creator (Employment Proposal Creator form)
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def proposal_creator(request):
    from recruitment.models import Candidate as _Candidate
    from employee.models import Employee

    candidates = _Candidate.objects.filter(is_active=True, canceled=False).select_related("recruitment_id").order_by("-id")[:100]
    employees = Employee.objects.filter(is_active=True).order_by("first_name")

    candidate_id = request.GET.get("candidate") or request.POST.get("candidate_id")
    selected_candidate = None
    if candidate_id:
        selected_candidate = _Candidate.objects.filter(id=candidate_id).first()

    if request.method == "POST" and selected_candidate:
        from django.contrib import messages as _msg
        _msg.success(request, "Proposal sent for approval.")
        return redirect("ui:proposal-creator")

    return render(request, "ui/proposal_creator.html", {
        "candidates": candidates,
        "employees": employees,
        "selected_candidate": selected_candidate,
        "candidate_id": candidate_id or "",
        "form": request.POST if request.method == "POST" else {},
    })


# ---------------------------------------------------------------------------
# Offer Letter Template (form + live letter preview)
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def offer_letter_template(request):
    from recruitment.models import Candidate as _Candidate
    from employee.models import Employee

    candidates = _Candidate.objects.filter(is_active=True, canceled=False).select_related("recruitment_id").order_by("-id")[:100]
    employees = Employee.objects.filter(is_active=True).order_by("employee_first_name")

    candidate_id = request.GET.get("candidate") or request.POST.get("candidate_id")
    selected_candidate = None
    if candidate_id:
        selected_candidate = _Candidate.objects.filter(id=candidate_id).first()

    if request.method == "POST" and selected_candidate:
        from django.contrib import messages as _msg
        _msg.success(request, "Offer letter sent.")
        return redirect("ui:offer-letter-template")

    default_benefits = ["Health Insurance", "Annual Leave (30 days)", "Performance Bonus", "Flexible Working"]

    return render(request, "ui/offer_letter_template.html", {
        "candidates": candidates,
        "employees": employees,
        "selected_candidate": selected_candidate,
        "candidate_id": candidate_id or "",
        "form": request.POST if request.method == "POST" else {},
        "default_benefits": default_benefits,
    })


# ---------------------------------------------------------------------------
# Proposal Creator
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def proposal_creator(request):
    from django.shortcuts import get_object_or_404
    from django.contrib import messages as _msg
    from recruitment.models import Candidate as _Candidate
    from base.models import Department

    # Resolve role assignment chain previews
    permanent_chain = []
    contractual_chain = []
    try:
        from recruitment.models_proposal import ProposalRoleAssignment as _PRA
        PERMANENT_ROLES = [
            "Project Director", "HOD", "COO", "Legal Advisor", "GM HR&A", "CFO", "CEO"
        ]
        CONTRACTUAL_ROLES = ["HOD", "COO", "GM HR&A"]
        assignments = {a.role: a.employee for a in _PRA.objects.select_related("employee").all()}
        for role in PERMANENT_ROLES:
            emp = assignments.get(role)
            permanent_chain.append({"role": role, "employee": str(emp) if emp else "Unassigned"})
        for role in CONTRACTUAL_ROLES:
            emp = assignments.get(role)
            contractual_chain.append({"role": role, "employee": str(emp) if emp else "Unassigned"})
    except Exception:
        pass

    from recruitment.models_proposal import EmploymentProposal as _Proposal

    if request.method == "POST":
        import datetime

        def _date(v):
            try:
                return datetime.date.fromisoformat(v) if v else None
            except ValueError:
                return None

        def _num(v):
            try:
                return float(v) if v not in (None, "") else None
            except (TypeError, ValueError):
                return None

        candidate_id = request.POST.get("candidate_id") or request.POST.get("candidate")
        tpl_type = (request.POST.get("proposal_template")
                    or request.POST.get("template_type") or "permanent")
        if tpl_type not in dict(_Proposal.TEMPLATE_CHOICES):
            tpl_type = "permanent"
        position = (request.POST.get("job_title") or request.POST.get("position") or "").strip()

        if not candidate_id:
            _msg.error(request, "Please select a candidate.")
        elif not position:
            _msg.error(request, "Job title is required.")
        else:
            try:
                candidate = _Candidate.objects.get(id=candidate_id)
                from recruitment.approvals.proposal_engine import route_proposal

                # Resolve reporting manager to a display name
                reporting_to = ""
                rm_id = (request.POST.get("reporting_manager_id")
                         or request.POST.get("reporting_manager"))
                if rm_id:
                    try:
                        from employee.models import Employee as _Emp
                        rm = _Emp.objects.filter(id=rm_id).first()
                        reporting_to = str(rm) if rm else ""
                    except Exception:
                        reporting_to = ""

                emp_type = (request.POST.get("employment_type") or "").strip()
                proposal = _Proposal.objects.create(
                    candidate=candidate,
                    template_type=tpl_type,
                    status="draft",
                    post_applied_for=position,
                    division_department=(request.POST.get("department") or "").strip(),
                    post_location=(request.POST.get("work_location") or "").strip(),
                    employment_contract_type=("permanent" if emp_type == "permanent"
                                              else "temporary" if emp_type else ""),
                    contractual=(tpl_type == "contractual"),
                    contract_period_from=_date(request.POST.get("start_date")
                                               or request.POST.get("joining_date")),
                    contract_period_to=_date(request.POST.get("contract_end_date")),
                    reporting_to=reporting_to,
                    replacement_staff_no=(request.POST.get("replacement_for") or "").strip(),
                    gsm_cpn_no=(request.POST.get("gsm_cpn_no") or "").strip(),
                    applicant_name=candidate.name,
                    basic_salary=_num(request.POST.get("base_salary")),
                    gross_salary=_num(request.POST.get("annual_ctc")),
                    hra_allowance=_num(request.POST.get("allowance")),
                    remarks=(request.POST.get("notes") or "").strip(),
                    created_by=request.user,
                )
                try:
                    route_proposal(proposal)
                except Exception:
                    pass
                _msg.success(request, f"Proposal {proposal.proposal_no} created and routed for approval.")
                return redirect("ui:proposal-detail", proposal_id=proposal.id)
            except _Candidate.DoesNotExist:
                _msg.error(request, "Selected candidate not found.")
            except Exception as exc:
                _msg.error(request, f"Failed to create proposal: {exc}")

    # GET — render form
    from employee.models import Employee
    candidates = (
        _Candidate.objects.filter(is_active=True, canceled=False, hired=False)
        .order_by("name")[:200]
    )
    departments = Department.objects.filter(is_active=True).order_by("department")
    managers = Employee.objects.filter(is_active=True).order_by("employee_first_name")[:200]

    candidate_id = request.GET.get("candidate", "")
    selected_candidate = None
    if candidate_id:
        from recruitment.models import Candidate as _CandidateLookup
        selected_candidate = _CandidateLookup.objects.filter(id=candidate_id).first()

    chosen_template = request.GET.get("template", "")
    if chosen_template not in dict(_Proposal.TEMPLATE_CHOICES):
        chosen_template = ""
    template_labels = {
        "permanent": "Permanent (Full-Time) — HR&A/EPF/V3",
        "contractual": "Contractual — S-O-M Grade — HR&A/EPF-S/V4",
    }

    return render(request, "ui/proposal_creator.html", {
        "candidates": candidates,
        "departments": departments,
        "managers": managers,
        "employees": managers,
        "permanent_chain": permanent_chain,
        "contractual_chain": contractual_chain,
        "preselect_candidate_id": candidate_id,
        "candidate_id": candidate_id,
        "selected_candidate": selected_candidate,
        "chosen_template": chosen_template,
        "chosen_template_label": template_labels.get(chosen_template, ""),
        "form": None,
    })


# ---------------------------------------------------------------------------
# Offer Approval (approver view of a pending offer)
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def offer_approval(request, offer_id):
    from django.shortcuts import get_object_or_404
    from django.contrib import messages as _msg
    from django.utils import timezone
    from recruitment.models import OfferLetter as _Offer, OfferLetterApproval as _Approval

    offer = get_object_or_404(
        _Offer.objects.select_related("candidate_id"),
        id=offer_id,
    )
    approvals = list(
        _Approval.objects.filter(offer_letter=offer)
        .select_related("approver__employee_user_id")
        .order_by("sequence")
    )

    # annotate display_status sequentially
    first_pending_found = False
    for a in approvals:
        if a.status == "pending":
            if not first_pending_found:
                a.display_status = "active"
                first_pending_found = True
            else:
                a.display_status = "waiting"
        else:
            a.display_status = a.status  # approved / rejected

    try:
        my_emp = request.user.employee_get
    except Exception:
        my_emp = None

    pending_ids = [a.id for a in approvals if a.status == "pending"]
    active_id = pending_ids[0] if pending_ids else None
    my_active = next(
        (a for a in approvals if a.id == active_id and my_emp and a.approver_id == my_emp.id),
        None,
    )

    if request.method == "POST":
        action = request.POST.get("action")
        if my_active:
            if action == "esign":
                my_active.signature_image = request.POST.get("signature_data", "")
                my_active.status = "approved"
                my_active.acted_at = timezone.now()
                my_active.feedback = request.POST.get("feedback", "")
                my_active.save()
                remaining = [a for a in approvals if a.status == "pending" and a.id != my_active.id]
                if not remaining:
                    offer.status = "approved"
                    offer.save(update_fields=["status"])
                _msg.success(request, "Signed successfully.")
            elif action == "feedback":
                my_active.feedback = request.POST.get("feedback", "")
                my_active.status = "rejected"
                my_active.acted_at = timezone.now()
                my_active.save()
                offer.status = "rejected"
                offer.save(update_fields=["status"])
                _msg.warning(request, "Offer rejected.")
        return redirect("ui:offer-approval", offer_id=offer_id)

    from employee.models import Employee
    employees = Employee.objects.filter(is_active=True).order_by("employee_first_name")[:200]

    return render(request, "ui/offer_approval.html", {
        "offer": offer,
        "approvals": approvals,
        "my_active": my_active,
        "employees": employees,
    })


# ---------------------------------------------------------------------------
# Candidate Documents
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def candidate_documents(request, cand_id):
    from types import SimpleNamespace
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages as _msg
    from recruitment.models import Candidate as _Candidate

    candidate = get_object_or_404(_Candidate, id=cand_id)

    if request.method == "POST":
        action = request.POST.get("action", "upload")
        uploaded_file = request.FILES.get("file")
        doc_title = request.POST.get("document_type", "").strip()

        try:
            from recruitment.models import CandidateDocument as _CDoc
            if action == "upload" and uploaded_file and doc_title:
                _CDoc.objects.create(
                    candidate_id=candidate,
                    title=doc_title,
                    document=uploaded_file,
                )
                _msg.success(request, f'"{doc_title}" uploaded successfully.')
            elif action == "update":
                doc_id = request.POST.get("doc_id", "")
                if doc_id.isdigit():
                    doc = _CDoc.objects.filter(id=int(doc_id), candidate_id=candidate).first()
                    if doc and uploaded_file:
                        doc.document = uploaded_file
                        doc.save()
                        _msg.success(request, "Document updated.")
        except Exception as exc:
            _msg.error(request, f"Upload failed: {exc}")

        return redirect("ui:candidate-documents", cand_id=cand_id)

    # ── Fetch CandidateDocument records ──────────────────────────────────
    try:
        from recruitment.models import CandidateDocument as _CDoc
        db_docs = list(_CDoc.objects.filter(candidate_id=cand_id).order_by("-id"))
    except Exception:
        db_docs = []

    # ── Synthetic docs from careers-page uploads on the Candidate model ──
    # Career applicants store files directly on Candidate fields; surface
    # them here if no matching CandidateDocument record already exists.
    career_field_labels = [
        ("resume",                  "Resume / CV"),
        ("cover_letter",            "Cover Letter"),
        ("graduation_certificate",  "Graduation Certificate"),
        ("transcripts",             "Transcripts"),
    ]
    existing_titles = {d.title.lower() for d in db_docs}
    synthetic = []
    for field, label in career_field_labels:
        f = getattr(candidate, field, None)
        if f and f.name and label.lower() not in existing_titles:
            synthetic.append(SimpleNamespace(
                id=None,
                title=label,
                document=f,
                status="verified",
                created_at=candidate.created_at,
                updated_at=candidate.created_at,
                is_career_upload=True,
            ))

    documents = synthetic + db_docs
    all_verified = bool(documents) and all(
        getattr(d, "status", "") == "verified" for d in documents
    )

    return render(request, "ui/candidate_documents.html", {
        "candidate": candidate,
        "documents": documents,
        "all_verified": all_verified,
    })


# ---------------------------------------------------------------------------
# Candidate Pipeline
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def candidate_pipeline(request):
    return render(request, "ui/candidate_pipeline.html", {})


# ---------------------------------------------------------------------------
# Candidate Interview (candidate-centric view)
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def candidate_interview_view(request, cand_id):
    from django.shortcuts import get_object_or_404
    from recruitment.models import Candidate as _Candidate, InterviewSchedule as _IV

    candidate = get_object_or_404(_Candidate, id=cand_id)
    interviews = (
        _IV.objects.filter(candidate_id=candidate)
        .prefetch_related("employee_id")
        .order_by("-interview_date")
    )
    return render(request, "ui/candidate_interview.html", {
        "cand": candidate,
        "interviews": interviews,
    })


# ---------------------------------------------------------------------------
# Candidate Communication
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def candidate_communication(request, cand_id):
    from django.shortcuts import get_object_or_404
    from recruitment.models import Candidate as _Candidate

    candidate = get_object_or_404(_Candidate, id=cand_id)
    return render(request, "ui/candidate_communication.html", {
        "c": candidate,
        "communications": [],
    })


# ---------------------------------------------------------------------------
# Candidate Offer (candidate-centric offer view)
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def candidate_offer_view(request, cand_id):
    from django.shortcuts import get_object_or_404
    from recruitment.models import Candidate as _Candidate, OfferLetter as _Offer, OfferLetterApproval as _Approval

    candidate = get_object_or_404(_Candidate, id=cand_id)
    try:
        offer = _Offer.objects.prefetch_related("approvals__approver").get(candidate_id=candidate)
    except _Offer.DoesNotExist:
        offer = None
    approvals = []
    if offer:
        approvals = list(offer.approvals.select_related("approver").order_by("sequence"))
        first_pending_found = False
        for a in approvals:
            if a.status == "pending":
                if not first_pending_found:
                    a.display_status = "active"
                    first_pending_found = True
                else:
                    a.display_status = "waiting"
            else:
                a.display_status = a.status
    return render(request, "ui/candidate_offer.html", {
        "c": candidate,
        "offer": offer,
        "approvals": approvals,
    })


# ---------------------------------------------------------------------------
# Candidate Profile
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def candidate_profile_view(request, cand_id):
    from django.shortcuts import get_object_or_404
    from recruitment.models import Candidate as _Candidate, InterviewSchedule as _IV, CandidateScreeningProfile as _CSP

    candidate = get_object_or_404(_Candidate, id=cand_id)
    profile = _CSP.objects.filter(candidate=candidate).first()
    interviews = (
        _IV.objects.filter(candidate_id=candidate)
        .prefetch_related("employee_id")
        .order_by("-interview_date")
    )
    return render(request, "ui/candidate_profile.html", {
        "candidate": candidate,
        "profile": profile,
        "interviews": interviews,
        "documents": [],
    })


# ---------------------------------------------------------------------------
# Offer Letter Template management
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def offer_letter_template_view(request):
    from django.shortcuts import redirect
    from django.contrib import messages as _msg
    from recruitment.models import OfferLetterTemplate as _Template

    if request.method == "POST":
        tpl_id = request.POST.get("template_id", "")
        name = request.POST.get("name", "").strip()
        body = request.POST.get("body_html", "")
        is_active = request.POST.get("is_active", "1") == "1"
        if name:
            if tpl_id.isdigit():
                tpl = _Template.objects.filter(id=int(tpl_id)).first()
                if tpl:
                    tpl.name = name
                    tpl.body_html = body
                    tpl.is_active = is_active
                    tpl.save()
                    _msg.success(request, f'Template "{name}" updated.')
            else:
                _Template.objects.create(name=name, body_html=body, is_active=is_active)
                _msg.success(request, f'Template "{name}" created.')
        return redirect("ui:offer-letter-template")

    templates = _Template.objects.order_by("-id")
    active_template = templates.filter(is_active=True).first()
    return render(request, "ui/offer_letter_template.html", {
        "templates": templates,
        "active_template": active_template,
    })


# ---------------------------------------------------------------------------
# Proposal Approval (approver e-sign view)
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def proposal_approval_view(request, proposal_id):
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages as _msg
    from django.utils import timezone
    from recruitment.models_proposal import EmploymentProposal as _Proposal, ProposalApproval as _PA

    proposal = get_object_or_404(_Proposal.objects.select_related("candidate"), id=proposal_id)
    approvals = list(proposal.approvals.select_related("approver").order_by("sequence"))

    try:
        my_emp = request.user.employee_get
    except Exception:
        my_emp = None

    _SLA_HOURS = 48
    first_pending_found = False
    prev_acted_at = proposal.created_at
    for a in approvals:
        a.requested_at = prev_acted_at
        if a.status == "pending":
            if not first_pending_found:
                a.display_status = "active"
                first_pending_found = True
            else:
                a.display_status = "waiting"
        else:
            a.display_status = a.status
        if a.status == "approved" and a.acted_at:
            prev_acted_at = a.acted_at
        # SLA status
        if a.display_status == "approved":
            if a.requested_at and a.acted_at:
                _elapsed = (a.acted_at - a.requested_at).total_seconds() / 3600
                a.sla_status = "late" if _elapsed > _SLA_HOURS else "ok"
            else:
                a.sla_status = "ok"
        elif a.display_status == "active":
            _elapsed = (timezone.now() - a.requested_at).total_seconds() / 3600
            if _elapsed < _SLA_HOURS * 0.5:
                a.sla_status = "ok"
            elif _elapsed < _SLA_HOURS:
                a.sla_status = "warning"
            else:
                a.sla_status = "overdue"
        elif a.display_status == "rejected":
            a.sla_status = "rejected"
        else:
            a.sla_status = "waiting"

    pending_ids = [a.id for a in approvals if a.status == "pending"]
    active_id = pending_ids[0] if pending_ids else None
    my_approval = next(
        (a for a in approvals if a.id == active_id and my_emp and a.approver_id == my_emp.id),
        None,
    )

    if request.method == "POST":
        action = request.POST.get("action")
        if my_approval:
            if action == "esign":
                my_approval.signature_image = request.POST.get("signature_data", "")
                my_approval.status = "approved"
                my_approval.acted_at = timezone.now()
                my_approval.save()
                remaining = [a for a in approvals if a.status == "pending" and a.id != my_approval.id]
                if not remaining:
                    proposal.status = "approved"
                    proposal.save(update_fields=["status"])
                _msg.success(request, "Proposal signed successfully.")
            elif action == "feedback":
                my_approval.feedback = request.POST.get("feedback", "")
                my_approval.status = "rejected"
                my_approval.acted_at = timezone.now()
                my_approval.save()
                proposal.status = "rejected"
                proposal.save(update_fields=["status"])
                _msg.warning(request, "Proposal rejected.")
        return redirect("ui:proposal-approval", proposal_id=proposal_id)

    return render(request, "ui/proposal_approval.html", {
        "proposal": proposal,
        "approvals": approvals,
        "my_approval": my_approval,
        "my_active": my_approval,
        "active_id": active_id,
    })


# ---------------------------------------------------------------------------
# Offer Letter Approval (approver e-sign view)
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def offer_letter_approval_view(request, offer_id):
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages as _msg
    from django.utils import timezone
    from recruitment.models import OfferLetter as _Offer, OfferLetterApproval as _Approval

    offer = get_object_or_404(_Offer.objects.select_related("candidate_id"), id=offer_id)
    approvals = list(offer.approvals.select_related("approver").order_by("sequence"))

    try:
        my_emp = request.user.employee_get
    except Exception:
        my_emp = None

    first_pending_found = False
    for a in approvals:
        if a.status == "pending":
            if not first_pending_found:
                a.display_status = "active"
                first_pending_found = True
            else:
                a.display_status = "waiting"
        else:
            a.display_status = a.status

    pending_ids = [a.id for a in approvals if a.status == "pending"]
    active_id = pending_ids[0] if pending_ids else None
    my_approval = next(
        (a for a in approvals if a.id == active_id and my_emp and a.approver_id == my_emp.id),
        None,
    )
    signed_count = sum(1 for a in approvals if a.status == "approved")
    total_count = len(approvals) or 1

    if request.method == "POST":
        action = request.POST.get("action")
        if my_approval:
            if action == "esign":
                my_approval.signature_image = request.POST.get("signature_data", "")
                my_approval.status = "approved"
                my_approval.acted_at = timezone.now()
                my_approval.save()
                remaining = [a for a in approvals if a.status == "pending" and a.id != my_approval.id]
                if not remaining:
                    offer.status = "approved"
                    offer.save(update_fields=["status"])
                _msg.success(request, "Offer letter signed successfully.")
            elif action == "feedback":
                my_approval.feedback = request.POST.get("feedback", "")
                my_approval.status = "rejected"
                my_approval.acted_at = timezone.now()
                my_approval.save()
                offer.status = "rejected"
                offer.save(update_fields=["status"])
                _msg.warning(request, "Offer letter rejected.")
        return redirect("ui:offer-letter-approval", offer_id=offer_id)

    return render(request, "ui/offer_letter_approval.html", {
        "offer": offer,
        "approvals": approvals,
        "my_approval": my_approval,
        "my_active": my_approval,
        "active_id": active_id,
        "signed_count": signed_count,
        "total_count": total_count,
    })


# ---------------------------------------------------------------------------
# Employment Proposal Form (Job Requisition) — Permanent & Contractual S-O-M
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def employment_proposal_form(request):
    """
    Raise an Employment Proposal (ONEIC EPF) directly from the Job Requisition
    section.  Supports two templates:
      • permanent    — HR&A/EPF/V3  — 7-step chain
      • contractual  — HR&A/EPF-S/V4 (S-O-M Grade) — 3-step chain
    """
    import datetime
    from django.contrib import messages as _msg
    from django.shortcuts import redirect
    from recruitment.models_proposal import (
        EmploymentProposal as _Proposal,
        PERMANENT_CHAIN, CONTRACTUAL_CHAIN, ROLE_LABELS,
        ProposalRoleAssignment,
    )
    from recruitment.models import Candidate as _Candidate
    from base.models import Department
    from employee.models import Employee

    TEMPLATE_CHOICES = {
        "permanent":   "Permanent (Non-Contractual) — HR&A/EPF/V3",
        "contractual": "Contractual — S-O-M Grade — HR&A/EPF-S/V4",
    }

    def _date(v):
        try:
            return datetime.date.fromisoformat(v) if v else None
        except ValueError:
            return None

    def _num(v):
        try:
            return float(v) if v not in (None, "") else None
        except (TypeError, ValueError):
            return None

    # ── Resolve approval chains for preview ──────────────────────────────────
    assignments = {a.role_key: str(a.employee)
                   for a in ProposalRoleAssignment.objects.select_related("employee")}

    def _chain_display(role_keys):
        return [
            {"role": ROLE_LABELS.get(rk, rk), "name": assignments.get(rk, "Unassigned")}
            for rk in role_keys
        ]

    permanent_chain   = _chain_display(PERMANENT_CHAIN)
    contractual_chain = _chain_display(CONTRACTUAL_CHAIN)

    # ── POST — create proposal and route ─────────────────────────────────────
    if request.method == "POST":
        tpl = request.POST.get("proposal_template", "permanent")
        if tpl not in TEMPLATE_CHOICES:
            tpl = "permanent"

        # Resolve or create candidate
        candidate_id = request.POST.get("candidate_id", "").strip()
        applicant_name = (request.POST.get("applicant_name") or "").strip()
        candidate = None

        if candidate_id:
            candidate = _Candidate.objects.filter(id=candidate_id).first()

        if not candidate and applicant_name:
            from base.models import Company
            emp = getattr(request.user, "employee_get", None)
            company = emp.get_company() if emp else Company.objects.first()
            placeholder_email = f"ep_{applicant_name.lower().replace(' ', '_')}@proposal.local"
            candidate = _Candidate.objects.filter(email=placeholder_email).first()
            if not candidate:
                candidate = _Candidate.objects.create(
                    name=applicant_name,
                    email=placeholder_email,
                    company_id=company,
                    source="software",
                )

        if not candidate:
            _msg.error(request, "Please select a candidate or enter the applicant's name.")
            return redirect("ui:employment-proposal")

        # Build salary_columns_json from HRC/CEO columns
        salary_rows = ["basic_salary", "hra_allowance", "transport_allowance",
                       "addl_resp_allowance", "overtime_allowance",
                       "food_allowance", "lsa_allowance"]
        salary_columns = {}
        for row in salary_rows:
            hrc = request.POST.get(f"hrc_{row}", "")
            ceo = request.POST.get(f"ceo_{row}", "")
            rmk = request.POST.get(f"rmk_{row}", "")
            if hrc or ceo or rmk:
                salary_columns[row] = {"hrc": hrc, "ceo": ceo, "remarks": rmk}

        try:
            proposal = _Proposal.objects.create(
                template_type=tpl,
                status=_Proposal.STATUS_DRAFT,
                candidate=candidate,
                # General
                post_applied_for=(request.POST.get("post_applied_for") or "").strip(),
                grade_group=(request.POST.get("grade_group") or "").strip(),
                division_department=(request.POST.get("division_department") or "").strip(),
                post_location=(request.POST.get("post_location") or "").strip(),
                contractual=(tpl == "contractual"),
                contract_name=(request.POST.get("contract_name") or "").strip(),
                contract_period_from=_date(request.POST.get("contract_period_from")),
                contract_period_to=_date(request.POST.get("contract_period_to")),
                job_no=(request.POST.get("job_no") or "").strip(),
                reporting_to=(request.POST.get("reporting_to") or "").strip(),
                reporting_staff_no=(request.POST.get("reporting_staff_no") or "").strip(),
                gsm_cpn_no=(request.POST.get("gsm_cpn_no") or "").strip(),
                # Brief
                is_new_appointment=(request.POST.get("is_new_appointment") == "yes"),
                replacement_staff_no=(request.POST.get("replacement_staff_no") or "").strip(),
                candidate_referred=(request.POST.get("candidate_referred") or "").strip(),
                referral_staff_number=(request.POST.get("referral_staff_number") or "").strip(),
                consultancy_reg=(request.POST.get("consultancy_reg") or "").strip(),
                consultancy_other=(request.POST.get("consultancy_other") or "").strip(),
                employment_contract_type=(request.POST.get("employment_contract_type") or "").strip(),
                employment_contract_months=int(request.POST.get("employment_contract_months") or 0) or None,
                has_relative_in_company=(request.POST.get("has_relative") == "yes"),
                relative_name=(request.POST.get("relative_name") or "").strip(),
                relative_staff_no=(request.POST.get("relative_staff_no") or "").strip(),
                relative_location=(request.POST.get("relative_location") or "").strip(),
                # Resume summary
                application_date=_date(request.POST.get("application_date")),
                interview_date=_date(request.POST.get("interview_date")),
                applicant_name=applicant_name or (candidate.name or ""),
                nationality=(request.POST.get("nationality") or "").strip(),
                present_employer=(request.POST.get("present_employer") or "").strip(),
                local_transfer=(request.POST.get("local_transfer") == "yes"),
                marital_status=(request.POST.get("marital_status") or "").strip(),
                dob=_date(request.POST.get("dob")),
                place_of_birth=(request.POST.get("place_of_birth") or "").strip(),
                qualification_academic=(request.POST.get("qualification_academic") or "").strip(),
                qualification_professional=(request.POST.get("qualification_professional") or "").strip(),
                experience_local_years=_num(request.POST.get("experience_local_years")),
                experience_overseas_years=_num(request.POST.get("experience_overseas_years")),
                lang_arabic=("lang_arabic" in request.POST),
                lang_english=("lang_english" in request.POST),
                lang_others=(request.POST.get("lang_others") or "").strip(),
                driving_license=(request.POST.get("driving_license") or "none"),
                # Salary
                salary_budgeted=(request.POST.get("salary_budgeted") or "budgeted"),
                basic_salary=_num(request.POST.get("basic_salary")),
                hra_allowance=_num(request.POST.get("hra_allowance")),
                transport_allowance=_num(request.POST.get("transport_allowance")),
                addl_resp_allowance=_num(request.POST.get("addl_resp_allowance")),
                overtime_allowance=_num(request.POST.get("overtime_allowance")),
                food_allowance=_num(request.POST.get("food_allowance")),
                lsa_allowance=_num(request.POST.get("lsa_allowance")),
                lsa_tier=(request.POST.get("lsa_tier") or ""),
                gross_salary=_num(request.POST.get("gross_salary")),
                salary_columns_json=salary_columns,
                # Notes
                air_passage_from=(request.POST.get("air_passage_from") or "").strip(),
                air_passage_to=(request.POST.get("air_passage_to") or "MUSCAT").strip(),
                air_passage_months=int(request.POST.get("air_passage_months") or 0) or None,
                family_status=(request.POST.get("family_status") or "").strip(),
                medical_clause=("medical_clause" in request.POST),
                salary_increase_clause=(request.POST.get("salary_increase_clause") or "").strip(),
                hod_comments=(request.POST.get("hod_comments") or "").strip(),
                remarks=(request.POST.get("remarks") or "").strip(),
                created_by=request.user,
            )
            try:
                from recruitment.approvals.proposal_engine import route_proposal
                route_proposal(proposal)
            except Exception:
                pass
            _msg.success(request, f"Employment Proposal {proposal.proposal_no} submitted for approval.")
            return redirect("ui:proposal-detail", proposal_id=proposal.id)
        except Exception as exc:
            _msg.error(request, f"Failed to create proposal: {exc}")
            return redirect("ui:employment-proposal")

    # ── GET ───────────────────────────────────────────────────────────────────
    chosen_template = request.GET.get("template", "")
    if chosen_template not in TEMPLATE_CHOICES:
        chosen_template = ""

    prefill_candidate_id = request.GET.get("candidate_id", "").strip()
    prefill_interview_id = request.GET.get("interview_id", "").strip()

    # Build a prefill dict from the candidate + optional interview record
    prefill = {}
    if prefill_candidate_id:
        cand = (
            _Candidate.objects
            .select_related("recruitment_id", "recruitment_id__job_position_id__department_id")
            .filter(id=prefill_candidate_id)
            .first()
        )
        if cand:
            # Try to get AI-extracted screening profile
            screening = None
            try:
                screening = cand.screening_profile
            except Exception:
                pass

            # Interview date from the linked interview (if passed)
            iv_date_str = ""
            if prefill_interview_id:
                from recruitment.models import InterviewSchedule as _IVSched
                iv_obj = _IVSched.objects.filter(id=prefill_interview_id).first()
                if iv_obj and iv_obj.interview_date:
                    iv_date_str = iv_obj.interview_date.strftime("%Y-%m-%d")

            nationality = ""
            if screening and getattr(screening, "extracted_nationality", ""):
                nationality = screening.extracted_nationality
            elif cand.country:
                nationality = cand.country

            dob_str = ""
            if cand.dob:
                dob_str = cand.dob.strftime("%Y-%m-%d")
            elif screening and getattr(screening, "extracted_dob", None):
                dob_str = screening.extracted_dob.strftime("%Y-%m-%d")

            # Safely resolve department through the FK chain
            _dept_name = ""
            try:
                _rec = cand.recruitment_id
                if _rec:
                    _jp = getattr(_rec, "job_position_id", None)
                    if _jp:
                        _dept_obj = getattr(_jp, "department_id", None)
                        if _dept_obj:
                            _dept_name = str(getattr(_dept_obj, "department", "") or "")
            except Exception:
                _dept_name = ""

            prefill = {
                "candidate_id":             cand.id,
                "applicant_name":           cand.name or "",
                "nationality":              nationality,
                "dob":                      dob_str,
                "marital_status":           getattr(screening, "extracted_marital_status", "") or "",
                "post_applied_for":         cand.recruitment_id.title if cand.recruitment_id else "",
                "division_department":      _dept_name,
                "interview_date":           iv_date_str,
                "qualification_academic":   getattr(screening, "extracted_qualification_academic", "") or "",
                "qualification_professional": getattr(screening, "extracted_qualification_professional", "") or "",
                "experience_local_years":   str(getattr(screening, "extracted_experience_local_years", "") or ""),
                "experience_overseas_years": str(getattr(screening, "extracted_experience_overseas_years", "") or ""),
            }

    candidates = (
        _Candidate.objects.filter(is_active=True, canceled=False, hired=False)
        .order_by("name")[:300]
    )

    return render(request, "ui/employment_proposal_form.html", {
        "chosen_template":       chosen_template,
        "chosen_template_label": TEMPLATE_CHOICES.get(chosen_template, ""),
        "permanent_chain":       permanent_chain,
        "contractual_chain":     contractual_chain,
        "candidates":            candidates,
        "template_choices":      TEMPLATE_CHOICES,
        "prefill":               prefill,
        "prefill_candidate_id":  prefill_candidate_id,
        "prefill_interview_id":  prefill_interview_id,
    })


# ---------------------------------------------------------------------------
# Offer Letter Document Downloads
# ---------------------------------------------------------------------------

@login_required(login_url="/ui/login/")
def offer_download_letter(request, offer_id):
    """Download the offer letter as a PDF."""
    from django.shortcuts import get_object_or_404
    from django.http import HttpResponse
    from recruitment.models import OfferLetter as _Offer
    from io import BytesIO

    offer = get_object_or_404(_Offer.objects.select_related("candidate_id"), id=offer_id)
    html_content = offer.generated_letter or f"<h2>Offer Letter</h2><p>Offer for {offer.candidate_id.name} — {offer.position}</p>"

    try:
        from xhtml2pdf import pisa
        buf = BytesIO()
        pisa.CreatePDF(html_content, dest=buf)
        buf.seek(0)
        filename = f"Offer-letter-{offer.candidate_id.name or offer.id}.pdf"
        response = HttpResponse(buf.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
    except Exception:
        response = HttpResponse(html_content, content_type="text/html")
        response["Content-Disposition"] = f'attachment; filename="Offer-letter.html"'
        return response


def _dummy_pdf(title, lines):
    """Generate a minimal placeholder PDF using reportlab."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 18)
    c.drawString(60, height - 80, title)
    c.setFont("Helvetica", 11)
    y = height - 120
    for line in lines:
        c.drawString(60, y, line)
        y -= 20
    c.save()
    buf.seek(0)
    return buf.read()


@login_required(login_url="/ui/login/")
def offer_download_ctc(request, offer_id):
    from django.shortcuts import get_object_or_404
    from django.http import HttpResponse
    from recruitment.models import OfferLetter as _Offer
    offer = get_object_or_404(_Offer, id=offer_id)
    lines = [
        f"Candidate : {offer.candidate_id.name}",
        f"Position  : {offer.position or '—'}",
        f"Basic Salary  : {offer.currency} {offer.basic_salary or '—'}",
        f"Gross Salary  : {offer.currency} {offer.gross_salary or '—'}",
        "",
        "This document is a summary of the compensation package.",
        "Final figures are subject to HR approval.",
    ]
    pdf = _dummy_pdf("CTC Breakup", lines)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="CTC-breakup.pdf"'
    return response


@login_required(login_url="/ui/login/")
def offer_download_policy(request, offer_id):
    from django.shortcuts import get_object_or_404
    from django.http import HttpResponse
    from recruitment.models import OfferLetter as _Offer
    offer = get_object_or_404(_Offer, id=offer_id)
    lines = [
        "Company Policy Document",
        "",
        "1. Code of Conduct",
        "   All employees are expected to maintain professional conduct at all times.",
        "",
        "2. Leave Policy",
        "   Annual leave entitlement is as per the employment contract.",
        "",
        "3. Confidentiality",
        "   Employees must not disclose confidential company information.",
        "",
        "4. Dress Code",
        "   Smart business attire is required unless otherwise specified.",
        "",
        "Please acknowledge receipt of this document by signing your offer letter.",
    ]
    pdf = _dummy_pdf("Company Policy", lines)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="company-policy.pdf"'
    return response


@login_required(login_url="/ui/login/")
def offer_download_terms(request, offer_id):
    from django.shortcuts import get_object_or_404
    from django.http import HttpResponse
    from recruitment.models import OfferLetter as _Offer
    offer = get_object_or_404(_Offer, id=offer_id)
    lines = [
        f"Candidate : {offer.candidate_id.name}",
        f"Position  : {offer.position or '—'}",
        f"Joining Date : {offer.joining_date or '—'}",
        f"Probation Period : {offer.probation_period} months",
        "",
        "Terms & Conditions",
        "",
        "1. This offer is conditional upon satisfactory background verification.",
        "2. The probation period is as stated above.",
        "3. Either party may terminate employment with notice as per labour law.",
        "4. Compensation is subject to applicable tax deductions.",
        "5. This offer lapses if not accepted within 7 days of issue.",
    ]
    if offer.terms_conditions:
        lines += ["", "Additional Terms:", offer.terms_conditions[:300]]
    pdf = _dummy_pdf("Terms & Conditions", lines)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="terms-condition.pdf"'
    return response
