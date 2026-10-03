"""
URL configuration for Learning & Development module
"""

from django.urls import path
from django.views.generic import RedirectView

from . import views
from . import views_dashboard

app_name = "learning"

urlpatterns = [
    # Dashboard
    path("", views_dashboard.LearningDashboardView.as_view(), name="dashboard"),
    path(
        "training-course/",
        RedirectView.as_view(url="/learning/courses/", permanent=False),
        name="training-course-alias",
    ),
    # Course management
    path("courses/", views.TrainingCourseListView.as_view(), name="course_list"),
    path(
        "courses/<int:pk>/",
        views.TrainingCourseDetailView.as_view(),
        name="course_detail",
    ),
    path(
        "courses/<int:pk>/enroll/",
        views.CourseEnrollmentCreateView.as_view(),
        name="enroll_course",
    ),
    # User-specific views
    path(
        "my-enrollments/", views.MyEnrollmentsListView.as_view(), name="my_enrollments"
    ),
    path("my-skills/", views.MySkillsListView.as_view(), name="my_skills"),
    path(
        "my-certifications/",
        views.MyCertificationsListView.as_view(),
        name="my_certifications",
    ),
    path(
        "my-learning-plans/",
        views.MyLearningPlansListView.as_view(),
        name="my_learning_plans",
    ),
    path(
        "create-learning-plan/",
        views.LearningPlanCreateView.as_view(),
        name="create_learning_plan",
    ),
    # Integration views
    path(
        "integrations/", views.IntegrationView.as_view(), name="learning-integrations"
    ),
    path("connect-linkedin/", views.connect_linkedin, name="connect-linkedin"),
    path("connect-udemy/", views.connect_udemy, name="connect-udemy"),
    path(
        "sync-external-catalog/",
        views.sync_external_catalog,
        name="sync-external-catalog",
    ),
    # New Features
    path("assessments/", views.AssessmentListView.as_view(), name="assessments"),
    path("leaderboards/", views.LeaderboardView.as_view(), name="leaderboards"),
    path("sessions/", views.SessionListView.as_view(), name="sessions"),
    path("trainers/", views.TrainerListView.as_view(), name="trainers"),
    path("integrations/", views.IntegrationView.as_view(), name="integrations"),
]
