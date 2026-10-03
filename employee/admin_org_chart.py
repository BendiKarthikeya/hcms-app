"""
employee/admin_org_chart.py
Django Admin Configuration for Organization Chart Models
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin

from employee.models_org_chart import (
    OrgChartPosition,
    PositionHierarchyCache,
    DraftPositionChange,
    OrgChartAuditLog,
)


@admin.register(OrgChartPosition)
class OrgChartPositionAdmin(SimpleHistoryAdmin):
    """Admin interface for organization chart positions"""
    
    list_display = (
        'position_code',
        'employee',
        'position_title',
        'reporting_manager',
        'department',
        'status',
        'cost_center',
        'hierarchy_level',
    )
    
    list_filter = (
        'status',
        'hierarchy_level',
        'department',
        'company',
        'created_at',
    )
    
    search_fields = (
        'position_code',
        'position_title',
        'employee__first_name',
        'employee__last_name',
        'cost_center',
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'hierarchy_level',
        'get_direct_reports_count',
        'get_total_reports_count',
        'get_hierarchy_path_display',
    )
    
    fieldsets = (
        (
            _('Position Information'),
            {
                'fields': (
                    'position_code',
                    'position_title',
                    'employee',
                    'status',
                )
            },
        ),
        (
            _('Reporting Structure'),
            {
                'fields': (
                    'reporting_manager',
                    'hierarchy_level',
                    'get_direct_reports_count',
                    'get_total_reports_count',
                    'get_hierarchy_path_display',
                )
            },
        ),
        (
            _('Organization Context'),
            {
                'fields': (
                    'department',
                    'company',
                )
            },
        ),
        (
            _('Cost & Budget'),
            {
                'fields': (
                    'cost_center',
                    'salary_min',
                    'salary_max',
                )
            },
        ),
        (
            _('Additional Information'),
            {
                'fields': (
                    'position_level',
                    'description',
                    'created_by',
                )
            },
        ),
        (
            _('Audit Trail'),
            {
                'fields': (
                    'created_at',
                    'updated_at',
                ),
                'classes': ('collapse',),
            },
        ),
    )
    
    def get_direct_reports_count(self, obj):
        """Display count of direct reports"""
        count = obj.get_direct_reports()
        return f"{count} { _('direct report(s)') }"
    get_direct_reports_count.short_description = _('Direct Reports')
    
    def get_total_reports_count(self, obj):
        """Display total reports including indirect"""
        count = obj.get_total_reports()
        return f"{count} total report(s)"
    get_total_reports_count.short_description = _('Total Reports')
    
    def get_hierarchy_path_display(self, obj):
        """Display reporting hierarchy path"""
        path = obj.get_hierarchy_path()
        if len(path) > 1:
            path_str = ' > '.join([p.position_title for p in path])
            return path_str
        return _('No manager (Root position)')
    get_hierarchy_path_display.short_description = _('Hierarchy Path')
    
    def has_delete_permission(self, request, obj=None):
        """Restrict deletion to admin users"""
        return request.user.is_superuser


@admin.register(PositionHierarchyCache)
class PositionHierarchyCacheAdmin(admin.ModelAdmin):
    """Admin interface for position hierarchy cache"""
    
    list_display = (
        'company',
        'root_position',
        'employee_count',
        'position_count',
        'depth',
        'is_valid',
        'expires_at',
    )
    
    list_filter = (
        'company',
        'is_valid',
        'created_at',
        'expires_at',
    )
    
    search_fields = (
        'company__name',
        'root_position__position_code',
    )
    
    readonly_fields = (
        'hierarchy_json',
        'created_at',
        'updated_at',
        'last_computed',
    )
    
    fieldsets = (
        (
            _('Cache Information'),
            {
                'fields': (
                    'company',
                    'root_position',
                    'is_valid',
                )
            },
        ),
        (
            _('Statistics'),
            {
                'fields': (
                    'employee_count',
                    'position_count',
                    'depth',
                )
            },
        ),
        (
            _('Hierarchy Data'),
            {
                'fields': (
                    'hierarchy_json',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            _('Cache Management'),
            {
                'fields': (
                    'created_at',
                    'updated_at',
                    'last_computed',
                    'expires_at',
                ),
                'classes': ('collapse',),
            },
        ),
    )
    
    actions = ['invalidate_cache', 'extend_expiration']
    
    def invalidate_cache(self, request, queryset):
        """Invalidate selected caches"""
        updated = queryset.update(is_valid=False)
        self.message_user(request, _('Invalidated {} cache(s)').format(updated))
    invalidate_cache.short_description = _('Invalidate selected cache(s)')
    
    def extend_expiration(self, request, queryset):
        """Extend cache expiration"""
        from django.utils import timezone
        from datetime import timedelta
        
        new_expiry = timezone.now() + timedelta(hours=24)
        updated = queryset.update(expires_at=new_expiry, is_valid=True)
        self.message_user(request, _('Extended {} cache(s) expiration').format(updated))
    extend_expiration.short_description = _('Extend expiration to 24 hours')
    
    def has_add_permission(self, request):
        """Prevent manual cache creation"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow cache deletion only by admin"""
        return request.user.is_superuser


