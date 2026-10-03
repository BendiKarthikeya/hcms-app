"""
Audit Log API Views
Location: fits_api/api_views/audit/views.py
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from django.apps import apps



class AuditLogPagination(PageNumberPagination):
    """Pagination for audit logs"""

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class AuditLogListView(APIView):
    """
    List audit logs with filtering

    GET /api/audit-logs/

    Query Parameters:
    - model: Filter by model name (e.g., 'employee', 'payslip')
    - user: Filter by username
    - action: Filter by action (create, update, delete)
    - time_period: Filter by time period (today, 7days, 30days, 90days)
    - start_date: Filter from date (YYYY-MM-DD)
    - end_date: Filter to date (YYYY-MM-DD)
    - search: Search in change reason/comments
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 200)
    """

    permission_classes = [IsAuthenticated]
    pagination_class = AuditLogPagination

    def get(self, request):
        # Check permission
        if not (
            request.user.is_staff
            or request.user.has_perm("fits_audit.view_fitsauditlog")
        ):
            return Response({"error": "Permission denied"}, status=403)

        audit_logs = []

        # Get all models with history
        for model in apps.get_models():
            if hasattr(model, "history"):
                try:
                    history_qs = model.history.all()

                    # Apply filters
                    model_filter = request.GET.get("model")
                    if model_filter and model.__name__.lower() != model_filter.lower():
                        continue

                    user_filter = request.GET.get("user")
                    if user_filter:
                        history_qs = history_qs.filter(
                            history_user__username__icontains=user_filter
                        )

                    action_filter = request.GET.get("action")
                    if action_filter:
                        reason = request.GET.get("action", "").lower()
                        history_qs = history_qs.filter(
                            history_change_reason__icontains=reason
                        )

                    # Time period filter
                    time_period = request.GET.get("time_period")
                    now = timezone.now()
                    if time_period == "today":
                        history_qs = history_qs.filter(history_date__date=now.date())
                    elif time_period == "7days":
                        history_qs = history_qs.filter(
                            history_date__gte=now - timedelta(days=7)
                        )
                    elif time_period == "30days":
                        history_qs = history_qs.filter(
                            history_date__gte=now - timedelta(days=30)
                        )
                    elif time_period == "90days":
                        history_qs = history_qs.filter(
                            history_date__gte=now - timedelta(days=90)
                        )

                    # Date range filter
                    start_date = request.GET.get("start_date")
                    if start_date:
                        history_qs = history_qs.filter(
                            history_date__date__gte=start_date
                        )

                    end_date = request.GET.get("end_date")
                    if end_date:
                        history_qs = history_qs.filter(history_date__date__lte=end_date)

                    # Search filter
                    search = request.GET.get("search")
                    if search:
                        history_qs = history_qs.filter(
                            Q(history_change_reason__icontains=search)
                            | Q(history_user__username__icontains=search)
                        )

                    # Add to list
                    for record in history_qs.order_by("-history_date")[
                        :1000
                    ]:  # Limit to prevent memory issues
                        audit_logs.append(
                            {
                                "id": record.id,
                                "model": model.__name__,
                                "record_id": record.pk,
                                "action": self._get_action_type(record),
                                "user": record.history_user.username
                                if record.history_user
                                else "System",
                                "timestamp": record.history_date.isoformat(),
                                "reason": record.history_change_reason
                                or "No reason provided",
                                "changes": self._format_changes(record),
                            }
                        )

                except Exception:
                    continue

        # Sort by timestamp descending
        audit_logs = sorted(audit_logs, key=lambda x: x["timestamp"], reverse=True)

        # Paginate
        paginator = AuditLogPagination()
        paginated_logs = paginator.paginate_queryset(audit_logs, request)

        return paginator.get_paginated_response(
            {
                "logs": paginated_logs,
                "total_count": len(audit_logs),
            }
        )

    def _get_action_type(self, record):
        """Determine action type from history"""
        reason = (record.history_change_reason or "").lower()
        if "create" in reason or not hasattr(record, "prev_record"):
            return "CREATE"
        elif "delete" in reason:
            return "DELETE"
        else:
            return "UPDATE"

    def _format_changes(self, record):
        """Format field changes"""
        try:
            prev = record.prev_record()
            if not prev:
                return {"_summary": "Record created"}

            changes = {}
            for field in record.__dict__.keys():
                if field.startswith("_") or field.startswith("history_"):
                    continue

                old_val = getattr(prev, field, None)
                new_val = getattr(record, field, None)

                if old_val != new_val:
                    changes[field] = {
                        "old": str(old_val),
                        "new": str(new_val),
                    }

            return changes if changes else {"_summary": "Metadata updated"}
        except:
            return {"_summary": "Unable to parse changes"}


class AuditStatsView(APIView):
    """
    Get audit statistics

    GET /api/audit-logs/stats/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check permission
        if not (
            request.user.is_staff
            or request.user.has_perm("fits_audit.view_fitsauditlog")
        ):
            return Response({"error": "Permission denied"}, status=403)

        now = timezone.now()
        stats = {
            "total_logs": 0,
            "today": 0,
            "this_week": 0,
            "this_month": 0,
            "by_model": {},
            "by_user": {},
            "by_action": {"CREATE": 0, "UPDATE": 0, "DELETE": 0},
        }

        # Count logs by model
        for model in apps.get_models():
            if hasattr(model, "history"):
                try:
                    count = model.history.count()
                    stats["total_logs"] += count

                    if count > 0:
                        stats["by_model"][model.__name__] = count

                        # Today
                        today_count = model.history.filter(
                            history_date__date=now.date()
                        ).count()
                        stats["today"] += today_count

                        # This week
                        week_count = model.history.filter(
                            history_date__gte=now - timedelta(days=7)
                        ).count()
                        stats["this_week"] += week_count

                        # This month
                        month_count = model.history.filter(
                            history_date__gte=now - timedelta(days=30)
                        ).count()
                        stats["this_month"] += month_count

                        # By user
                        for record in model.history.all():
                            user = (
                                record.history_user.username
                                if record.history_user
                                else "System"
                            )
                            stats["by_user"][user] = stats["by_user"].get(user, 0) + 1

                            # By action
                            reason = (record.history_change_reason or "").lower()
                            if "create" in reason or not hasattr(record, "prev_record"):
                                stats["by_action"]["CREATE"] += 1
                            elif "delete" in reason:
                                stats["by_action"]["DELETE"] += 1
                            else:
                                stats["by_action"]["UPDATE"] += 1

                except:
                    continue

        return Response(stats)


