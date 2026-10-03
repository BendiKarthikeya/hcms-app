"""
Dashboard views for Talent & Succession Planning module
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .models import TalentProfile, CriticalRole, SuccessionPlan


class TalentDashboardView(LoginRequiredMixin, TemplateView):
    """Talent & Succession Dashboard"""

    template_name = "talent/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get statistics for the dashboard cards
        total_profiles = TalentProfile.objects.count()
        succession_plans = SuccessionPlan.objects.count()
        critical_roles = CriticalRole.objects.count()
        ready_successors = SuccessionPlan.objects.filter(
            readiness_level="ready"
        ).count()

        context.update(
            {
                "total_profiles": total_profiles,
                "succession_plans": succession_plans,
                "critical_roles": critical_roles,
                "ready_successors": ready_successors,
            }
        )

        return context
