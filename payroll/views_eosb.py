"""
Views for End-of-Service Benefits (EOSB) and Gratuity Calculation
"""
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from datetime import date
from decimal import Decimal
import csv

from payroll.models.models_eosb import (
    EndOfServiceBenefit,
    EOSBGratuitySettings,
    ServiceAward,
)
from base.forms_new_features.forms_new_features import (
    EndOfServiceBenefitForm,
    EOSBGratuitySettingsForm,
    ServiceAwardForm,
)
from employee.models import Employee
from base.models import Company


# ============= EOSB SETTINGS VIEWS =============


@login_required
def eosb_settings(request):
    """Configure EOSB/Gratuity settings"""
    company = Company.objects.first()
    if not company:
        messages.error(request, _("No company configured"))
        return redirect("dashboard")
    settings, created = EOSBGratuitySettings.objects.get_or_create(company=company)

    if request.method == "POST":
        form = EOSBGratuitySettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, _("EOSB Settings updated successfully"))
            return redirect("eosb-settings")
    else:
        form = EOSBGratuitySettingsForm(instance=settings)

    context = {
        "form": form,
        "settings": settings,
        "page_title": _("EOSB Gratuity Settings"),
    }
    return render(request, "payroll/eosb/settings.html", context)


# ============= EOSB CALCULATION VIEWS =============


@login_required
def eosb_list(request):
    """List all End-of-Service Benefit records"""
    company = Company.objects.first()
    if not company:
        messages.error(request, _("No company configured"))
        return redirect("dashboard")
    eosblist = EndOfServiceBenefit.objects.filter(company=company).select_related(
        "employee"
    )

    # Filters
    status = request.GET.get("status")
    search = request.GET.get("search")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if status:
        eosblist = eosblist.filter(status=status)
    if search:
        eosblist = eosblist.filter(
            Q(employee__first_name__icontains=search)
            | Q(employee__last_name__icontains=search)
            | Q(employee__employee_code__icontains=search)
        )
    if date_from:
        eosblist = eosblist.filter(separation_date__gte=date_from)
    if date_to:
        eosblist = eosblist.filter(separation_date__lte=date_to)

    # Summary Stats
    total_amount = (
        eosblist.aggregate(Sum("net_eosb_amount"))["net_eosb_amount__sum"] or 0
    )

    context = {
        "eosblist": eosblist,
        "total_amount": total_amount,
        "page_title": _("End-of-Service Benefits"),
        "statuses": EndOfServiceBenefit.STATUS_CHOICES,
    }
    return render(request, "payroll/eosb/eosb_list.html", context)


@login_required
def eosb_create(request):
    """Create new End-of-Service Benefit calculation"""
    company = Company.objects.first()
    if not company:
        messages.error(request, _("No company configured"))
        return redirect("dashboard")

    if request.method == "POST":
        form = EndOfServiceBenefitForm(request.POST)
        if form.is_valid():
            eosb = form.save(commit=False)
            eosb.company = company
            eosb.calculated_by = request.user.employee_get
            eosb.calculated_date = timezone.now()

            # Fetch settings and calculate
            settings = company.eosb_settings

            # Calculate months of service
            start_date = eosb.initial_employment_date
            end_date = eosb.separation_date
            delta = end_date - start_date
            eosb.total_months_of_service = Decimal(delta.days) / Decimal(30)
            eosb.total_years_of_service = eosb.total_months_of_service / 12

            # Calculate final monthly salary
            eosb.final_monthly_salary = (
                eosb.basic_salary
                + (
                    eosb.monthly_fixed_allowances
                    if settings.include_fixed_allowances
                    else 0
                )
                + (
                    eosb.monthly_variable_allowances
                    if settings.include_variable_allowances
                    else 0
                )
            )

            # Calculate gratuity
            eosb.calculate_gratuity()

            eosb.status = "calculated"
            eosb.save()

            messages.success(request, _("EOSB calculated successfully"))
            return redirect("eosb-detail", pk=eosb.pk)
    else:
        form = EndOfServiceBenefitForm()

    context = {
        "form": form,
        "page_title": _("Calculate End-of-Service Benefit"),
    }
    return render(request, "payroll/eosb/eosb_form.html", context)


@login_required
def eosb_detail(request, pk):
    """View EOSB details"""
    eosb = get_object_or_404(EndOfServiceBenefit, pk=pk)

    context = {
        "eosb": eosb,
        "page_title": f"{eosb.employee.get_name()} - EOSB Calculation",
    }
    return render(request, "payroll/eosb/eosb_detail.html", context)


@login_required
def eosb_approve(request, pk):
    """HR approval of EOSB calculation"""
    eosb = get_object_or_404(EndOfServiceBenefit, pk=pk)

    if eosb.status != "calculated":
        messages.error(request, _("Can only approve calculated records"))
        return redirect("eosb-detail", pk=pk)

    if request.method == "POST":
        eosb.status = "hr_approved"
        eosb.hr_approved_by = request.user.employee_get
        eosb.hr_approval_date = timezone.now()
        eosb.hr_comments = request.POST.get("comments", "")
        eosb.save()

        messages.success(request, _("EOSB approved by HR"))
        return redirect("eosb-detail", pk=pk)

    context = {
        "eosb": eosb,
        "page_title": _("HR Approve EOSB"),
    }
    return render(request, "payroll/eosb/eosb_approve.html", context)


