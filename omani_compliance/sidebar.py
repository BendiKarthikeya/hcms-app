"""
omani_compliance/sidebar.py

To set Fits sidebar for Omani Labour Law Compliance module
"""

from django.urls import reverse
from django.utils.translation import gettext_lazy as trans

MENU = trans("Omani Compliance")
IMG_SRC = "images/ui/compliance.svg"

SUBMENUS = [
    {
        "menu": trans("Configuration"),
        "redirect": reverse("omani_compliance:omani_config"),
    },
    {
        "menu": trans("Compliance Audit"),
        "redirect": reverse("omani_compliance:omani_audit"),
    },
    {
        "menu": trans("Tax Calculations"),
        "redirect": reverse("omani_compliance:omani_tax_calculations"),
    },
    {
        "menu": trans("Compliance Reports"),
        "redirect": reverse("omani_compliance:omani_compliance_report"),
    },
]
