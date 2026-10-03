"""
urls.py

This module is used to map url path with view methods.
"""

from django.urls import path
from django.views.generic import RedirectView
from recruitment.views import views
import recruitment.views.actions
import recruitment.views.bulk_import
import recruitment.views.bulk_recruitment
import recruitment.views.email_templates
import recruitment.views.candidate_dashboard
import recruitment.views.careers
import recruitment.views.cv_upload
import recruitment.views.dashboard
import recruitment.views.manpower
import recruitment.views.offer_tracking
import recruitment.views.reports
import recruitment.views.search
import recruitment.views.surveys
import recruitment.views.advanced_recruitment
import recruitment.views.interview_evaluation
import recruitment.views.integrations
import recruitment.views.offer_management
import recruitment.views.proposal
import recruitment.views.candidate_portal
from base.views import add_remove_dynamic_fields, object_duplicate
from recruitment import cbvs
from recruitment.forms import QuestionForm, RecruitmentCreationForm, StageCreationForm
from recruitment.models import Candidate, Recruitment, RecruitmentSurvey, Stage
from recruitment.views import linkedin, views
from recruitment.views.actions import get_mail_preview, get_template, get_template_hint

urlpatterns = [
    path("recruitment-create", views.recruitment, name="recruitment-create"),
    path(
        "bulk-recruitment/",
        recruitment.views.bulk_recruitment.bulk_recruitment,
        name="bulk-recruitment",
    ),
    path("recruitment-view", views.recruitment_view, name="recruitment-view"),
    path(
        "recruitment-search",
        recruitment.views.search.recruitment_search,
        name="recruitment-search",
    ),
    path(
        "recruitment-update/<int:rec_id>/",
        views.recruitment_update,
        name="recruitment-update",
    ),
    path(
        "recruitment-duplicate/<int:obj_id>/",
        object_duplicate,
        name="recruitment-duplicate",
        kwargs={
            "model": Recruitment,
            "form": RecruitmentCreationForm,
            "template": "recruitment/recruitment_form.html",
        },
    ),
    path(
        "recruitment-update-pipeline/<int:rec_id>/",
        views.recruitment_update_pipeline,
        name="recruitment-update-pipeline",
    ),
    path(
        "recruitment-update-delete/<int:rec_id>/",
        recruitment.views.actions.recruitment_delete_pipeline,
        name="recruitment-delete-pipeline",
    ),
    path(
        "recruitment-delete/<int:rec_id>/",
        recruitment.views.actions.recruitment_delete,
        name="recruitment-delete",
    ),
    path(
        "recruitment-close-pipeline/<int:rec_id>/",
        views.recruitment_close_pipeline,
        name="recruitment-close-pipeline",
    ),
    path(
        "recruitment-reopen-pipeline/<int:rec_id>/",
        views.recruitment_reopen_pipeline,
        name="recruitment-reopen-pipeline",
    ),
    path("pipeline/", views.recruitment_pipeline, name="pipeline"),
    path("careers-apply/", views.careers_apply, name="careers-apply"),
    path("received-recruitments/", views.received_recruitments, name="received-recruitments"),
    path("received-recruitments/approve/<int:approval_id>/", views.approve_employee_recruitment, name="approve-employee-recruitment"),
    path("received-recruitments/reject/<int:approval_id>/", views.reject_employee_recruitment, name="reject-employee-recruitment"),
    path("received-recruitments/query/<int:approval_id>/", views.query_employee_recruitment, name="query-employee-recruitment"),
    path("raise-recruitment/resubmit/<int:rec_id>/", views.resubmit_employee_recruitment, name="resubmit-employee-recruitment"),
    path("received-recruitments/delete/<int:rec_id>/", views.delete_employee_recruitment, name="delete-employee-recruitment"),
    path("received-recruitments/publish/<int:rec_id>/", views.publish_employee_recruitment, name="publish-employee-recruitment"),
    path("received-recruitments/publish-linkedin/<int:rec_id>/", views.publish_to_linkedin_channel, name="publish-to-linkedin"),
    path("received-recruitments/publish-bayt/<int:rec_id>/", views.publish_to_bayt, name="publish-to-bayt"),
    path("received-recruitments/publish-naukrigulf/<int:rec_id>/", views.publish_to_naukrigulf, name="publish-to-naukrigulf"),
    path("received-recruitments/feedback/<int:rec_id>/", views.send_hr_feedback, name="send-hr-feedback"),
    path("received-recruitments/edit/<int:rec_id>/", views.edit_employee_recruitment, name="edit-employee-recruitment"),
    path("careers/", views.careers, name="careers"),
    path("pipeline-search/", views.filter_pipeline, name="pipeline-search"),
    path(
        "pipeline-stages-component/<str:view>/",
        views.stage_component,
        name="pipeline-stages-component",
    ),
    path("get-stage-count", views.get_stage_badge_count, name="get-stage-count"),
    path(
        "update-candidate-stage-and-sequence",
        views.update_candidate_stage_and_sequence,
        name="update-candidate-stage-and-sequence",
    ),
    path(
        "update-candidate-sequence",
        views.update_candidate_sequence,
        name="update-candidate-sequence",
    ),
    # path(
    #     "update-candidate-stage",
    #     views.update_candidate_stage,
    #     name="update-candidate-stage",
    # ),
    path(
        "candidate-stage-component",
        views.candidate_component,
        name="candidate-stage-component",
    ),
    path(
        "candidate-stage-change",
        views.change_candidate_stage,
        name="candidate-stage-change",
    ),
    path("pipeline-card", views.recruitment_pipeline_card, name="pipeline-card"),
    path(
        "recruitment-archive/<int:rec_id>",
        views.recruitment_archive,
        name="recruitment-archive",
    ),
    path(
        "candidate-schedule-date-update",
        views.candidate_schedule_date_update,
        name="candidate-schedule-date-update",
    ),
    path("stage-create", views.stage, name="rec-stage-create"),
    path("stage-view", views.stage_view, name="rec-stage-view"),
    path("stage-data/<int:rec_id>/", views.stage_data, name="stage-data"),
    path("stage-search", recruitment.views.search.stage_search, name="stage-search"),
    path("stage-update/<int:stage_id>/", views.stage_update, name="rec-stage-update"),
    path(
        "rec-stage-duplicate/<int:obj_id>/",
        object_duplicate,
        name="rec-stage-duplicate",
        kwargs={
            "model": Stage,
            "form": StageCreationForm,
            "template": "stage/stage_form.html",
        },
    ),
    path("add-candidate-to-stage", views.add_candidate, name="add-candidate-to-stage"),
    path(
        "stage-update-pipeline/<int:stage_id>/",
        views.stage_update_pipeline,
        name="stage-update-pipeline",
    ),
    path(
        "stage-title-update/<int:stage_id>/",
        views.stage_title_update,
        name="stage-title-update",
    ),
    path(
        "stage-delete/<int:stage_id>/",
        recruitment.views.actions.stage_delete,
        name="rec-stage-delete",
    ),
    path(
        "remove-stage-manager/<int:mid>/<int:sid>/",
        recruitment.views.actions.remove_stage_manager,
        name="rec-remove-stage-manager",
    ),
    path(
        "remove-recruitment-manager/<int:mid>/<int:rid>/",
        recruitment.views.actions.remove_recruitment_manager,
        name="remove-recruitment-manager",
    ),
    path("candidate-create", views.candidate, name="candidate-create"),
    path(
        "recruitment-stage-get/<int:rec_id>/",
        views.recruitment_stage_get,
        name="recruitment-stage-get",
    ),
    path(
        "candidate-stage-update/<int:cand_id>/",
        views.candidate_stage_update,
        name="candidate-stage-update",
    ),
    path("view-note/<int:cand_id>/", views.view_note, name="view-note"),
    path("add-note/<int:cand_id>/", views.add_note, name="add-note"),
    path("add-note", views.add_note, name="add-note-post"),
    path("create-note/<int:cand_id>/", views.create_note, name="create-note"),
    path("create-note", views.create_note, name="create-note-post"),
    path("note-update/<int:note_id>/", views.note_update, name="note-update"),
    path(
        "note-update-individual/<int:note_id>/",
        views.note_update_individual,
        name="note-update-individual",
    ),
    path(
        "note-delete/<int:note_id>/",
        recruitment.views.actions.note_delete,
        name="note-delete",
    ),
    path(
        "note-delete-individual/<int:note_id>/",
        recruitment.views.actions.note_delete_individual,
        name="note-delete-individual",
    ),
    path(
        "candidate-can-view-note/<int:id>/",
        views.candidate_can_view_note,
        name="candidate-can-view-note",
    ),
    path("send-mail/<int:cand_id>/", views.form_send_mail, name="send-mail"),
    path("send-mail/", views.form_send_mail, name="send-mail"),
    path(
        "interview-schedule/<int:cand_id>/",
        views.interview_schedule,
        name="interview-schedule",
    ),
    path(
        "create-interview-schedule/",
        views.create_interview_schedule,
        name="create-interview-schedule",
    ),
    path(
        "create-interview/",
        views.create_interview_schedule,
        name="create-interview",
    ),
    path(
        "edit-interview/<int:interview_id>/",
        views.interview_edit,
        name="edit-interview",
    ),
    path(
        "delete-interview/<int:interview_id>/",
        views.interview_delete,
        name="delete-interview",
    ),
    path("get_managers", views.get_managers, name="get_managers"),
    path("candidate-view/", views.candidate_view, name="candidate-view"),
    path("interview-view/", views.interview_view, name="interview-view"),
    path("candidate/<int:cand_id>/promote-to-onboarding/", views.candidate_promote_to_onboarding, name="candidate-promote-to-onboarding"),
    path("candidate/<int:cand_id>/promote-to-pipeline/", views.candidate_promote_to_pipeline, name="candidate-promote-to-pipeline"),
    path("candidate/<int:cand_id>/reject-send-email/", views.candidate_reject_send_email, name="candidate-reject-send-email"),
    path(
        "interview-filter-view/",
        views.interview_filter_view,
        name="interview-filter-view",
    ),
    path(
        "interview-employee-remove/<int:interview_id>/<int:employee_id>",
        views.interview_employee_remove,
        name="interview-employee-remove",
    ),
    path(
        "candidate-filter-view",
        recruitment.views.search.candidate_filter_view,
        name="candidate-filter-view",
    ),
    path(
        "search-candidate",
        recruitment.views.search.candidate_search,
        name="search-candidate",
    ),
    path("candidate-view-list", views.candidate_view_list, name="candidate-view-list"),
    path("candidate-view-card", views.candidate_view_card, name="candidate-view-card"),
    path("candidate-database/", views.candidate_database_view, name="candidate-database"),
    path("candidate-database-search/", views.candidate_database_search, name="candidate-database-search"),
    path("candidate-info-export", views.candidate_export, name="candidate-info-export"),
    path(
        "candidate-view/<int:cand_id>/",
        views.candidate_view_individual,
        name="candidate-view-individual",
        kwargs={"model": Candidate},
    ),
    path(
        "candidate-update/<int:cand_id>/",
        views.candidate_update,
        name="rec-candidate-update",
        kwargs={"model": Candidate},
    ),
    path(
        "candidate-conversion/<int:cand_id>/",
        views.candidate_conversion,
        name="candidate-conversion",
        kwargs={"model": Candidate},
    ),
    path(
        "delete-profile-image/<int:obj_id>/",
        views.delete_profile_image,
        name="delete-profile-image",
    ),
    path(
        "candidate-delete/<int:cand_id>/",
        recruitment.views.actions.candidate_delete,
        name="rec-candidate-delete",
    ),
    path(
        "candidate-archive/<int:cand_id>/",
        recruitment.views.actions.candidate_archive,
        name="rec-candidate-archive",
    ),
    path(
        "candidate-bulk-delete",
        recruitment.views.actions.candidate_bulk_delete,
        name="candidate-bulk-delete",
    ),
    path(
        "candidate-bulk-archive",
        recruitment.views.actions.candidate_bulk_archive,
        name="candidate-bulk-archive",
    ),
    path(
        "candidate-history/<int:cand_id>/",
        views.candidate_history,
        name="candidate-history",
    ),
    path(
        "application-form",
        recruitment.views.surveys.application_form,
        name="application-form",
    ),
    path(
        "send-acknowledgement", views.send_acknowledgement, name="send-acknowledgement"
    ),
    path(
        "dashboard", recruitment.views.dashboard.dashboard, name="recruitment-dashboard"
    ),
    path(
        "dashboard-pipeline",
        recruitment.views.dashboard.dashboard_pipeline,
        name="recruitment-pipeline",
    ),
    path(
        "get-open-positions",
        recruitment.views.dashboard.get_open_position,
        name="get-open-position",
    ),
    path(
        "dashboard-hiring",
        recruitment.views.dashboard.dashboard_hiring,
        name="dashboard-hiring",
    ),
    path(
        "dashboard-vacancy",
        recruitment.views.dashboard.dashboard_vacancy,
        name="dashboard-vacancy",
    ),
    path(
        "candidate-status",
        recruitment.views.dashboard.candidate_status,
        name="candidate-status",
    ),
    path(
        "candidate-sequence-update",
        views.candidate_sequence_update,
        name="candidate-sequence-update",
    ),
    path(
        "stage-sequence-update",
        views.stage_sequence_update,
        name="stage-sequence-update",
    ),
    path(
        "survey-template-preview/",
        recruitment.views.surveys.survey_preview,
        name="survey-template-preview",
    ),
    path(
        "survey-template-preview/<int:pk>/",
        recruitment.views.surveys.survey_preview,
        name="survey-template-preview",
    ),
    path(
        "update-question-order",
        recruitment.views.surveys.question_order_update,
        name="update-question-order",
    ),
    path(
        "recruitment-application-survey",
        recruitment.views.surveys.survey_form,
        name="recruitment-application-survey",
    ),
    path(
        "recruitment-survey-question-template-view/",
        recruitment.views.surveys.view_question_template,
        name="recruitment-survey-question-template-view",
    ),
    path(
        "recruitment-survey-question-template-create",
        recruitment.views.surveys.create_question_template,
        name="recruitment-survey-question-template-create",
    ),
    path(
        "add-remove-options-field",
        add_remove_dynamic_fields,
        name="add-remove-options-field",
        kwargs={
            "model": RecruitmentSurvey,
            "form_class": QuestionForm,
            "template": "survey/add_more_options.html",
            "field_type": "character",
            "field_name_pre": "options",
        },
    ),
    path(
        "recruitment-survey-question-template-edit/<int:survey_id>/",
        recruitment.views.surveys.update_question_template,
        name="recruitment-survey-question-template-edit",
    ),
    path(
        "recruitment-survey-question-template-duplicate/<int:obj_id>/",
        object_duplicate,
        name="recruitment-survey-question-template-duplicate",
        kwargs={
            "model": RecruitmentSurvey,
            "form": QuestionForm,
            "template": "survey/template_form.html",
        },
    ),
    path(
        "recruitment-survey-question-template-delete/<int:survey_id>/",
        recruitment.views.surveys.delete_survey_question,
        name="recruitment-survey-question-template-delete",
    ),
    path(
        "candidate-survey",
        recruitment.views.surveys.candidate_survey,
        name="candidate-survey",
    ),
    path(
        "filter-survey",
        recruitment.views.search.filter_survey,
        name="rec-filter-survey",
    ),
    path(
        "single-survey-view/<int:survey_id>/",
        recruitment.views.surveys.single_survey,
        name="single-survey-view",
    ),
    path(
        "survey-template-create",
        recruitment.views.surveys.create_template,
        name="survey-template-create",
    ),
    path(
        "survey-template-delete",
        recruitment.views.surveys.delete_template,
        name="survey-template-delete",
    ),
    path(
        "survey-template-question-add",
        recruitment.views.surveys.question_add,
        name="survey-template-question-add",
    ),
    path("candidate-select/", views.candidate_select, name="candidate-select"),
    path(
        "candidate-select-filter/",
        views.candidate_select_filter,
        name="candidate-select-filter",
    ),
    path("skill-zone-view/", views.skill_zone_view, name="skill-zone-view"),
    path("skill-zone-create", views.skill_zone_create, name="skill-zone-create"),
    path(
        "skill-zone-update/<int:sz_id>",
        views.skill_zone_update,
        name="skill-zone-update",
    ),
    path(
        "skill-zone-delete/<int:sz_id>",
        views.skill_zone_delete,
        name="skill-zone-delete",
    ),
    path(
        "skill-zone-archive/<int:sz_id>",
        views.skill_zone_archive,
        name="skill-zone-archive",
    ),
    path("skill-zone-filter", views.skill_zone_filter, name="skill-zone-filter"),
    path(
        "skill-zone-cand-create/<int:sz_id>",
        views.skill_zone_candidate_create,
        name="skill-zone-cand-create",
    ),
    path(
        "skill-zone-cand-card-view/<int:sz_id>/",
        views.skill_zone_cand_card_view,
        name="skill-zone-cand-card-view",
    ),
    path(
        "skill-zone-cand-edit/<int:sz_cand_id>/",
        views.skill_zone_cand_edit,
        name="skill-zone-cand-edit",
    ),
    path(
        "skill-zone-cand-filter",
        views.skill_zone_cand_filter,
        name="skill-zone-cand-filter",
    ),
    path(
        "skill-zone-cand-archive/<int:sz_cand_id>/",
        views.skill_zone_cand_archive,
        name="skill-zone-cand-archive",
    ),
    path("to-skill-zone/<int:cand_id>", views.to_skill_zone, name="to-skill-zone"),
    path(
        "skill-zone-cand-delete/<int:sz_cand_id>",
        views.skill_zone_cand_delete,
        name="skill-zone-cand-delete",
    ),
    path("get-template/<int:obj_id>/", get_template, name="get-template"),
    path("get-mail-preview/", get_mail_preview, name="get-mail-preview"),
    path("get-template-hint/", get_template_hint, name="get-template-hint"),
    path(
        "create-candidate-rating/<int:cand_id>/",
        views.create_candidate_rating,
        name="create-candidate-rating",
    ),
    path(
        "update-candidate-rating/<int:cand_id>/",
        views.update_candidate_rating,
        name="update-candidate-rating",
    ),
    path(
        "open-recruitments",
        views.open_recruitments,
        name="open-recruitments",
    ),
    path(
        "recruitment-details/<int:id>/",
        views.recruitment_details,
        name="recruitment-details",
    ),
    path(
        "add-more-files/<int:id>/",
        views.add_more_files,
        name="add-more-files",
    ),
    path(
        "add-more-files-individual/<int:id>/",
        views.add_more_individual_files,
        name="add-more-files-individual",
    ),
    path(
        "delete-stage-note-file/<int:id>/",
        views.delete_stage_note_file,
        name="delete-stage-note-file",
    ),
    path(
        "delete-individual-note-file/<int:id>/",
        views.delete_individual_note_file,
        name="delete-individual-note-file",
    ),
    path("get-mail-log-rec", views.get_mail_log, name="get-mail-log-rec"),
    path(
        "candidate-self-tracking",
        views.candidate_self_tracking,
        name="candidate-self-tracking",
    ),
    path(
        "candidate-self-tracking-rating-option",
        views.candidate_self_tracking_rating_option,
        name="candidate-self-tracking-rating-option",
    ),
    path(
        "candidate-self-status-tracking/",
        views.candidate_self_status_tracking,
        name="candidate-self-status-tracking",
    ),
    path(
        "candidate-self-status-tracking/<int:cand_id>/",
        views.candidate_self_status_tracking_managers_view,
        name="candidate-self-status-tracking",
    ),
    path(
        "candidate-login",
        views.candidate_login,
        name="candidate-login",
    ),
    path(
        "create-reject-reason", views.create_reject_reason, name="create-reject-reason"
    ),
    path(
        "delete-reject-reasons",
        views.delete_reject_reason,
        name="delete-reject-reasons",
    ),
    path(
        "resume-completion",
        views.resume_completion,
        name="resume-completion",
    ),
    path(
        "check-vaccancy",
        views.check_vaccancy,
        name="check-vaccancy",
    ),
    path(
        "skills-view/",
        views.skills_view,
        name="skills-view",
    ),
    path(
        "create-skills/",
        views.create_skills,
        name="create-skills",
    ),
    path(
        "delete-skills/",
        views.delete_skills,
        name="delete-skills",
    ),
    path(
        "add-bulk-resume/",
        views.add_bulk_resumes,
        name="add-bulk-resume",
    ),
    path(
        "view-bulk-resume/",
        views.view_bulk_resumes,
        name="view-bulk-resume",
    ),
    path(
        "delete-resume-file/",
        views.delete_resume_file,
        name="delete-resume-file",
    ),
    path(
        "matching-resumes/<int:rec_id>",
        views.matching_resumes,
        name="matching-resumes",
    ),
    path(
        "matching-resume-completion",
        views.matching_resume_completion,
        name="matching-resume-completion",
    ),
    path(
        "candidate-reject-reasons/",
        views.candidate_reject_reasons,
        name="candidate-reject-reasons",
    ),
    path(
        "hired-candidate-chart",
        views.hired_candidate_chart,
        name="hired-candidate-chart",
    ),
    path(
        "self-tracking-feature/",
        views.self_tracking_feature,
        name="self-tracking-feature",
    ),
    path(
        "candidate-document-request/",
        views.candidate_document_request,
        name="candidate-document-request",
    ),
    path(
        "candidate-file-upload/<int:id>",
        views.file_upload,
        name="candidate-file-upload",
    ),
    path("candidate-view-file/<int:id>", views.view_file, name="candidate-view-file"),
    path(
        "candidate-document-create/<int:id>",
        views.document_create,
        name="candidate-document-create",
    ),
    path(
        "candidate-update-document-title/<int:id>",
        views.update_document_title,
        name="candidate-update-document-title",
    ),
    path(
        "candidate-document-approve/<int:id>",
        views.document_approve,
        name="candidate-document-approve",
    ),
    path(
        "candidate-document-reject/<int:id>",
        views.document_reject,
        name="candidate-document-reject",
    ),
    path(
        "candidate-document-delete/<int:id>/",
        views.document_delete,
        name="candidate-document-delete",
    ),
    path(
        "candidate-add-notes/<int:cand_id>",
        views.candidate_add_notes,
        name="candidate-add-notes",
    ),
    path(
        "employee-interview-tab",
        views.employee_profile_interview_tab,
        name="employee-interview-tab",
    ),
    # Linkedin Integration urls
    path(
        "linkedin-integration-setting/",
        cbvs.LinkedinSettingSectionView.as_view(),
        name="linkedin-integration-setting",
    ),
    path(
        "linkedin-setting-nav/",
        cbvs.LinkedInSettingNavView.as_view(),
        name="linkedin-setting-nav",
    ),
    path(
        "linkedin-setting-list/",
        cbvs.LinkedInSettingListView.as_view(),
        name="linkedin-setting-list",
    ),
    path(
        "create-linkedin-account/",
        cbvs.LinkedInAccountFormView.as_view(),
        name="create-linkedin-account",
    ),
    path(
        "update-linkedin-account/<int:pk>/",
        cbvs.LinkedInAccountFormView.as_view(),
        name="update-linkedin-account",
    ),
    path(
        "delete-linkedin-account/<int:pk>/",
        linkedin.delete_linkedin_account,
        name="delete-linkedin-account",
    ),
    path(
        "update-isactive-linkedin-account/<int:obj_id>/",
        linkedin.update_isactive_linkedin,
        name="update-isactive-linkedin-account",
    ),
    path("check-linkedin/", linkedin.check_linkedin, name="check-linkedin"),
    path("linkedin/auth/", linkedin.linkedin_oauth_start, name="linkedin-oauth-start"),
    path("linkedin/callback/", linkedin.linkedin_oauth_callback, name="linkedin-oauth-callback"),
    path(
        "val-linkedin/<int:pk>/", linkedin.validate_linkedin_token, name="val-linkedin"
    ),
    path(
        "job-board-settings/",
        recruitment.views.advanced_recruitment.job_board_settings,
        name="job-board-settings",
    ),
    path(
        "cv-screening/",
        recruitment.views.advanced_recruitment.cv_screening,
        name="cv-screening",
    ),
    path(
        "cv-screening/trigger/<int:candidate_id>/",
        recruitment.views.advanced_recruitment.cv_screening_trigger,
        name="cv-screening-trigger",
    ),
    path(
        "evaluation/",
        recruitment.views.advanced_recruitment.candidate_evaluation,
        name="evaluation",
    ),
    path(
        "candidates/dashboard/",
        recruitment.views.candidate_dashboard.candidate_dashboard,
        name="candidate-dashboard",
    ),
    path(
        "candidates/cv-upload/",
        recruitment.views.cv_upload.cv_upload_single,
        name="cv-upload-single",
    ),
    path(
        "candidates/cv-upload/bulk/",
        recruitment.views.cv_upload.cv_upload_bulk,
        name="cv-upload-bulk",
    ),

    # Phase 2 — Manpower Requests & Approvals
    path("manpower/", recruitment.views.manpower.manpower_list, name="manpower-list"),
    path("manpower/create/", recruitment.views.manpower.manpower_create, name="manpower-create"),
    path("manpower/<int:req_id>/", recruitment.views.manpower.manpower_detail, name="manpower-detail"),
    path("manpower/<int:req_id>/submit/", recruitment.views.manpower.manpower_submit, name="manpower-submit"),
    path("manpower/<int:req_id>/resubmit/", recruitment.views.manpower.manpower_resubmit, name="manpower-resubmit"),
    path("manpower/<int:req_id>/stage/", recruitment.views.manpower.manpower_advance_stage, name="manpower-advance-stage"),
    path("approvals/inbox/", recruitment.views.manpower.approval_inbox, name="approval-inbox"),
    path("approvals/<int:req_id>/manual-approve/", recruitment.views.manpower.manual_approve, name="manual-approve"),
    path("approvals/<int:approval_id>/action/", recruitment.views.manpower.approval_action, name="approval-action"),
    path("approvals/rules/", recruitment.views.manpower.approval_rules, name="approval-rules"),
    path("approvals/rules/create/", recruitment.views.manpower.approval_rule_create, name="approval-rule-create"),

    # Phase 3 — Bulk Import
    path("bulk-import/candidates/", recruitment.views.bulk_import.bulk_import_candidates, name="bulk-import-candidates"),
    path("bulk-import/candidates/template/", recruitment.views.bulk_import.bulk_import_candidates_template, name="bulk-import-candidates-template"),
    path("bulk-import/manpower/", recruitment.views.bulk_import.bulk_import_manpower, name="bulk-import-manpower"),
    path("bulk-import/manpower/template/", recruitment.views.bulk_import.bulk_import_manpower_template, name="bulk-import-manpower-template"),

    # Phase 4 — Public Careers
    path("careers/", recruitment.views.careers.careers_index, name="careers-index"),
    path("careers/feed.json", recruitment.views.careers.careers_feed, name="careers-feed"),
    path("careers/<slug:slug>/", recruitment.views.careers.careers_detail, name="careers-detail"),
    path("careers/<slug:slug>/apply/", recruitment.views.careers.careers_apply, name="careers-apply"),

    # Phase 6 — Offer Tracking
    path("offer/", RedirectView.as_view(pattern_name="offer-list", permanent=False)),
    path("offers/", recruitment.views.offer_management.offer_list, name="offer-list"),
    path("offers/create/<int:cand_id>/", recruitment.views.offer_management.offer_create, name="offer-create"),
    path("interview/<int:interview_id>/generate-offer/", recruitment.views.offer_management.generate_offer_from_interview, name="generate-offer-from-interview"),
    path("offers/<int:offer_id>/", recruitment.views.offer_management.offer_detail, name="offer-detail"),
    path("offers/<int:offer_id>/pdf/", recruitment.views.offer_management.offer_pdf, name="offer-pdf"),
    path("offers/<int:offer_id>/send/", recruitment.views.offer_management.offer_send, name="offer-send"),
    path("offers/<int:offer_id>/accept/", recruitment.views.offer_management.offer_accept, name="offer-accept"),
    path("offers/<int:offer_id>/reject/", recruitment.views.offer_management.offer_reject, name="offer-reject"),
    path("offers/<int:offer_id>/submit-approval/", recruitment.views.offer_management.offer_submit_approval, name="offer-submit-approval"),
    path("offers/<int:offer_id>/approval-action/", recruitment.views.offer_management.offer_approval_action, name="offer-approval-action"),
    path("offers/<int:offer_id>/request-visa/", recruitment.views.offer_management.offer_request_visa, name="offer-request-visa"),
    path("offers/onboarding-doc/<int:doc_id>/approve/", recruitment.views.offer_management.onboarding_doc_approve, name="onboarding-doc-approve"),
    path("offers/onboarding-doc/<int:doc_id>/resign/", recruitment.views.offer_management.onboarding_doc_resign, name="onboarding-doc-resign"),
    path("offers/approval-inbox/", recruitment.views.offer_management.offer_approval_inbox, name="offer-approval-inbox"),
    path("offers/templates/", recruitment.views.offer_management.offer_template_list, name="offer-template-list"),
    path("offers/templates/<int:tpl_id>/delete/", recruitment.views.offer_management.offer_template_delete, name="offer-template-delete"),
    path("offers/templates/<int:tpl_id>/preview/", recruitment.views.offer_management.offer_template_preview, name="offer-template-preview"),
    path("offers/sign/<uuid:token>/", recruitment.views.offer_management.offer_candidate_sign, name="offer-candidate-sign"),

    # Candidate self-service portal (public, no login required)
    path("portal/<uuid:token>/", recruitment.views.candidate_portal.candidate_portal, name="candidate-portal"),
    path("portal/<uuid:token>/upload/", recruitment.views.candidate_portal.candidate_portal_upload, name="candidate-portal-upload"),
    path("portal/<uuid:token>/sign/<int:doc_id>/", recruitment.views.candidate_portal.candidate_portal_sign, name="candidate-portal-sign"),
    path("portal/<uuid:token>/delete/<int:upload_id>/", recruitment.views.candidate_portal.candidate_portal_delete, name="candidate-portal-delete"),

    path("offer-tracking/", recruitment.views.offer_tracking.offer_tracking, name="offer-tracking"),
    path("offer-tracking/<int:offer_id>/update/", recruitment.views.offer_tracking.offer_update, name="offer-update"),

    # Employment Proposal (Phase 4)
    path("proposals/", recruitment.views.proposal.proposal_list, name="proposal-list"),
    path("proposals/roles/", recruitment.views.proposal.proposal_role_mapping, name="proposal-roles"),
    path("proposals/picker/<int:interview_id>/", recruitment.views.proposal.proposal_picker, name="proposal-picker"),
    path("proposals/create/<int:interview_id>/", recruitment.views.proposal.proposal_create, name="proposal-create"),
    path("proposals/<int:pk>/", recruitment.views.proposal.proposal_detail, name="proposal-detail"),
    path("proposals/<int:pk>/edit/", recruitment.views.proposal.proposal_edit, name="proposal-edit"),
    path("proposals/<int:pk>/esign/", recruitment.views.proposal.proposal_esign, name="proposal-esign"),
    path("proposals/<int:pk>/reject/", recruitment.views.proposal.proposal_reject, name="proposal-reject"),
    path("proposals/<int:pk>/convert/", recruitment.views.proposal.proposal_convert_to_offer, name="proposal-convert-offer"),

    # Interview Evaluation
    path("interview/<int:interview_id>/evaluate/", recruitment.views.interview_evaluation.evaluation_form, name="interview-evaluation-form"),
    path("interview/<int:interview_id>/summary/", recruitment.views.interview_evaluation.evaluation_summary, name="interview-evaluation-summary"),

    # Integrations: Tawteen + email templates
    path("integrations/tawteen/", recruitment.views.integrations.tawteen_dashboard, name="tawteen-dashboard"),
    path("candidate/<int:cand_id>/email/interview/", recruitment.views.integrations.send_interview_email, name="send-interview-email"),
    path("candidate/<int:cand_id>/email/offer/", recruitment.views.integrations.send_offer_email, name="send-offer-email"),
    path("candidate/<int:cand_id>/email/rejection/", recruitment.views.integrations.send_rejection_email, name="send-rejection-email"),
    path("interview/<int:interview_id>/email/reminder/", recruitment.views.integrations.send_interview_reminder, name="send-interview-reminder"),

    # CV Screening — bulk actions
    path("cv-screening/<int:rec_id>/bulk-reject/", recruitment.views.advanced_recruitment.bulk_send_rejection_emails, name="bulk-reject-emails"),

    # Document Search (Module 9)
    path("document-search/", recruitment.views.manpower.document_search, name="document-search"),

    # Phase 7 — Reports
    path("reports/", recruitment.views.reports.recruitment_reports, name="recruitment-reports"),
    path("reports/export/candidates/", recruitment.views.reports.export_candidates_csv, name="export-candidates-csv"),
    path("reports/export/manpower/", recruitment.views.reports.export_manpower_csv, name="export-manpower-csv"),

    # Email template manager
    path("email-templates/", recruitment.views.email_templates.email_template_list, name="email-template-list"),
    path("email-templates/<int:tpl_id>/edit/", recruitment.views.email_templates.email_template_edit, name="email-template-edit"),
    path("email-templates/<int:tpl_id>/delete/", recruitment.views.email_templates.email_template_delete, name="email-template-delete"),
    path("email-templates/<int:tpl_id>/set-default/", recruitment.views.email_templates.email_template_set_default, name="email-template-set-default"),

    # API endpoints
    path("api/email-templates/", views.api_list_email_templates),
    path("api/email-templates/set-default/", views.api_set_email_template),
    path("api/apply/", views.apply_api),
    path("api/download-resume/<int:app_id>/", views.download_resume),
    path("api/view-resume/<int:app_id>/", views.view_resume),
    path("applications/<int:app_id>/documents/", views.application_documents, name="application-documents"),
    path("candidates/<int:candidate_id>/documents/", views.candidate_documents, name="candidate-documents"),
    path("api/delete/", views.delete_candidate),
    path("api/hr-override/", views.hr_override_application, name="hr-override-application"),
    path("api/second-filter/", views.second_filter_applications, name="second-filter-applications"),
    path("api/applications-poll/", views.applications_poll, name="applications-poll"),
    path("api/reject-with-email/", views.reject_application_with_email, name="reject-application-with-email"),
    path("api/generate-jd/", views.generate_jd_ai, name="generate-jd-ai"),
]
