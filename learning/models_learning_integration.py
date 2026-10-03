"""
learning/models/models_learning_integration.py

LinkedIn Learning and Udemy Integration
Single sign-on (SSO), course enrollment, and progress tracking
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from base.models import Company, Employee
import requests


class LinkedInLearningConfig(models.Model):
    """
    Configuration for LinkedIn Learning OAuth integration
    """

    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name="linkedin_learning_config"
    )

    # OAuth credentials
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)

    # Endpoints
    auth_endpoint = models.URLField(
        default="https://www.linkedin.com/oauth/v2/authorization"
    )
    token_endpoint = models.URLField(
        default="https://www.linkedin.com/oauth/v2/accessToken"
    )
    api_endpoint = models.URLField(default="https://api.linkedin.com/v2")

    # Redirect URL
    redirect_uri = models.URLField(help_text=_("OAuth2 callback URL"))

    # Scopes
    scopes = models.JSONField(default=list, help_text=_("LinkedIn OAuth scopes"))

    # Settings
    is_enabled = models.BooleanField(default=True)
    auto_enroll_enabled = models.BooleanField(
        default=False, help_text=_("Auto-enroll employees in recommended courses")
    )

    # Metadata
    configured_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )
    configured_at = models.DateTimeField(auto_now_add=True)
    last_validated = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "learning_linkedin_learning_config"
        verbose_name = _("LinkedIn Learning Configuration")

    def __str__(self):
        return f"LinkedIn Learning - {self.company}"

    def validate_oauth_credentials(self):
        """Validate LinkedIn OAuth credentials"""
        try:
            # Test if credentials are valid by requesting access token
            response = requests.post(
                self.token_endpoint,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                timeout=10,
            )
            self.last_validated = timezone.now()
            self.save()
            return response.status_code == 200
        except Exception as e:
            print(f"LinkedIn validation error: {str(e)}")
            return False


class UdemyConfig(models.Model):
    """
    Configuration for Udemy business account integration
    """

    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name="udemy_config"
    )

    # API credentials
    api_key = models.CharField(max_length=255)
    api_endpoint = models.URLField(default="https://www.udemy.com/api-2.0")
    organization_id = models.CharField(
        max_length=100, help_text=_("Udemy organization ID")
    )

    # Settings
    is_enabled = models.BooleanField(default=True)
    auto_enroll_enabled = models.BooleanField(
        default=False, help_text=_("Auto-enroll eligible employees")
    )

    # Course settings
    auto_assign_learning_paths = models.BooleanField(default=True)
    require_completion_progress = models.IntegerField(
        default=80, help_text=_("Required completion percentage for tracking")
    )

    # Metadata
    configured_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )
    configured_at = models.DateTimeField(auto_now_add=True)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "learning_udemy_config"
        verbose_name = _("Udemy Configuration")

    def __str__(self):
        return f"Udemy - {self.company}"

    def validate_api_key(self):
        """Validate Udemy API credentials"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(
                f"{self.api_endpoint}/organizations/{self.organization_id}/",
                headers=headers,
                timeout=10,
            )
            self.last_synced = timezone.now()
            self.save()
            return response.status_code == 200
        except Exception as e:
            print(f"Udemy validation error: {str(e)}")
            return False


