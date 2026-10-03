"""
AI CV Screening & Automated Candidate Ranking
AI-powered CV parsing, skill extraction, and candidate ranking against job requirements
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from base.models import Company
from fits.models import FitsModel
from recruitment.models import Recruitment, Candidate


class CVParsingSettings(models.Model):
    """
    Settings for CV Parsing and AI Candidate Screening
    """

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="cv_parsing_settings",
        verbose_name=_("Company"),
    )

    # AI Settings
    enable_ai_screening = models.BooleanField(
        default=True,
        verbose_name=_("Enable AI CV Screening"),
    )
    auto_parse_cv = models.BooleanField(
        default=True,
        verbose_name=_("Auto-Parse CV on Upload"),
    )
    auto_rank_candidates = models.BooleanField(
        default=True,
        verbose_name=_("Auto-Rank Candidates"),
    )

    # Parsing Engines
    PARSER_CHOICES = [
        ("pdfrw", _("PDFrw (Default)")),
        ("pdfplumber", _("PDFPlumber")),
        ("pypdf2", _("PyPDF2")),
        ("textract", _("Amazon Textract")),
    ]

    pdf_parser_engine = models.CharField(
        max_length=20,
        choices=PARSER_CHOICES,
        default="pdfrw",
        verbose_name=_("PDF Parser Engine"),
    )
    ocr_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Enable OCR for Scanned PDFs"),
        help_text=_("Uses Tesseract OCR"),
    )

    # Ranking Settings
    skill_match_weight = models.FloatField(
        default=0.40,
        verbose_name=_("Skill Match Weight"),
        help_text=_("Importance of skill matching (0-1)"),
    )
    experience_weight = models.FloatField(
        default=0.25,
        verbose_name=_("Experience Match Weight"),
        help_text=_("Importance of experience (0-1)"),
    )
    education_weight = models.FloatField(
        default=0.20,
        verbose_name=_("Education Match Weight"),
        help_text=_("Importance of education (0-1)"),
    )
    location_weight = models.FloatField(
        default=0.15,
        verbose_name=_("Location Preference Weight"),
        help_text=_("Importance of location (0-1)"),
    )

    # Minimum Thresholds
    min_skill_match_percentage = models.IntegerField(
        default=50,
        verbose_name=_("Minimum Skill Match %"),
        help_text=_("Candidates below this score auto-rejected"),
    )
    min_overall_score = models.IntegerField(
        default=40,
        verbose_name=_("Minimum Overall Score (%)"),
    )

    # Auto Actions
    auto_shortlist_above_score = models.IntegerField(
        default=75,
        verbose_name=_("Auto-Shortlist Above Score (%)"),
        help_text=_("Candidates scoring above this auto-shortlisted"),
    )
    auto_reject_below_score = models.IntegerField(
        default=30,
        verbose_name=_("Auto-Reject Below Score (%)"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Updated"),
    )

    class Meta:
        verbose_name = _("CV Parsing Settings")
        verbose_name_plural = _("CV Parsing Settings")

    def __str__(self):
        return f"CV Parsing Settings - {self.company.name}"


class ParsedCVData(FitsModel):
    """
    Extracted and Parsed CV Data
    Stores extracted information from candidate CVs
    """

    candidate = models.OneToOneField(
        Candidate,
        on_delete=models.CASCADE,
        related_name="parsed_cv_data",
        verbose_name=_("Candidate"),
    )

    # Personal Info
    full_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Full Name"),
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_("Email Address"),
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Phone Number"),
    )
    location_city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("City"),
    )
    location_country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Country"),
    )

    # Education
    education_json = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Education Details"),
        help_text=_(
            'Format: [{"degree": "BSc", "field": "Engineering", "university": "XYZ", "year": 2020}]'
        ),
    )
    highest_qualification = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Highest Qualification"),
        help_text=_("e.g., Bachelor's, Master's, PhD"),
    )

    # Experience
    total_years_experience = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        verbose_name=_("Total Years of Experience"),
    )
    work_experience_json = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Work Experience"),
        help_text=_(
            'Format: [{"position": "Manager", "company": "ABC", "duration": "2 years", "description": "..."}]'
        ),
    )
    current_job_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Current Job Title"),
    )
    current_company = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Current Company"),
    )

    # Skills
    extracted_skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Extracted Skills"),
        help_text=_("List of skills extracted from CV"),
    )
    skill_categories = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Skills by Category"),
        help_text=_(
            'Format: {"Technical": ["Python", "Java"], "Soft": ["Leadership", "Communication"]}'
        ),
    )

    # Languages
    languages_spoken = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Languages"),
        help_text=_('Format: [{"language": "English", "proficiency": "Native"}]'),
    )

    # Certifications
    certifications_json = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Certifications"),
        help_text=_(
            'Format: [{"name": "AWS Certified", "issuer": "Amazon", "date": "2023"}]'
        ),
    )

    # Parsing Metadata
    parsing_engine = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Parsing Engine Used"),
    )
    parsing_confidence = models.FloatField(
        default=0,
        verbose_name=_("Parsing Confidence Score (%)"),
        help_text=_("Quality of extraction (0-100)"),
    )
    parsing_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Parsing Date"),
    )
    requires_manual_review = models.BooleanField(
        default=False,
        verbose_name=_("Requires Manual Review"),
        help_text=_("Set if extraction quality is low"),
    )

    # Raw Text
    raw_cv_text = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Raw CV Text"),
        help_text=_("Extracted text from PDF before parsing"),
    )

    class Meta:
        verbose_name = _("Parsed CV Data")
        verbose_name_plural = _("Parsed CV  Data")

    def __str__(self):
        return f"Parsed CV - {self.candidate.name}"


class CandidateSkillMatch(FitsModel):
    """
    Skill Matching Score Between Candidate and Job Requirements
    """

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="skill_matches",
        verbose_name=_("Candidate"),
    )
    recruitment = models.ForeignKey(
        Recruitment,
        on_delete=models.CASCADE,
        related_name="candidate_skill_matches",
        verbose_name=_("Job Opening"),
    )

    # Required vs Available Skills
    required_skills = models.JSONField(
        default=list,
        verbose_name=_("Required Skills"),
        help_text=_("Skills required for the job"),
    )
    candidate_skills = models.JSONField(
        default=list,
        verbose_name=_("Candidate's Skills"),
    )

    # Matching Analysis
    matched_skills = models.JSONField(
        default=list,
        verbose_name=_("Matched Skills"),
        help_text=_("Skills candidate has that job requires"),
    )
    missing_skills = models.JSONField(
        default=list,
        verbose_name=_("Missing Skills"),
        help_text=_("Required skills candidate doesn't have"),
    )
    extra_skills = models.JSONField(
        default=list,
        verbose_name=_("Extra Skills"),
        help_text=_("Skills candidate has beyond job requirements"),
    )

    # Scoring
    skill_match_percentage = models.FloatField(
        verbose_name=_("Skill Match Score (%)"),
        help_text=_("Percentage of required skills matched"),
    )
    skill_relevance_score = models.FloatField(
        default=0,
        verbose_name=_("Skill Relevance Score"),
        help_text=_("How relevant candidate's skills are to job (0-100)"),
    )

    class Meta:
        verbose_name = _("Candidate Skill Match")
        verbose_name_plural = _("Candidate Skill Matches")
        unique_together = ["candidate", "recruitment"]

    def __str__(self):
        return f"{self.candidate.name} vs {self.recruitment.job_title} ({self.skill_match_percentage}%)"


class CandidateRankingScore(FitsModel):
    """
    Comprehensive Ranking Score for Candidates Against Job Requirements
    """

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="ranking_scores",
        verbose_name=_("Candidate"),
    )
    recruitment = models.ForeignKey(
        Recruitment,
        on_delete=models.CASCADE,
        related_name="candidate_ranking_scores",
        verbose_name=_("Job Opening"),
    )

    # Component Scores
    skill_match_score = models.FloatField(
        verbose_name=_("Skill Match Score (%)"),
    )
    experience_match_score = models.FloatField(
        verbose_name=_("Experience Match Score (%)"),
    )
    education_match_score = models.FloatField(
        verbose_name=_("Education Match Score (%)"),
    )
    location_match_score = models.FloatField(
        default=50,
        verbose_name=_("Location Match Score (%)"),
    )

    # Weighted Overall Score
    overall_ranking_score = models.FloatField(
        verbose_name=_("Overall Ranking Score (%)"),
        help_text=_("Weighted combination of all component scores"),
    )

    # Ranking & Recommendation
    RANKING_CHOICES = [
        ("highly_recommended", _("Highly Recommended (80-100%)")),
        ("recommended", _("Recommended (60-79%)")),
        ("moderate", _("Moderate Match (40-59%)")),
        ("weak", _("Weak Match (Below 40%)")),
    ]

    ranking_category = models.CharField(
        max_length=30,
        choices=RANKING_CHOICES,
        verbose_name=_("Ranking Category"),
    )

    recommendation_text = models.TextField(
        blank=True,
        verbose_name=_("AI Recommendation"),
        help_text=_("AI-generated summary of fit and gaps"),
    )

    # Auto Actions Taken
    action_taken = models.CharField(
        max_length=50,
        choices=[
            ("auto_shortlisted", _("Auto-Shortlisted")),
            ("auto_rejected", _("Auto-Rejected")),
            ("manual_review", _("Requires Manual Review")),
            ("none", _("No Auto Action")),
        ],
        default="none",
        verbose_name=_("Action Taken"),
    )

    # Metadata
    scoring_engine_version = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Scoring Engine Version"),
    )
    scoring_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Scoring Date"),
    )

    class Meta:
        verbose_name = _("Candidate Ranking Score")
        verbose_name_plural = _("Candidate Ranking Scores")
        unique_together = ["candidate", "recruitment"]
        indexes = [
            models.Index(fields=["-overall_ranking_score"]),
            models.Index(fields=["ranking_category"]),
        ]

    def __str__(self):
        return f"{self.candidate.name} - {self.recruitment.job_title} ({self.overall_ranking_score:.1f}%)"


class CVScreeningLog(models.Model):
    """
    Audit Log for CV Screening Activities
    """

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="screening_logs",
        verbose_name=_("Candidate"),
    )
    recruitment = models.ForeignKey(
        Recruitment,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Job Opening"),
    )

    ACTION_CHOICES = [
        ("cv_uploaded", _("CV Uploaded")),
        ("cv_parsed", _("CV Parsed")),
        ("parsing_failed", _("Parsing Failed")),
        ("skills_extracted", _("Skills Extracted")),
        ("ranked", _("Candidate Ranked")),
        ("auto_rejected", _("Auto-Rejected")),
        ("auto_shortlisted", _("Auto-Shortlisted")),
        ("manual_review_set", _("Manual Review Set")),
    ]

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        verbose_name=_("Action"),
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Timestamp"),
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Details"),
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Error Message (if failed)"),
    )

    class Meta:
        verbose_name = _("CV Screening Log")
        verbose_name_plural = _("CV Screening Logs")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.candidate.name} - {self.get_action_display()}"
