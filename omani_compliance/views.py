"""
Views for Omani Labour Law Compliance
"""

from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

from employee.filters import EmployeeFilter
from employee.models import Employee
from fits_views.generic.cbv.views import FitsListView

from .methods import OmaniComplianceEngine
from .models import OmaniComplianceAudit, OmaniLabourLawConfig


@method_decorator(login_required, name="dispatch")
class OmaniComplianceConfigView(TemplateView):
    """View for Omani Labour Law configuration"""

    template_name = "omani_compliance/config.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get or create configuration for current company
        if hasattr(self.request.user, "employee_get"):
            company = self.request.user.employee_get.get_company()
            config, created = OmaniLabourLawConfig.objects.get_or_create(
                company=company
            )
            context["config"] = config
            context["company"] = company

        return context


@method_decorator(login_required, name="dispatch")
class OmaniComplianceAuditView(FitsListView):
    """View for Omani compliance audit records"""

    model = OmaniComplianceAudit
    template_name = "omani_compliance/audit.html"

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by employee if specified
        employee_id = self.request.GET.get("employee")
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        # Filter by status if specified
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter form
        context["filter_form"] = EmployeeFilter()

        return context


@method_decorator(login_required, name="dispatch")
class OmaniTaxCalculationsView(FitsListView):
    """View for Omani tax calculations"""

    template_name = "omani_compliance/tax_calculations.html"

    def get_queryset(self):
        # This would typically query OmaniTaxCalculation model
        # For now, return empty queryset
        return Employee.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add tax calculation engine
        context["tax_engine"] = OmaniComplianceEngine()

        return context


@method_decorator(login_required, name="dispatch")
class OmaniComplianceReportView(TemplateView):
    """View for Omani compliance reports"""

    template_name = "omani_compliance/compliance_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get compliance statistics (only if user is authenticated and has employee record)
        if hasattr(self.request.user, "employee_get"):
            company = self.request.user.employee_get.get_company()
            total_employees = Employee.objects.filter(
                employee_work_info__company_id=company
            ).count()
            context["total_employees"] = total_employees
            context["compliance_rate"] = 95.0  # Mock value
            context["non_compliant_count"] = max(
                0, total_employees * 0.05
            )  # Mock value

        return context
