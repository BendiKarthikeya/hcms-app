"""
URL configuration for Talent & Succession Planning module
"""

from django.urls import path

from . import views
from . import views_dashboard

app_name = "talent"

urlpatterns = [
    # Dashboard
    path("", views_dashboard.TalentDashboardView.as_view(), name="dashboard"),
    # Talent profiles
    path("profiles/", views.TalentProfileListView.as_view(), name="profile_list"),
    path(
        "profiles/<int:pk>/",
        views.TalentProfileDetailView.as_view(),
        name="profile_detail",
    ),
    # Critical roles
    path(
        "critical-roles/",
        views.CriticalRoleListView.as_view(),
        name="critical_role_list",
    ),
    path(
        "critical-roles/<int:pk>/",
        views.CriticalRoleDetailView.as_view(),
        name="critical_role_detail",
    ),
    # Succession plans
    path(
        "succession-plans/",
        views.SuccessionPlanListView.as_view(),
        name="succession_plan_list",
    ),
    path(
        "succession-plans/<int:pk>/",
        views.SuccessionPlanDetailView.as_view(),
        name="succession_plan_detail",
    ),
    # My talent profile
    path("my-profile/", views.MyTalentProfileView.as_view(), name="my_profile"),
    # New Talent Features
    path("9-box-matrix/", views.NineBoxMatrixView.as_view(), name="nine_box_matrix"),
    path("career-paths/", views.CareerPathListView.as_view(), name="career_paths"),
    path("idp/", views.IDPListView.as_view(), name="idp"),
    path(
        "high-potential/", views.HighPotentialListView.as_view(), name="high_potential"
    ),
    path(
        "succession/", views.SuccessionPlanListView.as_view()
    ),  # Redirect for short link
]