@login_required
def eosb_director_approve(request, pk):
    """Director approval of EOSB calculation"""
    eosb = get_object_or_404(EndOfServiceBenefit, pk=pk)

    if eosb.status != "hr_approved":
        messages.error(request, _("Requires prior HR approval"))
        return redirect("eosb-detail", pk=pk)

    if request.method == "POST":
        eosb.status = "director_approved"
        eosb.director_approved_by = request.user.employee_get
        eosb.director_approval_date = timezone.now()
        eosb.director_comments = request.POST.get("comments", "")
        eosb.save()

        messages.success(request, _("EOSB approved by Director"))
        return redirect("eosb-detail", pk=pk)

    context = {
        "eosb": eosb,
        "page_title": _("Director Approve EOSB"),
    }
    return render(request, "payroll/eosb/eosb_director_approve.html", context)


@login_required
def eosb_mark_paid(request, pk):
    """Mark EOSB as paid"""
    eosb = get_object_or_404(EndOfServiceBenefit, pk=pk)

    if eosb.status != "director_approved":
        messages.error(request, _("Can only mark approved records as paid"))
        return redirect("eosb-detail", pk=pk)

    if request.method == "POST":
        eosb.status = "processed"
        eosb.paid_date = request.POST.get("paid_date", date.today())
        eosb.payment_method = request.POST.get("payment_method", "bank_transfer")
        eosb.payment_reference = request.POST.get("payment_reference", "")
        eosb.save()

        messages.success(request, _("EOSB marked as paid"))
        return redirect("eosb-detail", pk=pk)

    context = {
        "eosb": eosb,
        "page_title": _("Mark EOSB as Paid"),
    }
    return render(request, "payroll/eosb/eosb_mark_paid.html", context)


# ============= SERVICE AWARD VIEWS =============


@login_required
def service_award_list(request):
    """List service awards"""
    company = Company.objects.first()
    if not company:
        messages.error(request, _("No company configured"))
        return redirect("dashboard")
    awards = ServiceAward.objects.filter(company=company).select_related("employee")

    context = {
        "awards": awards,
        "page_title": _("Service Awards"),
        "award_types": ServiceAward.AWARD_CHOICES,
    }
    return render(request, "payroll/eosb/service_award_list.html", context)


@login_required
def service_award_create(request):
    """Create service award"""
    company = Company.objects.first()
    if not company:
        messages.error(request, _("No company configured"))
        return redirect("dashboard")

    if request.method == "POST":
        form = ServiceAwardForm(request.POST)
        if form.is_valid():
            award = form.save(commit=False)
            award.company = company
            award.save()
            messages.success(request, _("Service award recorded"))
            return redirect("service-award-list")
    else:
        form = ServiceAwardForm()

    context = {
        "form": form,
        "page_title": _("Record Service Award"),
    }
    return render(request, "payroll/eosb/service_award_form.html", context)


# ============= REPORTS & EXPORTS =============


@login_required
def eosb_report_export(request):
    """Export EOSB report as CSV"""
    company = Company.objects.first()
    if not company:
        messages.error(request, _("No company configured"))
        return redirect("dashboard")
    eosblist = EndOfServiceBenefit.objects.filter(company=company)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="eosb_report.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            _("Employee"),
            _("Separation Date"),
            _("Years of Service"),
            _("Basic Salary"),
            _("Gratuity Rate"),
            _("Gross Gratuity"),
            _("Total Deductions"),
            _("Net EOSB Amount"),
            _("Status"),
        ]
    )

    for eosb in eosblist:
        writer.writerow(
            [
                eosb.employee.get_name(),
                eosb.separation_date,
                eosb.total_years_of_service,
                eosb.basic_salary,
                eosb.applicable_gratuity_rate,
                eosb.gross_gratuity_amount,
                eosb.total_deductions,
                eosb.net_eosb_amount,
                eosb.get_status_display(),
            ]
        )

    return response


@login_required
def eosb_dashboard(request):
    """EOSB Dashboard"""
    company = Company.objects.first()
    if not company:
        messages.error(request, _("No company configured"))
        return redirect("dashboard")

    stats = {
        "total_eosbrecords": EndOfServiceBenefit.objects.filter(
            company=company
        ).count(),
        "pending_approval": EndOfServiceBenefit.objects.filter(
            company=company, status="hr_approved"
        ).count(),
        "total_paid": EndOfServiceBenefit.objects.filter(
            company=company, status="processed"
        ).aggregate(Sum("net_eosb_amount"))["net_eosb_amount__sum"]
        or 0,
        "pending_payment": EndOfServiceBenefit.objects.filter(
            company=company, status="director_approved"
        ).aggregate(Sum("net_eosb_amount"))["net_eosb_amount__sum"]
        or 0,
    }

    context = {
        "stats": stats,
        "page_title": _("EOSB & Gratuity Dashboard"),
    }
    return render(request, "payroll/eosb/eosb_dashboard.html", context)


from django.utils import timezone


@login_required
def eosb_bulk_calculate(request):
    """Bulk EOSB calculation for separations in a period"""
    company = Company.objects.first()
    if not company:
        messages.error(request, _("No company configured"))
        return redirect("dashboard")

    if request.method == "POST":
        date_from = request.POST.get("date_from")
        date_to = request.POST.get("date_to")

        # Get separated employees in date range
        separated_employees = Employee.objects.filter(
            company=company,
            employee_separation__separation_date__range=[date_from, date_to],
        )

        count = 0
        for emp in separated_employees:
            # Check if EOSB already calculated
            if not EndOfServiceBenefit.objects.filter(employee=emp).exists():
                # Create EOSB record
                eosb = EndOfServiceBenefit()
                eosb.employee = emp
                eosb.company = company
                # Populate with data and calculate
                eosb.save()
                count += 1
        
        messages.success(request, _("Bulk calculated {count} EOSB records", count=count))
        return redirect("eosb-list")

    context = {
        "page_title": _("Bulk Calculate EOSB"),
    }
    return render(request, "payroll/eosb/eosb_bulk_calculate.html", context)
