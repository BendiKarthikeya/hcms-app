"""
fits/config.py

Fits app configurations
"""

import importlib
import logging

from django.apps import apps
from django.contrib.auth.context_processors import PermWrapper

from fits.fits_apps import SIDEBARS

logger = logging.getLogger(__name__)


def get_apps_in_base_dir():
    return SIDEBARS


def import_method(accessibility):
    module_path, method_name = accessibility.rsplit(".", 1)
    module = __import__(module_path, fromlist=[method_name])
    accessibility_method = getattr(module, method_name)
    return accessibility_method


ALL_MENUS = {}

SUPERUSER_SIDEBAR_APPS = {
    "attendance",
    "employee",
    "leave",
    "project",
    "report",
    "asset",
    "pms",
    "expenses",
    "helpdesk",
    "omani_compliance",
    "fits_audit",
    "recruitment",
    "onboarding",
}

HR_SIDEBAR_APPS = {
    "learning",
    "talent",
    "recruitment",
    "pms",
    "onboarding",
    "offboarding",
    "payroll",
}

REGULAR_EMPLOYEE_SIDEBAR_APPS = {
    "recruitment",
    "onboarding",
    "employee",
    "attendance",
    "leave",
    "offboarding",
    "project",
    "expenses",
    "report",
    "fits_audit",
}


def _is_hr_staff_user(user):
    employee = getattr(user, "employee_get", None)
    if employee is None:
        return False

    from base.models import HRUser

    return HRUser.objects.filter(employee=employee, is_hr_staff=True).exists()


def _get_role_based_sidebar_apps(request, base_dir_apps):
    if _is_hr_staff_user(request.user):
        allowed_apps = HR_SIDEBAR_APPS
        return [app for app in base_dir_apps if app in allowed_apps]

    if request.user.is_superuser:
        allowed_apps = SUPERUSER_SIDEBAR_APPS
        return [app for app in base_dir_apps if app in allowed_apps]

    if not request.user.has_perm("employee.view_employee"):
        allowed_apps = REGULAR_EMPLOYEE_SIDEBAR_APPS
        return [app for app in base_dir_apps if app in allowed_apps]

    return base_dir_apps


def sidebar(request):

    base_dir_apps = get_apps_in_base_dir()

    if not request.user.is_anonymous:
        base_dir_apps = _get_role_based_sidebar_apps(request, base_dir_apps)
        request.MENUS = []
        MENUS = request.MENUS

        for app in base_dir_apps:
            if apps.is_installed(app):
                try:
                    sidebar = importlib.import_module(app + ".sidebar")

                except Exception as e:
                    logger.error(e)
                    continue

                if sidebar:
                    accessibility = None
                    if getattr(sidebar, "ACCESSIBILITY", None):
                        accessibility = import_method(sidebar.ACCESSIBILITY)

                    if not accessibility or accessibility(
                        request,
                        sidebar.MENU,
                        PermWrapper(request.user),
                    ):
                        MENU = {}
                        MENU["menu"] = sidebar.MENU
                        MENU["app"] = app
                        MENU["img_src"] = sidebar.IMG_SRC
                        MENU["submenu"] = []
                        MENUS.append(MENU)
                        for submenu in sidebar.SUBMENUS:
                            accessibility = None

                            if submenu.get("accessibility"):
                                accessibility = import_method(submenu["accessibility"])
                            redirect: str = submenu["redirect"]
                            redirect = redirect.split("?")
                            submenu["redirect"] = redirect[0]

                            if not accessibility or accessibility(
                                request,
                                submenu,
                                PermWrapper(request.user),
                            ):
                                MENU["submenu"].append(submenu)
        ALL_MENUS[request.session.session_key] = MENUS


def get_MENUS(request):
    ALL_MENUS[request.session.session_key] = []
    sidebar(request)
    return {"sidebar": ALL_MENUS.get(request.session.session_key)}
