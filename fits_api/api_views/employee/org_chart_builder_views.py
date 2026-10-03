"""
fits_api/api_views/employee/org_chart_builder_views.py
Organization Chart Builder REST API Views

Provides endpoints for building and managing organizational structures with drag-drop support.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from datetime import date

from employee.models import Employee
from employee.org_chart_service import OrgChartBuilderService


class OrgChartHierarchyView(APIView):
    """
    GET: Fetch complete organization chart hierarchy

    Query Parameters:
        - root_id: Root employee ID (None = all roots)
        - max_depth: Maximum hierarchy depth (None = unlimited)
        - company_id: Filter by company

    Returns:
        Hierarchical tree structure ready for rendering
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get org chart hierarchy"""
        root_id = request.GET.get("root_id")
        max_depth = request.GET.get("max_depth")
        company_id = request.GET.get("company_id")

        try:
            max_depth = int(max_depth) if max_depth else None
        except ValueError:
            max_depth = None

        root_employee = None
        if root_id:
            try:
                root_employee = Employee.objects.get(id=root_id)
            except Employee.DoesNotExist:
                return Response(
                    {"error": _("Root employee not found")},
                    status=status.HTTP_404_NOT_FOUND,
                )

        try:
            service = OrgChartBuilderService(company_id=company_id)
            hierarchy = service.get_org_chart_data(root_employee, max_depth)

            return Response(
                {
                    "status": "success",
                    "data": hierarchy,
                    "generated_at": date.today().isoformat(),
                }
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DragDropReorganizeView(APIView):
    """
    POST: Move employee under new reporting manager (drag-drop operation)

    Body:
    {
        "employee_id": 42,
        "new_manager_id": 15,
        "reason": "Organizational restructuring"
    }

    Returns:
        Operation result with old and new manager info
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        """Handle drag-drop reorganization"""
        employee_id = request.data.get("employee_id")
        new_manager_id = request.data.get("new_manager_id")
        reason = request.data.get("reason", "")

        if not all([employee_id, new_manager_id]):
            return Response(
                {"error": _("employee_id and new_manager_id are required")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = OrgChartBuilderService()
        result = service.reorganize_reporting_manager(
            employee_id, new_manager_id, reason
        )

        if result["success"]:
            return Response(
                {
                    "status": "success",
                    "message": result["message"],
                    "old_manager": result.get("old_manager"),
                    "new_manager": result.get("new_manager"),
                }
            )
        else:
            return Response(
                {"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST
            )


class PositionDetailsUpdateView(APIView):
    """
    PATCH: Update position details (inline edit)

    Body:
    {
        "employee_id": 42,
        "job_position_id": 5,
        "department_id": 3,
        "cost_center": "CC-001"
    }

    Returns:
        Updated position information
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        """Update position details"""
        employee_id = request.data.get("employee_id")

        if not employee_id:
            return Response(
                {"error": _("employee_id is required")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = OrgChartBuilderService()
        result = service.update_position_details(employee_id, dict(request.data))

        if result["success"]:
            return Response(
                {
                    "status": "success",
                    "message": result["message"],
                    "changes": result.get("changes", {}),
                }
            )
        else:
            return Response(
                {"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST
            )


class OrgStructureStatsView(APIView):
    """
    GET: Get organizational structure statistics

    Returns:
        - total_employees, managers, individual_contributors
        - avg_team_size, max_team_size, max_hierarchy_depth
        - departments count
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get org stats"""
        company_id = request.GET.get("company_id")

        service = OrgChartBuilderService(company_id=company_id)
        stats = service.get_org_structure_stats()

        return Response(
            {
                "status": "success",
                "data": stats,
                "generated_at": date.today().isoformat(),
            }
        )


class CostCenterBreakdownView(APIView):
    """
    GET: Get organization chart grouped by cost center

    Returns:
        dict: Cost centers with employee counts and department breakdown
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get cost center breakdown"""
        company_id = request.GET.get("company_id")

        service = OrgChartBuilderService(company_id=company_id)
        breakdown = service.get_cost_center_breakdown()

        return Response(
            {
                "status": "success",
                "data": breakdown,
                "generated_at": date.today().isoformat(),
            }
        )


class DepartmentStructureView(APIView):
    """
    GET: Get organization structure for specific department

    Path Parameters:
        - department_id: Department ID

    Returns:
        Hierarchical structure for employees in department
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, department_id):
        """Get department structure"""
        service = OrgChartBuilderService()

        try:
            structure = service.get_department_structure(department_id)

            if structure is None:
                return Response(
                    {"error": _("Department not found")},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {
                    "status": "success",
                    "data": structure,
                    "generated_at": date.today().isoformat(),
                }
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrgChartFlatStructureView(APIView):
    """
    GET: Get flat list of employees and their reporting managers

    Useful for CSV export, import, or validation.

    Returns:
        List of employees with manager assignments
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get flat structure"""
        company_id = request.GET.get("company_id")

        service = OrgChartBuilderService(company_id=company_id)
        flat_list = service.get_flat_structure()

        return Response(
            {
                "status": "success",
                "data": flat_list,
                "count": len(flat_list),
                "generated_at": date.today().isoformat(),
            }
        )


class RecentOrgChangesView(APIView):
    """
    GET: Get recent organizational changes from audit log

    Query Parameters:
        - limit: Number of records to return (default: 20, max: 100)

    Returns:
        List of recent changes with timestamps and modified fields
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get recent org changes"""
        try:
            limit = min(int(request.GET.get("limit", 20)), 100)
        except ValueError:
            limit = 20

        service = OrgChartBuilderService()
        changes = service.get_recent_org_changes(limit)

        return Response(
            {
                "status": "success",
                "data": changes,
                "count": len(changes),
                "generated_at": date.today().isoformat(),
            }
        )


class OrgChartValidationView(APIView):
    """
    GET: Validate organization chart for issues

    Checks for:
        - Circular reporting structures
        - Dangling employees
        - Missing cost centers

    Returns:
        List of issues and warnings
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Validate org chart"""
        issues = {
            "circular_reporting": [],
            "missing_managers": [],
            "missing_cost_centers": [],
            "missing_departments": [],
            "duplicate_positions": [],
            "warnings": [],
        }

        employees = Employee.objects.filter(is_active=True)

        # Check for circular reporting
        for emp in employees:
            work_info = getattr(emp, "employee_work_info", None)
            if work_info and work_info.reporting_manager_id:
                service = OrgChartBuilderService()
                if service._is_circular_reporting(
                    emp.id, work_info.reporting_manager_id.id
                ):
                    issues["circular_reporting"].append(
                        {
                            "employee_id": emp.id,
                            "employee_name": emp.get_full_name(),
                            "manager_id": work_info.reporting_manager_id.id,
                            "severity": "critical",
                        }
                    )

        # Check for missing managers (for non-executives)
        for emp in employees.filter(is_active=True):
            work_info = getattr(emp, "employee_work_info", None)
            if not work_info:
                issues["missing_managers"].append(
                    {
                        "employee_id": emp.id,
                        "employee_name": emp.get_full_name(),
                        "severity": "warning",
                    }
                )
            elif not work_info.reporting_manager_id:
                # Check if this is an intended root (CEO, etc.)
                warning = {
                    "employee_id": emp.id,
                    "employee_name": emp.get_full_name(),
                    "severity": "info",
                }
                if emp.id != 1:  # Assuming CEO has ID 1
                    warning["severity"] = "warning"
                issues["missing_managers"].append(warning)

            # Check for missing cost center
            if work_info and not work_info.cost_center:
                issues["missing_cost_centers"].append(
                    {
                        "employee_id": emp.id,
                        "employee_name": emp.get_full_name(),
                        "severity": "warning",
                    }
                )

            # Check for missing department
            if not work_info or not work_info.department_id:
                issues["missing_departments"].append(
                    {
                        "employee_id": emp.id,
                        "employee_name": emp.get_full_name(),
                        "severity": "warning",
                    }
                )

        # Count summary
        issue_count = sum(len(v) for k, v in issues.items() if k != "warnings")

        severity_counts = {
            "critical": len(
                [
                    item
                    for values in issues.values()
                    for item in values
                    if isinstance(item, dict) and item.get("severity") == "critical"
                ]
            ),
            "warning": len(
                [
                    item
                    for values in issues.values()
                    for item in values
                    if isinstance(item, dict) and item.get("severity") == "warning"
                ]
            ),
            "info": len(
                [
                    item
                    for values in issues.values()
                    for item in values
                    if isinstance(item, dict) and item.get("severity") == "info"
                ]
            ),
        }

        return Response(
            {
                "status": "success",
                "data": issues,
                "summary": {
                    "total_issues": issue_count,
                    "severity_counts": severity_counts,
                },
                "generated_at": date.today().isoformat(),
            }
        )
