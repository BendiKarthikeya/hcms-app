"""
Views for PIP (Performance Improvement Plan) Management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from datetime import date

from pms.models_pip import (
    PerformanceImprovementPlan,
    PIPTemplate,
)
from base.forms_new_features.forms_new_features import (
    PerformanceImprovementPlanForm,
    PIPTemplateForm,
    PIPMilestoneFormSet,
    PIPReviewForm,
    PIPExtensionForm,
)
from base.models import Company


# ============= PIP TEMPLATE VIEWS =============


@login_required
def pip_template_list(request):
    """List all PIP templates"""
    company = Company.objects.first()
    templates = PIPTemplate.objects.filter(company=company)

    context = {
        "templates": templates,
        "page_title": _("PIP Templates"),
    }
    return render(request, "pms/pip/template_list.html", context)


@login_required
def pip_template_create(request):
    """Create a new PIP template"""
    company = Company.objects.first()

    if request.method == "POST":
        form = PIPTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.company = company
            template.save()
            messages.success(request, _("PIP Template created successfully"))
            return redirect("pip-template-list")
    else:
        form = PIPTemplateForm()

    context = {
        "form": form,
        "page_title": _("Create PIP Template"),
    }
    return render(request, "pms/pip/template_form.html", context)


@login_required
def pip_template_update(request, pk):
    """Update a PIP template"""
    template = get_object_or_404(PIPTemplate, pk=pk)

    if request.method == "POST":
        form = PIPTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, _("PIP Template updated successfully"))
            return redirect("pip-template-list")
    else:
        form = PIPTemplateForm(instance=template)

    context = {
        "form": form,
        "object": template,
        "page_title": _("Edit PIP Template"),
    }
    return render(request, "pms/pip/template_form.html", context)


# ============= PIP MANAGEMENT VIEWS =============


@login_required
def pip_list(request):
    """List Performance Improvement Plans"""
    company = Company.objects.first()
    pips = PerformanceImprovementPlan.objects.filter(company=company).select_related(
        "employee"
    )

    # Filters
    status = request.GET.get("status")
    employee_id = request.GET.get("employee")
    search = request.GET.get("search")

    if status:
        pips = pips.filter(status=status)
    if employee_id:
        pips = pips.filter(employee_id=employee_id)
    if search:
        pips = pips.filter(
            Q(employee__first_name__icontains=search)
            | Q(employee__last_name__icontains=search)
            | Q(title__icontains=search)
        )

    context = {
        "pips": pips,
        "page_title": _("Performance Improvement Plans"),
        "statuses": PerformanceImprovementPlan.STATUS_CHOICES,
    }
    return render(request, "pms/pip/pip_list.html", context)


@login_required
def pip_create(request):
    """Create a new Performance Improvement Plan"""
    company = Company.objects.first()

    if request.method == "POST":
        form = PerformanceImprovementPlanForm(request.POST)
        formset = PIPMilestoneFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            pip = form.save(commit=False)
            pip.company = company
            pip.initiated_by = request.user.employee_get
            pip.save()
            formset.instance = pip
            formset.save()

            messages.success(
                request, _("Performance Improvement Plan created successfully")
            )
            return redirect("pip-detail", pk=pip.pk)
    else:
        form = PerformanceImprovementPlanForm()
        formset = PIPMilestoneFormSet()

    context = {
        "form": form,
        "formset": formset,
        "page_title": _("Create Performance Improvement Plan"),
    }
    return render(request, "pms/pip/pip_form.html", context)


@login_required
def pip_detail(request, pk):
    """View PIP details"""
    pip = get_object_or_404(PerformanceImprovementPlan, pk=pk)
    milestones = pip.milestones.all().order_by("order")
    reviews = pip.reviews.all().order_by("-review_date")

    context = {
        "pip": pip,
        "milestones": milestones,
        "reviews": reviews,
        "page_title": f"{pip.employee.get_name()} - PIP",
    }
    return render(request, "pms/pip/pip_detail.html", context)


@login_required
def pip_update(request, pk):
    """Update a PIP"""
    pip = get_object_or_404(PerformanceImprovementPlan, pk=pk)

    # Only allow updates if in draft status
    if pip.status != "draft":
        messages.error(request, _("Can only edit PIP in draft status"))
        return redirect("pip-detail", pk=pk)

    if request.method == "POST":
        form = PerformanceImprovementPlanForm(request.POST, instance=pip)
        if form.is_valid():
            form.save()
            messages.success(request, _("PIP updated successfully"))
            return redirect("pip-detail", pk=pk)
    else:
        form = PerformanceImprovementPlanForm(instance=pip)

    context = {
        "form": form,
        "pip": pip,
        "page_title": _("Edit Performance Improvement Plan"),
    }
    return render(request, "pms/pip/pip_form.html", context)


@login_required
def pip_approve(request, pk):
    """Approve a PIP"""
    pip = get_object_or_404(PerformanceImprovementPlan, pk=pk)

    if request.method == "POST":
        pip.status = "active"
        pip.approved_by = request.user.employee_get
        pip.approved_date = timezone.now()
        pip.save()

        messages.success(request, _("PIP approved and activated"))
        return redirect("pip-detail", pk=pk)

    context = {
        "pip": pip,
        "page_title": _("Approve PIP"),
    }
    return render(request, "pms/pip/pip_approve.html", context)


@login_required
def pip_review_create(request, pk):
    """Conduct a PIP review"""
    pip = get_object_or_404(PerformanceImprovementPlan, pk=pk)

    if pip.status != "active":
        messages.error(request, _("Can only review active PIPs"))
        return redirect("pip-detail", pk=pk)

    if request.method == "POST":
        form = PIPReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.pip = pip
            review.reviewed_by = request.user.employee_get
            review.save()

            messages.success(request, _("Review recorded successfully"))
            return redirect("pip-detail", pk=pk)
    else:
        form = PIPReviewForm()

    context = {
        "form": form,
        "pip": pip,
        "page_title": _("Record PIP Review"),
    }
    return render(request, "pms/pip/pip_review_form.html", context)


@login_required
def pip_extension_request(request, pk):
    """Request PIP extension"""
    pip = get_object_or_404(PerformanceImprovementPlan, pk=pk)

    if pip.extension:
        messages.error(request, _("Extension already requested"))
        return redirect("pip-detail", pk=pk)

    if request.method == "POST":
        form = PIPExtensionForm(request.POST)
        if form.is_valid():
            extension = form.save(commit=False)
            extension.pip = pip
            extension.current_end_date = pip.end_date
            extension.requested_by = request.user.employee_get
            extension.save()

            messages.success(request, _("Extension request submitted"))
            return redirect("pip-detail", pk=pk)
    else:
        form = PIPExtensionForm()

    context = {
        "form": form,
        "pip": pip,
        "page_title": _("Request PIP Extension"),
    }
    return render(request, "pms/pip/pip_extension_form.html", context)


@login_required
def pip_complete(request, pk):
    """Complete/Close a PIP"""
    pip = get_object_or_404(PerformanceImprovementPlan, pk=pk)

    if request.method == "POST":
        outcome = request.POST.get("outcome", "")
        completion_status = request.POST.get("completion_status", "")

        pip.status = (
            "successful" if request.POST.get("was_successful") else "unsuccessful"
        )
        pip.outcome = outcome
        pip.completion_status = completion_status
        pip.completion_date = timezone.now()
        pip.save()

        messages.success(request, _("PIP completed"))
        return redirect("pip-detail", pk=pk)

    context = {
        "pip": pip,
        "page_title": _("Complete Performance Improvement Plan"),
    }
    return render(request, "pms/pip/pip_complete.html", context)


# API VIEWS FOR DASHBOARD

from django.utils import timezone


@login_required
def pip_dashboard(request):
    """PIP Dashboard with statistics"""
    company = Company.objects.first()

    stats = {
        "total_pips": PerformanceImprovementPlan.objects.filter(
            company=company
        ).count(),
        "active_pips": PerformanceImprovementPlan.objects.filter(
            company=company, status="active"
        ).count(),
        "completed_successful": PerformanceImprovementPlan.objects.filter(
            company=company, status="successful"
        ).count(),
        "overdue_pips": PerformanceImprovementPlan.objects.filter(
            company=company, status="active", end_date__lt=date.today()
        ).count(),
    }

    recent_pips = PerformanceImprovementPlan.objects.filter(company=company).order_by(
        "-created_at"
    )[:10]

    context = {
        "stats": stats,
        "recent_pips": recent_pips,
        "page_title": _("PIP Dashboard"),
    }
    return render(request, "pms/pip/pip_dashboard.html", context)