class AuditDetailView(APIView):
    """
    Get details of a specific audit log entry

    GET /api/audit-logs/<model>/<record_id>/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, model_name, record_id):
        # Check permission
        if not (
            request.user.is_staff
            or request.user.has_perm("fits_audit.view_fitsauditlog")
        ):
            return Response({"error": "Permission denied"}, status=403)

        try:
            model = apps.get_model("app", model_name)  # May need to adjust app name
        except:
            return Response({"error": "Model not found"}, status=404)

        if not hasattr(model, "history"):
            return Response({"error": "No history for this model"}, status=400)

        try:
            history_records = model.history.filter(id=record_id).order_by(
                "-history_date"
            )
            if not history_records.exists():
                return Response({"error": "Record not found"}, status=404)

            records_data = []
            for record in history_records:
                records_data.append(
                    {
                        "timestamp": record.history_date.isoformat(),
                        "user": record.history_user.username
                        if record.history_user
                        else "System",
                        "action": self._get_action_type(record),
                        "reason": record.history_change_reason,
                        "changes": self._format_changes(record),
                    }
                )

            return Response(
                {
                    "model": model_name,
                    "record_id": record_id,
                    "history": records_data,
                    "total_changes": len(records_data),
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def _get_action_type(self, record):
        """Determine action type from history"""
        reason = (record.history_change_reason or "").lower()
        if "create" in reason or not hasattr(record, "prev_record"):
            return "CREATE"
        elif "delete" in reason:
            return "DELETE"
        else:
            return "UPDATE"

    def _format_changes(self, record):
        """Format field changes"""
        try:
            prev = record.prev_record()
            if not prev:
                return {"_summary": "Record created"}

            changes = {}
            for field in record.__dict__.keys():
                if field.startswith("_") or field.startswith("history_"):
                    continue

                old_val = getattr(prev, field, None)
                new_val = getattr(record, field, None)

                if old_val != new_val:
                    changes[field] = {
                        "old": str(old_val),
                        "new": str(new_val),
                    }

            return changes if changes else {"_summary": "Metadata updated"}
        except:
            return {"_summary": "Unable to parse changes"}
