"""
Dashboard views for Learning & Development module
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .models import CourseEnrollment, TrainingCourse, EmployeeSkill, EmployeeCertification


class LearningDashboardView(LoginRequiredMixin, TemplateView):
    """Learning & Development Dashboard"""

    template_name = "learning/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the current user's employee profile
        try:
            employee = self.request.user.employee_set.first()
        except:
            employee = None

        # Get statistics for the dashboard cards
        courses_count = TrainingCourse.objects.filter(is_active=True).count()
        enrollments_count = CourseEnrollment.objects.filter(
            employee__employee_user_id=self.request.user
        ).count()
        skills_count = EmployeeSkill.objects.filter(
            employee__employee_user_id=self.request.user
        ).count()
        certifications_count = EmployeeCertification.objects.filter(
            employee__employee_user_id=self.request.user, is_active=True
        ).count()

        context.update(
            {
                "courses_count": courses_count,
                "enrollments_count": enrollments_count,
                "skills_count": skills_count,
                "certifications_count": certifications_count,
                "employee": employee,
            }
        )

        return context