class EmployeeLearningProfile(models.Model):
    """
    Employee's learning profile for external platform access
    """

    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name="learning_profile"
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    # LinkedIn Learning
    linkedin_email = models.EmailField(blank=True)
    linkedin_oauth_token = models.TextField(blank=True)
    linkedin_token_expires = models.DateTimeField(null=True, blank=True)
    linkedin_is_connected = models.BooleanField(default=False)

    # Udemy
    udemy_email = models.EmailField(blank=True)
    udemy_user_id = models.CharField(max_length=100, blank=True)
    udemy_is_enrolled = models.BooleanField(default=False)

    # Learning preferences
    learning_style = models.CharField(
        max_length=50,
        choices=[
            ("visual", _("Visual")),
            ("auditory", _("Auditory")),
            ("reading", _("Reading/Writing")),
            ("kinesthetic", _("Kinesthetic")),
        ],
        blank=True,
    )
    preferred_categories = models.JSONField(
        default=list, help_text=_("Preferred course categories")
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_employee_learning_profile"
        verbose_name = _("Employee Learning Profile")

    def __str__(self):
        return f"Learning Profile - {self.employee}"


class LinkedInLearningCourse(models.Model):
    """
    LinkedIn Learning courses mapped to company learning paths
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="linkedin_courses"
    )

    linkedin_course_id = models.CharField(max_length=100)
    linkedin_course_name = models.CharField(max_length=255)

    description = models.TextField(blank=True)
    instructor = models.CharField(max_length=255, blank=True)
    duration_minutes = models.IntegerField()

    # Difficulty level
    difficulty_level = models.CharField(
        max_length=50,
        choices=[
            ("beginner", _("Beginner")),
            ("intermediate", _("Intermediate")),
            ("advanced", _("Advanced")),
        ],
        blank=True,
    )

    # Categorization
    category = models.CharField(max_length=255, blank=True)
    tags = models.JSONField(default=list)

    # Company customization
    is_recommended = models.BooleanField(default=False)
    is_mandatory = models.BooleanField(default=False)

    # Sync data
    last_synced = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_linkedin_learning_course"
        unique_together = ("company", "linkedin_course_id")

    def __str__(self):
        return self.linkedin_course_name


class UdemyCourse(models.Model):
    """
    Udemy courses available to employees
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="udemy_courses"
    )

    udemy_course_id = models.CharField(max_length=100)
    udemy_course_name = models.CharField(max_length=255)
    udemy_course_url = models.URLField()

    description = models.TextField(blank=True)
    instructor = models.CharField(max_length=255, blank=True)
    duration_minutes = models.IntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    # Difficulty level
    difficulty_level = models.CharField(
        max_length=50,
        choices=[
            ("beginner", _("Beginner")),
            ("intermediate", _("Intermediate")),
            ("advanced", _("Advanced")),
        ],
        blank=True,
    )

    # Categorization
    category = models.CharField(max_length=255, blank=True)
    tags = models.JSONField(default=list)

    # Company settings
    is_recommended = models.BooleanField(default=False)
    is_mandatory = models.BooleanField(default=False)

    # Sync data
    last_synced = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_udemy_course"
        unique_together = ("company", "udemy_course_id")

    def __str__(self):
        return self.udemy_course_name


class CourseEnrollment(models.Model):
    """
    Track employee enrollments in courses
    """

    ENROLLMENT_STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("enrolled", _("Enrolled")),
        ("in_progress", _("In Progress")),
        ("completed", _("Completed")),
        ("dropped", _("Dropped")),
    ]

    PLATFORM_CHOICES = [
        ("linkedin", _("LinkedIn Learning")),
        ("udemy", _("Udemy")),
        ("internal", _("Internal")),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="course_enrollments"
    )

    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    course_name = models.CharField(max_length=255)

    # External IDs
    external_course_id = models.CharField(max_length=100, blank=True)
    external_enrollment_id = models.CharField(max_length=100, blank=True)

    # Status
    status = models.CharField(
        max_length=20, choices=ENROLLMENT_STATUS_CHOICES, default="pending"
    )

    # Progress
    progress_percentage = models.IntegerField(
        default=0, help_text=_("Completion percentage 0-100")
    )
    completion_date = models.DateField(null=True, blank=True)

    # Learning path association
    learning_path = models.ForeignKey(
        "learning.LearningPath", on_delete=models.SET_NULL, null=True, blank=True
    )

    # Dates
    enrolled_date = models.DateField(auto_now_add=True)
    last_accessed_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "learning_course_enrollment"
        verbose_name = _("Course Enrollment")
        verbose_name_plural = _("Course Enrollments")
        ordering = ["-enrolled_date"]

    def __str__(self):
        return f"{self.employee} - {self.course_name}"

    def mark_completed(self):
        """Mark course as completed"""
        self.status = "completed"
        self.progress_percentage = 100
        self.completion_date = timezone.now().date()
        self.save()


class LearningPath(models.Model):
    """
    Learning paths combining multiple courses
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="learning_paths"
    )

    path_name = models.CharField(max_length=255)
    description = models.TextField()

    # Path composition
    courses = models.JSONField(default=list, help_text=_("List of course IDs in order"))

    # Target audience
    target_roles = models.JSONField(default=list)
    target_departments = models.JSONField(default=list)

    # Duration
    estimated_hours = models.IntegerField()

    # Status
    is_active = models.BooleanField(default=True)
    is_mandatory = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_learning_path"
        verbose_name = _("Learning Path")
        verbose_name_plural = _("Learning Paths")

    def __str__(self):
        return self.path_name
