"""
learning/sidebar.py

To set Fits sidebar for Learning & Development module
"""

from django.urls import reverse
from django.utils.translation import gettext_lazy as trans

MENU = trans("Learning & Development")
IMG_SRC = "images/ui/learning.svg"

SUBMENUS = [
    {
        "menu": trans("Dashboard"),
        "redirect": reverse("learning:dashboard"),
    },
    {
        "menu": trans("Training Courses"),
        "redirect": reverse("learning:course_list"),
    },
    {
        "menu": trans("My Enrollments"),
        "redirect": reverse("learning:my_enrollments"),
    },
    {
        "menu": trans("My Skills"),
        "redirect": reverse("learning:my_skills"),
    },
    {
        "menu": trans("My Certifications"),
        "redirect": reverse("learning:my_certifications"),
    },
    {
        "menu": trans("My Learning Plans"),
        "redirect": reverse("learning:my_learning_plans"),
    },
    {
        "menu": trans("Assessments"),
        "redirect": reverse("learning:assessments"),
    },
    {
        "menu": trans("Leaderboards"),
        "redirect": reverse("learning:leaderboards"),
    },
    {
        "menu": trans("Sessions"),
        "redirect": reverse("learning:sessions"),
    },
    {
        "menu": trans("Trainers"),
        "redirect": reverse("learning:trainers"),
    },
    {
        "menu": trans("Integrations"),
        "redirect": reverse("learning:integrations"),
    },
]
