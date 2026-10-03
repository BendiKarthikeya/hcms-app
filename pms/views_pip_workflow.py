"""
pms/views_pip_workflow.py

Views for Performance Improvement Plan Workflow
Handles traditional PIP workflow CRUD and milestone tracking
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone

from .models_pip_workflow import (
    PerformanceImprovementPlanWorkflow,
    PIPMilestone,
    PIPReview,
    PIPFeedback,
)
from pms.forms import *


class PIPWorkflowListView(LoginRequiredMixin, ListView):
    """List all PIP workflows"""

    model = PerformanceImprovementPlanWorkflow
    template_name = "pms/pip_workflow_list.html"
    context_object_name = "pips"
    paginate_by = 20

    def get_queryset(self):
        """Filter PIP workflows by company"""
        queryset = PerformanceImprovementPlanWorkflow.objects.all()

        # Filter by user's company if not HR/Admin
        if not self.request.user.is_superuser:
            try:
                company_id = self.request.session.get("selected_company")
                if company_id and company_id != "all":
                    queryset = queryset.filter(company_id=company_id)
            except:
                pass

        # Filter by status if provided
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset.select_related("employee", "manager", "hr_manager")


class PIPWorkflowDetailView(LoginRequiredMixin, DetailView):
    """View detailed PIP workflow with milestones and reviews"""

    model = PerformanceImprovementPlanWorkflow
    template_name = "pms/pip_workflow_detail.html"
    context_object_name = "pip"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pip = self.get_object()

        context["milestones"] = pip.milestones.all()
        context["reviews"] = pip.reviews.all()
        context["feedback"] = pip.feedback.all()
        context["elapsed_days"] = (timezone.now().date() - pip.start_date).days

        return context


class PIPWorkflowCreateView(LoginRequiredMixin, CreateView):
    """Create new PIP workflow"""

    model = PerformanceImprovementPlanWorkflow
    template_name = "pms/pip_workflow_form.html"
    fields = [
        "employee",
        "title",
        "description",
        "objectives",
        "manager",
        "hr_manager",
    ]
    success_url = reverse_lazy("pip-workflow-list")

    def form_valid(self, form):
        """Set current user as creator"""
        form.instance.created_by = self.request.user.employee_get
        try:
            form.instance.company_id = self.request.session.get("selected_company")
        except:
            pass
        return super().form_valid(form)


class PIPWorkflowUpdateView(LoginRequiredMixin, UpdateView):
    """Update PIP workflow details"""

    model = PerformanceImprovementPlanWorkflow
    template_name = "pms/pip_workflow_form.html"
    fields = [
        "title",
        "description",
        "objectives",
        "manager",
        "hr_manager",
        "status",
        "outcome",
    ]
    success_url = reverse_lazy("pip-workflow-list")


@login_required
def activate_pip_workflow(request, pk):
    """Activate a draft PIP"""
    pip = get_object_or_404(PerformanceImprovementPlanWorkflow, pk=pk)

    if request.method == "POST" and pip.status == "draft":
        pip.activate()
        return redirect("pip-workflow-detail", pk=pk)

    return redirect("pip-workflow-detail", pk=pk)


@login_required
def record_milestone(request, pip_id):
    """Record milestone completion"""
    pip = get_object_or_404(PerformanceImprovementPlanWorkflow, pk=pip_id)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        target_date = request.POST.get("target_date")
        status = request.POST.get("status", "pending")

        milestone = PIPMilestone.objects.create(
            pip=pip,
            title=title,
            description=description,
            target_date=target_date,
            status=status,
        )

        return JsonResponse({"status": "success", "milestone_id": milestone.id})

    return JsonResponse({"status": "error"}, status=400)


@login_required
def record_pip_review(request, pip_id):
    """Record 30/60/90 day review"""
    pip = get_object_or_404(PerformanceImprovementPlanWorkflow, pk=pip_id)

    if request.method == "POST":
        review_type = request.POST.get("review_type")
        employee_progress = request.POST.get("employee_progress")
        manager_feedback = request.POST.get("manager_feedback")
        progress_percentage = request.POST.get("progress_percentage", 0)
        is_on_track = request.POST.get("is_on_track") == "true"

        review = PIPReview.objects.create(
            pip=pip,
            review_type=review_type,
            employee_progress_note=employee_progress,
            manager_feedback=manager_feedback,
            progress_percentage=int(progress_percentage),
            is_on_track=is_on_track,
            reviewed_by=request.user.employee_get,
        )

        # Update PIP status
        pip.status = "review"
        pip.save()

        return JsonResponse({"status": "success", "review_id": review.id})

    return JsonResponse({"status": "error"}, status=400)


@login_required
def complete_pip_workflow(request, pip_id):
    """Complete PIP with final outcome"""
    pip = get_object_or_404(PerformanceImprovementPlanWorkflow, pk=pip_id)

    if request.method == "POST":
        outcome = request.POST.get("outcome")
        notes = request.POST.get("notes")

        if outcome in ["success", "unsuccessful", "extended"]:
            pip.complete_pip(outcome)

            if outcome == "extended":
                pip.is_extended = True
                pip.extension_reason = notes
                pip.save()

            return redirect("pip-workflow-detail", pk=pip.id)

    return redirect("pip-workflow-detail", pk=pip.id)


@login_required
def add_pip_feedback(request, pip_id):
    """Add weekly/periodic feedback"""
    pip = get_object_or_404(PerformanceImprovementPlanWorkflow, pk=pip_id)

    if request.method == "POST":
        feedback_text = request.POST.get("feedback")
        is_positive = request.POST.get("is_positive") == "true"

        PIPFeedback.objects.create(
            pip=pip,
            feedback_text=feedback_text,
            feedback_by=request.user.employee_get,
            is_positive=is_positive,
        )

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error"}, status=400)


@login_required
def pip_dashboard(request):
    """PIP dashboard with statistics"""
    context = {}

    try:
        company_id = request.session.get("selected_company")
        if company_id and company_id != "all":
            pips = PerformanceImprovementPlanWorkflow.objects.filter(
                company_id=company_id
            )
        else:
            pips = PerformanceImprovementPlanWorkflow.objects.all()
    except:
        pips = PerformanceImprovementPlanWorkflow.objects.all()

    context["total_pips"] = pips.count()
    context["active_pips"] = pips.filter(status="active").count()
    context["completed_pips"] = pips.filter(status="completed").count()
    context["successful_pips"] = pips.filter(outcome="success").count()
    context["unsuccessful_pips"] = pips.filter(outcome="unsuccessful").count()

    context["recent_pips"] = pips.order_by("-created_at")[:10]

    return render(request, "pms/pip_workflow_dashboard.html", context)
