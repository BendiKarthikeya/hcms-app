"""
context_processor.py

This module is used to register context processor`
"""

import re

from django.apps import apps
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from base.models import Company, TrackLateComeEarlyOut
from base.urls import urlpatterns
from employee.models import (
    Employee,
    EmployeeGeneralSetting,
    ProfileEditFeature,
)
from fits import fits_apps
from fits.decorators import hx_request_required, login_required, permission_required
from fits.methods import get_fits_model_class


class AllCompany:
    """
    Dummy class
    """

    class Urls:
        url = "https://ui-avatars.com/api/?name=All+Company&background=random"

    company = "All Company"
    icon = Urls()
    text = "All companies"
    id = None


def get_last_section(path):
    # Remove any trailing slash and split the path
    segments = path.strip("/").split("/")

    # Get the last section (the ID)
    last_section = segments[-1] if segments else None
    return last_section


def get_companies(request):
    """
    This method will return the history additional field form
    """
    # Cache the company list (DB query) but still compute selected state per request
    companies = cache.get("ctx_all_companies")
    if companies is None:
        def _icon_url(company):
            initial = (company.company or "C")[0].upper()
            fallback = f"https://ui-avatars.com/api/?name={initial}&background=16A34A&color=fff"
            return company.icon.url if company.icon.name else fallback

        companies = list(
            [company.id, company.company, _icon_url(company), False]
            for company in Company.objects.all()
        )
        companies = [
            [
                "all",
                "All Company",
                "https://ui-avatars.com/api/?name=All+Company&background=random",
                False,
            ],
        ] + companies
        cache.set("ctx_all_companies", companies, 120)
    else:
        # Reset selection state on cached copy
        companies = [[c[0], c[1], c[2], False] for c in companies]
    selected_company = request.session.get("selected_company")
    company_selected = False
    if selected_company and selected_company == "all":
        companies[0][3] = True
        company_selected = True
    else:
        for company in companies:
            if str(company[0]) == selected_company:
                company[3] = True
                company_selected = True
    return {"all_companies": companies, "company_selected": company_selected}


@login_required
@hx_request_required
@permission_required("base.change_company")
def update_selected_company(request):
    """
    This method is used to update the selected company on the session
    """
    company_id = request.GET.get("company_id")
    user = request.user.employee_get
    user_company = getattr(
        getattr(user, "employee_work_info", None), "company_id", None
    )
    request.session["selected_company"] = company_id
    company = (
        AllCompany()
        if company_id == "all"
        else (
            Company.objects.filter(id=company_id).first()
            if Company.objects.filter(id=company_id).first()
            else AllCompany()
        )
    )
    previous_path = request.GET.get("next", "/")
    # Define the regex pattern for the path
    pattern = r"^/employee/employee-view/\d+/$"
    # Check if the previous path matches the pattern
    if company_id != "all":
        if re.match(pattern, previous_path):
            employee_id = get_last_section(previous_path)
            employee = Employee.objects.filter(id=employee_id).first()
            emp_company = getattr(
                getattr(employee, "employee_work_info", None), "company_id", None
            )
            if emp_company != company:
                text = "Other Company"
                if company_id == user_company:
                    text = "My Company"
                company = {
                    "company": company.company,
                    "icon": company.icon.url,
                    "text": text,
                    "id": company.id,
                }
                messages.error(
                    request, _("Employee is not working in the selected company.")
                )
                request.session["selected_company_instance"] = company
                return HttpResponse(
                    f"""
                    <script>window.location.href = `{reverse("employee-view")}`</script>
                """
                )

    if company_id == "all":
        text = "All companies"
    elif company_id == user_company:
        text = "My Company"
    else:
        text = "Other Company"

    company = {
        "company": company.company,
        "icon": company.icon.url,
        "text": text,
        "id": company.id,
    }
    request.session["selected_company_instance"] = company
    return HttpResponse("<script>window.location.reload();</script>")


urlpatterns.append(
    path(
        "update-selected-company",
        update_selected_company,
        name="update-selected-company",
    )
)


def white_labelling_company(request):
    white_labelling = getattr(fits_apps, "WHITE_LABELLING", False)
    if white_labelling:
        hq = Company.objects.filter(hq=True).last()
        try:
            company = (
                request.user.employee_get.get_company()
                if request.user.employee_get.get_company()
                else hq
            )
        except:
            company = hq

        return {
            "white_label_company_name": company.company if company else "FITS HCMS",
            "white_label_company": company,
        }
    else:
        return {
            "white_label_company_name": "FITS HCMS",
            "white_label_company": None,
        }


