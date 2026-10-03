"""
fits_audit sidebar configuration
"""

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as trans

MENU = trans("Audit & Compliance")
IMG_SRC = "images/ui/report.svg"
ACCESSIBILITY = "fits_audit.sidebar.menu_accessibility"

SUBMENUS = [
    {
        "menu": trans("Audit Dashboard"),
        "redirect": reverse_lazy("fits_audit:audit-dashboard"),
        "accessibility": "fits_audit.sidebar.audit_dashboard_accessibility",
    },
]


def menu_accessibility(request, submenu, user_perms, *args, **kwargs):
    """Check if user can access Audit menu"""
    return request.user.is_superuser or request.user.has_perm("base.view_company")


def audit_dashboard_accessibility(request, submenu, user_perms, *args, **kwargs):
    """Check if user can access Audit Dashboard"""
    return request.user.is_superuser or request.user.has_perm("base.view_company")
