"""
employee/org_chart_service.py
Organization Chart Builder Service Layer

Provides business logic for org chart operations including:
- Position hierarchy management
- Drag-drop reorganization
- Real-time reporting manager assignment
- Cost center visualization
- Org structure export/import
"""

from django.db.models import Q
from django.db import transaction
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from datetime import datetime
import json

from employee.models import Employee, EmployeeWorkInformation
from base.models import Department


class OrgChartBuilderService:
    """
    Service layer for organization chart building and management.
    Handles hierarchy operations, reorganization, and structure analysis.
    """

    def __init__(self, company_id=None):
        """Initialize with optional company filter"""
        self.company_id = company_id

    def _get_employee_queryset(self):
        """Get base queryset with company filtering"""
        queryset = Employee.objects.filter(is_active=True)
        if self.company_id:
            queryset = queryset.filter(employee_work_info__company_id=self.company_id)
        return queryset

    # ==================== HIERARCHY OPERATIONS ====================

    def get_org_chart_data(self, root_employee=None, max_depth=None):
        """
        Generate hierarchical org chart data structure.

        Args:
            root_employee: Root node for hierarchy (None = all roots)
            max_depth: Maximum depth to traverse (None = unlimited)

        Returns:
            dict or list: Hierarchical structure suitable for frontend rendering
        """
        if root_employee:
            return self._build_hierarchy(root_employee, max_depth)
        else:
            # Get all root employees (no reporting manager)
            roots = self._get_employee_queryset().filter(
                employee_work_info__reporting_manager_id__isnull=True
            )
            return [self._build_hierarchy(root, max_depth) for root in roots]

    def _build_hierarchy(self, employee, max_depth=None, current_depth=0):
        """Recursively build hierarchy structure"""
        if max_depth and current_depth >= max_depth:
            return None

        work_info = getattr(employee, "employee_work_info", None)

        node_data = {
            "id": employee.id,
            "name": employee.get_full_name(),
            "email": employee.email,
            "phone": employee.phone,
            "job_position": str(
                getattr(work_info.job_position_id, "job_position", _("Not Set"))
            )
            if work_info
            else _("Not Set"),
            "department": str(
                getattr(work_info.department_id, "department", _("Not Set"))
            )
            if work_info
            else _("Not Set"),
            "cost_center": str(getattr(work_info, "cost_center", ""))
            if work_info
            else "",
            "profile_url": str(employee.get_avatar())
            if hasattr(employee, "get_avatar")
            else "",
            "children": [],
        }

        # Get direct subordinates
        subordinates = Employee.objects.filter(
            employee_work_info__reporting_manager_id=employee, is_active=True
        )

        for subordinate in subordinates:
            child_node = self._build_hierarchy(
                subordinate, max_depth, current_depth + 1
            )
            if child_node:
                node_data["children"].append(child_node)

        return node_data

    # ==================== DRAG-DROP REORGANIZATION ====================

    @transaction.atomic
    def reorganize_reporting_manager(self, employee_id, new_manager_id, reason=""):
        """
        Update reporting manager for an employee (drag-drop operation).

        Args:
            employee_id: Employee being moved
            new_manager_id: New manager's employee ID
            reason: Business reason for change

        Returns:
            dict: Operation result with status and message
        """
        try:
            employee = Employee.objects.get(id=employee_id)
            new_manager = Employee.objects.get(id=new_manager_id)

            # Validation: prevent circular reporting
            if self._is_circular_reporting(employee_id, new_manager_id):
                return {
                    "success": False,
                    "error": _(
                        "Cannot assign as reporting manager - would create circular reporting structure"
                    ),
                }

            # Get or create work info
            work_info = getattr(employee, "employee_work_info", None)
            if not work_info:
                work_info = EmployeeWorkInformation.objects.create(employee_id=employee)

            old_manager = work_info.reporting_manager_id
            work_info.reporting_manager_id = new_manager
            work_info.save()

            # Log the change
            self._log_org_change(
                employee, old_manager, new_manager, "reporting_manager_change", reason
            )

            return {
                "success": True,
                "message": _(
                    f"{employee.get_full_name()} now reports to {new_manager.get_full_name()}"
                ),
                "old_manager": old_manager.get_full_name()
                if old_manager
                else "Unassigned",
                "new_manager": new_manager.get_full_name(),
            }
        
        except Employee.DoesNotExist:
            return {'success': False, 'error': _('Employee not found')}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _is_circular_reporting(self, employee_id, proposed_manager_id, visited=None):
        """Check if assignment would create circular reporting"""
        if visited is None:
            visited = set()

        if proposed_manager_id in visited:
            return True

        visited.add(proposed_manager_id)

        try:
            manager = Employee.objects.get(id=proposed_manager_id)
            work_info = getattr(manager, "employee_work_info", None)

            if work_info and work_info.reporting_manager_id:
                # If proposed manager's manager is the employee being moved
                if work_info.reporting_manager_id.id == employee_id:
                    return True

                # Recursively check up the chain
                return self._is_circular_reporting(
                    employee_id, work_info.reporting_manager_id.id, visited
                )
        except:
            pass

        return False

    # ==================== INLINE EDITING ====================

    def update_position_details(self, employee_id, updates_dict):
        """
        Update employee position details (inline edit).

        Args:
            employee_id: Employee ID
            updates_dict: Dict with fields to update (job_position, department, etc.)

        Returns:
            dict: Operation result
        """
        try:
            employee = Employee.objects.get(id=employee_id)
            work_info = getattr(employee, "employee_work_info", None)

            if not work_info:
                work_info = EmployeeWorkInformation.objects.create(employee_id=employee)

            # Allowed fields to update
            allowed_fields = [
                "job_position_id",
                "department_id",
                "cost_center",
                "job_role_id",
                "location",
            ]

            changes = {}
            for field in allowed_fields:
                if field in updates_dict and updates_dict[field]:
                    old_value = getattr(work_info, field)
                    setattr(work_info, field, updates_dict[field])
                    changes[field] = (old_value, updates_dict[field])

            if changes:
                work_info.save()
                return {
                    "success": True,
                    "message": _("Position details updated successfully"),
                    "changes": {k: f"{v[0]} → {v[1]}" for k, v in changes.items()},
                }

            return {"success": True, "message": _("No changes made")}

        except Employee.DoesNotExist:
            return {"success": False, "error": _("Employee not found")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== COST CENTER MANAGEMENT ====================

    def get_cost_center_breakdown(self):
        """Get organization structure by cost center"""
        
        breakdown = {}
        work_infos = EmployeeWorkInformation.objects.filter(
            employee_id__is_active=True
        ).select_related("department_id", "job_position_id")

        if self.company_id:
            work_infos = work_infos.filter(company_id=self.company_id)

        for work_info in work_infos:
            cost_center = work_info.cost_center or "Unassigned"

            if cost_center not in breakdown:
                breakdown[cost_center] = {
                    "total_employees": 0,
                    "departments": {},
                    "budget": 0,
                }

            breakdown[cost_center]["total_employees"] += 1

            dept = work_info.department_id
            dept_name = str(dept) if dept else "Unknown"

            if dept_name not in breakdown[cost_center]["departments"]:
                breakdown[cost_center]["departments"][dept_name] = 0

            breakdown[cost_center]["departments"][dept_name] += 1

        return breakdown

    # ==================== STRUCTURE ANALYSIS ====================

    def get_org_structure_stats(self):
        """Get organizational structure statistics"""
        queryset = self._get_employee_queryset()

        work_infos = EmployeeWorkInformation.objects.filter(
            employee_id__in=queryset.values_list("id", flat=True)
        )

        stats = {
            "total_employees": queryset.count(),
            "managers": queryset.filter(reporting_manager__isnull=False)
            .distinct()
            .count(),
            "individual_contributors": 0,
            "avg_team_size": 0,
            "max_team_size": 0,
            "max_hierarchy_depth": 0,
            "departments": work_infos.values("department_id").distinct().count(),
        }

        # Calculate team sizes
        team_sizes = []
        for emp in queryset:
            team = Employee.objects.filter(
                employee_work_info__reporting_manager_id=emp
            ).count()
            team_sizes.append(team)

        if team_sizes:
            stats["avg_team_size"] = round(sum(team_sizes) / len(team_sizes), 2)
            stats["max_team_size"] = max(team_sizes)
            stats["individual_contributors"] = sum(
                1 for size in team_sizes if size == 0
            )

        # Calculate hierarchy depth
        roots = queryset.filter(employee_work_info__reporting_manager_id__isnull=True)
        for root in roots:
            depth = self._calculate_hierarchy_depth(root)
            stats["max_hierarchy_depth"] = max(stats["max_hierarchy_depth"], depth)

        return stats

    def _calculate_hierarchy_depth(self, employee, depth=1):
        """Recursively calculate hierarchy depth"""
        subordinates = Employee.objects.filter(
            employee_work_info__reporting_manager_id=employee
        )

        if not subordinates.exists():
            return depth

        max_depth = depth
        for subordinate in subordinates:
            sub_depth = self._calculate_hierarchy_depth(subordinate, depth + 1)
            max_depth = max(max_depth, sub_depth)

        return max_depth

    # ==================== DEPARTMENT REORGANIZATION ====================

    def get_department_structure(self, department_id):
        """Get organization chart for specific department"""
        
        try:
            dept = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return None

        # Find root employee in this department (dept head with no manager in same dept)
        roots = EmployeeWorkInformation.objects.filter(
            department_id=dept, employee_id__is_active=True
        ).filter(
            Q(reporting_manager_id__isnull=True)
            | ~Q(reporting_manager_id__employee_work_info__department_id=dept)
        )

        structures = []
        for work_info in roots:
            structure = self._build_hierarchy(work_info.employee_id)
            if structure:
                structures.append(structure)

        return structures

    # ==================== LOGGING ====================

    def _log_org_change(
        self, employee, old_manager, new_manager, change_type, reason=""
    ):
        """Log organizational structure changes"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "employee_id": employee.id,
            "employee_name": employee.get_full_name(),
            "change_type": change_type,
            "old_manager": old_manager.get_full_name() if old_manager else "Unassigned",
            "new_manager": new_manager.get_full_name() if new_manager else "Unassigned",
            "reason": reason,
        }

        # In production, this would be persisted to a database
        # For now, it's logged but can be extended
        return log_entry

    def get_recent_org_changes(self, limit=20):
        """Get recent organizational changes (from audit logs if available)"""
        if apps.is_installed("fits_audit"):
            from fits_audit.models import AuditLog

            changes = AuditLog.objects.filter(
                model_name="employeeworkinformation",
                field_name__in=["reporting_manager_id", "department_id"],
            ).order_by("-timestamp")[:limit]

            return [
                {
                    "timestamp": change.timestamp,
                    "employee": change.object_id,
                    "field": change.field_name,
                    "old_value": change.old_value,
                    "new_value": change.new_value,
                    "changed_by": str(change.changed_by)
                    if change.changed_by
                    else "System",
                }
                for change in changes
            ]

        return []

    # ==================== EXPORT/IMPORT ====================

    def export_org_chart_json(self, root_employee=None):
        """Export organization chart as JSON"""
        data = self.get_org_chart_data(root_employee)
        return json.dumps(data, indent=2, default=str)

    def get_flat_structure(self):
        """Get flat list of all employees with their managers (for import/export)"""
        queryset = self._get_employee_queryset()

        flat_list = []
        for emp in queryset:
            work_info = getattr(emp, "employee_work_info", None)
            manager = work_info.reporting_manager_id if work_info else None

            flat_list.append(
                {
                    "employee_id": emp.id,
                    "employee_name": emp.get_full_name(),
                    "email": emp.email,
                    "manager_id": manager.id if manager else None,
                    "manager_name": manager.get_full_name()
                    if manager
                    else "No Manager",
                    "job_position": str(work_info.job_position_id)
                    if work_info and work_info.job_position_id
                    else "",
                    "department": str(work_info.department_id)
                    if work_info and work_info.department_id
                    else "",
                    "cost_center": work_info.cost_center if work_info else "",
                }
            )

        return flat_list
