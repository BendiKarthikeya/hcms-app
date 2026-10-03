"""
Views for Talent & Succession Planning module
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView

from .models import CriticalRole, SuccessionPlan, TalentProfile


class TalentProfileListView(LoginRequiredMixin, ListView):
    """List all talent profiles"""

    model = TalentProfile
    template_name = "talent/profile_list.html"
    context_object_name = "profiles"
    paginate_by = 20


class TalentProfileDetailView(LoginRequiredMixin, DetailView):
    """View details of a specific talent profile"""

    model = TalentProfile
    template_name = "talent/profile_detail.html"
    context_object_name = "profile"


class CriticalRoleListView(LoginRequiredMixin, ListView):
    """List all critical roles"""

    model = CriticalRole
    template_name = "talent/critical_role_list.html"
    context_object_name = "critical_roles"
    paginate_by = 20


class CriticalRoleDetailView(LoginRequiredMixin, DetailView):
    """View details of a specific critical role"""

    model = CriticalRole
    template_name = "talent/critical_role_detail.html"
    context_object_name = "critical_role"


class SuccessionPlanListView(LoginRequiredMixin, ListView):
    """List all succession plans"""

    model = SuccessionPlan
    template_name = "talent/succession_plan_list.html"
    context_object_name = "succession_plans"
    paginate_by = 20


class SuccessionPlanDetailView(LoginRequiredMixin, DetailView):
    """View details of a specific succession plan"""

    model = SuccessionPlan
    template_name = "talent/succession_plan_detail.html"
    context_object_name = "succession_plan"


class MyTalentProfileView(LoginRequiredMixin, DetailView):
    """View current user's talent profile"""

    model = TalentProfile
    template_name = "talent/my_profile.html"
    context_object_name = "profile"

    def get_object(self):
        """Get or create a minimal talent profile for the current user.

        If an Employee linked to the current User does not exist, create a
        minimal Employee record. Then create a minimal TalentProfile with
        default values so the view can render without raising DoesNotExist.
        """
        from datetime import date, timedelta
        from employee.models import Employee

        user = self.request.user
        # Try to get existing talent profile
        profile = TalentProfile.objects.filter(employee__employee_user_id=user).first()
        if profile:
            return profile

        # Ensure an Employee exists linked to this user
        employee = Employee.objects.filter(employee_user_id=user).first()
        if not employee:
            full_name = getattr(user, "get_full_name", None)
            first = user.username
            last = ""
            try:
                if callable(full_name):
                    name = user.get_full_name()
                    if name:
                        parts = name.split(None, 1)
                        first = parts[0]
                        last = parts[1] if len(parts) > 1 else ""
            except Exception:
                pass
            employee = Employee.objects.create(
                employee_user_id=user,
                employee_first_name=first,
                employee_last_name=last,
                email=getattr(user, "email", "") or f"{user.username}@local",
                phone="",
            )

        # Create a minimal TalentProfile with safe defaults
        today = date.today()
        tp_defaults = dict(
            performance_level="medium",
            potential_level="medium",
            career_aspirations="",
            mobility_willingness=False,
            readiness_level="not_ready",
            development_needs="",
            last_assessment_date=today,
            next_assessment_date=today + timedelta(days=365),
        )
        profile, created = TalentProfile.objects.get_or_create(
            employee=employee, defaults=tp_defaults
        )
        return profile


class NineBoxMatrixView(LoginRequiredMixin, TemplateView):
    """View the 9-Box Talent Matrix."""

    template_name = "talent/nine_box_matrix.html"


class CareerPathListView(LoginRequiredMixin, ListView):
    """View career paths and milestones."""

    template_name = "talent/career_paths.html"

    def get_queryset(self):
        return []


class IDPListView(LoginRequiredMixin, ListView):
    """Individual Development Plan generation."""

    template_name = "talent/idp_list.html"

    def get_queryset(self):
        return []


class HighPotentialListView(LoginRequiredMixin, ListView):
    """High-Potential (HiPo) employee tracking."""

    template_name = "talent/high_potential.html"

    def get_queryset(self):
        return []
