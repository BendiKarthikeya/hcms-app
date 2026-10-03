"""
payroll/sidebar.py

"""

from django.urls import reverse
from django.utils.translation import gettext_lazy as trans

MENU = trans("Payroll")
IMG_SRC = "images/ui/wallet-outline.svg"

SUBMENUS = [
    {
        "menu": trans("Dashboard"),
        "redirect": reverse("view-payroll-dashboard"),
        "accessibility": "payroll.sidebar.dasbhoard_accessibility",
    },
    {
        "menu": trans("Contract"),
        "redirect": reverse("view-contract"),
        "accessibility": "payroll.sidebar.dasbhoard_accessibility",
    },
    {
        "menu": trans("Allowances"),
        "redirect": reverse("view-allowance"),
        "accessibility": "payroll.sidebar.allowance_accessibility",
    },
    {
        "menu": trans("Deductions"),
        "redirect": reverse("view-deduction"),
        "accessibility": "payroll.sidebar.deduction_accessibility",
    },
    {
        "menu": trans("Payslips"),
        "redirect": reverse("view-payslip"),
    },
    {
        "menu": trans("Loan / Advanced Salary"),
        "redirect": reverse("view-loan"),
        "accessibility": "payroll.sidebar.loan_accessibility",
    },
    {
        "menu": trans("Encashments & Reimbursements"),
        "redirect": reverse("view-reimbursement"),
    },
    {
        "menu": trans("Federal Tax"),
        "redirect": reverse("filing-status-view"),
        "accessibility": "payroll.sidebar.federal_tax_accessibility",
    },
    {
        "menu": trans("End-of-Service Benefits"),
        "redirect": reverse("eosb-list"),
        "accessibility": "payroll.sidebar.eosb_accessibility",
    },
    {
        "menu": trans("EOSB Dashboard"),
        "redirect": reverse("eosb-dashboard"),
        "accessibility": "payroll.sidebar.eosb_accessibility",
    },
    {
        "menu": trans("Wage Protection System"),
        "redirect": reverse("wps-file-list"),
        "accessibility": "payroll.sidebar.wps_accessibility",
    },
    {
        "menu": trans("WPS Dashboard"),
        "redirect": reverse("wps-dashboard"),
        "accessibility": "payroll.sidebar.wps_accessibility",
    },
]


def dasbhoard_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("payroll.view_contract")


def allowance_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("payroll.view_allowance")


def deduction_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("payroll.view_deduction")


def loan_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("payroll.view_loanaccount")


def federal_tax_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("payroll.view_filingstatus")


def eosb_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm(
        "payroll.view_employeegratuity"
    ) or request.user.has_perm("payroll.add_employeegratuity")


def wps_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm(
        "payroll.view_wpsfilegeneration"
    ) or request.user.has_perm("payroll.add_wpsfilegeneration")


SUBMENUS += [
    {
        "menu": trans("ICBS Disbursement"),
        "redirect": reverse("icbs-integration"),
    },
    {
        "menu": trans("GL Integration"),
        "redirect": reverse("gl-integration"),
    },
]
