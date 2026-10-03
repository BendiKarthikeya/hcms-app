"""
Learning & Development Models

This module contains models for training courses, certifications,
skills development, and learning management.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import Company
from employee.models import Employee


class CourseCategory(models.Model):
    """Category for organizing training courses"""

    name = models.CharField(_("Category Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Course Category")
        verbose_name_plural = _("Course Categories")

    def __str__(self):
        return self.name


class TrainingCourse(models.Model):
    """Training course model"""

    COURSE_FORMATS = [
        ("online", _("Online")),
        ("classroom", _("Classroom")),
        ("blended", _("Blended")),
        ("self-paced", _("Self-Paced")),
    ]

    COURSE_LEVELS = [
        ("beginner", _("Beginner")),
        ("intermediate", _("Intermediate")),
        ("advanced", _("Advanced")),
        ("expert", _("Expert")),
    ]

    name = models.CharField(_("Course Name"), max_length=200)
    description = models.TextField(_("Description"))
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    format = models.CharField(_("Format"), max_length=20, choices=COURSE_FORMATS)
    level = models.CharField(_("Level"), max_length=20, choices=COURSE_LEVELS)
    duration_hours = models.PositiveIntegerField(_("Duration (Hours)"))
    cost = models.DecimalField(_("Cost"), max_digits=10, decimal_places=2, default=0)
    instructor = models.CharField(_("Instructor"), max_length=100, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Training Course")
        verbose_name_plural = _("Training Courses")

    def __str__(self):
        return self.name


class CourseEnrollment(models.Model):
    """Employee enrollment in training courses"""

    ENROLLMENT_STATUS = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
        ("in_progress", _("In Progress")),
        ("completed", _("Completed")),
        ("cancelled", _("Cancelled")),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE)
    status = models.CharField(
        _("Status"), max_length=20, choices=ENROLLMENT_STATUS, default="pending"
    )
    enrollment_date = models.DateField(_("Enrollment Date"), auto_now_add=True)
    start_date = models.DateField(_("Start Date"), null=True, blank=True)
    completion_date = models.DateField(_("Completion Date"), null=True, blank=True)
    progress_percentage = models.PositiveIntegerField(_("Progress %"), default=0)
    final_score = models.DecimalField(
        _("Final Score"), max_digits=5, decimal_places=2, null=True, blank=True
    )
    certificate_issued = models.BooleanField(_("Certificate Issued"), default=False)
    certificate_issue_date = models.DateField(
        _("Certificate Issue Date"), null=True, blank=True
    )
    notes = models.TextField(_("Notes"), blank=True)

    class Meta:
        verbose_name = _("Course Enrollment")
        verbose_name_plural = _("Course Enrollments")
        unique_together = ("employee", "course")

    def __str__(self):
        return f"{self.employee} - {self.course}"


class Skill(models.Model):
    """Employee skills model"""

    SKILL_LEVELS = [
        ("beginner", _("Beginner")),
        ("intermediate", _("Intermediate")),
        ("advanced", _("Advanced")),
        ("expert", _("Expert")),
    ]

    name = models.CharField(_("Skill Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    category = models.CharField(_("Category"), max_length=50, blank=True)

    class Meta:
        verbose_name = _("Skill")
        verbose_name_plural = _("Skills")

    def __str__(self):
        return self.name


class EmployeeSkill(models.Model):
    """Employee skills with proficiency levels"""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.CharField(
        _("Proficiency Level"), max_length=20, choices=Skill.SKILL_LEVELS
    )
    years_experience = models.PositiveIntegerField(_("Years of Experience"), default=0)
    last_used = models.DateField(_("Last Used"), null=True, blank=True)
    verified_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_skills",
    )
    verification_date = models.DateField(_("Verification Date"), null=True, blank=True)

    class Meta:
        verbose_name = _("Employee Skill")
        verbose_name_plural = _("Employee Skills")
        unique_together = ("employee", "skill")

    def __str__(self):
        return f"{self.employee} - {self.skill}"


class Certification(models.Model):
    """Professional certifications model"""

    name = models.CharField(_("Certification Name"), max_length=200)
    issuing_authority = models.CharField(_("Issuing Authority"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    validity_period_months = models.PositiveIntegerField(
        _("Validity Period (Months)"), null=True, blank=True
    )

    class Meta:
        verbose_name = _("Certification")
        verbose_name_plural = _("Certifications")

    def __str__(self):
        return self.name


class EmployeeCertification(models.Model):
    """Employee certifications"""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE)
    issue_date = models.DateField(_("Issue Date"))
    expiry_date = models.DateField(_("Expiry Date"), null=True, blank=True)
    certificate_number = models.CharField(
        _("Certificate Number"), max_length=100, blank=True
    )
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Employee Certification")
        verbose_name_plural = _("Employee Certifications")

    def __str__(self):
        return f"{self.employee} - {self.certification}"


class TrainingBudget(models.Model):
    """Training budget allocation by department"""

    department = models.ForeignKey("base.Department", on_delete=models.CASCADE)
    year = models.PositiveIntegerField(_("Year"))
    budget_amount = models.DecimalField(
        _("Budget Amount"), max_digits=12, decimal_places=2
    )
    allocated_amount = models.DecimalField(
        _("Allocated Amount"), max_digits=12, decimal_places=2, default=0
    )
    remaining_amount = models.DecimalField(
        _("Remaining Amount"), max_digits=12, decimal_places=2, default=0
    )

    class Meta:
        verbose_name = _("Training Budget")
        verbose_name_plural = _("Training Budgets")
        unique_together = ("department", "year")

    def __str__(self):
        return f"{self.department} - {self.year}"


class LearningPlan(models.Model):
    """Individual learning plans for employees"""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    title = models.CharField(_("Plan Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True)
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=CourseEnrollment.ENROLLMENT_STATUS,
        default="pending",
    )
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_learning_plans",
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Learning Plan")
        verbose_name_plural = _("Learning Plans")

    def __str__(self):
        return f"{self.employee} - {self.title}"


class LearningPlanItem(models.Model):
    """Items within a learning plan"""

    learning_plan = models.ForeignKey(LearningPlan, on_delete=models.CASCADE)
    course = models.ForeignKey(
        TrainingCourse, on_delete=models.CASCADE, null=True, blank=True
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(_("Description"))
    target_date = models.DateField(_("Target Date"))
    completed = models.BooleanField(_("Completed"), default=False)
    completion_date = models.DateField(_("Completion Date"), null=True, blank=True)

    class Meta:
        verbose_name = _("Learning Plan Item")
        verbose_name_plural = _("Learning Plan Items")

    def __str__(self):
        return f"{self.learning_plan} - {self.description}"
