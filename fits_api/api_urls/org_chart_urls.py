"""
fits_api/api_urls/org_chart_urls.py
Organization Chart Builder URL Routing
"""

from django.urls import path
from fits_api.api_views.employee.org_chart_builder_views import (
    OrgChartHierarchyView,
    DragDropReorganizeView,
    PositionDetailsUpdateView,
    OrgStructureStatsView,
    CostCenterBreakdownView,
    DepartmentStructureView,
    OrgChartFlatStructureView,
    RecentOrgChangesView,
    OrgChartValidationView,
)

app_name = "org_chart"

urlpatterns = [
    # Hierarchy & Structure
    path("hierarchy/", OrgChartHierarchyView.as_view(), name="hierarchy"),
    path("flat-structure/", OrgChartFlatStructureView.as_view(), name="flat_structure"),
    path(
        "department/<int:department_id>/",
        DepartmentStructureView.as_view(),
        name="department_structure",
    ),
    # Reorganization & Editing
    path("reorganize/", DragDropReorganizeView.as_view(), name="reorganize"),
    path(
        "position/update/", PositionDetailsUpdateView.as_view(), name="position_update"
    ),
    # Analytics & Reporting
    path("stats/", OrgStructureStatsView.as_view(), name="stats"),
    path("cost-centers/", CostCenterBreakdownView.as_view(), name="cost_centers"),
    path("recent-changes/", RecentOrgChangesView.as_view(), name="recent_changes"),
    # Validation
    path("validate/", OrgChartValidationView.as_view(), name="validate"),
]
