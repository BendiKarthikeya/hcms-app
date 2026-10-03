"""
Views for WPS (Wage Protection System) File Generation
Central Bank of Oman compliance
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from datetime import date
import io
import csv

from payroll.models.models_wps import (
    WPSPeriodicFile,
    WPSGlobalSettings,
    WPSAuditLog,
    WPSPaymentException,
)
from base.forms_new_features.forms_new_features import WPSGlobalSettingsForm
from payroll.models.models import Payslip
from base.models import Company


# ============= WPS SETTINGS VIEWS =============


@login_required
def wps_global_settings(request):
    """Configure global WPS settings"""
    # Get first company for now (simplified)
    company = Company.objects.first()
    if not company:
        messages.error(request, _("No company configured"))
        return redirect("dashboard")
    settings, created = WPSGlobalSettings.objects.get_or_create(company=company)

    if request.method == "POST":
        form = WPSGlobalSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, _("WPS Settings updated successfully"))
            return redirect("wps-global-settings")
    else:
        form = WPSGlobalSettingsForm(instance=settings)

    context = {
        "form": form,
        "settings": settings,
        "page_title": _("WPS Global Settings"),
    }
    return render(request, "payroll/wps/global_settings.html", context)


# ============= WPS FILE MANAGEMENT VIEWS =============


@login_required
def wps_file_list(request):
    """List all WPS files"""
    # Get first company for now (simplified)
    company = Company.objects.first()
    if not company:
        wps_files = WPSPeriodicFile.objects.none()
    else:
        wps_files = WPSPeriodicFile.objects.filter(company=company).order_by(
            "-payment_date"
        )

    # Filters
    status = request.GET.get("status")
    search = request.GET.get("search")

    if status:
        wps_files = wps_files.filter(status=status)
    if search:
        wps_files = wps_files.filter(
            Q(payroll_period__icontains=search)
            | Q(file_reference_number__icontains=search)
        )

    # Summary
    total_amount = (
        wps_files.filter(status__in=["submitted", "processed"]).aggregate(
            Sum("total_amount")
        )["total_amount__sum"]
        or 0
    )
    pending_amount = (
        wps_files.filter(status__in=["generated", "approved"]).aggregate(
            Sum("total_amount")
        )["total_amount__sum"]
        or 0
    )

    context = {
        "wps_files": wps_files,
        "total_submitted_amount": total_amount,
        "pending_amount": pending_amount,
        "page_title": _("WPS Files"),
        "statuses": WPSPeriodicFile.STATUS_CHOICES,
    }
    return render(request, "payroll/wps/wps_file_list.html", context)


@login_required
def wps_file_generate(request):
    """Generate new WPS file for a payroll period"""
    # Get first company for now (simplified)
    company = Company.objects.first()
    if not company:
        messages.error(request, _("No company configured"))
        return redirect("dashboard")

    if request.method == "POST":
        payroll_period = request.POST.get("payroll_period")
        payment_date = request.POST.get("payment_date")

        # Check if file already exists for this period
        if WPSPeriodicFile.objects.filter(
            company=company, payroll_period=payroll_period
        ).exists():
            messages.error(request, _("WPS file already exists for this period"))
            return redirect("wps-file-generate")

        # Get payslips for the period
        payslips = Payslip.objects.filter(
            employee__company=company,
            payroll_period=payroll_period,
            status__in=["computed", "email_sent"],
        )

        if not payslips.exists():
            messages.error(request, _("No payslips found for this period"))
            return redirect("wps-file-generate")

        # Create WPS file
        wps_file = WPSPeriodicFile()
        wps_file.company = company
        wps_file.payroll_period = payroll_period
        wps_file.payment_date = payment_date
        wps_file.file_reference_number = (
            f"WPS-{company.id}-{payroll_period}-{date.today().strftime('%Y%m%d')}"
        )
        wps_file.generated_by = request.user.employee_get
        wps_file.total_records = payslips.count()
        wps_file.total_amount = (
            payslips.aggregate(Sum("gross_pay"))["gross_pay__sum"] or 0
        )
        wps_file.status = "generated"

        # Create settings
        settings = company.wps_settings
        wps_file.file_version = settings.wps_format_version

        # Build employee records
        employee_records = []
        for payslip in payslips:
            record = {
                "employee_id": payslip.employee.id,
                "employee_name": payslip.employee.get_name(),
                "bank_account": payslip.employee.employeebankdetails.account_number
                if hasattr(payslip.employee, "employeebankdetails")
                else "",
                "amount": str(payslip.net_pay),
            }
            employee_records.append(record)

        wps_file.employee_records = employee_records
        wps_file.save()

        # Log action
        WPSAuditLog.objects.create(
            wps_file=wps_file,
            action="created",
            user=request.user.employee_get,
            details=f"WPS file generated for period {payroll_period}",
        )

        messages.success(request, _("WPS file generated successfully"))
        return redirect("wps-file-detail", pk=wps_file.pk)

    context = {
        "page_title": _("Generate WPS File"),
    }
    return render(request, "payroll/wps/wps_file_generate.html", context)


@login_required
def wps_file_detail(request, pk):
    """View WPS file details"""
    wps_file = get_object_or_404(WPSPeriodicFile, pk=pk)
    audit_logs = wps_file.audit_logs.all().order_by("-timestamp")
    exceptions = wps_file.exceptions.all()

    context = {
        "wps_file": wps_file,
        "audit_logs": audit_logs,
        "exceptions": exceptions,
        "page_title": f"WPS File - {wps_file.payroll_period}",
    }
    return render(request, "payroll/wps/wps_file_detail.html", context)


@login_required
def wps_file_approve(request, pk):
    """Approve WPS file"""
    wps_file = get_object_or_404(WPSPeriodicFile, pk=pk)

    if wps_file.status != "generated":
        messages.error(request, _("Can only approve generated WPS files"))
        return redirect("wps-file-detail", pk=pk)

    if request.method == "POST":
        wps_file.status = "approved"
        wps_file.approved_by = request.user.employee_get
        wps_file.approval_date = timezone.now()
        wps_file.approval_comments = request.POST.get("comments", "")
        wps_file.save()

        # Log action
        WPSAuditLog.objects.create(
            wps_file=wps_file,
            action="approved",
            user=request.user.employee_get,
            details=f"WPS file approved: {wps_file.approval_comments}",
        )

        messages.success(request, _("WPS file approved"))
        return redirect("wps-file-detail", pk=pk)

    context = {
        "wps_file": wps_file,
        "page_title": _("Approve WPS File"),
    }
    return render(request, "payroll/wps/wps_file_approve.html", context)


@login_required
def wps_file_submit(request, pk):
    """Submit WPS file to bank"""
    wps_file = get_object_or_404(WPSPeriodicFile, pk=pk)

    if wps_file.status != "approved":
        messages.error(request, _("Can only submit approved WPS files"))
        return redirect("wps-file-detail", pk=pk)

    if request.method == "POST":
        wps_file.status = "submitted"
        wps_file.submitted_date = timezone.now()
        wps_file.save()

        # Log action
        WPSAuditLog.objects.create(
            wps_file=wps_file,
            action="submitted",
            user=request.user.employee_get,
            details=f"WPS file submitted to bank {wps_file.company.wps_settings.company_bank_name}",
        )

        messages.success(request, _("WPS file submitted to bank"))
        return redirect("wps-file-detail", pk=pk)

    context = {
        "wps_file": wps_file,
        "page_title": _("Submit WPS File to Bank"),
    }
    return render(request, "payroll/wps/wps_file_submit.html", context)


@login_required
def wps_file_process_response(request, pk):
    """Process bank response for WPS file"""
    wps_file = get_object_or_404(WPSPeriodicFile, pk=pk)

    if request.method == "POST":
        response_code = request.POST.get("bank_response_code", "")
        response_message = request.POST.get("bank_response_message", "")

        if response_code == "00":  # Success code
            wps_file.status = "processed"
            wps_file.processing_status = "Completed"
            wps_file.processing_date = timezone.now()
        else:
            wps_file.status = "rejected"
            wps_file.rejection_reason = response_message

        wps_file.bank_response_code = response_code
        wps_file.bank_response_message = response_message
        wps_file.save()

        # Log action
        action = "processed" if wps_file.status == "processed" else "rejected"
        WPSAuditLog.objects.create(
            wps_file=wps_file,
            action=action,
            user=request.user.employee_get,
            details=f"Bank response received: {response_code} - {response_message}",
        )

        messages.success(request, _("Bank response processed"))
        return redirect("wps-file-detail", pk=pk)

    context = {
        "wps_file": wps_file,
        "page_title": _("Process Bank Response"),
    }
    return render(request, "payroll/wps/wps_file_process_response.html", context)


@login_required
def wps_file_download(request, pk):
    """Download WPS file"""
    wps_file = get_object_or_404(WPSPeriodicFile, pk=pk)

    # Generate WPS content based on format
    settings = wps_file.company.wps_settings

    if settings.wps_format_version == "v3.0":
        content = generate_wps_v3_content(wps_file)
    elif settings.wps_format_version == "v2.0":
        content = generate_wps_v2_content(wps_file)
    else:
        content = generate_wps_v1_content(wps_file)

    # Create response
    response = HttpResponse(content, content_type="text/plain")
    response["Content-Disposition"] = (
        f'attachment; filename="wps_{wps_file.file_reference_number}.txt"'
    )

    return response


@login_required
def wps_file_resubmit(request, pk):
    """Resubmit rejected WPS file"""
    wps_file = get_object_or_404(WPSPeriodicFile, pk=pk)

    if wps_file.status != "rejected":
        messages.error(request, _("Can only resubmit rejected WPS files"))
        return redirect("wps-file-detail", pk=pk)

    if request.method == "POST":
        wps_file.status = "submitted"
        wps_file.is_resubmitted = True
        wps_file.resubmission_date = timezone.now()
        wps_file.save()

        WPSAuditLog.objects.create(
            wps_file=wps_file,
            action="resubmitted",
            user=request.user.employee_get,
            details="WPS file resubmitted after rejection",
        )

        messages.success(request, _("WPS file resubmitted"))
        return redirect("wps-file-detail", pk=pk)

    context = {
        "wps_file": wps_file,
        "page_title": _("Resubmit WPS File"),
    }
    return render(request, "payroll/wps/wps_file_resubmit.html", context)


# ============= WPS FILE FORMAT GENERATION =============


def generate_wps_v1_content(wps_file):
    """Generate WPS v1.0 format content"""
    settings = wps_file.company.wps_settings
    lines = []

    # Header
    header = f"01|{settings.company_cr_number}|{wps_file.file_reference_number}|{wps_file.payment_date}|{wps_file.total_records}|{wps_file.total_amount}|{wps_file.currency}"
    lines.append(header)

    # Detail records
    for i, record in enumerate(wps_file.employee_records, 1):
        detail = f"02|{i}|{record.get('employee_id')}|{record.get('employee_name')}|{record.get('bank_account')}|{record.get('amount')}"
        lines.append(detail)

    # Trailer
    trailer = f"99|{wps_file.total_records}|{wps_file.total_amount}"
    lines.append(trailer)

    return "\r\n".join(lines)


def generate_wps_v2_content(wps_file):
    """Generate WPS v2.0 format content"""
    settings = wps_file.company.wps_settings
    content = io.StringIO()
    writer = csv.writer(content)

    # Header
    writer.writerow(
        [
            "HEADER",
            settings.company_cr_number,
            wps_file.file_reference_number,
            wps_file.payment_date,
            wps_file.total_records,
            wps_file.total_amount,
            wps_file.currency,
        ]
    )

    # Detail records
    for i, record in enumerate(wps_file.employee_records, 1):
        writer.writerow(
            [
                "DETAIL",
                i,
                record.get("employee_id"),
                record.get("employee_name"),
                record.get("bank_account"),
                record.get("amount"),
            ]
        )

    # Trailer
    writer.writerow(
        [
            "TRAILER",
            wps_file.total_records,
            wps_file.total_amount,
        ]
    )

    return content.getvalue()


def generate_wps_v3_content(wps_file):
    """Generate WPS v3.0 format with IBAN"""
    settings = wps_file.company.wps_settings
    content = io.StringIO()
    writer = csv.DictWriter(
        content,
        fieldnames=[
            "Record Type",
            "CR Number",
            "File Reference",
            "Payment Date",
            "Employee ID",
            "Employee Name",
            "Bank Account",
            "IBAN",
            "Amount",
            "Currency",
        ],
    )

    writer.writeheader()

    for record in wps_file.employee_records:
        writer.writerow(
            {
                "Record Type": "DETAIL",
                "CR Number": settings.company_cr_number,
                "File Reference": wps_file.file_reference_number,
                "Payment Date": wps_file.payment_date,
                "Employee ID": record.get("employee_id"),
                "Employee Name": record.get("employee_name"),
                "Bank Account": record.get("bank_account"),
                "IBAN": record.get("iban", ""),
                "Amount": record.get("amount"),
                "Currency": wps_file.currency,
            }
        )

    return content.getvalue()


# ============= WPS EXCEPTION HANDLING =============


@login_required
def wps_exception_list(request):
    """List WPS processing exceptions"""
    company = Company.objects.first()
    exceptions = WPSPaymentException.objects.filter(wps_file__company=company)

    # Filter unresolved
    unresolved = request.GET.get("unresolved")
    if unresolved:
        exceptions = exceptions.filter(is_resolved=False)

    context = {
        "exceptions": exceptions,
        "page_title": _("WPS Exceptions"),
    }
    return render(request, "payroll/wps/wps_exception_list.html", context)


@login_required
def wps_exception_resolve(request, pk):
    """Resolve WPS exception"""
    exception = get_object_or_404(WPSPaymentException, pk=pk)

    if request.method == "POST":
        exception.is_resolved = True
        exception.resolved_date = timezone.now()
        exception.resolution_notes = request.POST.get("resolution_notes", "")
        exception.save()

        messages.success(request, _("Exception resolved"))
        return redirect("wps-exception-list")

    context = {
        "exception": exception,
        "page_title": _("Resolve Exception"),
    }
    return render(request, "payroll/wps/wps_exception_resolve.html", context)


# ============= WPS DASHBOARD =============


@login_required
def wps_dashboard(request):
    """WPS Dashboard"""
    company = Company.objects.first()

    stats = {
        "total_files": WPSPeriodicFile.objects.filter(company=company).count(),
        "submitted_this_month": WPSPeriodicFile.objects.filter(
            company=company,
            status__in=["submitted", "processed"],
            submitted_date__month=date.today().month,
        ).count(),
        "pending_approval": WPSPeriodicFile.objects.filter(
            company=company, status="generated"
        ).count(),
        "total_submitted_amount": WPSPeriodicFile.objects.filter(
            company=company, status="processed"
        ).aggregate(Sum("total_amount"))["total_amount__sum"]
        or 0,
    }

    recent_files = WPSPeriodicFile.objects.filter(company=company).order_by(
        "-submitted_date"
    )[:5]
    pending_exceptions = WPSPaymentException.objects.filter(
        wps_file__company=company, is_resolved=False
    ).count()

    context = {
        "stats": stats,
        "recent_files": recent_files,
        "pending_exceptions": pending_exceptions,
        "page_title": _("WPS Dashboard"),
    }
    return render(request, "payroll/wps/wps_dashboard.html", context)


from django.utils import timezone
from django.db.models import Q
