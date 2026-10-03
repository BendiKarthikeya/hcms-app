"""
expenses/sidebar.py

To set Fits sidebar for Expenses & Travel Management module
"""

from django.urls import reverse
from django.utils.translation import gettext_lazy as trans

MENU = trans("Expenses & Travel")
IMG_SRC = "images/ui/expenses.svg"

SUBMENUS = [
    {
        "menu": trans("Dashboard"),
        "redirect": reverse("expenses:dashboard"),
    },
    {
        "menu": trans("Travel Requests"),
        "redirect": reverse("expenses:travel_request_list"),
    },
    {
        "menu": trans("Expense Claims"),
        "redirect": reverse("expenses:expense_claim_list"),
    },
    {
        "menu": trans("My Travel Requests"),
        "redirect": reverse("expenses:my_travel_requests"),
    },
    {
        "menu": trans("My Expense Claims"),
        "redirect": reverse("expenses:my_expense_claims"),
    },
    {
        "menu": trans("Expense Categories"),
        "redirect": reverse("expenses:category_list"),
    },
]
