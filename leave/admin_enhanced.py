"""
Admin configuration for enhanced leave approval models
Location: leave/admin_enhanced.py
"""

from django.contrib import admin
from leave.models_enhanced_approvals import (
    ApprovalPolicy,
    ApprovalDelegation,
    ApprovalRequest,
    ApprovalOverride,
    ApprovalSLAAlert,
    ApprovalMetrics,
)


@admin.register(ApprovalPolicy)
class ApprovalPolicyAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "company",
        "sla_hours",
        "allow_parallel_approvals",
        "is_active",
        "created_at",
    ]
    list_filter = ["company", "is_active", "allow_parallel_approvals", "created_at"]
    search_fields = ["name", "company__company_name"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Basic Information", {"fields": ("company", "name", "is_active")}),
        ("SLA Configuration", {"fields": ("sla_hours", "escalation_hours")}),
        (
            "Approval Settings",
            {
                "fields": (
                    "allow_parallel_approvals",
                    "auto_approve_threshold_days",
                    "require_manager_confirmation",
                )
            },
        ),
        ("Override Settings", {"fields": ("allow_override", "max_override_count")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(ApprovalDelegation)
class ApprovalDelegationAdmin(admin.ModelAdmin):
    list_display = [
        "delegating_manager",
        "delegated_to",
        "start_date",
        "end_date",
        "status",
        "is_currently_active",
    ]
    list_filter = ["status", "start_date", "end_date", "created_at"]
    search_fields = [
        "delegating_manager__employee_first_name",
        "delegated_to__employee_first_name",
        "reason",
    ]
    filter_horizontal = ["departments"]
    readonly_fields = ["created_at", "revoked_at"]

    fieldsets = (
        (
            "Delegation Details",
            {"fields": ("delegating_manager", "delegated_to", "status")},
        ),
        ("Duration", {"fields": ("start_date", "end_date")}),
        ("Scope", {"fields": ("departments", "reason")}),
        ("Expiry Handling", {"fields": ("is_back_to_original",)}),
        (
            "Revocation",
            {"fields": ("revoked_at", "revoked_by"), "classes": ("collapse",)},
        ),
        ("Timestamps", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = [
        "leave_request",
        "approver",
        "sequence_order",
        "status",
        "assigned_at",
        "sla_deadline",
        "is_overdue",
    ]
    list_filter = [
        "status",
        "approval_type",
        "assigned_at",
        "sla_deadline",
    ]
    search_fields = [
        "leave_request__employee_id__employee_first_name",
        "approver__employee_first_name",
        "approval_comment",
    ]
    readonly_fields = [
        "assigned_at",
        "approved_at",
        "rejected_at",
        "escalated_at",
        "first_notified_at",
        "last_notified_at",
        "is_overdue",
        "days_until_sla_breach",
    ]

    fieldsets = (
        (
            "Assignment",
            {
                "fields": (
                    "leave_request",
                    "approver",
                    "sequence_order",
                    "approval_type",
                    "status",
                )
            },
        ),
        (
            "SLA & Deadlines",
            {
                "fields": (
                    "sla_deadline",
                    "escalation_deadline",
                    "is_overdue",
                    "days_until_sla_breach",
                )
            },
        ),
        (
            "Approval",
            {
                "fields": ("approved_at", "approved_by", "approval_comment"),
                "classes": ("collapse",),
            },
        ),
        (
            "Rejection",
            {
                "fields": ("rejected_at", "rejected_by", "rejection_reason"),
                "classes": ("collapse",),
            },
        ),
        (
            "Escalation",
            {
                "fields": ("escalated_at", "escalation_reason", "escalated_to"),
                "classes": ("collapse",),
            },
        ),
        (
            "Auto-Approval",
            {
                "fields": ("auto_approved", "confirmation_required"),
                "classes": ("collapse",),
            },
        ),
        (
            "Notifications",
            {
                "fields": ("notified_count", "first_notified_at", "last_notified_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ApprovalOverride)
class ApprovalOverrideAdmin(admin.ModelAdmin):
    list_display = [
        "leave_request",
        "original_status",
        "new_status",
        "action",
        "overridden_by",
        "overridden_at",
    ]
    list_filter = ["action", "overridden_at", "original_status", "new_status"]
    search_fields = [
        "leave_request__employee_id__employee_first_name",
        "overridden_by__employee_first_name",
        "reason",
    ]
    readonly_fields = ["overridden_at"]

    fieldsets = (
        (
            "Override Details",
            {"fields": ("leave_request", "original_status", "new_status", "action")},
        ),
        ("Authority", {"fields": ("overridden_by",)}),
        ("Related Request", {"fields": ("approval_request",)}),
        ("Justification", {"fields": ("reason",)}),
        ("Timestamp", {"fields": ("overridden_at",), "classes": ("collapse",)}),
    )


@admin.register(ApprovalSLAAlert)
class ApprovalSLAAlertAdmin(admin.ModelAdmin):
    list_display = [
        "approval_request",
        "alert_type",
        "triggered_at",
        "notification_sent",
        "escalation_triggered",
    ]
    list_filter = [
        "alert_type",
        "notification_sent",
        "escalation_triggered",
        "triggered_at",
    ]
    search_fields = [
        "approval_request__leave_request__employee_id__employee_first_name",
    ]
    readonly_fields = ["triggered_at"]

    def has_add_permission(self, request):
        """Alerts are system-generated, not manually created"""
        return False

    def has_change_permission(self, request, obj=None):
        """Allow marking as notified, but not main fields"""
        return request.user.is_superuser


@admin.register(ApprovalMetrics)
class ApprovalMetricsAdmin(admin.ModelAdmin):
    list_display = [
        "company",
        "approval_period",
        "total_requests",
        "sla_compliance_percentage",
        "escalation_count",
        "calculated_at",
    ]
    list_filter = ["company", "approval_period", "calculated_at"]
    readonly_fields = [
        "total_requests",
        "approved_count",
        "rejected_count",
        "pending_count",
        "auto_approved_count",
        "avg_approval_time_hours",
        "sla_compliance_percentage",
        "escalation_count",
        "bottleneck_approver",
        "bottleneck_requests",
        "bottleneck_avg_days_pending",
        "calculated_at",
    ]

    fieldsets = (
        ("Period", {"fields": ("company", "approval_period")}),
        (
            "Volume Metrics",
            {
                "fields": (
                    "total_requests",
                    "approved_count",
                    "rejected_count",
                    "pending_count",
                    "auto_approved_count",
                )
            },
        ),
        (
            "Performance",
            {
                "fields": (
                    "avg_approval_time_hours",
                    "sla_compliance_percentage",
                    "escalation_count",
                )
            },
        ),
        (
            "Bottleneck Analysis",
            {
                "fields": (
                    "bottleneck_approver",
                    "bottleneck_requests",
                    "bottleneck_avg_days_pending",
                )
            },
        ),
        ("Metadata", {"fields": ("calculated_at",), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request):
        """Metrics are auto-calculated"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of metrics"""
        return False
