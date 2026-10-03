from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from auditlog.models import LogEntry

from fits.decorators import login_required as fits_login_required


@fits_login_required
def audit_dashboard(request):
    """Display audit logs in the main dashboard"""

    # Get filter parameters
    model_filter = request.GET.get("model", "")
    user_filter = request.GET.get("user", "")
    action_filter = request.GET.get("action", "")
    search = request.GET.get("search", "")

    # Get all audit logs from auditlog app
    audit_logs = LogEntry.objects.all().order_by("-timestamp")

    # Apply filters
    if model_filter:
        try:
            ct = ContentType.objects.get(model=model_filter.lower())
            audit_logs = audit_logs.filter(content_type=ct)
        except:
            pass

    if user_filter:
        audit_logs = audit_logs.filter(actor__username__icontains=user_filter)

    if action_filter:
        # action_filter: 0=Create, 1=Update, 2=Delete
        action_map = {0: 0, 1: 1, 2: 2}  # Map to LogEntry action values
        try:
            action_int = int(action_filter)
            if action_int in action_map:
                audit_logs = audit_logs.filter(action=action_map[action_int])
        except ValueError:
            pass

    if search:
        audit_logs = audit_logs.filter(
            Q(changes__icontains=search) | Q(actor__username__icontains=search)
        )

    # Pagination
    paginator = Paginator(audit_logs, 25)  # 25 logs per page
    page = request.GET.get("page", 1)
    logs_page = paginator.get_page(page)

    # Get unique models and users for filter dropdowns
    models = (
        ContentType.objects.filter(logentry__isnull=False)
        .distinct()
        .values_list("model", flat=True)
    )

    users = (
        LogEntry.objects.filter(actor__isnull=False)
        .distinct()
        .values_list("actor__username", flat=True)
    )

    context = {
        "logs": logs_page,
        "models": sorted(set(models)),
        "users": sorted(set(users)),
        "model_filter": model_filter,
        "user_filter": user_filter,
        "action_filter": action_filter,
        "search": search,
        "action_choices": [
            (0, "➕ Created"),
            (1, "✏️ Modified"),
            (2, "🗑️ Deleted"),
        ],
        "paginator": paginator,
    }

    return render(request, "fits_audit/audit_dashboard.html", context)


@fits_login_required
def audit_detail(request, log_id):
    """Display detailed view of a specific audit log"""
    try:
        audit_log = LogEntry.objects.get(id=log_id)
    except LogEntry.DoesNotExist:
        return JsonResponse({"error": "Log not found"}, status=404)

    context = {
        "log": audit_log,
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string("fits_audit/audit_detail.html", context, request)
        return JsonResponse({"html": html})
    else:
        return render(request, "fits_audit/audit_detail.html", context)
