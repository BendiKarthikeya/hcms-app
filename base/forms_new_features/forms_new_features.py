"""
Forms for Performance Improvement Plans (PIP), EOSB, and WPS
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import inlineformset_factory
from datetime import timedelta, date

# PMS Forms
from pms.models_pip import (
    PerformanceImprovementPlan,
    PIPTemplate,
    PIPMilestone,
    PIPReview,
    PIPExtension,
)

# Payroll Forms
from payroll.models.models_eosb import (
    EndOfServiceBenefit,
    EOSBGratuitySettings,
    ServiceAward,
)
from payroll.models.models_wps import (
    WPSGlobalSettings,
)

# Recruitment Forms
from recruitment.models_cv_screening import (
    CVParsingSettings,
)


# ============= PIP FORMS =============


class PIPTemplateForm(forms.ModelForm):
    """Form for creating/editing PIP Templates"""

    class Meta:
        model = PIPTemplate
        fields = ["name", "description", "duration_days", "status"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("e.g., Technical Skills Improvement"),
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": _("Description of this template"),
                }
            ),
            "duration_days": forms.NumberInput(
                attrs={"class": "form-control", "min": "30", "max": "180", "step": "30"}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
        }


class PerformanceImprovementPlanForm(forms.ModelForm):
    """Form for creating/editing Performance Improvement Plans"""

    class Meta:
        model = PerformanceImprovementPlan
        fields = [
            "employee",
            "template",
            "title",
            "reason",
            "reason_details",
            "expected_outcomes",
            "support_provided",
            "start_date",
            "end_date",
            "mid_review_date",
        ]
        widgets = {
            "employee": forms.Select(attrs={"class": "form-control"}),
            "template": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("PIP Title")}
            ),
            "reason": forms.Select(attrs={"class": "form-control"}),
            "reason_details": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": _("Specific performance issues"),
                }
            ),
            "expected_outcomes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": _("What should be achieved"),
                }
            ),
            "support_provided": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("Training, mentoring, tools, etc."),
                }
            ),
            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "mid_review_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default end_date to 90 days from start_date
        if not self.instance.pk:
            self.fields["start_date"].initial = date.today()
            self.fields["end_date"].initial = date.today() + timedelta(days=90)
            self.fields["mid_review_date"].initial = date.today() + timedelta(days=45)


class PIPMilestoneForm(forms.ModelForm):
    """Form for adding/editing PIP Milestones"""

    class Meta:
        model = PIPMilestone
        fields = [
            "milestone_title",
            "description",
            "target_date",
            "success_criteria",
            "status",
            "comments",
            "order",
        ]
        widgets = {
            "milestone_title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("Milestone title")}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": _("Optional description"),
                }
            ),
            "target_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "success_criteria": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("How will success be measured?"),
                }
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "comments": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": _("Completion comments"),
                }
            ),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }


PIPMilestoneFormSet = inlineformset_factory(
    PerformanceImprovementPlan,
    PIPMilestone,
    form=PIPMilestoneForm,
    extra=3,
    can_delete=True,
)


class PIPReviewForm(forms.ModelForm):
    """Form for conducting PIP reviews"""

    class Meta:
        model = PIPReview
        fields = [
            "review_type",
            "overall_rating",
            "achievements",
            "areas_for_improvement",
            "recommendations",
            "employee_comments",
            "notes",
        ]
        widgets = {
            "review_type": forms.Select(attrs={"class": "form-control"}),
            "overall_rating": forms.RadioSelect(
                choices=PIPReview.RATING_CHOICES,
                attrs={"class": "form-check-input"},
            ),
            "achievements": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("What has improved"),
                }
            ),
            "areas_for_improvement": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("Areas still needing work"),
                }
            ),
            "recommendations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("Suggested next steps"),
                }
            ),
            "employee_comments": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("Employee's input"),
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": _("Internal notes"),
                }
            ),
        }


class PIPExtensionForm(forms.ModelForm):
    """Form for requesting PIP extension"""

    class Meta:
        model = PIPExtension
        fields = [
            "requested_new_end_date",
            "extension_days",
            "justification",
        ]
        widgets = {
            "requested_new_end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "extension_days": forms.NumberInput(
                attrs={"class": "form-control", "min": "15", "max": "90"}
            ),
            "justification": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": _("Why is extension needed?"),
                }
            ),
        }


# ============= EOSB FORMS =============


class EOSBGratuitySettingsForm(forms.ModelForm):
    """Form for configuring EOSB/Gratuity settings"""

    class Meta:
        model = EOSBGratuitySettings
        fields = [
            "gratuity_less_than_3_years",
            "gratuity_3_to_5_years",
            "gratuity_5_to_20_years",
            "gratuity_20_plus_years",
            "consider_unpaid_leave",
            "include_fixed_allowances",
            "include_variable_allowances",
            "include_last_bonus",
            "auto_deduct_loans",
            "auto_deduct_advances",
            "requires_hr_approval",
            "requires_director_approval",
        ]
        widgets = {
            "gratuity_less_than_3_years": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.001"}
            ),
            "gratuity_3_to_5_years": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.001"}
            ),
            "gratuity_5_to_20_years": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.001"}
            ),
            "gratuity_20_plus_years": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.001"}
            ),
            "consider_unpaid_leave": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "include_fixed_allowances": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "include_variable_allowances": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "include_last_bonus": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "auto_deduct_loans": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "auto_deduct_advances": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "requires_hr_approval": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "requires_director_approval": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }


class EndOfServiceBenefitForm(forms.ModelForm):
    """Form for calculating and recording End-of-Service Benefits"""

    class Meta:
        model = EndOfServiceBenefit
        fields = [
            "employee",
            "separation_date",
            "separation_reason",
            "initial_employment_date",
            "basic_salary",
            "monthly_fixed_allowances",
            "monthly_variable_allowances",
            "last_year_annual_bonus",
            "unpaid_leave_days",
            "outstanding_loan_balance",
            "outstanding_advance",
            "salary_adjustments",
            "other_deductions",
            "notes",
        ]
        widgets = {
            "employee": forms.Select(attrs={"class": "form-control"}),
            "separation_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "separation_reason": forms.Select(attrs={"class": "form-control"}),
            "initial_employment_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "basic_salary": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "monthly_fixed_allowances": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "monthly_variable_allowances": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "last_year_annual_bonus": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "unpaid_leave_days": forms.NumberInput(
                attrs={"class": "form-control", "min": "0"}
            ),
            "outstanding_loan_balance": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "outstanding_advance": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "salary_adjustments": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "other_deductions": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ServiceAwardForm(forms.ModelForm):
    """Form for recording service awards"""

    class Meta:
        model = ServiceAward
        fields = ["employee", "award_type", "award_date", "award_amount", "description"]
        widgets = {
            "employee": forms.Select(attrs={"class": "form-control"}),
            "award_type": forms.Select(attrs={"class": "form-control"}),
            "award_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "award_amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


# ============= WPS FORMS =============


class WPSGlobalSettingsForm(forms.ModelForm):
    """Form for WPS Global Settings"""

    class Meta:
        model = WPSGlobalSettings
        fields = [
            "company_bank_name",
            "company_bank_code",
            "company_bank_account_number",
            "company_bank_account_iban",
            "company_cr_number",
            "company_wps_code",
            "enable_wps_processing",
            "wps_submission_frequency",
            "wps_format_version",
            "auto_generate_wps_file",
            "include_end_of_service",
            "include_loans",
            "requires_director_approval",
            "digital_signature_required",
        ]
        widgets = {
            "company_bank_name": forms.TextInput(attrs={"class": "form-control"}),
            "company_bank_code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., NBOMOM"}
            ),
            "company_bank_account_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "company_bank_account_iban": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "company_cr_number": forms.TextInput(attrs={"class": "form-control"}),
            "company_wps_code": forms.TextInput(attrs={"class": "form-control"}),
            "enable_wps_processing": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "wps_submission_frequency": forms.Select(attrs={"class": "form-control"}),
            "wps_format_version": forms.Select(attrs={"class": "form-control"}),
            "auto_generate_wps_file": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "include_end_of_service": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "include_loans": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "requires_director_approval": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "digital_signature_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }


# ============= CV SCREENING FORMS =============


class CVParsingSettingsForm(forms.ModelForm):
    """Form for CV Parsing Settings"""

    class Meta:
        model = CVParsingSettings
        fields = [
            "enable_ai_screening",
            "auto_parse_cv",
            "auto_rank_candidates",
            "pdf_parser_engine",
            "ocr_enabled",
            "skill_match_weight",
            "experience_weight",
            "education_weight",
            "location_weight",
            "min_skill_match_percentage",
            "min_overall_score",
            "auto_shortlist_above_score",
            "auto_reject_below_score",
        ]
        widgets = {
            "enable_ai_screening": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "auto_parse_cv": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "auto_rank_candidates": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "pdf_parser_engine": forms.Select(attrs={"class": "form-control"}),
            "ocr_enabled": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "skill_match_weight": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "1"}
            ),
            "experience_weight": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "1"}
            ),
            "education_weight": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "1"}
            ),
            "location_weight": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "1"}
            ),
            "min_skill_match_percentage": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "max": "100"}
            ),
            "min_overall_score": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "max": "100"}
            ),
            "auto_shortlist_above_score": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "max": "100"}
            ),
            "auto_reject_below_score": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "max": "100"}
            ),
        }
