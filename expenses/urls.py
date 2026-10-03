"""
URL configuration for Expenses & Travel Management module
"""

from django.urls import path

from . import views
from . import views_dashboard

app_name = "expenses"

urlpatterns = [
    # Dashboard
    path("", views_dashboard.ExpensesDashboardView.as_view(), name="dashboard"),
    # Travel requests
    path(
        "travel-requests/",
        views.TravelRequestListView.as_view(),
        name="travel_request_list",
    ),
    path(
        "travel-requests/<int:pk>/",
        views.TravelRequestDetailView.as_view(),
        name="travel_request_detail",
    ),
    # Expense claims
    path(
        "expense-claims/",
        views.ExpenseClaimListView.as_view(),
        name="expense_claim_list",
    ),
    path(
        "expense-claims/<int:pk>/",
        views.ExpenseClaimDetailView.as_view(),
        name="expense_claim_detail",
    ),
    # My expenses
    path(
        "my-travel-requests/",
        views.MyTravelRequestsView.as_view(),
        name="my_travel_requests",
    ),
    path(
        "my-expense-claims/",
        views.MyExpenseClaimsView.as_view(),
        name="my_expense_claims",
    ),
    # Categories
    path("categories/", views.ExpenseCategoryListView.as_view(), name="category_list"),
]