@admin.register(DraftPositionChange)
class DraftPositionChangeAdmin(admin.ModelAdmin):
    """Admin interface for draft position changes"""
    
    list_display = (
        'change_id',
        'get_change_type_display',
        'position',
        'approval_status',
        'created_by',
        'created_at',
        'affected_team_size',
    )
    
    list_filter = (
        'change_type',
        'approval_status',
        'created_at',
        'created_by',
        ('scheduled_effective_date', admin.DateFieldListFilter),
    )
    
    search_fields = (
        'change_id',
        'position__position_code',
        'created_by',
        'approved_by',
    )
    
    readonly_fields = (
        'change_id',
        'created_at',
        'updated_at',
        'old_values',
        'new_values',
        'get_impact_summary',
    )
    
    fieldsets = (
        (
            _('Change Information'),
            {
                'fields': (
                    'change_id',
                    'change_type',
                    'position',
                    'change_description',
                )
            },
        ),
        (
            _('Change Details'),
            {
                'fields': (
                    'old_values',
                    'new_values',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            _('Affected Positions'),
            {
                'fields': (
                    'affected_positions',
                    'affected_team_size',
                )
            },
        ),
        (
            _('Approval'),
            {
                'fields': (
                    'approval_status',
                    'created_by',
                    'approved_by',
                    'approval_comment',
                )
            },
        ),
        (
            _('Impact Analysis'),
            {
                'fields': (
                    'estimated_cost_impact',
                    'get_impact_summary',
                )
            },
        ),
        (
            _('Scheduling'),
            {
                'fields': (
                    'scheduled_effective_date',
                )
            },
        ),
        (
            _('Audit Trail'),
            {
                'fields': (
                    'created_at',
                    'updated_at',
                ),
                'classes': ('collapse',),
            },
        ),
    )
    
    actions = ['approve_changes', 'reject_changes']
    
    def get_impact_summary(self, obj):
        """Display impact summary"""
        summary = obj.get_impact_summary()
        return f"""
        <strong>Change Type:</strong> {summary['change_type']}<br>
        <strong>Affected Positions:</strong> {summary['affected_count']}<br>
        <strong>Team Size Impact:</strong> {summary['team_size_impact']}<br>
        <strong>Cost Impact:</strong> ${summary['cost_impact']}<br>
        <strong>Status:</strong> {summary['status']}
        """
    get_impact_summary.short_description = _('Impact Summary')
    get_impact_summary.allow_tags = True
    
    def approve_changes(self, request, queryset):
        """Approve selected changes"""
        updated = queryset.filter(approval_status='pending').update(
            approval_status='approved',
            approved_by=request.user.username,
        )
        self.message_user(request, _('Approved {} change(s)').format(updated))
    approve_changes.short_description = _('Approve selected changes')
    
    def reject_changes(self, request, queryset):
        """Reject selected changes"""
        updated = queryset.filter(approval_status='pending').update(
            approval_status='rejected',
            approved_by=request.user.username,
        )
        self.message_user(request, _('Rejected {} change(s)').format(updated))
    reject_changes.short_description = _('Reject selected changes')
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion only by admin"""
        return request.user.is_superuser


@admin.register(OrgChartAuditLog)
class OrgChartAuditLogAdmin(admin.ModelAdmin):
    """Admin interface for organization chart audit logs"""
    
    list_display = (
        'get_action_display',
        'position',
        'affected_employee',
        'performed_by',
        'performed_at',
    )
    
    list_filter = (
        'action',
        'performed_at',
        'performed_by',
    )
    
    search_fields = (
        'position__position_code',
        'affected_employee__first_name',
        'affected_employee__last_name',
        'performed_by',
        'change_summary',
    )
    
    readonly_fields = (
        'action',
        'position',
        'affected_employee',
        'old_value',
        'new_value',
        'change_summary',
        'performed_by',
        'performed_at',
        'ip_address',
        'request_id',
    )
    
    fieldsets = (
        (
            _('Action Details'),
            {
                'fields': (
                    'action',
                    'position',
                    'affected_employee',
                )
            },
        ),
        (
            _('Change Information'),
            {
                'fields': (
                    'change_summary',
                    'old_value',
                    'new_value',
                )
            },
        ),
        (
            _('Audit Trail'),
            {
                'fields': (
                    'performed_by',
                    'performed_at',
                    'ip_address',
                    'request_id',
                )
            },
        ),
    )
    
    def has_add_permission(self, request):
        """Prevent manual audit log creation"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make audit logs read-only"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent audit log deletion"""
        return False
