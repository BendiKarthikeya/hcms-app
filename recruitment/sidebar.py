"""
recruitment/sidebar.py

To set Fits sidebar for onboarding
"""

from django.contrib.auth.context_processors import PermWrapper
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from recruitment.models import InterviewSchedule
from recruitment.templatetags.recruitmentfilters import (
    is_recruitmentmangers,
    is_stagemanager,
)

MENU = _("Recruitment")
ACCESSIBILITY = "recruitment.sidebar.menu_accessibility"
IMG_SRC = "images/ui/recruitment.svg"

SUBMENUS = [
    {
        "menu": _("Dashboard"),
        "redirect": reverse("recruitment-dashboard"),
    },
    {
        "menu": _("Recruitment Pipeline"),
        "redirect": reverse("pipeline"),
        "accessibility": "recruitment.sidebar.pipeline_accessibility",
    },
    {
        "menu": _("Create Candidate"),
        "redirect": reverse("candidate-create"),
        "accessibility": "recruitment.sidebar.create_candidate_accessibility",
    },
    {
        "menu": _("Candidates"),
        "redirect": reverse("candidate-dashboard"),
        "accessibility": "recruitment.sidebar.candidates_accessibility",
    },
    {
        "menu": _("CV Upload"),
        "redirect": reverse("cv-upload-single"),
        "accessibility": "recruitment.sidebar.create_candidate_accessibility",
    },
    {
        "menu": _("Recruitment Survey"),
        "redirect": reverse("recruitment-survey-question-template-view"),
        "accessibility": "recruitment.sidebar.survey_accessibility",
    },
    {
        "menu": _("Interview"),
        "redirect": reverse("interview-view"),
        "accessibility": "recruitment.sidebar.interview_accessibility",
    },
    {
        "menu": _("Recruitment"),
        "redirect": reverse("recruitment-view"),
        "accessibility": "recruitment.sidebar.recruitment_accessibility",
    },
    {
        "menu": _("Received Recruitments"),
        "redirect": reverse("received-recruitments"),
        "accessibility": "recruitment.sidebar.received_recruitments_accessibility",
    },
    
    {
        "menu": _("Open Jobs"),
        "redirect": reverse("open-recruitments"),
        "accessibility": "recruitment.sidebar.recruitment_accessibility",
    },
    {
        "menu": _("Stages"),
        "redirect": reverse("rec-stage-view"),
        "accessibility": "recruitment.sidebar.stage_accessibility",
    },
    {
        "menu": _("Skill Zone"),
        "redirect": reverse("skill-zone-view"),
        "accessibility": "recruitment.sidebar.skill_zone_accessibility",
    },
    {
        "menu": _("Employment Proposals"),
        "redirect": reverse("proposal-list"),
        "accessibility": "recruitment.sidebar.proposals_accessibility",
    },
]


def proposals_accessibility(
    request, _submenu: dict = {}, user_perms: PermWrapper = [], *args, **kwargs
) -> bool:
    if request.user.is_superuser or request.user.has_perm(
        "recruitment.view_employmentproposal"
    ):
        return True
    employee = getattr(request.user, "employee_get", None)
    if employee is None:
        return False
    from recruitment.models_proposal import ProposalApproval
    return ProposalApproval.objects.filter(
        approver=employee, status="pending"
    ).exists()


def menu_accessibility(
    request, _menu: str = "", user_perms: PermWrapper = [], *args, **kwargs
) -> bool:
    if (
        request.user.is_superuser
        or is_stagemanager(request.user)
        or "recruitment" in user_perms
        or request.user.has_perm("recruitment.view_recruitment")
        or request.user.has_perm("recruitment.add_recruitment")
    ):
        return True
    employee = getattr(request.user, "employee_get", None)
    if employee is None:
        return False
    from recruitment.models import RecruitmentApproval
    return RecruitmentApproval.objects.filter(
        approver=employee, status="pending"
    ).exists()


def pipeline_accessibility(
    request, _submenu: dict = {}, user_perms: PermWrapper = [], *args, **kwargs
) -> bool:
    _submenu["redirect"] = _submenu["redirect"] + "?closed=false"
    return is_stagemanager(request.user) or request.user.has_perm(
        "recruitment.view_recruitment"
    )


def candidates_accessibility(
    request, _submenu: dict = {}, user_perms: PermWrapper = [], *args, **kwargs
) -> bool:
    return request.user.has_perm("recruitment.view_candidate")


def create_candidate_accessibility(
    request, _submenu: dict = {}, user_perms: PermWrapper = [], *args, **kwargs
) -> bool:
    return request.user.has_perm("recruitment.add_candidate")


def survey_accessibility(
    request, _submenu: dict = {}, user_perms: PermWrapper = [], *args, **kwargs
) -> bool:
    _submenu["redirect"] = _submenu["redirect"] + "?closed=false"
    return is_recruitmentmangers(request.user) or request.user.has_perm(
        "recruitment.view_recruitmentsurvey"
    )


def recruitment_accessibility(
    request, _submenu: dict = {}, user_perms: PermWrapper = [], *args, **kwargs
) -> bool:
    return request.user.has_perm("recruitment.view_recruitment")


def received_recruitments_accessibility(
    request, _submenu: dict = {}, user_perms: PermWrapper = [], *args, **kwargs
) -> bool:
    if request.user.has_perm("recruitment.view_recruitment"):
        return True
    employee = getattr(request.user, "employee_get", None)
    if employee is None:
        return False
    from recruitment.models import RecruitmentApproval
    return RecruitmentApproval.objects.filter(
        approver=employee, status="pending"
    ).exists()


def interview_accessibility(
    request, _submenu: dict = {}, user_perms: PermWrapper = [], *args, **kwargs
) -> bool:
    if request.user.has_perm("recruitment.view_interviewschedule"):
        return True
    employee = getattr(request.user, "employee_get", None)
    if employee is None:
        return False
    return InterviewSchedule.objects.filter(employee_id=employee).exists()


def stage_accessibility(
    request, _submenu: dict = {}, user_perms: PermWrapper = [], *args, **kwargs
) -> bool:
    return request.user.has_perm("recruitment.view_stage")


def skill_zone_accessibility(
    request, _submenu: dict = {}, user_perms: PermWrapper = [], *args, **kwargs
) -> bool:
    return is_stagemanager(request.user) or request.user.has_perm(
        "recruitment.view_skillzone"
    )


def dashboard_accessibility(request, submenu, user_perms, *args, **kwargs):
    return (
        request.user.is_superuser
        or is_stagemanager(request.user)
        or "recruitment" in user_perms
        or request.user.has_perm("recruitment.view_recruitment")
    )


# --- FEATURE UI MAPPING ADDITIONS ---
from django.utils.translation import gettext_lazy as trans
SUBMENUS += [
    { "menu": trans("Offer Approval Inbox"), "redirect": "/recruitment/offers/approval-inbox/" },
    { "menu": trans("Approval Rules"), "redirect": "/recruitment/approvals/rules/" },
    { "menu": trans("Bulk Import Candidates"), "redirect": "/recruitment/bulk-import/candidates/" },
    { "menu": trans("Offer Tracking"), "redirect": "/recruitment/offer-tracking/" },
    { "menu": trans("Reports"), "redirect": "/recruitment/reports/" },
    { "menu": trans("Career Page"), "redirect": "/recruitment/careers/" },
    { "menu": trans("CV Screening"), "redirect": "/recruitment/cv-screening/" },
    { "menu": trans("Document Search"), "redirect": "/recruitment/document-search/" },
]

