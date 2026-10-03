"""
urls.py

This module is used to map url pattern or request path with view functions
"""

from django.urls import include, path
from django.views.generic import RedirectView

from payroll.models.models import Contract, Payslip
from payroll.views import views, integration_views as views_integration
from payroll import views_eosb, views_wps

urlpatterns = [
    path(
        "payslip-view/",
        RedirectView.as_view(url="/payroll/view-payslip/", permanent=False),
        name="payslip-view-alias",
    ),
    path(
        "allowance-view/",
        RedirectView.as_view(url="/payroll/view-allowance/", permanent=False),
        name="allowance-view-alias",
    ),
    path(
        "deduction-view/",
        RedirectView.as_view(url="/payroll/view-deduction/", permanent=False),
        name="deduction-view-alias",
    ),
    path(
        "contract-view/",
        RedirectView.as_view(url="/payroll/view-contract/", permanent=False),
        name="contract-view-alias",
    ),
    path(
        "wps/",
        RedirectView.as_view(url="/payroll/wps-file-list/", permanent=False),
        name="wps-root-alias",
    ),
    path(
        "eosb/",
        RedirectView.as_view(url="/payroll/eosb-list/", permanent=False),
        name="eosb-root-alias",
    ),
    path(
        "gl-integration/",
        views_integration.gl_integration_dashboard,
        name="gl-integration",
    ),
    path(
        "gl-mapping-create/",
        views_integration.gl_mapping_create,
        name="gl-mapping-create",
    ),
    path(
        "gl-mapping-edit/<int:mapping_id>/",
        views_integration.gl_mapping_edit,
        name="gl-mapping-edit",
    ),
    path(
        "gl-mapping-delete/<int:mapping_id>/",
        views_integration.gl_mapping_delete,
        name="gl-mapping-delete",
    ),
    path(
        "icbs-integration/",
        views_integration.icbs_disbursement_view,
        name="icbs-integration",
    ),
    path(
        "icbs-process-bulk/",
        views_integration.icbs_process_bulk,
        name="icbs-process-bulk",
    ),
    path(
        "icbs-process-payment/<int:payment_id>/",
        views_integration.icbs_process_payment,
        name="icbs-process-payment",
    ),
    path(
        "icbs-config-update/",
        views_integration.icbs_config_update,
        name="icbs-config-update",
    ),
    path("", include("payroll.urls.component_urls")),
    path("", include("payroll.urls.tax_urls")),
    path("get-language-code/", views.get_language_code, name="get-language-code"),
    path("contract-create", views.contract_create, name="contract-create"),
    path(
        "update-contract/<int:contract_id>",
        views.contract_update,
        name="update-contract",
        kwargs={"model": Contract},
    ),
    path(
        "update-contract-status/<int:contract_id>",
        views.contract_status_update,
        name="update-contract-status",
    ),
    path(
        "bulk-update-contract-status",
        views.bulk_contract_status_update,
        name="bulk-update-contract-status",
    ),
    path(
        "update-contract-filing-status/<int:contract_id>",
        views.update_contract_filing_status,
        name="update-contract-filing-status",
    ),
    path(
        "delete-contract/<int:contract_id>",
        views.contract_delete,
        name="delete-contract",
    ),
    path(
        "delete-contract-modal/<int:contract_id>",
        views.contract_delete,
        name="delete-contract-modal",
    ),
    path("view-contract/", views.contract_view, name="view-contract"),
    path(
        "single-contract-view/<int:contract_id>/",
        views.view_single_contract,
        name="single-contract-view",
    ),
    path("payslip-pdf/<int:id>", views.payslip_pdf, name="payslip-pdf"),
    path("contract-filter", views.contract_filter, name="contract-filter"),
    path("settings", views.settings, name="payroll-settings"),
    path(
        "payslip-status-update/<int:payslip_id>/",
        views.update_payslip_status,
        name="payslip-status-update",
    ),
    path(
        "payslip-status-update-no-id",
        views.update_payslip_status_no_id,
        name="payslip-status-update-no-id",
    ),
    path(
        "bulk-payslip-status-update",
        views.bulk_update_payslip_status,
        name="bulk-payslip-status-update",
    ),
    path(
        "view-payslip/<int:payslip_id>/",
        views.view_created_payslip,
        name="view-created-payslip",
        kwargs={"model": Payslip},
    ),
    path(
        "view-payslip-pdf/<int:payslip_id>/",
        views.view_payslip_pdf,
        name="view-payslip-pdf",
    ),
    path(
        "delete-payslip/<int:payslip_id>/", views.delete_payslip, name="delete-payslip"
    ),
    path(
        "contract-info-initial",
        views.contract_info_initial,
        name="contract-info-initial",
    ),
    path(
        "view-payroll-dashboard/",
        views.view_payroll_dashboard,
        name="view-payroll-dashboard",
    ),
    path(
        "dashboard-employee-chart",
        views.dashboard_employee_chart,
        name="dashboard-employee-chart",
    ),
    path(
        "dashboard-payslip-details",
        views.payslip_details,
        name="dashboard-payslip-details",
    ),
    path(
        "dashboard-department-chart",
        views.dashboard_department_chart,
        name="dashboard-department-chart",
    ),
    path(
        "dashboard-contract-ending",
        views.contract_ending,
        name="dashboard-contract-ending",
    ),
    path(
        "dashboard-export/",
        views.payslip_export,
        name="dashboard-export",
    ),
    path(
        "payslip-bulk-delete",
        views.payslip_bulk_delete,
        name="payslip-bulk-delete",
    ),
    path(
        "update-batch-group-name",
        views.slip_group_name_update,
        name="update-batch-group-name",
    ),
    path("contract-export", views.contract_export, name="contract-export"),
    path(
        "contract-bulk-delete",
        views.contract_bulk_delete,
        name="contract-bulk-delete",
    ),
    path("contract-select/", views.contract_select, name="contract-select"),
    path(
        "contract-select-filter/",
        views.contract_select_filter,
        name="contract-select-filter",
    ),
    path("payslip-select/", views.payslip_select, name="payslip-select"),
    path(
        "payslip-select-filter/",
        views.payslip_select_filter,
        name="payslip-select-filter",
    ),
    path(
        "payroll-request-add-comment/<int:payroll_id>/",
        views.create_payrollrequest_comment,
        name="payroll-request-add-comment",
    ),
    path(
        "payroll-request-view-comment/<int:payroll_id>/",
        views.view_payrollrequest_comment,
        name="payroll-request-view-comment",
    ),
    path(
        "payroll-request-delete-comment/<int:comment_id>/",
        views.delete_payrollrequest_comment,
        name="payroll-request-delete-comment",
    ),
    path(
        "delete-reimbursement-comment-file/",
        views.delete_reimbursement_comment_file,
        name="delete-reimbursement-comment-file",
    ),
    path(
        "initial-notice-period",
        views.initial_notice_period,
        name="initial-notice-period",
    ),
    # ===========================Auto payslip generate================================
    path(
        "auto-payslip-settings-view/",
        views.auto_payslip_settings_view,
        name="auto-payslip-settings-view",
    ),
    path(
        "create-auto-payslip",
        views.create_or_update_auto_payslip,
        name="create-auto-payslip",
    ),
    path(
        "update-auto-payslip/<int:auto_id>",
        views.create_or_update_auto_payslip,
        name="update-auto-payslip",
    ),
    path(
        "delete-auto-payslip/<int:auto_id>",
        views.delete_auto_payslip,
        name="delete-auto-payslip",
    ),
    path(
        "activate-auto-payslip-generate",
        views.activate_auto_payslip_generate,
        name="activate-auto-payslip-generate",
    ),
    # ===========================EOSB (End-of-Service Benefits)================================
    path("eosb-settings/", views_eosb.eosb_settings, name="eosb-settings"),
    path("eosb-list/", views_eosb.eosb_list, name="eosb-list"),
    path("eosb-create/", views_eosb.eosb_create, name="eosb-create"),
    path("eosb/<int:pk>/", views_eosb.eosb_detail, name="eosb-detail"),
    path("eosb-export/", views_eosb.eosb_report_export, name="eosb-export"),
    path("eosb-approve/<int:pk>/", views_eosb.eosb_approve, name="eosb-approve"),
    path(
        "eosb-director-approve/<int:pk>/",
        views_eosb.eosb_director_approve,
        name="eosb-director-approve",
    ),
    path("eosb-mark-paid/<int:pk>/", views_eosb.eosb_mark_paid, name="eosb-mark-paid"),
    path(
        "eosb-bulk-calculate/",
        views_eosb.eosb_bulk_calculate,
        name="eosb-bulk-calculate",
    ),
    path("eosb-dashboard/", views_eosb.eosb_dashboard, name="eosb-dashboard"),
    # ===========================WPS (Wage Protection System)================================
    path(
        "wps-global-settings/",
        views_wps.wps_global_settings,
        name="wps-global-settings",
    ),
    path("wps-file-list/", views_wps.wps_file_list, name="wps-file-list"),
    path("wps-file-generate/", views_wps.wps_file_generate, name="wps-file-generate"),
    path("wps-file/<int:pk>/", views_wps.wps_file_detail, name="wps-file-detail"),
    path(
        "wps-file-approve/<int:pk>/",
        views_wps.wps_file_approve,
        name="wps-file-approve",
    ),
    path(
        "wps-file-submit/<int:pk>/", views_wps.wps_file_submit, name="wps-file-submit"
    ),
    path(
        "wps-file-download/<int:pk>/",
        views_wps.wps_file_download,
        name="wps-file-download",
    ),
    path(
        "wps-file-process-response/<int:pk>/",
        views_wps.wps_file_process_response,
        name="wps-file-process-response",
    ),
    path(
        "wps-file-resubmit/<int:pk>/",
        views_wps.wps_file_resubmit,
        name="wps-file-resubmit",
    ),
    path("wps-exceptions/", views_wps.wps_exception_list, name="wps-exceptions"),
    path(
        "wps-exception-resolve/<int:pk>/",
        views_wps.wps_exception_resolve,
        name="wps-exception-resolve",
    ),
    path("wps-dashboard/", views_wps.wps_dashboard, name="wps-dashboard"),
]
