"""
pms/sidebar.py
"""

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as trans

from base.templatetags.basefilters import is_reportingmanager

MENU = trans("Performance")
IMG_SRC = "images/ui/pms.svg"


SUBMENUS = [
    {
        "menu": trans("Dashboard"),
        "redirect": reverse_lazy("dashboard-view"),
    },
    {
        "menu": trans("Objectives & KPIs"),
        "redirect": reverse_lazy("objective-list-view"),
    },
    {
        "menu": trans("Goal Tracking (Key Results)"),
        "redirect": reverse_lazy("view-key-result"),
    },
    {
        "menu": trans("360-Degree Feedback"),
        "redirect": reverse_lazy("feedback-view"),
    },
    {
        "menu": trans("Performance Ratings"),
        "redirect": reverse_lazy("performance-rating-view"),
    },
    {
        "menu": trans("Competency Framework"),
        "redirect": reverse_lazy("question-template-view"),
    },
    {
        "menu": trans("Appraisal Meetings (1-on-1s)"),
        "redirect": reverse_lazy("view-meetings"),
    },
    {
        "menu": trans("Review Cycles"),
        "redirect": reverse_lazy("period-view"),
    },
    {
        "menu": trans("PIP Management"),
        "redirect": reverse_lazy("pip-list"),
    },
    {
        "menu": trans("Employee Bonus Point"),
        "redirect": reverse_lazy("employee-bonus-point"),
    },
]


def key_result_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("pms.view_keyresult")


def performance_rating_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("pms.view_performancerating")


def period_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("pms.view_period") or is_reportingmanager(request.user)


def question_template_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("pms.view_questiontemplate") or is_reportingmanager(
        request.user
    )


def pip_accessibility(request, submenu, user_perms, *args, **kwargs):
    return (
        request.user.has_perm("pms.view_performanceimprovementplanworkflow")
        or request.user.has_perm("pms.add_performanceimprovementplanworkflow")
        or is_reportingmanager(request.user)
    )