def resignation_request_enabled(request):
    """
    Check weather resignation_request enabled of not in offboarding
    """
    cached = cache.get("ctx_resignation_request_enabled")
    if cached is not None:
        return cached
    enabled_resignation_request = False
    first = None
    if apps.is_installed("offboarding"):
        OffboardingGeneralSetting = get_fits_model_class(
            app_label="offboarding", model="offboardinggeneralsetting"
        )
        first = OffboardingGeneralSetting.objects.first()
    if first:
        enabled_resignation_request = first.resignation_request
    result = {"enabled_resignation_request": enabled_resignation_request}
    cache.set("ctx_resignation_request_enabled", result, 120)
    return result


def timerunner_enabled(request):
    """
    Check weather resignation_request enabled of not in offboarding
    """
    cached = cache.get("ctx_timerunner_enabled")
    if cached is not None:
        return cached
    first = None
    enabled_timerunner = True
    if apps.is_installed("attendance"):
        AttendanceGeneralSetting = get_fits_model_class(
            app_label="attendance", model="attendancegeneralsetting"
        )
        first = AttendanceGeneralSetting.objects.first()
    if first:
        enabled_timerunner = first.time_runner
    result = {"enabled_timerunner": enabled_timerunner}
    cache.set("ctx_timerunner_enabled", result, 120)
    return result


def intial_notice_period(request):
    """
    Check weather resignation_request enabled of not in offboarding
    """
    cached = cache.get("ctx_initial_notice_period")
    if cached is not None:
        return cached
    initial = 30
    first = None
    if apps.is_installed("payroll"):
        PayrollGeneralSetting = get_fits_model_class(
            app_label="payroll", model="payrollgeneralsetting"
        )
        first = PayrollGeneralSetting.objects.first()
    if first:
        initial = first.notice_period
    result = {"get_initial_notice_period": initial}
    cache.set("ctx_initial_notice_period", result, 120)
    return result


def check_candidate_self_tracking(request):
    """
    This method is used to get the candidate self tracking is enabled or not
    """
    cached = cache.get("ctx_candidate_self_tracking")
    if cached is not None:
        return cached
    candidate_self_tracking = False
    if apps.is_installed("recruitment"):
        RecruitmentGeneralSetting = get_fits_model_class(
            app_label="recruitment", model="recruitmentgeneralsetting"
        )
        first = RecruitmentGeneralSetting.objects.first()
    else:
        first = None
    if first:
        candidate_self_tracking = first.candidate_self_tracking
    result = {"check_candidate_self_tracking": candidate_self_tracking}
    cache.set("ctx_candidate_self_tracking", result, 120)
    return result


def check_candidate_self_tracking_rating(request):
    """
    This method is used to check enabled/disabled of rating option
    """
    cached = cache.get("ctx_candidate_self_tracking_rating")
    if cached is not None:
        return cached
    rating_option = False
    if apps.is_installed("recruitment"):
        RecruitmentGeneralSetting = get_fits_model_class(
            app_label="recruitment", model="recruitmentgeneralsetting"
        )
        first = RecruitmentGeneralSetting.objects.first()
    else:
        first = None
    if first:
        rating_option = first.show_overall_rating
    result = {"check_candidate_self_tracking_rating": rating_option}
    cache.set("ctx_candidate_self_tracking_rating", result, 120)
    return result


def get_initial_prefix(request):
    """
    This method is used to get the initial prefix
    """
    cached = cache.get("ctx_initial_prefix")
    if cached is not None:
        return cached
    settings = EmployeeGeneralSetting.objects.first()
    instance_id = None
    prefix = "PEP"
    if settings:
        instance_id = settings.id
        prefix = settings.badge_id_prefix
    result = {"get_initial_prefix": prefix, "prefix_instance_id": instance_id}
    cache.set("ctx_initial_prefix", result, 120)
    return result


def biometric_app_exists(request):
    from django.conf import settings

    biometric_app_exists = "biometric" in settings.INSTALLED_APPS
    return {"biometric_app_exists": biometric_app_exists}


def enable_late_come_early_out_tracking(request):
    cached = cache.get("ctx_late_come_early_out_tracking")
    if cached is not None:
        return cached
    tracking = TrackLateComeEarlyOut.objects.first()
    enable = tracking.is_enable if tracking else True
    result = {"tracking": enable, "late_come_early_out_tracking": enable}
    cache.set("ctx_late_come_early_out_tracking", result, 120)
    return result


def enable_profile_edit(request):
    from accessibility.accessibility import ACCESSBILITY_FEATURE

    cached = cache.get("ctx_enable_profile_edit")
    if cached is not None:
        return cached
    profile_edit = ProfileEditFeature.objects.filter().first()
    enable = True if profile_edit and profile_edit.is_enabled else False
    if enable:
        if not any(item[0] == "profile_edit" for item in ACCESSBILITY_FEATURE):
            ACCESSBILITY_FEATURE.append(("profile_edit", _("Profile Edit Access")))
    result = {"profile_edit_enabled": enable}
    cache.set("ctx_enable_profile_edit", result, 120)
    return result
