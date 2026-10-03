"""
Views for Expenses & Travel Management module
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

from .models import ExpenseCategory, ExpenseClaim, TravelRequest


class TravelRequestListView(LoginRequiredMixin, ListView):
    """List all travel requests"""

    model = TravelRequest
    template_name = "expenses/travel_request_list.html"
    context_object_name = "travel_requests"
    paginate_by = 20


class TravelRequestDetailView(LoginRequiredMixin, DetailView):
    """View details of a specific travel request"""

    model = TravelRequest
    template_name = "expenses/travel_request_detail.html"
    context_object_name = "travel_request"


class ExpenseClaimListView(LoginRequiredMixin, ListView):
    """List all expense claims"""

    model = ExpenseClaim
    template_name = "expenses/expense_claim_list.html"
    context_object_name = "expense_claims"
    paginate_by = 20


class ExpenseClaimDetailView(LoginRequiredMixin, DetailView):
    """View details of a specific expense claim"""

    model = ExpenseClaim
    template_name = "expenses/expense_claim_detail.html"
    context_object_name = "expense_claim"


class MyTravelRequestsView(LoginRequiredMixin, ListView):
    """List current user's travel requests"""

    model = TravelRequest
    template_name = "expenses/my_travel_requests.html"
    context_object_name = "travel_requests"
    paginate_by = 10

    def get_queryset(self):
        """Filter travel requests for current user"""
        return TravelRequest.objects.filter(
            employee__employee_user_id=self.request.user
        )


class MyExpenseClaimsView(LoginRequiredMixin, ListView):
    """List current user's expense claims"""

    model = ExpenseClaim
    template_name = "expenses/my_expense_claims.html"
    context_object_name = "expense_claims"
    paginate_by = 10

    def get_queryset(self):
        """Filter expense claims for current user"""
        return ExpenseClaim.objects.filter(employee__employee_user_id=self.request.user)


class ExpenseCategoryListView(LoginRequiredMixin, ListView):
    """List all expense categories"""

    model = ExpenseCategory
    template_name = "expenses/category_list.html"
    context_object_name = "categories"
    paginate_by = 20
