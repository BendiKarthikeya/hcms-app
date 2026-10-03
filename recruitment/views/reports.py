"""
recruitment/views/reports.py — Phase 7: dashboards and CSV reports.
Includes: Omanization %, hiring cycle time, monthly stats, source effectiveness.
"""

import csv
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.utils import timezone

from fits.decorators import login_required
from recruitment.decorators import manager_can_enter
from recruitment.models import Candidate, ManpowerRequest, Recruitment


class _Echo:
    def write(self, value):
        return value


@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def recruitment_reports(request):
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # ── KPIs ─────────────────────────────────────────────────────────
    open_vac = Recruitment.objects.filter(closed=False).count()
    total_candidates = Candidate.objects.count()
    monthly_hires = Candidate.objects.filter(
        created_at__gte=month_start
    ).count()

    omani_count = Candidate.objects.filter(country__iexact="OM").count()
    omanization_pct = round((omani_count / total_candidates * 100), 1) if total_candidates else 0

    # ── Hiring cycle time (days from created_at to joining_date) ─────
    avg_cycle_days = 0
    try:
        hired_with_dates = Candidate.objects.filter(
            hired=True, joining_date__isnull=False, created_at__isnull=False
        )
        if hired_with_dates.exists():
            days_list = [
                (c.joining_date - c.created_at.date()).days
                for c in hired_with_dates
                if c.joining_date and c.created_at
            ]
            if days_list:
                avg_cycle_days = round(sum(days_list) / len(days_list), 1)
    except Exception:
        avg_cycle_days = 0

    # ── Monthly candidates added (last 6 months) ─────────────────────
    # Always show all 6 months — fill zeros for months with no candidates
    six_months_ago = now - timedelta(days=180)
    monthly_data = (
        Candidate.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    # Build a dict of month_label → count from real data
    real_counts = {}
    for m in monthly_data:
        if m["month"]:
            label = m["month"].strftime("%b %Y")
            real_counts[label] = m["count"]

    # Build full 6-month series using proper month arithmetic
    chart_labels = []
    chart_values = []
    year, month = now.year, now.month
    months = []
    for i in range(5, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))
    for y, m in months:
        from datetime import date
        label = date(y, m, 1).strftime("%b %Y")
        chart_labels.append(label)
        chart_values.append(real_counts.get(label, 0))

    # ── Source effectiveness ──────────────────────────────────────────
    sources = (
        Candidate.objects.values("source")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # ── Candidate pipeline funnel ─────────────────────────────────────
    pipeline_stages = (
        Candidate.objects.values("stage_id__stage", "stage_id__stage_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # ── Manpower request stats ────────────────────────────────────────
    mr_all = ManpowerRequest.objects.all()
    mr_stats = {
        "total": mr_all.count(),
        "draft": mr_all.filter(status="draft").count(),
        "pending": mr_all.filter(status__in=["submitted", "under_approval"]).count(),
        "approved": mr_all.filter(status="approved").count(),
        "sourcing": mr_all.filter(status="sourcing").count(),
        "interviewing": mr_all.filter(status="interviewing").count(),
        "offer": mr_all.filter(status="offer").count(),
        "joined": mr_all.filter(status="joined").count(),
        "closed": mr_all.filter(status="closed").count(),
        "rejected": mr_all.filter(status="rejected").count(),
    }

    # ── Candidates joining soon ───────────────────────────────────────
    joining_soon = Candidate.objects.filter(
        joining_date__gte=now.date(),
        joining_date__lte=(now + timedelta(days=30)).date(),
    ).select_related("job_position_id")

    import json

    in_pipeline = Candidate.objects.filter(hired=False, canceled=False).count()
    joining_soon_count = joining_soon.count()

    kpi_cards = [
        ("Open Vacancies", open_vac, f"{mr_stats['approved']} approved requests"),
        ("Total Candidates", total_candidates, f"{in_pipeline} in pipeline"),
        ("New This Month", monthly_hires, "candidates added"),
        ("Joining Soon (30d)", joining_soon_count, "candidates with joining date set"),
        ("Omanization %", f"{omanization_pct}%", f"{omani_count} Omani of {total_candidates}"),
        ("Avg. Hire Cycle", f"{avg_cycle_days}d", "days from apply to join"),
    ]

    return render(request, "recruitment/reports/dashboard.html", {
        "open_vac": open_vac,
        "monthly_hires": monthly_hires,
        "omanization_pct": omanization_pct,
        "omani_count": omani_count,
        "total_candidates": total_candidates,
        "in_pipeline": in_pipeline,
        "sources": sources,
        "mr_stats": mr_stats,
        "mr_stat_items": mr_stats.items(),
        "avg_cycle_days": avg_cycle_days,
        "chart_labels": json.dumps(chart_labels),
        "chart_values": json.dumps(chart_values),
        "pipeline_stages": pipeline_stages,
        "kpi_cards": kpi_cards,
        "joining_soon": joining_soon,
    })


@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def export_candidates_csv(request):
    rows = Candidate.objects.values_list(
        "id", "name", "email", "mobile", "country", "source",
        "experience_years", "notice_period_days", "stage_id__stage",
        "hired", "joining_date",
    )
    header = ["ID", "Name", "Email", "Mobile", "Country", "Source",
              "Experience Yrs", "Notice Period Days", "Stage", "Hired", "Joining Date"]

    def gen():
        yield header
        for row in rows:
            yield [str(v) if v is not None else "" for v in row]

    pseudo_buf = _Echo()
    writer = csv.writer(pseudo_buf)
    resp = StreamingHttpResponse(
        (writer.writerow(r) for r in gen()), content_type="text/csv"
    )
    resp["Content-Disposition"] = 'attachment; filename="candidates.csv"'
    return resp


@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def export_manpower_csv(request):
    rows = ManpowerRequest.objects.values_list(
        "requisition_no", "department__department", "job_position__job_position",
        "grade", "positions_count", "employment_type", "nationality_preference",
        "status", "requested_on",
    )
    header = ["Req No", "Department", "Job Position", "Grade", "Positions",
              "Employment Type", "Nationality", "Status", "Requested On"]

    def gen():
        yield header
        for row in rows:
            yield [str(v) if v is not None else "" for v in row]

    pseudo_buf = _Echo()
    writer = csv.writer(pseudo_buf)
    resp = StreamingHttpResponse(
        (writer.writerow(r) for r in gen()), content_type="text/csv"
    )
    resp["Content-Disposition"] = 'attachment; filename="manpower_requests.csv"'
    return resp
