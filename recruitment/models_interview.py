"""
recruitment/models_interview.py

Interview panel evaluation — stores per-panelist scores and aggregates them.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from employee.models import Employee
from fits.models import FitsModel
from recruitment.models import Candidate, InterviewSchedule


class InterviewRound(models.Model):
    """Tracks individual rounds within a scheduled interview."""

    interview = models.ForeignKey(
        InterviewSchedule,
        on_delete=models.CASCADE,
        related_name="rounds",
        verbose_name=_("Interview"),
    )
    round_number = models.PositiveIntegerField(verbose_name=_("Round Number"))
    label = models.CharField(max_length=100, default="", verbose_name=_("Label"))
    completed = models.BooleanField(default=False, verbose_name=_("Completed"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed At"))
    interviewer = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interview_rounds_as_interviewer",
        verbose_name=_("Interviewer"),
    )
    round_date = models.DateField(null=True, blank=True, verbose_name=_("Round Date"))
    round_time = models.TimeField(null=True, blank=True, verbose_name=_("Round Time"))
    interviewers = models.ManyToManyField(
        Employee,
        blank=True,
        related_name="interview_rounds_as_panelist",
        verbose_name=_("Panelists"),
    )

    class Meta:
        ordering = ["round_number"]
        verbose_name = _("Interview Round")
        verbose_name_plural = _("Interview Rounds")

    def __str__(self):
        return f"{self.interview} — {self.label}"


class EvaluationCriteria(models.Model):
    """Reusable scoring criteria (e.g. Technical Skills, Communication)."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    max_score = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Evaluation Criteria")
        verbose_name_plural = _("Evaluation Criteria")

    def __str__(self):
        return self.name


class InterviewEvaluation(FitsModel):
    """One panelist's full evaluation of a candidate for a scheduled interview."""

    RECOMMENDATION_CHOICES = [
        ("strong_yes", _("Strong Yes")),
        ("yes", _("Yes")),
        ("maybe", _("Maybe")),
        ("no", _("No")),
        ("strong_no", _("Strong No")),
    ]

    interview = models.ForeignKey(
        InterviewSchedule,
        on_delete=models.CASCADE,
        related_name="evaluations",
        verbose_name=_("Interview"),
    )
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="evaluations",
        verbose_name=_("Candidate"),
    )
    panelist = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="evaluations_given",
        verbose_name=_("Panelist"),
    )
    overall_score = models.DecimalField(
        max_digits=4, decimal_places=1, default=0,
        verbose_name=_("Overall Score (0-10)"),
    )
    recommendation = models.CharField(
        max_length=20,
        choices=RECOMMENDATION_CHOICES,
        default="maybe",
        verbose_name=_("Recommendation"),
    )
    round_number = models.PositiveIntegerField(
        default=1, verbose_name=_("Round Number"),
    )
    strengths = models.TextField(blank=True, verbose_name=_("Strengths"))
    weaknesses = models.TextField(blank=True, verbose_name=_("Areas for Improvement"))
    notes = models.TextField(blank=True, verbose_name=_("Interview Notes"))
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("interview", "panelist", "round_number")
        verbose_name = _("Interview Evaluation")

    def __str__(self):
        return f"{self.candidate.name} — {self.panelist} ({self.recommendation})"


class EvaluationScore(models.Model):
    """Per-criteria score within one panelist's evaluation."""
    evaluation = models.ForeignKey(
        InterviewEvaluation,
        on_delete=models.CASCADE,
        related_name="scores",
    )
    criteria = models.ForeignKey(
        EvaluationCriteria,
        on_delete=models.CASCADE,
    )
    score = models.PositiveIntegerField(default=0)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ("evaluation", "criteria")

    def __str__(self):
        return f"{self.criteria.name}: {self.score}"
