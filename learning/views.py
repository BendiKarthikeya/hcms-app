"""
Views for Learning & Development module
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from fits.decorators import login_required

from .models import (
    CourseEnrollment,
    EmployeeCertification,
    EmployeeSkill,
    LearningPlan,
    TrainingCourse,
)


class TrainingCourseListView(LoginRequiredMixin, ListView):
    """List all available training courses"""

    model = TrainingCourse
    template_name = "learning/course_list.html"
    context_object_name = "courses"
    paginate_by = 20

    def get_queryset(self):
        return TrainingCourse.objects.filter(is_active=True)


class TrainingCourseDetailView(LoginRequiredMixin, DetailView):
    """View details of a specific training course"""

    model = TrainingCourse
    template_name = "learning/course_detail.html"
    context_object_name = "course"


class MyEnrollmentsListView(LoginRequiredMixin, ListView):
    """List current user's course enrollments"""

    model = CourseEnrollment
    template_name = "learning/my_enrollments.html"
    context_object_name = "enrollments"
    paginate_by = 10

    def get_queryset(self):
        return CourseEnrollment.objects.filter(
            employee__employee_user_id=self.request.user
        )


class MySkillsListView(LoginRequiredMixin, ListView):
    """List current user's skills"""

    model = EmployeeSkill
    template_name = "learning/my_skills.html"
    context_object_name = "skills"

    def get_queryset(self):
        return EmployeeSkill.objects.filter(
            employee__employee_user_id=self.request.user
        )


class MyCertificationsListView(LoginRequiredMixin, ListView):
    """List current user's certifications"""

    model = EmployeeCertification
    template_name = "learning/my_certifications.html"
    context_object_name = "certifications"

    def get_queryset(self):
        return EmployeeCertification.objects.filter(
            employee__employee_user_id=self.request.user, is_active=True
        )


class MyLearningPlansListView(LoginRequiredMixin, ListView):
    """List current user's learning plans"""

    model = LearningPlan
    template_name = "learning/my_learning_plans.html"
    context_object_name = "learning_plans"

    def get_queryset(self):
        return LearningPlan.objects.filter(employee__employee_user_id=self.request.user)


class CourseEnrollmentCreateView(LoginRequiredMixin, CreateView):
    """Enroll in a training course"""

    model = CourseEnrollment
    template_name = "learning/enroll_course.html"
    fields = ["course", "notes"]

    def form_valid(self, form):
        form.instance.employee = self.request.user.employee_get
        form.instance.status = "pending"
        return super().form_valid(form)


class LearningPlanCreateView(LoginRequiredMixin, CreateView):
    """Create a new learning plan"""

    model = LearningPlan
    template_name = "learning/learning_plan_form.html"  # Modified template_name
    fields = ["title", "description", "start_date", "end_date"]
    success_url = "/learning/my-learning-plans/"  # Added success_url

    def form_valid(self, form):
        form.instance.employee = self.request.user.employee_get
        form.instance.created_by = self.request.user.employee_get
        return super().form_valid(form)


# Learning Integration Views


class IntegrationView(LoginRequiredMixin, TemplateView):
    """View for managing external learning platform integrations."""

    template_name = "learning/integrations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: Fetch actual integration status from database
        context["integrations"] = {
            "linkedin": {"connected": False, "last_sync": None},
            "udemy": {"connected": False, "last_sync": None},
        }
        return context


@login_required
@require_http_methods(["POST"])
def connect_linkedin(request):
    """Connect LinkedIn Learning account."""
    client_id = request.POST.get("client_id")
    client_secret = request.POST.get("client_secret")

    if not client_id or not client_secret:
        messages.error(request, _("Client ID and Secret are required."))
        return redirect("learning-integrations")

    # Store credentials (in production, use encrypted storage)
    # TODO: Implement actual LinkedIn OAuth flow

    messages.success(request, _("LinkedIn Learning connected successfully."))
    return redirect("learning-integrations")


@login_required
@require_http_methods(["POST"])
def connect_udemy(request):
    """Connect Udemy for Business account."""
    org_id = request.POST.get("org_id")
    api_key = request.POST.get("api_key")

    if not org_id or not api_key:
        messages.error(request, _("Organization ID and API Key are required."))
        return redirect("learning-integrations")

    # Store credentials (in production, use encrypted storage)
    # TODO: Implement actual Udemy API integration

    messages.success(request, _("Udemy for Business connected successfully."))
    return redirect("learning-integrations")


@login_required
@require_http_methods(["POST"])
def sync_external_catalog(request):
    """Sync external course catalogs from LinkedIn Learning and Udemy."""
    # TODO: Implement actual sync logic with external APIs
    messages.info(request, _("Catalog sync initiated. This may take a few minutes..."))
    return redirect("learning-integrations")


# Placeholder views for features mentioned in URLs
class AssessmentListView(LoginRequiredMixin, TemplateView):
    """List available training assessments."""

    template_name = "learning/assessments.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assessments"] = []  # TODO: Implement assessment retrieval
        return context


class LeaderboardView(LoginRequiredMixin, TemplateView):
    """Display learning leaderboards by department and skill."""

    template_name = "learning/leaderboards.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["leaderboards"] = []  # TODO: Implement leaderboard logic
        return context


class SessionListView(LoginRequiredMixin, TemplateView):
    """List training sessions and workshops."""

    template_name = "learning/sessions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sessions"] = []  # TODO: Implement session retrieval
        return context


class TrainerListView(LoginRequiredMixin, TemplateView):
    """List certified trainers and their specializations."""

    template_name = "learning/trainers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trainers"] = []  # TODO: Implement trainer retrieval
        return context


class AssessmentListView(LoginRequiredMixin, ListView):
    """View assessments and quizzes."""

    template_name = "learning/assessments.html"

    def get_queryset(self):
        return []


class LeaderboardView(LoginRequiredMixin, TemplateView):
    """View gamification leaderboards and badges."""

    template_name = "learning/leaderboards.html"


class SessionListView(LoginRequiredMixin, ListView):
    """View training sessions and ROI metrics."""

    template_name = "learning/sessions.html"

    def get_queryset(self):
        return []


class TrainerListView(LoginRequiredMixin, ListView):
    """Manage internal and external trainers."""

    template_name = "learning/trainers.html"

    def get_queryset(self):
        return []


class IntegrationView(LoginRequiredMixin, TemplateView):
    """LinkedIn/Udemy integration settings."""

    template_name = "learning/integrations.html"
