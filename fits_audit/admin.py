"""
admin.py
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin

from fits_audit.models import AuditTag


class AuditTagAdmin(admin.ModelAdmin):
    """Admin interface for Audit Tags"""

    list_display = ("title", "highlight_badge")
    list_filter = ("highlight",)
    search_fields = ("title",)

    def highlight_badge(self, obj):
        """Display highlight status as badge"""
        if obj.highlight:
            return format_html(
                '<span style="background-color: #ffeb3b; padding: 3px 10px; border-radius: 3px; font-weight: bold;">⭐ Highlighted</span>'
            )
        return "—"

    highlight_badge.short_description = "Highlight Status"


class AuditLogFilter(admin.SimpleListFilter):
    """Custom filter for audit logs by model"""

    title = _("Model/Table")
    parameter_name = "model"

    def lookups(self, request, model_admin):
        """Get list of models with audit history"""
        from django.apps import apps
        from django.contrib.contenttypes.models import ContentType

        models_list = []
        for model in apps.get_models():
            if hasattr(model, "history"):
                ct = ContentType.objects.get_for_model(model)
                models_list.append((ct.id, model.__name__))
        return sorted(set(models_list), key=lambda x: x[1])

    def queryset(self, request, queryset):
        """Filter by content type"""
        if self.value():
            from django.contrib.contenttypes.models import ContentType

            try:
                ContentType.objects.get(id=self.value())
                # Filter historical records by content type
                return queryset.filter(content_type_id=self.value())
            except:
                pass
        return queryset


class ActionFilter(admin.SimpleListFilter):
    """Custom filter for audit action type"""

    title = _("Action Type")
    parameter_name = "action"

    def lookups(self, request, model_admin):
        return [
            ("create", _("Create")),
            ("update", _("Update")),
            ("delete", _("Delete")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "create":
            return queryset.filter(history_change_reason__icontains="created")
        elif self.value() == "update":
            return queryset.filter(history_change_reason__icontains="updated")
        elif self.value() == "delete":
            return queryset.filter(history_change_reason__icontains="deleted")
        return queryset


class DateRangeFilter(admin.SimpleListFilter):
    """Custom filter for date ranges"""

    title = _("Time Period")
    parameter_name = "time_period"

    def lookups(self, request, model_admin):
        from django.utils import timezone

        timezone.now()
        return [
            ("today", _("Today")),
            ("7days", _("Last 7 Days")),
            ("30days", _("Last 30 Days")),
            ("90days", _("Last 90 Days")),
        ]

    def queryset(self, request, queryset):
        from datetime import timedelta
        from django.utils import timezone

        now = timezone.now()
        if self.value() == "today":
            return queryset.filter(history_date__date=now.date())
        elif self.value() == "7days":
            start = now - timedelta(days=7)
            return queryset.filter(history_date__gte=start)
        elif self.value() == "30days":
            start = now - timedelta(days=30)
            return queryset.filter(history_date__gte=start)
        elif self.value() == "90days":
            start = now - timedelta(days=90)
            return queryset.filter(history_date__gte=start)
        return queryset


class FitsAuditLogAdmin(SimpleHistoryAdmin):
    """Enhanced admin interface for audit logs"""

    readonly_fields = (
        "history_date",
        "history_user",
        "history_change_reason",
        "display_changes",
        "display_tags",
    )

    list_display = (
        "get_model_name",
        "history_user",
        "get_action_type",
        "history_date",
        "get_record_id",
        "highlight_status_badge",
    )

    list_filter = (
        DateRangeFilter,
        ActionFilter,
        "history_date",
        "history_user",
    )

    search_fields = (
        "history_user__username",
        "history_user__first_name",
        "history_user__last_name",
        "history_change_reason",
    )

    date_hierarchy = "history_date"

    fieldsets = (
        (
            _("Record Information"),
            {
                "fields": ("history_change_reason", "history_date", "history_user"),
            },
        ),
        (_("Changes"), {"fields": ("display_changes",), "classes": ("collapse",)}),
        (
            _("Metadata"),
            {"fields": ("display_tags", "history_title"), "classes": ("collapse",)},
        ),
    )

    def get_model_name(self, obj):
        """Display the model/table name"""
        if hasattr(obj, "content_type"):
            return obj.content_type.name
        return "—"

    get_model_name.short_description = _("Model")
    get_model_name.admin_order_field = "content_type"

    def get_action_type(self, obj):
        """Display action type with styling"""
        reason = obj.history_change_reason or ""

        if "created" in reason.lower() or not obj.prev_record():
            action = "➕ CREATE"
            color = "green"
        elif "deleted" in reason.lower():
            action = "🗑️ DELETE"
            color = "red"
        else:
            action = "✏️ UPDATE"
            color = "blue"

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            action,
        )

    get_action_type.short_description = _("Action")

    def get_record_id(self, obj):
        """Display ID of modified record"""
        if hasattr(obj, "id"):
            return format_html(
                '<code style="background-color: #f0f0f0; padding: 2px 6px;">{}</code>',
                obj.id,
            )
        return "—"

    get_record_id.short_description = _("Record ID")

    def display_changes(self, obj):
        """Display what changed in readable format"""
        try:
            prev = obj.prev_record()
            if not prev:
                return "New record created"

            changes = []
            for field in obj.__dict__.keys():
                if field.startswith("_"):
                    continue

                old_val = getattr(prev, field, "N/A")
                new_val = getattr(obj, field, "N/A")

                if old_val != new_val and field not in [
                    "history_date",
                    "history_user",
                    "history_id",
                    "history_type",
                ]:
                    changes.append(
                        f"<li><strong>{field}</strong>: <code>{old_val}</code> → <code>{new_val}</code></li>"
                    )

            if changes:
                return format_html(
                    '<ul style="margin: 0; padding-left: 20px;">{}</ul>',
                    "".join(changes),
                )
            else:
                return "No fields changed (metadata update)"
        except Exception as e:
            return f"Error parsing changes: {str(e)}"

    display_changes.short_description = _("What Changed")

    def display_tags(self, obj):
        """Display audit tags if present"""
        if hasattr(obj, "history_tags") and obj.history_tags.exists():
            tags = obj.history_tags.all()
            tag_html = " ".join(
                [
                    f'<span style="background-color: #e0e0e0; padding: 2px 8px; margin: 2px; border-radius: 3px; font-size: 12px;">{tag.title}</span>'
                    for tag in tags
                ]
            )
            return format_html(tag_html)
        return "—"

    display_tags.short_description = _("Tags")

    def highlight_status_badge(self, obj):
        """Display if this record is highlighted"""
        if hasattr(obj, "history_highlight") and obj.history_highlight:
            return format_html("🌟")
        return "—"

    highlight_status_badge.short_description = _("★")

    def has_add_permission(self, request):
        """Audit logs cannot be added manually"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Audit logs cannot be deleted - for data integrity"""
        return False

    def has_change_permission(self, request, obj=None):
        """Audit logs are read-only"""
        return False

    def changelist_view(self, request, extra_context=None):
        """Add statistics to changelist"""
        from django.utils import timezone
        from datetime import timedelta

        extra_context = extra_context or {}

        # Calculate statistics
        total_logs = self.get_queryset(request).count()
        today_logs = (
            self.get_queryset(request)
            .filter(history_date__date=timezone.now().date())
            .count()
        )
        week_logs = (
            self.get_queryset(request)
            .filter(history_date__gte=timezone.now() - timedelta(days=7))
            .count()
        )

        extra_context["audit_stats"] = {
            "total": total_logs,
            "today": today_logs,
            "week": week_logs,
        }

        return super().changelist_view(request, extra_context=extra_context)


# Register your models here.
admin.site.register(AuditTag, AuditTagAdmin)
