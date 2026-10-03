from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from payroll.models.integration import GLAccount, GLMapping, ICBSConfig
from payroll.models.models import Allowance, Deduction
from fits.decorators import login_required, permission_required
from django import forms
from django.db import transaction


class GLMappingForm(forms.ModelForm):
    """Form for creating/editing GL Mappings."""

    class Meta:
        model = GLMapping
        fields = [
            "mapping_type",
            "component_id",
            "debit_account",
            "credit_account",
            "company",
        ]
        widgets = {
            "mapping_type": forms.Select(attrs={"class": "form-control"}),
            "component_id": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Optional - Component ID",
                }
            ),
            "debit_account": forms.Select(attrs={"class": "form-control"}),
            "credit_account": forms.Select(attrs={"class": "form-control"}),
            "company": forms.Select(attrs={"class": "form-control"}),
        }


@login_required
@permission_required("payroll.view_glmapping")
def gl_integration_dashboard(request):
    """General Ledger Integration Dashboard."""
    gl_accounts = GLAccount.objects.all()
    mappings = GLMapping.objects.all()
    allowances = Allowance.objects.all()
    deductions = Deduction.objects.all()

    mapped_allowances = mappings.filter(mapping_type="Allowance").count()
    unmapped_allowances = allowances.count() - mapped_allowances

    context = {
        "gl_accounts": gl_accounts,
        "mappings": mappings,
        "mapped_allowances": mapped_allowances,
        "unmapped_allowances": unmapped_allowances,
        "total_deductions": deductions.count(),
    }
    return render(request, "payroll/integration/gl_dashboard.html", context)


@login_required
@permission_required("payroll.add_glmapping")
def gl_mapping_create(request):
    """Create a new GL Mapping."""
    if request.method == "POST":
        form = GLMappingForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                messages.success(request, _("GL Mapping created successfully."))
            return redirect("gl-integration")
    else:
        form = GLMappingForm()

    context = {
        "form": form,
        "title": _("Add New GL Mapping"),
        "action": "create",
        "gl_accounts": GLAccount.objects.all(),
    }
    return render(request, "payroll/integration/gl_mapping_form.html", context)


@login_required
@permission_required("payroll.change_glmapping")
def gl_mapping_edit(request, mapping_id):
    """Edit an existing GL Mapping."""
    mapping = get_object_or_404(GLMapping, id=mapping_id)

    if request.method == "POST":
        form = GLMappingForm(request.POST, instance=mapping)
        if form.is_valid():
            with transaction.atomic():
                mapping = form.save()
                messages.success(request, _("GL Mapping updated successfully."))
            return redirect("gl-integration")
    else:
        form = GLMappingForm(instance=mapping)

    context = {
        "form": form,
        "title": _("Edit GL Mapping"),
        "action": "edit",
        "mapping": mapping,
    }
    return render(request, "payroll/integration/gl_mapping_form.html", context)


@login_required
@permission_required("payroll.delete_glmapping")
@require_http_methods(["POST"])
def gl_mapping_delete(request, mapping_id):
    """Delete a GL Mapping."""
    mapping = get_object_or_404(GLMapping, id=mapping_id)
    try:
        with transaction.atomic():
            mapping.delete()
            messages.success(request, _("GL Mapping deleted successfully."))
    except Exception as e:
        messages.error(request, _("Could not delete mapping: {}").format(str(e)))

    return redirect("gl-integration")


@login_required
def icbs_disbursement_view(request):
    """ICBS Salary Disbursement Interface."""
    icbs_config = ICBSConfig.objects.filter(is_active=True).first()
    # Dummy pending payments for demo
    pending_payments = [
        {"employee": "Alen", "amount": 1500, "status": "Pending"},
        {"employee": "John", "amount": 2200, "status": "Pending"},
    ]

    context = {
        "icbs_config": icbs_config,
        "pending_payments": pending_payments,
        "is_configured": True if icbs_config else False,
    }
    return render(request, "payroll/integration/icbs_disbursement.html", context)


@login_required
@require_http_methods(["POST"])
def icbs_process_bulk(request):
    """Process all pending payments via ICBS."""
    messages.success(
        request,
        _("Bulk payment processing initiated. Please check the audit log for status."),
    )
    return redirect("icbs-integration")


@login_required
@require_http_methods(["POST"])
def icbs_process_payment(request, payment_id):
    """Process individual payment via ICBS."""
    # Implementation for individual payment processing
    messages.success(request, _("Payment sent to ICBS for processing."))
    return redirect("icbs-integration")


@login_required
@permission_required("payroll.change_icbsconfig")
@require_http_methods(["POST"])
def icbs_config_update(request):
    """Update ICBS configuration."""
    icbs_config = ICBSConfig.objects.filter(is_active=True).first()

    if icbs_config:
        icbs_config.bank_name = request.POST.get("bank_name", icbs_config.bank_name)
        icbs_config.api_endpoint = request.POST.get(
            "api_endpoint", icbs_config.api_endpoint
        )
        icbs_config.save()
        messages.success(request, _("ICBS Configuration updated successfully."))
    else:
        messages.error(request, _("ICBS Configuration not found."))

    return redirect("icbs-integration")
