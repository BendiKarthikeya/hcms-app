from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def workforce_planning(request):
    return render(request, "report/workforce_planning.html")


@login_required
def diversity_analytics(request):
    return render(request, "report/diversity_analytics.html")


@login_required
def hr_analytics_dashboard(request):
    return render(request, "report/hr_analytics_dashboard.html")
