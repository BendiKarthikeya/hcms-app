"""
talent/sidebar.py

To set Fits sidebar for Talent & Succession Planning module
"""

from django.urls import reverse
from django.utils.translation import gettext_lazy as trans

MENU = trans("Talent & Succession")
IMG_SRC = "images/ui/talent.svg"

SUBMENUS = [
    {
        "menu": trans("Dashboard"),
        "redirect": reverse("talent:dashboard"),
    },
    {
        "menu": trans("Talent Profiles"),
        "redirect": reverse("talent:profile_list"),
    },
    {
        "menu": trans("Critical Roles"),
        "redirect": reverse("talent:critical_role_list"),
    },
    {
        "menu": trans("Succession Plans"),
        "redirect": reverse("talent:succession_plan_list"),
    },
    {
        "menu": trans("My Talent Profile"),
        "redirect": reverse("talent:my_profile"),
    },
    {
        "menu": trans("Succession Planning"),
        "redirect": "/talent/succession/",
    },
    {
        "menu": trans("9-Box Matrix"),
        "redirect": "/talent/9-box-matrix/",
    },
    {
        "menu": trans("Career Paths"),
        "redirect": "/talent/career-paths/",
    },
    {
        "menu": trans("IDP Generation"),
        "redirect": "/talent/idp/",
    },
    {
        "menu": trans("High-Potential Tracking"),
        "redirect": "/talent/high-potential/",
    },
]
