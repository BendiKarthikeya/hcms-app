"""
Dashboard views for Expenses & Travel Management module
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .models import TravelRequest, ExpenseClaim


class ExpensesDashboardView(LoginRequiredMixin, TemplateView):
    """Expenses & Travel Dashboard"""

    template_name = "expenses/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get statistics for the dashboard cards
        pending_requests = TravelRequest.objects.filter(status="pending").count()
        approved_requests = TravelRequest.objects.filter(status="approved").count()
        total_claims = ExpenseClaim.objects.count()
        paid_claims = ExpenseClaim.objects.filter(status="paid").count()

        context.update(
            {
                "pending_requests": pending_requests,
                "approved_requests": approved_requests,
                "total_claims": total_claims,
                "paid_claims": paid_claims,
            }
        )

        return context
