BEGIN TRANSACTION;
CREATE TABLE "accessibility_defaultaccessibility" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "feature" varchar(100) NOT NULL, "filter" text NOT NULL CHECK ((JSON_VALID("filter") OR "filter" IS NULL)), "exclude_all" bool NOT NULL, "is_enabled" bool NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "accessibility_defaultaccessibility_employees" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "defaultaccessibility_id" bigint NOT NULL REFERENCES "accessibility_defaultaccessibility" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "asset_asset" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "asset_name" varchar(255) NOT NULL, "asset_description" text NULL, "asset_tracking_id" varchar(30) NOT NULL UNIQUE, "asset_purchase_date" date NOT NULL, "asset_purchase_cost" decimal NOT NULL, "asset_status" varchar(40) NOT NULL, "expiry_date" date NULL, "notify_before" integer NULL, "asset_category_id_id" bigint NOT NULL REFERENCES "asset_assetcategory" ("id") DEFERRABLE INITIALLY DEFERRED, "asset_lot_number_id_id" bigint NULL REFERENCES "asset_assetlot" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "owner_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "asset_assetassignment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "assigned_date" date NOT NULL, "return_date" date NULL, "return_condition" text NULL, "return_status" varchar(30) NULL, "return_request" bool NOT NULL, "asset_id_id" bigint NOT NULL REFERENCES "asset_asset" ("id") DEFERRABLE INITIALLY DEFERRED, "assigned_by_employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "assigned_to_employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "asset_assetassignment_assign_images" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "assetassignment_id" bigint NOT NULL REFERENCES "asset_assetassignment" ("id") DEFERRABLE INITIALLY DEFERRED, "returnimages_id" bigint NOT NULL REFERENCES "asset_returnimages" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "asset_assetassignment_return_images" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "assetassignment_id" bigint NOT NULL REFERENCES "asset_assetassignment" ("id") DEFERRABLE INITIALLY DEFERRED, "returnimages_id" bigint NOT NULL REFERENCES "asset_returnimages" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "asset_assetcategory" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "asset_category_name" varchar(255) NOT NULL UNIQUE, "asset_category_description" text NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "asset_assetcategory_company_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "assetcategory_id" bigint NOT NULL REFERENCES "asset_assetcategory" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "asset_assetdocuments" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "file" varchar(100) NULL, "asset_report_id" bigint NOT NULL REFERENCES "asset_assetreport" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "asset_assetlot" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "lot_number" varchar(30) NOT NULL UNIQUE, "lot_description" text NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "asset_assetlot_company_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "assetlot_id" bigint NOT NULL REFERENCES "asset_assetlot" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "asset_assetreport" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(255) NULL, "asset_id_id" bigint NOT NULL REFERENCES "asset_asset" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "asset_assetrequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "asset_request_date" date NOT NULL, "description" text NULL, "asset_request_status" varchar(30) NULL, "asset_category_id_id" bigint NOT NULL REFERENCES "asset_assetcategory" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "requested_employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "asset_returnimages" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "image" varchar(100) NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "attendance_attendancegeneralsetting" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "time_runner" bool NOT NULL);
CREATE TABLE "attendance_attendancelatecomeearlyout" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT);
CREATE TABLE "attendance_gracetime" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "allowed_time" bigint NOT NULL);
CREATE TABLE "auditlog_logentry" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "object_pk" varchar(255) NOT NULL, "object_id" bigint NULL, "object_repr" text NOT NULL, "action" smallint unsigned NOT NULL CHECK ("action" >= 0), "timestamp" datetime NOT NULL, "actor_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "remote_addr" char(39) NULL, "additional_data" text NULL CHECK ((JSON_VALID("additional_data") OR "additional_data" IS NULL)), "serialized_data" text NULL CHECK ((JSON_VALID("serialized_data") OR "serialized_data" IS NULL)), "cid" varchar(255) NULL, "changes_text" text NOT NULL, "changes" text NULL CHECK ((JSON_VALID("changes") OR "changes" IS NULL)), "remote_port" integer unsigned NULL CHECK ("remote_port" >= 0), "actor_email" varchar(254) NULL);
INSERT INTO "auditlog_logentry" VALUES(1,'2',2,'karthikeya',0,'2026-05-29 10:18:28.588446',NULL,4,NULL,NULL,NULL,NULL,'','{"shiftrequestcomment_modified_by": ["None", "base.ShiftRequestComment.None"], "rejectedcandidate_modified_by": ["None", "recruitment.RejectedCandidate.None"], "rotatingworktypeassign_modified_by": ["None", "base.RotatingWorkTypeAssign.None"], "announcementcomment_modified_by": ["None", "base.AnnouncementComment.None"], "password": ["None", "!2i63aq1FAs35q0YZmXEQBoLjG92ahR0IfNVmluiw"], "last_login": ["None", "None"], "is_superuser": ["None", "True"], "username": ["None", "karthikeya"], "first_name": ["None", ""], "last_name": ["None", ""], "email": ["None", "karthikeya@fits.one"], "is_staff": ["None", "True"], "is_active": ["None", "True"], "date_joined": ["None", "2026-05-29 10:18:28.581530"], "recruitmentsurvey_modified_by": ["None", "recruitment.RecruitmentSurvey.None"], "recruitmentapproval_modified_by": ["None", "recruitment.RecruitmentApproval.None"], "employmentproposal_modified_by": ["None", "recruitment.EmploymentProposal.None"], "skillzone_modified_by": ["None", "recruitment.SkillZone.None"], "employeeshiftschedule_modified_by": ["None", "base.EmployeeShiftSchedule.None"], "actiontype_modified_by": ["None", "employee.Actiontype.None"], "approvalstep_modified_by": ["None", "recruitment.ApprovalStep.None"], "savedfilter_modified_by": ["None", "fits_views.SavedFilter.None"], "linkedinaccount_modified_by": ["None", "recruitment.LinkedInAccount.None"], "employeegeneralsetting_modified_by": ["None", "employee.EmployeeGeneralSetting.None"], "recruitmentapprovaldelegation_modified_by": ["None", "recruitment.RecruitmentApprovalDelegation.None"], "policy_modified_by": ["None", "employee.Policy.None"], "notefiles_modified_by": ["None", "employee.NoteFiles.None"], "candidaterating_modified_by": ["None", "recruitment.CandidateRating.None"], "interviewschedule_modified_by": ["None", "recruitment.InterviewSchedule.None"], "jobposition_modified_by": ["None", "base.JobPosition.None"], "interviewevaluation_modified_by": ["None", "recruitment.InterviewEvaluation.None"], "surveytemplate_modified_by": ["None", "recruitment.SurveyTemplate.None"], "togglecolumn_modified_by": ["None", "fits_views.ToggleColumn.None"], "mailbox_integrations": ["None", "base.MailboxIntegration.None"], "candidatedocument_modified_by": ["None", "recruitment.CandidateDocument.None"], "skillzonecandidate_modified_by": ["None", "recruitment.SkillZoneCandidate.None"], "recruitmentsurveyanswer_modified_by": ["None", "recruitment.RecruitmentSurveyAnswer.None"], "questionordering_modified_by": ["None", "recruitment.QuestionOrdering.None"], "skill_modified_by": ["None", "recruitment.Skill.None"], "recruitmentgeneralsetting_modified_by": ["None", "recruitment.RecruitmentGeneralSetting.None"], "rotatingworktype_modified_by": ["None", "base.RotatingWorkType.None"], "manpowerrequest_modified_by": ["None", "recruitment.ManpowerRequest.None"], "employeeshift_modified_by": ["None", "base.EmployeeShift.None"], "rejectreason_modified_by": ["None", "recruitment.RejectReason.None"], "dashboardemployeecharts_modified_by": ["None", "base.DashboardEmployeeCharts.None"], "candidatedocumentrequest_modified_by": ["None", "recruitment.CandidateDocumentRequest.None"], "user_excluded_column": ["None", "fits_views.ToggleColumn.None"], "fitsmailtemplate_modified_by": ["None", "base.FitsMailTemplate.None"], "worktype_modified_by": ["None", "base.WorkType.None"], "accountblockunblock_modified_by": ["None", "fits_audit.AccountBlockUnblock.None"], "bonuspoint_modified_by": ["None", "employee.BonusPoint.None"], "stagefiles_modified_by": ["None", "recruitment.StageFiles.None"], "activegroup_modified_by": ["None", "fits_views.ActiveGroup.None"], "department_modified_by": ["None", "base.Department.None"], "approvalrule_modified_by": ["None", "recruitment.ApprovalRule.None"], "shiftrequest_modified_by": ["None", "base.ShiftRequest.None"], "policymultiplefile_modified_by": ["None", "employee.PolicyMultipleFile.None"], "historytrackingfields_modified_by": ["None", "fits_audit.HistoryTrackingFields.None"], "stagenote_modified_by": ["None", "recruitment.StageNote.None"], "penaltyaccounts_modified_by": ["None", "base.PenaltyAccounts.None"], "activeview_modified_by": ["None", "fits_views.ActiveView.None"], "worktyperequest_modified_by": ["None", "base.WorkTypeRequest.None"], "disciplinaryaction_modified_by": ["None", "employee.DisciplinaryAction.None"], "dynamicemailconfiguration_modified_by": ["None", "base.DynamicEmailConfiguration.None"], "notifications": ["None", "notifications.Notification.None"], "company_modified_by": ["None", "base.Company.None"], "employeebankdetails_modified_by": ["None", "employee.EmployeeBankDetails.None"], "holidays_modified_by": ["None", "base.Holidays.None"], "companyleaves_modified_by": ["None", "base.CompanyLeaves.None"], "is_new_employee": ["None", "False"], "offerletter_modified_by": ["None", "recruitment.OfferLetter.None"], "rotatingshiftassign_modified_by": ["None", "base.RotatingShiftAssign.None"], "profileeditfeature_modified_by": ["None", "employee.ProfileEditFeature.None"], "worktyperequestcomment_modified_by": ["None", "base.WorkTypeRequestComment.None"], "multipleapprovalcondition_modified_by": ["None", "base.MultipleApprovalCondition.None"], "tracklatecomeearlyout_modified_by": ["None", "base.TrackLateComeEarlyOut.None"], "candidate_modified_by": ["None", "recruitment.Candidate.None"], "employeetype_modified_by": ["None", "base.EmployeeType.None"], "employeenote_modified_by": ["None", "employee.EmployeeNote.None"], "activetab_modified_by": ["None", "fits_views.ActiveTab.None"], "rotatingshift_modified_by": ["None", "base.RotatingShift.None"], "jobrole_modified_by": ["None", "base.JobRole.None"], "documentrequest_modified_by": ["None", "fits_documents.DocumentRequest.None"], "recruitment_modified_by": ["None", "recruitment.Recruitment.None"], "stage_modified_by": ["None", "recruitment.Stage.None"], "employeetag_modified_by": ["None", "employee.EmployeeTag.None"], "proposal_status_logs": ["None", "recruitment.ProposalStatusLog.None"], "announcement_modified_by": ["None", "base.Announcement.None"], "tags_modified_by": ["None", "base.Tags.None"], "id": ["None", "2"], "document_modified_by": ["None", "fits_documents.Document.None"]}',NULL,NULL);
INSERT INTO "auditlog_logentry" VALUES(2,'2',2,'karthikeya',1,'2026-05-29 10:18:36.784820',NULL,4,NULL,NULL,NULL,NULL,'','{"password": ["!2i63aq1FAs35q0YZmXEQBoLjG92ahR0IfNVmluiw", "pbkdf2_sha256$600000$uggtVu3v4q0B3r06HhtlQ6$6ENtdvh7esnDlVZiw+kUqhxGwoCpm6yZlXEpTb72UgQ="]}',NULL,NULL);
INSERT INTO "auditlog_logentry" VALUES(3,'2a29vjtrq4ermab8fs34i7sokfqpiwnz',NULL,'2a29vjtrq4ermab8fs34i7sokfqpiwnz',0,'2026-05-29 12:05:38.046466',NULL,6,'127.0.0.1',NULL,NULL,NULL,'','{"expire_date": ["None", "2026-06-12 12:05:38.045424"], "session_key": ["None", "2a29vjtrq4ermab8fs34i7sokfqpiwnz"], "session_data": ["None", "e30:1wSvy6:zrvVFgpL7WRgiTEpf-Af_Nt39QYKoG8VTHKk45tHNGA"]}',NULL,NULL);
INSERT INTO "auditlog_logentry" VALUES(4,'1',1,'hr@fits.com',1,'2026-05-29 12:05:38.047788',NULL,4,'127.0.0.1',NULL,NULL,NULL,'','{"last_login": ["None", "2026-05-29 12:05:38.047165"]}',NULL,NULL);
CREATE TABLE "auth_group" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(150) NOT NULL UNIQUE);
CREATE TABLE "auth_group_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "auth_permission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "codename" varchar(100) NOT NULL, "name" varchar(255) NOT NULL);
INSERT INTO "auth_permission" VALUES(1,1,'add_logentry','Can add log entry');
INSERT INTO "auth_permission" VALUES(2,1,'change_logentry','Can change log entry');
INSERT INTO "auth_permission" VALUES(3,1,'delete_logentry','Can delete log entry');
INSERT INTO "auth_permission" VALUES(4,1,'view_logentry','Can view log entry');
INSERT INTO "auth_permission" VALUES(5,2,'add_permission','Can add permission');
INSERT INTO "auth_permission" VALUES(6,2,'change_permission','Can change permission');
INSERT INTO "auth_permission" VALUES(7,2,'delete_permission','Can delete permission');
INSERT INTO "auth_permission" VALUES(8,2,'view_permission','Can view permission');
INSERT INTO "auth_permission" VALUES(9,3,'add_group','Can add group');
INSERT INTO "auth_permission" VALUES(10,3,'change_group','Can change group');
INSERT INTO "auth_permission" VALUES(11,3,'delete_group','Can delete group');
INSERT INTO "auth_permission" VALUES(12,3,'view_group','Can view group');
INSERT INTO "auth_permission" VALUES(13,4,'add_user','Can add user');
INSERT INTO "auth_permission" VALUES(14,4,'change_user','Can change user');
INSERT INTO "auth_permission" VALUES(15,4,'delete_user','Can delete user');
INSERT INTO "auth_permission" VALUES(16,4,'view_user','Can view user');
INSERT INTO "auth_permission" VALUES(17,5,'add_contenttype','Can add content type');
INSERT INTO "auth_permission" VALUES(18,5,'change_contenttype','Can change content type');
INSERT INTO "auth_permission" VALUES(19,5,'delete_contenttype','Can delete content type');
INSERT INTO "auth_permission" VALUES(20,5,'view_contenttype','Can view content type');
INSERT INTO "auth_permission" VALUES(21,6,'add_session','Can add session');
INSERT INTO "auth_permission" VALUES(22,6,'change_session','Can change session');
INSERT INTO "auth_permission" VALUES(23,6,'delete_session','Can delete session');
INSERT INTO "auth_permission" VALUES(24,6,'view_session','Can view session');
INSERT INTO "auth_permission" VALUES(25,7,'add_audittag','Can add audit tag');
INSERT INTO "auth_permission" VALUES(26,7,'change_audittag','Can change audit tag');
INSERT INTO "auth_permission" VALUES(27,7,'delete_audittag','Can delete audit tag');
INSERT INTO "auth_permission" VALUES(28,7,'view_audittag','Can view audit tag');
INSERT INTO "auth_permission" VALUES(29,8,'add_historytrackingfields','Can add history tracking fields');
INSERT INTO "auth_permission" VALUES(30,8,'change_historytrackingfields','Can change history tracking fields');
INSERT INTO "auth_permission" VALUES(31,8,'delete_historytrackingfields','Can delete history tracking fields');
INSERT INTO "auth_permission" VALUES(32,8,'view_historytrackingfields','Can view history tracking fields');
INSERT INTO "auth_permission" VALUES(33,9,'add_accountblockunblock','Can add account block unblock');
INSERT INTO "auth_permission" VALUES(34,9,'change_accountblockunblock','Can change account block unblock');
INSERT INTO "auth_permission" VALUES(35,9,'delete_accountblockunblock','Can delete account block unblock');
INSERT INTO "auth_permission" VALUES(36,9,'view_accountblockunblock','Can view account block unblock');
INSERT INTO "auth_permission" VALUES(37,10,'add_defaultaccessibility','Can add default accessibility');
INSERT INTO "auth_permission" VALUES(38,10,'change_defaultaccessibility','Can change default accessibility');
INSERT INTO "auth_permission" VALUES(39,10,'delete_defaultaccessibility','Can delete default accessibility');
INSERT INTO "auth_permission" VALUES(40,10,'view_defaultaccessibility','Can view default accessibility');
INSERT INTO "auth_permission" VALUES(41,11,'add_project','Can add project');
INSERT INTO "auth_permission" VALUES(42,11,'change_project','Can change project');
INSERT INTO "auth_permission" VALUES(43,11,'delete_project','Can delete project');
INSERT INTO "auth_permission" VALUES(44,11,'view_project','Can view project');
INSERT INTO "auth_permission" VALUES(45,12,'add_gracetime','Can add grace time');
INSERT INTO "auth_permission" VALUES(46,12,'change_gracetime','Can change grace time');
INSERT INTO "auth_permission" VALUES(47,12,'delete_gracetime','Can delete grace time');
INSERT INTO "auth_permission" VALUES(48,12,'view_gracetime','Can view grace time');
INSERT INTO "auth_permission" VALUES(49,13,'add_attendancelatecomeearlyout','Can add attendance late come early out');
INSERT INTO "auth_permission" VALUES(50,13,'change_attendancelatecomeearlyout','Can change attendance late come early out');
INSERT INTO "auth_permission" VALUES(51,13,'delete_attendancelatecomeearlyout','Can delete attendance late come early out');
INSERT INTO "auth_permission" VALUES(52,13,'view_attendancelatecomeearlyout','Can view attendance late come early out');
INSERT INTO "auth_permission" VALUES(53,14,'add_leavetype','Can add leave type');
INSERT INTO "auth_permission" VALUES(54,14,'change_leavetype','Can change leave type');
INSERT INTO "auth_permission" VALUES(55,14,'delete_leavetype','Can delete leave type');
INSERT INTO "auth_permission" VALUES(56,14,'view_leavetype','Can view leave type');
INSERT INTO "auth_permission" VALUES(57,15,'add_leaverequest','Can add leave request');
INSERT INTO "auth_permission" VALUES(58,15,'change_leaverequest','Can change leave request');
INSERT INTO "auth_permission" VALUES(59,15,'delete_leaverequest','Can delete leave request');
INSERT INTO "auth_permission" VALUES(60,15,'view_leaverequest','Can view leave request');
INSERT INTO "auth_permission" VALUES(61,16,'add_announcement','Can add Announcement');
INSERT INTO "auth_permission" VALUES(62,16,'change_announcement','Can change Announcement');
INSERT INTO "auth_permission" VALUES(63,16,'delete_announcement','Can delete Announcement');
INSERT INTO "auth_permission" VALUES(64,16,'view_announcement','Can view Announcement');
INSERT INTO "auth_permission" VALUES(65,17,'add_announcementcomment','Can add announcement comment');
INSERT INTO "auth_permission" VALUES(66,17,'change_announcementcomment','Can change announcement comment');
INSERT INTO "auth_permission" VALUES(67,17,'delete_announcementcomment','Can delete announcement comment');
INSERT INTO "auth_permission" VALUES(68,17,'view_announcementcomment','Can view announcement comment');
INSERT INTO "auth_permission" VALUES(69,18,'add_announcementexpire','Can add announcement expire');
INSERT INTO "auth_permission" VALUES(70,18,'change_announcementexpire','Can change announcement expire');
INSERT INTO "auth_permission" VALUES(71,18,'delete_announcementexpire','Can delete announcement expire');
INSERT INTO "auth_permission" VALUES(72,18,'view_announcementexpire','Can view announcement expire');
INSERT INTO "auth_permission" VALUES(73,19,'add_announcementview','Can add announcement view');
INSERT INTO "auth_permission" VALUES(74,19,'change_announcementview','Can change announcement view');
INSERT INTO "auth_permission" VALUES(75,19,'delete_announcementview','Can delete announcement view');
INSERT INTO "auth_permission" VALUES(76,19,'view_announcementview','Can view announcement view');
INSERT INTO "auth_permission" VALUES(77,20,'add_attachment','Can add attachment');
INSERT INTO "auth_permission" VALUES(78,20,'change_attachment','Can change attachment');
INSERT INTO "auth_permission" VALUES(79,20,'delete_attachment','Can delete attachment');
INSERT INTO "auth_permission" VALUES(80,20,'view_attachment','Can view attachment');
INSERT INTO "auth_permission" VALUES(81,21,'add_attendanceallowedip','Can add attendance allowed ip');
INSERT INTO "auth_permission" VALUES(82,21,'change_attendanceallowedip','Can change attendance allowed ip');
INSERT INTO "auth_permission" VALUES(83,21,'delete_attendanceallowedip','Can delete attendance allowed ip');
INSERT INTO "auth_permission" VALUES(84,21,'view_attendanceallowedip','Can view attendance allowed ip');
INSERT INTO "auth_permission" VALUES(85,22,'add_baserequestfile','Can add baserequest file');
INSERT INTO "auth_permission" VALUES(86,22,'change_baserequestfile','Can change baserequest file');
INSERT INTO "auth_permission" VALUES(87,22,'delete_baserequestfile','Can delete baserequest file');
INSERT INTO "auth_permission" VALUES(88,22,'view_baserequestfile','Can view baserequest file');
INSERT INTO "auth_permission" VALUES(89,23,'add_biometricattendance','Can add biometric attendance');
INSERT INTO "auth_permission" VALUES(90,23,'change_biometricattendance','Can change biometric attendance');
INSERT INTO "auth_permission" VALUES(91,23,'delete_biometricattendance','Can delete biometric attendance');
INSERT INTO "auth_permission" VALUES(92,23,'view_biometricattendance','Can view biometric attendance');
INSERT INTO "auth_permission" VALUES(93,24,'add_company','Can add Company');
INSERT INTO "auth_permission" VALUES(94,24,'change_company','Can change Company');
INSERT INTO "auth_permission" VALUES(95,24,'delete_company','Can delete Company');
INSERT INTO "auth_permission" VALUES(96,24,'view_company','Can view Company');
INSERT INTO "auth_permission" VALUES(97,25,'add_companyleaves','Can add Company Leave');
INSERT INTO "auth_permission" VALUES(98,25,'change_companyleaves','Can change Company Leave');
INSERT INTO "auth_permission" VALUES(99,25,'delete_companyleaves','Can delete Company Leave');
INSERT INTO "auth_permission" VALUES(100,25,'view_companyleaves','Can view Company Leave');
INSERT INTO "auth_permission" VALUES(101,26,'add_dashboardemployeecharts','Can add Dashboard Employee Charts');
INSERT INTO "auth_permission" VALUES(102,26,'change_dashboardemployeecharts','Can change Dashboard Employee Charts');
INSERT INTO "auth_permission" VALUES(103,26,'delete_dashboardemployeecharts','Can delete Dashboard Employee Charts');
INSERT INTO "auth_permission" VALUES(104,26,'view_dashboardemployeecharts','Can view Dashboard Employee Charts');
INSERT INTO "auth_permission" VALUES(105,27,'add_department','Can add Department');
INSERT INTO "auth_permission" VALUES(106,27,'change_department','Can change Department');
INSERT INTO "auth_permission" VALUES(107,27,'delete_department','Can delete Department');
INSERT INTO "auth_permission" VALUES(108,27,'view_department','Can view Department');
INSERT INTO "auth_permission" VALUES(109,28,'add_driverviewed','Can add driver viewed');
INSERT INTO "auth_permission" VALUES(110,28,'change_driverviewed','Can change driver viewed');
INSERT INTO "auth_permission" VALUES(111,28,'delete_driverviewed','Can delete driver viewed');
INSERT INTO "auth_permission" VALUES(112,28,'view_driverviewed','Can view driver viewed');
INSERT INTO "auth_permission" VALUES(113,29,'add_dynamicemailconfiguration','Can add Email Configuration');
INSERT INTO "auth_permission" VALUES(114,29,'change_dynamicemailconfiguration','Can change Email Configuration');
INSERT INTO "auth_permission" VALUES(115,29,'delete_dynamicemailconfiguration','Can delete Email Configuration');
INSERT INTO "auth_permission" VALUES(116,29,'view_dynamicemailconfiguration','Can view Email Configuration');
INSERT INTO "auth_permission" VALUES(117,30,'add_dynamicpagination','Can add dynamic pagination');
INSERT INTO "auth_permission" VALUES(118,30,'change_dynamicpagination','Can change dynamic pagination');
INSERT INTO "auth_permission" VALUES(119,30,'delete_dynamicpagination','Can delete dynamic pagination');
INSERT INTO "auth_permission" VALUES(120,30,'view_dynamicpagination','Can view dynamic pagination');
INSERT INTO "auth_permission" VALUES(121,31,'add_emaillog','Can add email log');
INSERT INTO "auth_permission" VALUES(122,31,'change_emaillog','Can change email log');
INSERT INTO "auth_permission" VALUES(123,31,'delete_emaillog','Can delete email log');
INSERT INTO "auth_permission" VALUES(124,31,'view_emaillog','Can view email log');
INSERT INTO "auth_permission" VALUES(125,32,'add_employeeshift','Can add Employee Shift');
INSERT INTO "auth_permission" VALUES(126,32,'change_employeeshift','Can change Employee Shift');
INSERT INTO "auth_permission" VALUES(127,32,'delete_employeeshift','Can delete Employee Shift');
INSERT INTO "auth_permission" VALUES(128,32,'view_employeeshift','Can view Employee Shift');
INSERT INTO "auth_permission" VALUES(129,33,'add_employeeshiftday','Can add Employee Shift Day');
INSERT INTO "auth_permission" VALUES(130,33,'change_employeeshiftday','Can change Employee Shift Day');
INSERT INTO "auth_permission" VALUES(131,33,'delete_employeeshiftday','Can delete Employee Shift Day');
INSERT INTO "auth_permission" VALUES(132,33,'view_employeeshiftday','Can view Employee Shift Day');
INSERT INTO "auth_permission" VALUES(133,34,'add_employeeshiftschedule','Can add Employee Shift Schedule');
INSERT INTO "auth_permission" VALUES(134,34,'change_employeeshiftschedule','Can change Employee Shift Schedule');
INSERT INTO "auth_permission" VALUES(135,34,'delete_employeeshiftschedule','Can delete Employee Shift Schedule');
INSERT INTO "auth_permission" VALUES(136,34,'view_employeeshiftschedule','Can view Employee Shift Schedule');
INSERT INTO "auth_permission" VALUES(137,35,'add_employeetype','Can add Employee Type');
INSERT INTO "auth_permission" VALUES(138,35,'change_employeetype','Can change Employee Type');
INSERT INTO "auth_permission" VALUES(139,35,'delete_employeetype','Can delete Employee Type');
INSERT INTO "auth_permission" VALUES(140,35,'view_employeetype','Can view Employee Type');
INSERT INTO "auth_permission" VALUES(141,36,'add_fitsmailtemplate','Can add fits mail template');
INSERT INTO "auth_permission" VALUES(142,36,'change_fitsmailtemplate','Can change fits mail template');
INSERT INTO "auth_permission" VALUES(143,36,'delete_fitsmailtemplate','Can delete fits mail template');
INSERT INTO "auth_permission" VALUES(144,36,'view_fitsmailtemplate','Can view fits mail template');
INSERT INTO "auth_permission" VALUES(145,37,'add_historicalrotatingshiftassign','Can add historical Rotating Shift Assign');
INSERT INTO "auth_permission" VALUES(146,37,'change_historicalrotatingshiftassign','Can change historical Rotating Shift Assign');
INSERT INTO "auth_permission" VALUES(147,37,'delete_historicalrotatingshiftassign','Can delete historical Rotating Shift Assign');
INSERT INTO "auth_permission" VALUES(148,37,'view_historicalrotatingshiftassign','Can view historical Rotating Shift Assign');
INSERT INTO "auth_permission" VALUES(149,38,'add_historicalrotatingworktypeassign','Can add historical Rotating Work Type Assign');
INSERT INTO "auth_permission" VALUES(150,38,'change_historicalrotatingworktypeassign','Can change historical Rotating Work Type Assign');
INSERT INTO "auth_permission" VALUES(151,38,'delete_historicalrotatingworktypeassign','Can delete historical Rotating Work Type Assign');
INSERT INTO "auth_permission" VALUES(152,38,'view_historicalrotatingworktypeassign','Can view historical Rotating Work Type Assign');
INSERT INTO "auth_permission" VALUES(153,39,'add_historicalshiftrequest','Can add historical Shift Request');
INSERT INTO "auth_permission" VALUES(154,39,'change_historicalshiftrequest','Can change historical Shift Request');
INSERT INTO "auth_permission" VALUES(155,39,'delete_historicalshiftrequest','Can delete historical Shift Request');
INSERT INTO "auth_permission" VALUES(156,39,'view_historicalshiftrequest','Can view historical Shift Request');
INSERT INTO "auth_permission" VALUES(157,40,'add_historicalworktyperequest','Can add historical Work Type Request');
INSERT INTO "auth_permission" VALUES(158,40,'change_historicalworktyperequest','Can change historical Work Type Request');
INSERT INTO "auth_permission" VALUES(159,40,'delete_historicalworktyperequest','Can delete historical Work Type Request');
INSERT INTO "auth_permission" VALUES(160,40,'view_historicalworktyperequest','Can view historical Work Type Request');
INSERT INTO "auth_permission" VALUES(161,41,'add_holidays','Can add Holiday');
INSERT INTO "auth_permission" VALUES(162,41,'change_holidays','Can change Holiday');
INSERT INTO "auth_permission" VALUES(163,41,'delete_holidays','Can delete Holiday');
INSERT INTO "auth_permission" VALUES(164,41,'view_holidays','Can view Holiday');
INSERT INTO "auth_permission" VALUES(165,42,'add_hruser','Can add HR User');
INSERT INTO "auth_permission" VALUES(166,42,'change_hruser','Can change HR User');
INSERT INTO "auth_permission" VALUES(167,42,'delete_hruser','Can delete HR User');
INSERT INTO "auth_permission" VALUES(168,42,'view_hruser','Can view HR User');
INSERT INTO "auth_permission" VALUES(169,43,'add_jobposition','Can add Job Position');
INSERT INTO "auth_permission" VALUES(170,43,'change_jobposition','Can change Job Position');
INSERT INTO "auth_permission" VALUES(171,43,'delete_jobposition','Can delete Job Position');
INSERT INTO "auth_permission" VALUES(172,43,'view_jobposition','Can view Job Position');
INSERT INTO "auth_permission" VALUES(173,44,'add_jobrole','Can add Job Role');
INSERT INTO "auth_permission" VALUES(174,44,'change_jobrole','Can change Job Role');
INSERT INTO "auth_permission" VALUES(175,44,'delete_jobrole','Can delete Job Role');
INSERT INTO "auth_permission" VALUES(176,44,'view_jobrole','Can view Job Role');
INSERT INTO "auth_permission" VALUES(177,45,'add_multipleapprovalcondition','Can add multiple approval condition');
INSERT INTO "auth_permission" VALUES(178,45,'change_multipleapprovalcondition','Can change multiple approval condition');
INSERT INTO "auth_permission" VALUES(179,45,'delete_multipleapprovalcondition','Can delete multiple approval condition');
INSERT INTO "auth_permission" VALUES(180,45,'view_multipleapprovalcondition','Can view multiple approval condition');
INSERT INTO "auth_permission" VALUES(181,46,'add_multipleapprovalmanagers','Can add Multiple Approval Managers');
INSERT INTO "auth_permission" VALUES(182,46,'change_multipleapprovalmanagers','Can change Multiple Approval Managers');
INSERT INTO "auth_permission" VALUES(183,46,'delete_multipleapprovalmanagers','Can delete Multiple Approval Managers');
INSERT INTO "auth_permission" VALUES(184,46,'view_multipleapprovalmanagers','Can view Multiple Approval Managers');
INSERT INTO "auth_permission" VALUES(185,47,'add_notificationsound','Can add notification sound');
INSERT INTO "auth_permission" VALUES(186,47,'change_notificationsound','Can change notification sound');
INSERT INTO "auth_permission" VALUES(187,47,'delete_notificationsound','Can delete notification sound');
INSERT INTO "auth_permission" VALUES(188,47,'view_notificationsound','Can view notification sound');
INSERT INTO "auth_permission" VALUES(189,48,'add_penaltyaccounts','Can add Penalty Account');
INSERT INTO "auth_permission" VALUES(190,48,'change_penaltyaccounts','Can change Penalty Account');
INSERT INTO "auth_permission" VALUES(191,48,'delete_penaltyaccounts','Can delete Penalty Account');
INSERT INTO "auth_permission" VALUES(192,48,'view_penaltyaccounts','Can view Penalty Account');
INSERT INTO "auth_permission" VALUES(193,49,'add_rotatingshift','Can add Rotating Shift');
INSERT INTO "auth_permission" VALUES(194,49,'change_rotatingshift','Can change Rotating Shift');
INSERT INTO "auth_permission" VALUES(195,49,'delete_rotatingshift','Can delete Rotating Shift');
INSERT INTO "auth_permission" VALUES(196,49,'view_rotatingshift','Can view Rotating Shift');
INSERT INTO "auth_permission" VALUES(197,50,'add_rotatingshiftassign','Can add Rotating Shift Assign');
INSERT INTO "auth_permission" VALUES(198,50,'change_rotatingshiftassign','Can change Rotating Shift Assign');
INSERT INTO "auth_permission" VALUES(199,50,'delete_rotatingshiftassign','Can delete Rotating Shift Assign');
INSERT INTO "auth_permission" VALUES(200,50,'view_rotatingshiftassign','Can view Rotating Shift Assign');
INSERT INTO "auth_permission" VALUES(201,51,'add_rotatingworktype','Can add Rotating Work Type');
INSERT INTO "auth_permission" VALUES(202,51,'change_rotatingworktype','Can change Rotating Work Type');
INSERT INTO "auth_permission" VALUES(203,51,'delete_rotatingworktype','Can delete Rotating Work Type');
INSERT INTO "auth_permission" VALUES(204,51,'view_rotatingworktype','Can view Rotating Work Type');
INSERT INTO "auth_permission" VALUES(205,52,'add_rotatingworktypeassign','Can add Rotating Work Type Assign');
INSERT INTO "auth_permission" VALUES(206,52,'change_rotatingworktypeassign','Can change Rotating Work Type Assign');
INSERT INTO "auth_permission" VALUES(207,52,'delete_rotatingworktypeassign','Can delete Rotating Work Type Assign');
INSERT INTO "auth_permission" VALUES(208,52,'view_rotatingworktypeassign','Can view Rotating Work Type Assign');
INSERT INTO "auth_permission" VALUES(209,53,'add_shiftrequest','Can add Shift Request');
INSERT INTO "auth_permission" VALUES(210,53,'change_shiftrequest','Can change Shift Request');
INSERT INTO "auth_permission" VALUES(211,53,'delete_shiftrequest','Can delete Shift Request');
INSERT INTO "auth_permission" VALUES(212,53,'view_shiftrequest','Can view Shift Request');
INSERT INTO "auth_permission" VALUES(213,53,'approve_shiftrequest','Approve Shift Request');
INSERT INTO "auth_permission" VALUES(214,53,'cancel_shiftrequest','Cancel Shift Request');
INSERT INTO "auth_permission" VALUES(215,54,'add_shiftrequestcomment','Can add shift request comment');
INSERT INTO "auth_permission" VALUES(216,54,'change_shiftrequestcomment','Can change shift request comment');
INSERT INTO "auth_permission" VALUES(217,54,'delete_shiftrequestcomment','Can delete shift request comment');
INSERT INTO "auth_permission" VALUES(218,54,'view_shiftrequestcomment','Can view shift request comment');
INSERT INTO "auth_permission" VALUES(219,55,'add_tags','Can add Tag');
INSERT INTO "auth_permission" VALUES(220,55,'change_tags','Can change Tag');
INSERT INTO "auth_permission" VALUES(221,55,'delete_tags','Can delete Tag');
INSERT INTO "auth_permission" VALUES(222,55,'view_tags','Can view Tag');
INSERT INTO "auth_permission" VALUES(223,56,'add_tracklatecomeearlyout','Can add Track Late Come Early Out');
INSERT INTO "auth_permission" VALUES(224,56,'change_tracklatecomeearlyout','Can change Track Late Come Early Out');
INSERT INTO "auth_permission" VALUES(225,56,'delete_tracklatecomeearlyout','Can delete Track Late Come Early Out');
INSERT INTO "auth_permission" VALUES(226,56,'view_tracklatecomeearlyout','Can view Track Late Come Early Out');
INSERT INTO "auth_permission" VALUES(227,57,'add_worktype','Can add Work Type');
INSERT INTO "auth_permission" VALUES(228,57,'change_worktype','Can change Work Type');
INSERT INTO "auth_permission" VALUES(229,57,'delete_worktype','Can delete Work Type');
INSERT INTO "auth_permission" VALUES(230,57,'view_worktype','Can view Work Type');
INSERT INTO "auth_permission" VALUES(231,58,'add_worktyperequest','Can add Work Type Request');
INSERT INTO "auth_permission" VALUES(232,58,'change_worktyperequest','Can change Work Type Request');
INSERT INTO "auth_permission" VALUES(233,58,'delete_worktyperequest','Can delete Work Type Request');
INSERT INTO "auth_permission" VALUES(234,58,'view_worktyperequest','Can view Work Type Request');
INSERT INTO "auth_permission" VALUES(235,58,'approve_worktyperequest','Approve Work Type Request');
INSERT INTO "auth_permission" VALUES(236,58,'cancel_worktyperequest','Cancel Work Type Request');
INSERT INTO "auth_permission" VALUES(237,59,'add_worktyperequestcomment','Can add work type request comment');
INSERT INTO "auth_permission" VALUES(238,59,'change_worktyperequestcomment','Can change work type request comment');
INSERT INTO "auth_permission" VALUES(239,59,'delete_worktyperequestcomment','Can delete work type request comment');
INSERT INTO "auth_permission" VALUES(240,59,'view_worktyperequestcomment','Can view work type request comment');
INSERT INTO "auth_permission" VALUES(241,60,'add_mailboxintegration','Can add Mailbox Integration');
INSERT INTO "auth_permission" VALUES(242,60,'change_mailboxintegration','Can change Mailbox Integration');
INSERT INTO "auth_permission" VALUES(243,60,'delete_mailboxintegration','Can delete Mailbox Integration');
INSERT INTO "auth_permission" VALUES(244,60,'view_mailboxintegration','Can view Mailbox Integration');
INSERT INTO "auth_permission" VALUES(245,61,'add_actiontype','Can add Action Type');
INSERT INTO "auth_permission" VALUES(246,61,'change_actiontype','Can change Action Type');
INSERT INTO "auth_permission" VALUES(247,61,'delete_actiontype','Can delete Action Type');
INSERT INTO "auth_permission" VALUES(248,61,'view_actiontype','Can view Action Type');
INSERT INTO "auth_permission" VALUES(249,62,'add_bonuspoint','Can add bonus point');
INSERT INTO "auth_permission" VALUES(250,62,'change_bonuspoint','Can change bonus point');
INSERT INTO "auth_permission" VALUES(251,62,'delete_bonuspoint','Can delete bonus point');
INSERT INTO "auth_permission" VALUES(252,62,'view_bonuspoint','Can view bonus point');
INSERT INTO "auth_permission" VALUES(253,63,'add_employee','Can add employee');
INSERT INTO "auth_permission" VALUES(254,63,'change_employee','Can change employee');
INSERT INTO "auth_permission" VALUES(255,63,'delete_employee','Can delete employee');
INSERT INTO "auth_permission" VALUES(256,63,'view_employee','Can view employee');
INSERT INTO "auth_permission" VALUES(257,63,'change_ownprofile','Update own profile');
INSERT INTO "auth_permission" VALUES(258,63,'view_ownprofile','View Own Profile');
INSERT INTO "auth_permission" VALUES(259,64,'add_employeetag','Can add employee tag');
INSERT INTO "auth_permission" VALUES(260,64,'change_employeetag','Can change employee tag');
INSERT INTO "auth_permission" VALUES(261,64,'delete_employeetag','Can delete employee tag');
INSERT INTO "auth_permission" VALUES(262,64,'view_employeetag','Can view employee tag');
INSERT INTO "auth_permission" VALUES(263,65,'add_employeeworkinformation','Can add employee work information');
INSERT INTO "auth_permission" VALUES(264,65,'change_employeeworkinformation','Can change employee work information');
INSERT INTO "auth_permission" VALUES(265,65,'delete_employeeworkinformation','Can delete employee work information');
INSERT INTO "auth_permission" VALUES(266,65,'view_employeeworkinformation','Can view employee work information');
INSERT INTO "auth_permission" VALUES(267,66,'add_profileeditfeature','Can add profile edit feature');
INSERT INTO "auth_permission" VALUES(268,66,'change_profileeditfeature','Can change profile edit feature');
INSERT INTO "auth_permission" VALUES(269,66,'delete_profileeditfeature','Can delete profile edit feature');
INSERT INTO "auth_permission" VALUES(270,66,'view_profileeditfeature','Can view profile edit feature');
INSERT INTO "auth_permission" VALUES(271,67,'add_policymultiplefile','Can add policy multiple file');
INSERT INTO "auth_permission" VALUES(272,67,'change_policymultiplefile','Can change policy multiple file');
INSERT INTO "auth_permission" VALUES(273,67,'delete_policymultiplefile','Can delete policy multiple file');
INSERT INTO "auth_permission" VALUES(274,67,'view_policymultiplefile','Can view policy multiple file');
INSERT INTO "auth_permission" VALUES(275,68,'add_policy','Can add Policy');
INSERT INTO "auth_permission" VALUES(276,68,'change_policy','Can change Policy');
INSERT INTO "auth_permission" VALUES(277,68,'delete_policy','Can delete Policy');
INSERT INTO "auth_permission" VALUES(278,68,'view_policy','Can view Policy');
INSERT INTO "auth_permission" VALUES(279,69,'add_notefiles','Can add note files');
INSERT INTO "auth_permission" VALUES(280,69,'change_notefiles','Can change note files');
INSERT INTO "auth_permission" VALUES(281,69,'delete_notefiles','Can delete note files');
INSERT INTO "auth_permission" VALUES(282,69,'view_notefiles','Can view note files');
INSERT INTO "auth_permission" VALUES(283,70,'add_historicalemployeeworkinformation','Can add historical employee work information');
INSERT INTO "auth_permission" VALUES(284,70,'change_historicalemployeeworkinformation','Can change historical employee work information');
INSERT INTO "auth_permission" VALUES(285,70,'delete_historicalemployeeworkinformation','Can delete historical employee work information');
INSERT INTO "auth_permission" VALUES(286,70,'view_historicalemployeeworkinformation','Can view historical employee work information');
INSERT INTO "auth_permission" VALUES(287,71,'add_historicalbonuspoint','Can add historical bonus point');
INSERT INTO "auth_permission" VALUES(288,71,'change_historicalbonuspoint','Can change historical bonus point');
INSERT INTO "auth_permission" VALUES(289,71,'delete_historicalbonuspoint','Can delete historical bonus point');
INSERT INTO "auth_permission" VALUES(290,71,'view_historicalbonuspoint','Can view historical bonus point');
INSERT INTO "auth_permission" VALUES(291,72,'add_employeesalaryhistory','Can add Salary History');
INSERT INTO "auth_permission" VALUES(292,72,'change_employeesalaryhistory','Can change Salary History');
INSERT INTO "auth_permission" VALUES(293,72,'delete_employeesalaryhistory','Can delete Salary History');
INSERT INTO "auth_permission" VALUES(294,72,'view_employeesalaryhistory','Can view Salary History');
INSERT INTO "auth_permission" VALUES(295,73,'add_employeenote','Can add employee note');
INSERT INTO "auth_permission" VALUES(296,73,'change_employeenote','Can change employee note');
INSERT INTO "auth_permission" VALUES(297,73,'delete_employeenote','Can delete employee note');
INSERT INTO "auth_permission" VALUES(298,73,'view_employeenote','Can view employee note');
INSERT INTO "auth_permission" VALUES(299,74,'add_employeegeneralsetting','Can add employee general setting');
INSERT INTO "auth_permission" VALUES(300,74,'change_employeegeneralsetting','Can change employee general setting');
INSERT INTO "auth_permission" VALUES(301,74,'delete_employeegeneralsetting','Can delete employee general setting');
INSERT INTO "auth_permission" VALUES(302,74,'view_employeegeneralsetting','Can view employee general setting');
INSERT INTO "auth_permission" VALUES(303,75,'add_employeebankdetails','Can add Employee Bank Details');
INSERT INTO "auth_permission" VALUES(304,75,'change_employeebankdetails','Can change Employee Bank Details');
INSERT INTO "auth_permission" VALUES(305,75,'delete_employeebankdetails','Can delete Employee Bank Details');
INSERT INTO "auth_permission" VALUES(306,75,'view_employeebankdetails','Can view Employee Bank Details');
INSERT INTO "auth_permission" VALUES(307,76,'add_disciplinaryaction','Can add disciplinary action');
INSERT INTO "auth_permission" VALUES(308,76,'change_disciplinaryaction','Can change disciplinary action');
INSERT INTO "auth_permission" VALUES(309,76,'delete_disciplinaryaction','Can delete disciplinary action');
INSERT INTO "auth_permission" VALUES(310,76,'view_disciplinaryaction','Can view disciplinary action');
INSERT INTO "auth_permission" VALUES(311,77,'add_approvalrule','Can add Approval Rule');
INSERT INTO "auth_permission" VALUES(312,77,'change_approvalrule','Can change Approval Rule');
INSERT INTO "auth_permission" VALUES(313,77,'delete_approvalrule','Can delete Approval Rule');
INSERT INTO "auth_permission" VALUES(314,77,'view_approvalrule','Can view Approval Rule');
INSERT INTO "auth_permission" VALUES(315,78,'add_approvalstep','Can add Approval Step');
INSERT INTO "auth_permission" VALUES(316,78,'change_approvalstep','Can change Approval Step');
INSERT INTO "auth_permission" VALUES(317,78,'delete_approvalstep','Can delete Approval Step');
INSERT INTO "auth_permission" VALUES(318,78,'view_approvalstep','Can view Approval Step');
INSERT INTO "auth_permission" VALUES(319,79,'add_candidate','Can add Candidate');
INSERT INTO "auth_permission" VALUES(320,79,'change_candidate','Can change Candidate');
INSERT INTO "auth_permission" VALUES(321,79,'delete_candidate','Can delete Candidate');
INSERT INTO "auth_permission" VALUES(322,79,'view_candidate','Can view Candidate');
INSERT INTO "auth_permission" VALUES(323,79,'view_history','View Candidate History');
INSERT INTO "auth_permission" VALUES(324,79,'archive_candidate','Archive Candidate');
INSERT INTO "auth_permission" VALUES(325,80,'add_evaluationcriteria','Can add Evaluation Criteria');
INSERT INTO "auth_permission" VALUES(326,80,'change_evaluationcriteria','Can change Evaluation Criteria');
INSERT INTO "auth_permission" VALUES(327,80,'delete_evaluationcriteria','Can delete Evaluation Criteria');
INSERT INTO "auth_permission" VALUES(328,80,'view_evaluationcriteria','Can view Evaluation Criteria');
INSERT INTO "auth_permission" VALUES(329,81,'add_jobemailtemplate','Can add job email template');
INSERT INTO "auth_permission" VALUES(330,81,'change_jobemailtemplate','Can change job email template');
INSERT INTO "auth_permission" VALUES(331,81,'delete_jobemailtemplate','Can delete job email template');
INSERT INTO "auth_permission" VALUES(332,81,'view_jobemailtemplate','Can view job email template');
INSERT INTO "auth_permission" VALUES(333,82,'add_linkedinaccount','Can add LinkedIn Account');
INSERT INTO "auth_permission" VALUES(334,82,'change_linkedinaccount','Can change LinkedIn Account');
INSERT INTO "auth_permission" VALUES(335,82,'delete_linkedinaccount','Can delete LinkedIn Account');
INSERT INTO "auth_permission" VALUES(336,82,'view_linkedinaccount','Can view LinkedIn Account');
INSERT INTO "auth_permission" VALUES(337,83,'add_manpowerrequest','Can add Manpower Request');
INSERT INTO "auth_permission" VALUES(338,83,'change_manpowerrequest','Can change Manpower Request');
INSERT INTO "auth_permission" VALUES(339,83,'delete_manpowerrequest','Can delete Manpower Request');
INSERT INTO "auth_permission" VALUES(340,83,'view_manpowerrequest','Can view Manpower Request');
INSERT INTO "auth_permission" VALUES(341,84,'add_offerlettertemplate','Can add Offer Letter Template');
INSERT INTO "auth_permission" VALUES(342,84,'change_offerlettertemplate','Can change Offer Letter Template');
INSERT INTO "auth_permission" VALUES(343,84,'delete_offerlettertemplate','Can delete Offer Letter Template');
INSERT INTO "auth_permission" VALUES(344,84,'view_offerlettertemplate','Can view Offer Letter Template');
INSERT INTO "auth_permission" VALUES(345,85,'add_recruitment','Can add Recruitment');
INSERT INTO "auth_permission" VALUES(346,85,'change_recruitment','Can change Recruitment');
INSERT INTO "auth_permission" VALUES(347,85,'delete_recruitment','Can delete Recruitment');
INSERT INTO "auth_permission" VALUES(348,85,'view_recruitment','Can view Recruitment');
INSERT INTO "auth_permission" VALUES(349,85,'archive_recruitment','Archive Recruitment');
INSERT INTO "auth_permission" VALUES(350,86,'add_skillzone','Can add Skill Zone');
INSERT INTO "auth_permission" VALUES(351,86,'change_skillzone','Can change Skill Zone');
INSERT INTO "auth_permission" VALUES(352,86,'delete_skillzone','Can delete Skill Zone');
INSERT INTO "auth_permission" VALUES(353,86,'view_skillzone','Can view Skill Zone');
INSERT INTO "auth_permission" VALUES(354,87,'add_stage','Can add Stage');
INSERT INTO "auth_permission" VALUES(355,87,'change_stage','Can change Stage');
INSERT INTO "auth_permission" VALUES(356,87,'delete_stage','Can delete Stage');
INSERT INTO "auth_permission" VALUES(357,87,'view_stage','Can view Stage');
INSERT INTO "auth_permission" VALUES(358,87,'archive_Stage','Archive Stage');
INSERT INTO "auth_permission" VALUES(359,88,'add_stagefiles','Can add stage files');
INSERT INTO "auth_permission" VALUES(360,88,'change_stagefiles','Can change stage files');
INSERT INTO "auth_permission" VALUES(361,88,'delete_stagefiles','Can delete stage files');
INSERT INTO "auth_permission" VALUES(362,88,'view_stagefiles','Can view stage files');
INSERT INTO "auth_permission" VALUES(363,89,'add_surveytemplate','Can add Survey Template');
INSERT INTO "auth_permission" VALUES(364,89,'change_surveytemplate','Can change Survey Template');
INSERT INTO "auth_permission" VALUES(365,89,'delete_surveytemplate','Can delete Survey Template');
INSERT INTO "auth_permission" VALUES(366,89,'view_surveytemplate','Can view Survey Template');
INSERT INTO "auth_permission" VALUES(367,90,'add_stagenote','Can add stage note');
INSERT INTO "auth_permission" VALUES(368,90,'change_stagenote','Can change stage note');
INSERT INTO "auth_permission" VALUES(369,90,'delete_stagenote','Can delete stage note');
INSERT INTO "auth_permission" VALUES(370,90,'view_stagenote','Can view stage note');
INSERT INTO "auth_permission" VALUES(371,91,'add_skillzonecandidate','Can add skill zone candidate');
INSERT INTO "auth_permission" VALUES(372,91,'change_skillzonecandidate','Can change skill zone candidate');
INSERT INTO "auth_permission" VALUES(373,91,'delete_skillzonecandidate','Can delete skill zone candidate');
INSERT INTO "auth_permission" VALUES(374,91,'view_skillzonecandidate','Can view skill zone candidate');
INSERT INTO "auth_permission" VALUES(375,92,'add_skill','Can add Skill');
INSERT INTO "auth_permission" VALUES(376,92,'change_skill','Can change Skill');
INSERT INTO "auth_permission" VALUES(377,92,'delete_skill','Can delete Skill');
INSERT INTO "auth_permission" VALUES(378,92,'view_skill','Can view Skill');
INSERT INTO "auth_permission" VALUES(379,93,'add_resume','Can add resume');
INSERT INTO "auth_permission" VALUES(380,93,'change_resume','Can change resume');
INSERT INTO "auth_permission" VALUES(381,93,'delete_resume','Can delete resume');
INSERT INTO "auth_permission" VALUES(382,93,'view_resume','Can view resume');
INSERT INTO "auth_permission" VALUES(383,94,'add_rejectreason','Can add Reject Reason');
INSERT INTO "auth_permission" VALUES(384,94,'change_rejectreason','Can change Reject Reason');
INSERT INTO "auth_permission" VALUES(385,94,'delete_rejectreason','Can delete Reject Reason');
INSERT INTO "auth_permission" VALUES(386,94,'view_rejectreason','Can view Reject Reason');
INSERT INTO "auth_permission" VALUES(387,95,'add_rejectedcandidate','Can add Rejected Candidate');
INSERT INTO "auth_permission" VALUES(388,95,'change_rejectedcandidate','Can change Rejected Candidate');
INSERT INTO "auth_permission" VALUES(389,95,'delete_rejectedcandidate','Can delete Rejected Candidate');
INSERT INTO "auth_permission" VALUES(390,95,'view_rejectedcandidate','Can view Rejected Candidate');
INSERT INTO "auth_permission" VALUES(391,96,'add_recruitmentsurveyanswer','Can add recruitment survey answer');
INSERT INTO "auth_permission" VALUES(392,96,'change_recruitmentsurveyanswer','Can change recruitment survey answer');
INSERT INTO "auth_permission" VALUES(393,96,'delete_recruitmentsurveyanswer','Can delete recruitment survey answer');
INSERT INTO "auth_permission" VALUES(394,96,'view_recruitmentsurveyanswer','Can view recruitment survey answer');
INSERT INTO "auth_permission" VALUES(395,97,'add_recruitmentsurvey','Can add recruitment survey');
INSERT INTO "auth_permission" VALUES(396,97,'change_recruitmentsurvey','Can change recruitment survey');
INSERT INTO "auth_permission" VALUES(397,97,'delete_recruitmentsurvey','Can delete recruitment survey');
INSERT INTO "auth_permission" VALUES(398,97,'view_recruitmentsurvey','Can view recruitment survey');
INSERT INTO "auth_permission" VALUES(399,98,'add_recruitmentgeneralsetting','Can add recruitment general setting');
INSERT INTO "auth_permission" VALUES(400,98,'change_recruitmentgeneralsetting','Can change recruitment general setting');
INSERT INTO "auth_permission" VALUES(401,98,'delete_recruitmentgeneralsetting','Can delete recruitment general setting');
INSERT INTO "auth_permission" VALUES(402,98,'view_recruitmentgeneralsetting','Can view recruitment general setting');
INSERT INTO "auth_permission" VALUES(403,99,'add_recruitmentapprovaldelegation','Can add Approval Delegation');
INSERT INTO "auth_permission" VALUES(404,99,'change_recruitmentapprovaldelegation','Can change Approval Delegation');
INSERT INTO "auth_permission" VALUES(405,99,'delete_recruitmentapprovaldelegation','Can delete Approval Delegation');
INSERT INTO "auth_permission" VALUES(406,99,'view_recruitmentapprovaldelegation','Can view Approval Delegation');
INSERT INTO "auth_permission" VALUES(407,100,'add_recruitmentapproval','Can add Recruitment Approval');
INSERT INTO "auth_permission" VALUES(408,100,'change_recruitmentapproval','Can change Recruitment Approval');
INSERT INTO "auth_permission" VALUES(409,100,'delete_recruitmentapproval','Can delete Recruitment Approval');
INSERT INTO "auth_permission" VALUES(410,100,'view_recruitmentapproval','Can view Recruitment Approval');
INSERT INTO "auth_permission" VALUES(411,101,'add_questionordering','Can add question ordering');
INSERT INTO "auth_permission" VALUES(412,101,'change_questionordering','Can change question ordering');
INSERT INTO "auth_permission" VALUES(413,101,'delete_questionordering','Can delete question ordering');
INSERT INTO "auth_permission" VALUES(414,101,'view_questionordering','Can view question ordering');
INSERT INTO "auth_permission" VALUES(415,102,'add_parsedcvdata','Can add Parsed CV Data');
INSERT INTO "auth_permission" VALUES(416,102,'change_parsedcvdata','Can change Parsed CV Data');
INSERT INTO "auth_permission" VALUES(417,102,'delete_parsedcvdata','Can delete Parsed CV Data');
INSERT INTO "auth_permission" VALUES(418,102,'view_parsedcvdata','Can view Parsed CV Data');
INSERT INTO "auth_permission" VALUES(419,103,'add_offerletter','Can add Offer Letter');
INSERT INTO "auth_permission" VALUES(420,103,'change_offerletter','Can change Offer Letter');
INSERT INTO "auth_permission" VALUES(421,103,'delete_offerletter','Can delete Offer Letter');
INSERT INTO "auth_permission" VALUES(422,103,'view_offerletter','Can view Offer Letter');
INSERT INTO "auth_permission" VALUES(423,104,'add_offerapproval','Can add Offer Approval');
INSERT INTO "auth_permission" VALUES(424,104,'change_offerapproval','Can change Offer Approval');
INSERT INTO "auth_permission" VALUES(425,104,'delete_offerapproval','Can delete Offer Approval');
INSERT INTO "auth_permission" VALUES(426,104,'view_offerapproval','Can view Offer Approval');
INSERT INTO "auth_permission" VALUES(427,105,'add_manpowerrequeststatuslog','Can add Status Log');
INSERT INTO "auth_permission" VALUES(428,105,'change_manpowerrequeststatuslog','Can change Status Log');
INSERT INTO "auth_permission" VALUES(429,105,'delete_manpowerrequeststatuslog','Can delete Status Log');
INSERT INTO "auth_permission" VALUES(430,105,'view_manpowerrequeststatuslog','Can view Status Log');
INSERT INTO "auth_permission" VALUES(431,106,'add_manpowerapproval','Can add Manpower Approval');
INSERT INTO "auth_permission" VALUES(432,106,'change_manpowerapproval','Can change Manpower Approval');
INSERT INTO "auth_permission" VALUES(433,106,'delete_manpowerapproval','Can delete Manpower Approval');
INSERT INTO "auth_permission" VALUES(434,106,'view_manpowerapproval','Can view Manpower Approval');
INSERT INTO "auth_permission" VALUES(435,107,'add_jobapplication','Can add job application');
INSERT INTO "auth_permission" VALUES(436,107,'change_jobapplication','Can change job application');
INSERT INTO "auth_permission" VALUES(437,107,'delete_jobapplication','Can delete job application');
INSERT INTO "auth_permission" VALUES(438,107,'view_jobapplication','Can view job application');
INSERT INTO "auth_permission" VALUES(439,108,'add_interviewschedule','Can add Schedule Interview');
INSERT INTO "auth_permission" VALUES(440,108,'change_interviewschedule','Can change Schedule Interview');
INSERT INTO "auth_permission" VALUES(441,108,'delete_interviewschedule','Can delete Schedule Interview');
INSERT INTO "auth_permission" VALUES(442,108,'view_interviewschedule','Can view Schedule Interview');
INSERT INTO "auth_permission" VALUES(443,109,'add_interviewevaluation','Can add Interview Evaluation');
INSERT INTO "auth_permission" VALUES(444,109,'change_interviewevaluation','Can change Interview Evaluation');
INSERT INTO "auth_permission" VALUES(445,109,'delete_interviewevaluation','Can delete Interview Evaluation');
INSERT INTO "auth_permission" VALUES(446,109,'view_interviewevaluation','Can view Interview Evaluation');
INSERT INTO "auth_permission" VALUES(447,110,'add_historicalrejectedcandidate','Can add historical Rejected Candidate');
INSERT INTO "auth_permission" VALUES(448,110,'change_historicalrejectedcandidate','Can change historical Rejected Candidate');
INSERT INTO "auth_permission" VALUES(449,110,'delete_historicalrejectedcandidate','Can delete historical Rejected Candidate');
INSERT INTO "auth_permission" VALUES(450,110,'view_historicalrejectedcandidate','Can view historical Rejected Candidate');
INSERT INTO "auth_permission" VALUES(451,111,'add_historicalcandidate','Can add historical Candidate');
INSERT INTO "auth_permission" VALUES(452,111,'change_historicalcandidate','Can change historical Candidate');
INSERT INTO "auth_permission" VALUES(453,111,'delete_historicalcandidate','Can delete historical Candidate');
INSERT INTO "auth_permission" VALUES(454,111,'view_historicalcandidate','Can view historical Candidate');
INSERT INTO "auth_permission" VALUES(455,112,'add_cvscreeninglog','Can add CV Screening Log');
INSERT INTO "auth_permission" VALUES(456,112,'change_cvscreeninglog','Can change CV Screening Log');
INSERT INTO "auth_permission" VALUES(457,112,'delete_cvscreeninglog','Can delete CV Screening Log');
INSERT INTO "auth_permission" VALUES(458,112,'view_cvscreeninglog','Can view CV Screening Log');
INSERT INTO "auth_permission" VALUES(459,113,'add_cvparsingsettings','Can add CV Parsing Settings');
INSERT INTO "auth_permission" VALUES(460,113,'change_cvparsingsettings','Can change CV Parsing Settings');
INSERT INTO "auth_permission" VALUES(461,113,'delete_cvparsingsettings','Can delete CV Parsing Settings');
INSERT INTO "auth_permission" VALUES(462,113,'view_cvparsingsettings','Can view CV Parsing Settings');
INSERT INTO "auth_permission" VALUES(463,114,'add_candidatescreeningprofile','Can add candidate screening profile');
INSERT INTO "auth_permission" VALUES(464,114,'change_candidatescreeningprofile','Can change candidate screening profile');
INSERT INTO "auth_permission" VALUES(465,114,'delete_candidatescreeningprofile','Can delete candidate screening profile');
INSERT INTO "auth_permission" VALUES(466,114,'view_candidatescreeningprofile','Can view candidate screening profile');
INSERT INTO "auth_permission" VALUES(467,115,'add_candidatedocumentrequest','Can add candidate document request');
INSERT INTO "auth_permission" VALUES(468,115,'change_candidatedocumentrequest','Can change candidate document request');
INSERT INTO "auth_permission" VALUES(469,115,'delete_candidatedocumentrequest','Can delete candidate document request');
INSERT INTO "auth_permission" VALUES(470,115,'view_candidatedocumentrequest','Can view candidate document request');
INSERT INTO "auth_permission" VALUES(471,116,'add_candidatedocument','Can add candidate document');
INSERT INTO "auth_permission" VALUES(472,116,'change_candidatedocument','Can change candidate document');
INSERT INTO "auth_permission" VALUES(473,116,'delete_candidatedocument','Can delete candidate document');
INSERT INTO "auth_permission" VALUES(474,116,'view_candidatedocument','Can view candidate document');
INSERT INTO "auth_permission" VALUES(475,117,'add_evaluationscore','Can add evaluation score');
INSERT INTO "auth_permission" VALUES(476,117,'change_evaluationscore','Can change evaluation score');
INSERT INTO "auth_permission" VALUES(477,117,'delete_evaluationscore','Can delete evaluation score');
INSERT INTO "auth_permission" VALUES(478,117,'view_evaluationscore','Can view evaluation score');
INSERT INTO "auth_permission" VALUES(479,118,'add_candidateskillmatch','Can add Candidate Skill Match');
INSERT INTO "auth_permission" VALUES(480,118,'change_candidateskillmatch','Can change Candidate Skill Match');
INSERT INTO "auth_permission" VALUES(481,118,'delete_candidateskillmatch','Can delete Candidate Skill Match');
INSERT INTO "auth_permission" VALUES(482,118,'view_candidateskillmatch','Can view Candidate Skill Match');
INSERT INTO "auth_permission" VALUES(483,119,'add_candidaterating','Can add candidate rating');
INSERT INTO "auth_permission" VALUES(484,119,'change_candidaterating','Can change candidate rating');
INSERT INTO "auth_permission" VALUES(485,119,'delete_candidaterating','Can delete candidate rating');
INSERT INTO "auth_permission" VALUES(486,119,'view_candidaterating','Can view candidate rating');
INSERT INTO "auth_permission" VALUES(487,120,'add_candidaterankingscore','Can add Candidate Ranking Score');
INSERT INTO "auth_permission" VALUES(488,120,'change_candidaterankingscore','Can change Candidate Ranking Score');
INSERT INTO "auth_permission" VALUES(489,120,'delete_candidaterankingscore','Can delete Candidate Ranking Score');
INSERT INTO "auth_permission" VALUES(490,120,'view_candidaterankingscore','Can view Candidate Ranking Score');
INSERT INTO "auth_permission" VALUES(491,121,'add_offerletterapproval','Can add Offer Letter Approval');
INSERT INTO "auth_permission" VALUES(492,121,'change_offerletterapproval','Can change Offer Letter Approval');
INSERT INTO "auth_permission" VALUES(493,121,'delete_offerletterapproval','Can delete Offer Letter Approval');
INSERT INTO "auth_permission" VALUES(494,121,'view_offerletterapproval','Can view Offer Letter Approval');
INSERT INTO "auth_permission" VALUES(495,122,'add_interviewround','Can add Interview Round');
INSERT INTO "auth_permission" VALUES(496,122,'change_interviewround','Can change Interview Round');
INSERT INTO "auth_permission" VALUES(497,122,'delete_interviewround','Can delete Interview Round');
INSERT INTO "auth_permission" VALUES(498,122,'view_interviewround','Can view Interview Round');
INSERT INTO "auth_permission" VALUES(499,123,'add_medicallettertemplate','Can add Medical Letter Template');
INSERT INTO "auth_permission" VALUES(500,123,'change_medicallettertemplate','Can change Medical Letter Template');
INSERT INTO "auth_permission" VALUES(501,123,'delete_medicallettertemplate','Can delete Medical Letter Template');
INSERT INTO "auth_permission" VALUES(502,123,'view_medicallettertemplate','Can view Medical Letter Template');
INSERT INTO "auth_permission" VALUES(503,124,'add_visalettertemplate','Can add Visa Letter Template');
INSERT INTO "auth_permission" VALUES(504,124,'change_visalettertemplate','Can change Visa Letter Template');
INSERT INTO "auth_permission" VALUES(505,124,'delete_visalettertemplate','Can delete Visa Letter Template');
INSERT INTO "auth_permission" VALUES(506,124,'view_visalettertemplate','Can view Visa Letter Template');
INSERT INTO "auth_permission" VALUES(507,125,'add_visaletter','Can add Visa Letter');
INSERT INTO "auth_permission" VALUES(508,125,'change_visaletter','Can change Visa Letter');
INSERT INTO "auth_permission" VALUES(509,125,'delete_visaletter','Can delete Visa Letter');
INSERT INTO "auth_permission" VALUES(510,125,'view_visaletter','Can view Visa Letter');
INSERT INTO "auth_permission" VALUES(511,126,'add_medicalletter','Can add Medical Letter');
INSERT INTO "auth_permission" VALUES(512,126,'change_medicalletter','Can change Medical Letter');
INSERT INTO "auth_permission" VALUES(513,126,'delete_medicalletter','Can delete Medical Letter');
INSERT INTO "auth_permission" VALUES(514,126,'view_medicalletter','Can view Medical Letter');
INSERT INTO "auth_permission" VALUES(515,127,'add_offerletterstatuslog','Can add Offer Letter Status Log');
INSERT INTO "auth_permission" VALUES(516,127,'change_offerletterstatuslog','Can change Offer Letter Status Log');
INSERT INTO "auth_permission" VALUES(517,127,'delete_offerletterstatuslog','Can delete Offer Letter Status Log');
INSERT INTO "auth_permission" VALUES(518,127,'view_offerletterstatuslog','Can view Offer Letter Status Log');
INSERT INTO "auth_permission" VALUES(519,128,'add_medicalletterstatuslog','Can add Medical Letter Status Log');
INSERT INTO "auth_permission" VALUES(520,128,'change_medicalletterstatuslog','Can change Medical Letter Status Log');
INSERT INTO "auth_permission" VALUES(521,128,'delete_medicalletterstatuslog','Can delete Medical Letter Status Log');
INSERT INTO "auth_permission" VALUES(522,128,'view_medicalletterstatuslog','Can view Medical Letter Status Log');
INSERT INTO "auth_permission" VALUES(523,129,'add_visaletterstatuslog','Can add Visa Letter Status Log');
INSERT INTO "auth_permission" VALUES(524,129,'change_visaletterstatuslog','Can change Visa Letter Status Log');
INSERT INTO "auth_permission" VALUES(525,129,'delete_visaletterstatuslog','Can delete Visa Letter Status Log');
INSERT INTO "auth_permission" VALUES(526,129,'view_visaletterstatuslog','Can view Visa Letter Status Log');
INSERT INTO "auth_permission" VALUES(527,130,'add_employmentproposal','Can add Employment Proposal');
INSERT INTO "auth_permission" VALUES(528,130,'change_employmentproposal','Can change Employment Proposal');
INSERT INTO "auth_permission" VALUES(529,130,'delete_employmentproposal','Can delete Employment Proposal');
INSERT INTO "auth_permission" VALUES(530,130,'view_employmentproposal','Can view Employment Proposal');
INSERT INTO "auth_permission" VALUES(531,131,'add_proposalstatuslog','Can add proposal status log');
INSERT INTO "auth_permission" VALUES(532,131,'change_proposalstatuslog','Can change proposal status log');
INSERT INTO "auth_permission" VALUES(533,131,'delete_proposalstatuslog','Can delete proposal status log');
INSERT INTO "auth_permission" VALUES(534,131,'view_proposalstatuslog','Can view proposal status log');
INSERT INTO "auth_permission" VALUES(535,132,'add_proposalroleassignment','Can add Proposal Role Assignment');
INSERT INTO "auth_permission" VALUES(536,132,'change_proposalroleassignment','Can change Proposal Role Assignment');
INSERT INTO "auth_permission" VALUES(537,132,'delete_proposalroleassignment','Can delete Proposal Role Assignment');
INSERT INTO "auth_permission" VALUES(538,132,'view_proposalroleassignment','Can view Proposal Role Assignment');
INSERT INTO "auth_permission" VALUES(539,133,'add_proposalapproval','Can add Proposal Approval');
INSERT INTO "auth_permission" VALUES(540,133,'change_proposalapproval','Can change Proposal Approval');
INSERT INTO "auth_permission" VALUES(541,133,'delete_proposalapproval','Can delete Proposal Approval');
INSERT INTO "auth_permission" VALUES(542,133,'view_proposalapproval','Can view Proposal Approval');
INSERT INTO "auth_permission" VALUES(543,134,'add_candidateportalupload','Can add Candidate Portal Upload');
INSERT INTO "auth_permission" VALUES(544,134,'change_candidateportalupload','Can change Candidate Portal Upload');
INSERT INTO "auth_permission" VALUES(545,134,'delete_candidateportalupload','Can delete Candidate Portal Upload');
INSERT INTO "auth_permission" VALUES(546,134,'view_candidateportalupload','Can view Candidate Portal Upload');
INSERT INTO "auth_permission" VALUES(547,135,'add_logentry','Can add log entry');
INSERT INTO "auth_permission" VALUES(548,135,'change_logentry','Can change log entry');
INSERT INTO "auth_permission" VALUES(549,135,'delete_logentry','Can delete log entry');
INSERT INTO "auth_permission" VALUES(550,135,'view_logentry','Can view log entry');
INSERT INTO "auth_permission" VALUES(551,136,'add_attendancegeneralsetting','Can add attendance general setting');
INSERT INTO "auth_permission" VALUES(552,136,'change_attendancegeneralsetting','Can change attendance general setting');
INSERT INTO "auth_permission" VALUES(553,136,'delete_attendancegeneralsetting','Can delete attendance general setting');
INSERT INTO "auth_permission" VALUES(554,136,'view_attendancegeneralsetting','Can view attendance general setting');
INSERT INTO "auth_permission" VALUES(555,137,'add_docusignaccount','Can add DocuSign Account');
INSERT INTO "auth_permission" VALUES(556,137,'change_docusignaccount','Can change DocuSign Account');
INSERT INTO "auth_permission" VALUES(557,137,'delete_docusignaccount','Can delete DocuSign Account');
INSERT INTO "auth_permission" VALUES(558,137,'view_docusignaccount','Can view DocuSign Account');
INSERT INTO "auth_permission" VALUES(559,138,'add_adobesignaccount','Can add Adobe Sign Account');
INSERT INTO "auth_permission" VALUES(560,138,'change_adobesignaccount','Can change Adobe Sign Account');
INSERT INTO "auth_permission" VALUES(561,138,'delete_adobesignaccount','Can delete Adobe Sign Account');
INSERT INTO "auth_permission" VALUES(562,138,'view_adobesignaccount','Can view Adobe Sign Account');
INSERT INTO "auth_permission" VALUES(563,139,'add_onboardingdocument','Can add Onboarding Document');
INSERT INTO "auth_permission" VALUES(564,139,'change_onboardingdocument','Can change Onboarding Document');
INSERT INTO "auth_permission" VALUES(565,139,'delete_onboardingdocument','Can delete Onboarding Document');
INSERT INTO "auth_permission" VALUES(566,139,'view_onboardingdocument','Can view Onboarding Document');
INSERT INTO "auth_permission" VALUES(567,140,'add_bulkrequestline','Can add Bulk Request Line');
INSERT INTO "auth_permission" VALUES(568,140,'change_bulkrequestline','Can change Bulk Request Line');
INSERT INTO "auth_permission" VALUES(569,140,'delete_bulkrequestline','Can delete Bulk Request Line');
INSERT INTO "auth_permission" VALUES(570,140,'view_bulkrequestline','Can view Bulk Request Line');
CREATE TABLE "auth_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "first_name" varchar(150) NOT NULL, "last_name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "is_new_employee" bool NOT NULL);
INSERT INTO "auth_user" VALUES(1,'pbkdf2_sha256$600000$IEcVshYgpkHVe0jQT30DWz$fM15h24zfdTWZeXq7Q2cJ258Ye4/NfTH01PLb4Onu+g=','2026-05-29 12:05:38.047165',1,'hr@fits.com','HR','Manager','hr@fits.com',1,1,'2026-05-29 10:18:08.437981',0);
INSERT INTO "auth_user" VALUES(2,'pbkdf2_sha256$600000$uggtVu3v4q0B3r06HhtlQ6$6ENtdvh7esnDlVZiw+kUqhxGwoCpm6yZlXEpTb72UgQ=',NULL,1,'karthikeya','','','karthikeya@fits.one',1,1,'2026-05-29 10:18:28.581530',0);
CREATE TABLE "auth_user_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "auth_user_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_adobesignaccount" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "api_access_point" varchar(255) NOT NULL, "email_address" varchar(254) NOT NULL, "display_name" varchar(255) NOT NULL, "access_token" text NOT NULL, "refresh_token" text NOT NULL, "token_expires_at" datetime NULL, "scope" text NOT NULL, "is_active" bool NOT NULL, "last_used_at" datetime NULL, "last_error" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_announcement" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(100) NOT NULL, "description" text NULL, "expire_date" date NULL, "disable_comments" bool NOT NULL, "public_comments" bool NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_announcement_attachments" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "announcement_id" bigint NOT NULL REFERENCES "base_announcement" ("id") DEFERRABLE INITIALLY DEFERRED, "attachment_id" bigint NOT NULL REFERENCES "base_attachment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_announcement_company_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "announcement_id" bigint NOT NULL REFERENCES "base_announcement" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_announcement_department" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "announcement_id" bigint NOT NULL REFERENCES "base_announcement" ("id") DEFERRABLE INITIALLY DEFERRED, "department_id" bigint NOT NULL REFERENCES "base_department" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_announcement_employees" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "announcement_id" bigint NOT NULL REFERENCES "base_announcement" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_announcement_filtered_employees" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "announcement_id" bigint NOT NULL REFERENCES "base_announcement" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_announcement_job_position" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "announcement_id" bigint NOT NULL REFERENCES "base_announcement" ("id") DEFERRABLE INITIALLY DEFERRED, "jobposition_id" bigint NOT NULL REFERENCES "base_jobposition" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_announcementcomment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "comment" text NULL, "announcement_id_id" bigint NOT NULL REFERENCES "base_announcement" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_announcementexpire" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "days" integer NULL);
CREATE TABLE "base_announcementview" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "viewed" bool NOT NULL, "created_at" datetime NULL, "announcement_id" bigint NOT NULL REFERENCES "base_announcement" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_attachment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "file" varchar(100) NOT NULL);
CREATE TABLE "base_attendanceallowedip" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "is_enabled" bool NOT NULL, "additional_data" text NULL CHECK ((JSON_VALID("additional_data") OR "additional_data" IS NULL)));
CREATE TABLE "base_baserequestfile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "file" varchar(100) NOT NULL);
CREATE TABLE "base_biometricattendance" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "is_installed" bool NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_company" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "company" varchar(50) NOT NULL, "hq" bool NOT NULL, "address" text NOT NULL, "country" varchar(50) NOT NULL, "state" varchar(50) NOT NULL, "city" varchar(50) NOT NULL, "zip" varchar(20) NOT NULL, "icon" varchar(100) NULL, "date_format" varchar(30) NULL, "time_format" varchar(20) NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_companyleaves" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "based_on_week" varchar(100) NULL, "based_on_week_day" varchar(100) NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_dashboardemployeecharts" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "charts" text NULL CHECK ((JSON_VALID("charts") OR "charts" IS NULL)), "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_department" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "department" varchar(50) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_department_company_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "department_id" bigint NOT NULL REFERENCES "base_department" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_docusignaccount" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "account_id" varchar(100) NOT NULL, "base_uri" varchar(255) NOT NULL, "email_address" varchar(254) NOT NULL, "display_name" varchar(255) NOT NULL, "access_token" text NOT NULL, "refresh_token" text NOT NULL, "token_expires_at" datetime NULL, "scope" text NOT NULL, "is_active" bool NOT NULL, "last_used_at" datetime NULL, "last_error" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_driverviewed" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "viewed" varchar(10) NOT NULL, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_dynamicemailconfiguration" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "host" varchar(256) NULL, "port" smallint NULL, "from_email" varchar(256) NULL, "username" varchar(256) NULL, "display_name" varchar(256) NULL, "password" varchar(256) NULL, "use_tls" bool NOT NULL, "use_ssl" bool NOT NULL, "fail_silently" bool NOT NULL, "is_primary" bool NOT NULL, "use_dynamic_display_name" bool NOT NULL, "timeout" smallint NULL, "company_id_id" bigint NULL UNIQUE REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_dynamicpagination" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "pagination" integer NOT NULL, "user_id_id" integer NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_emaillog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "subject" varchar(255) NOT NULL, "body" text NOT NULL, "from_email" varchar(254) NOT NULL, "to" varchar(254) NOT NULL, "status" varchar(6) NOT NULL, "created_at" datetime NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_employeeshift" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "employee_shift" varchar(50) NOT NULL, "weekly_full_time" varchar(6) NULL, "full_time" varchar(6) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "grace_time_id_id" integer NULL REFERENCES "attendance_gracetime" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_employeeshift_company_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "employeeshift_id" bigint NOT NULL REFERENCES "base_employeeshift" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_employeeshiftday" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "day" varchar(20) NOT NULL);
INSERT INTO "base_employeeshiftday" VALUES(1,'monday');
INSERT INTO "base_employeeshiftday" VALUES(2,'tuesday');
INSERT INTO "base_employeeshiftday" VALUES(3,'wednesday');
INSERT INTO "base_employeeshiftday" VALUES(4,'thursday');
INSERT INTO "base_employeeshiftday" VALUES(5,'friday');
INSERT INTO "base_employeeshiftday" VALUES(6,'saturday');
INSERT INTO "base_employeeshiftday" VALUES(7,'sunday');
CREATE TABLE "base_employeeshiftday_company_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "employeeshiftday_id" bigint NOT NULL REFERENCES "base_employeeshiftday" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_employeeshiftschedule" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "minimum_working_hour" varchar(5) NOT NULL, "start_time" time NULL, "end_time" time NULL, "is_night_shift" bool NOT NULL, "is_auto_punch_out_enabled" bool NOT NULL, "auto_punch_out_time" time NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "day_id" bigint NOT NULL REFERENCES "base_employeeshiftday" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "shift_id_id" bigint NOT NULL REFERENCES "base_employeeshift" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_employeeshiftschedule_company_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "employeeshiftschedule_id" bigint NOT NULL REFERENCES "base_employeeshiftschedule" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_employeetype" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "employee_type" varchar(50) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_employeetype_company_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "employeetype_id" bigint NOT NULL REFERENCES "base_employeetype" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_fitsmailtemplate" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(100) NOT NULL UNIQUE, "body" text NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_historicalrotatingshiftassign" ("id" bigint NOT NULL, "created_at" datetime NULL, "is_active" bool NOT NULL, "history_title" varchar(20) NULL, "history_description" text NULL, "history_highlight" bool NULL, "start_date" date NOT NULL, "next_change_date" date NULL, "based_on" varchar(10) NOT NULL, "rotate_after_day" integer NULL, "rotate_every_weekend" varchar(10) NULL, "rotate_every" varchar(10) NULL, "additional_data" text NULL CHECK ((JSON_VALID("additional_data") OR "additional_data" IS NULL)), "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "history_date" datetime NOT NULL, "history_change_reason" varchar(100) NULL, "history_type" varchar(1) NOT NULL, "created_by_id" integer NULL, "current_shift_id" bigint NULL, "employee_id_id" bigint NULL, "history_relation_id" bigint NOT NULL, "history_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL, "next_shift_id" bigint NULL, "rotating_shift_id_id" bigint NULL);
CREATE TABLE "base_historicalrotatingshiftassign_history_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "historicalrotatingshiftassign_id" integer NOT NULL REFERENCES "base_historicalrotatingshiftassign" ("history_id") DEFERRABLE INITIALLY DEFERRED, "audittag_id" bigint NOT NULL REFERENCES "fits_audit_audittag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_historicalrotatingworktypeassign" ("id" bigint NOT NULL, "created_at" datetime NULL, "is_active" bool NOT NULL, "history_title" varchar(20) NULL, "history_description" text NULL, "history_highlight" bool NULL, "start_date" date NOT NULL, "next_change_date" date NULL, "based_on" varchar(10) NOT NULL, "rotate_after_day" integer NOT NULL, "rotate_every_weekend" varchar(10) NULL, "rotate_every" varchar(10) NOT NULL, "additional_data" text NULL CHECK ((JSON_VALID("additional_data") OR "additional_data" IS NULL)), "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "history_date" datetime NOT NULL, "history_change_reason" varchar(100) NULL, "history_type" varchar(1) NOT NULL, "created_by_id" integer NULL, "current_work_type_id" bigint NULL, "employee_id_id" bigint NULL, "history_relation_id" bigint NOT NULL, "history_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL, "next_work_type_id" bigint NULL, "rotating_work_type_id_id" bigint NULL);
CREATE TABLE "base_historicalrotatingworktypeassign_history_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "historicalrotatingworktypeassign_id" integer NOT NULL REFERENCES "base_historicalrotatingworktypeassign" ("history_id") DEFERRABLE INITIALLY DEFERRED, "audittag_id" bigint NOT NULL REFERENCES "fits_audit_audittag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_historicalshiftrequest" ("id" bigint NOT NULL, "created_at" datetime NULL, "is_active" bool NOT NULL, "history_title" varchar(20) NULL, "history_description" text NULL, "history_highlight" bool NULL, "requested_date" date NULL, "reallocate_approved" bool NOT NULL, "reallocate_canceled" bool NOT NULL, "requested_till" date NULL, "description" text NULL, "is_permanent_shift" bool NOT NULL, "approved" bool NOT NULL, "canceled" bool NOT NULL, "shift_changed" bool NOT NULL, "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "history_date" datetime NOT NULL, "history_change_reason" varchar(100) NULL, "history_type" varchar(1) NOT NULL, "created_by_id" integer NULL, "employee_id_id" bigint NULL, "history_relation_id" bigint NOT NULL, "history_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL, "previous_shift_id_id" bigint NULL, "reallocate_to_id" bigint NULL, "shift_id_id" bigint NULL);
CREATE TABLE "base_historicalshiftrequest_history_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "historicalshiftrequest_id" integer NOT NULL REFERENCES "base_historicalshiftrequest" ("history_id") DEFERRABLE INITIALLY DEFERRED, "audittag_id" bigint NOT NULL REFERENCES "fits_audit_audittag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_historicalworktyperequest" ("id" bigint NOT NULL, "created_at" datetime NULL, "is_active" bool NOT NULL, "history_title" varchar(20) NULL, "history_description" text NULL, "history_highlight" bool NULL, "requested_date" date NULL, "requested_till" date NULL, "description" text NULL, "is_permanent_work_type" bool NOT NULL, "approved" bool NOT NULL, "canceled" bool NOT NULL, "work_type_changed" bool NOT NULL, "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "history_date" datetime NOT NULL, "history_change_reason" varchar(100) NULL, "history_type" varchar(1) NOT NULL, "created_by_id" integer NULL, "employee_id_id" bigint NULL, "history_relation_id" bigint NOT NULL, "history_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL, "previous_work_type_id_id" bigint NULL, "work_type_id_id" bigint NULL);
CREATE TABLE "base_historicalworktyperequest_history_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "historicalworktyperequest_id" integer NOT NULL REFERENCES "base_historicalworktyperequest" ("history_id") DEFERRABLE INITIALLY DEFERRED, "audittag_id" bigint NOT NULL REFERENCES "fits_audit_audittag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_holidays" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "name" varchar(30) NOT NULL, "start_date" date NOT NULL, "end_date" date NULL, "recurring" bool NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_hruser" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "is_hr_staff" bool NOT NULL, "can_view_all_companies" bool NOT NULL, "can_manage_employees" bool NOT NULL, "can_manage_leaves" bool NOT NULL, "can_manage_attendance" bool NOT NULL, "can_manage_payroll" bool NOT NULL, "can_manage_recruitment" bool NOT NULL, "can_manage_assets" bool NOT NULL, "can_manage_biometric" bool NOT NULL, "can_manage_pms" bool NOT NULL, "can_manage_reports" bool NOT NULL, "can_manage_onboarding" bool NOT NULL, "can_manage_offboarding" bool NOT NULL, "can_manage_projects" bool NOT NULL, "can_manage_omani_compliance" bool NOT NULL, "can_manage_expenses" bool NOT NULL, "can_manage_learning" bool NOT NULL, "can_manage_fits_audit" bool NOT NULL, "can_manage_helpdesk" bool NOT NULL, "can_manage_talent" bool NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "employee_id" bigint NOT NULL UNIQUE REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "base_hruser" VALUES(1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,'2026-05-29 10:18:08.444174','2026-05-29 10:18:08.444180',1);
CREATE TABLE "base_jobposition" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "job_position" varchar(50) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "department_id_id" bigint NOT NULL REFERENCES "base_department" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_jobposition_company_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "jobposition_id" bigint NOT NULL REFERENCES "base_jobposition" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_jobrole" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "job_role" varchar(50) NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "job_position_id_id" bigint NOT NULL REFERENCES "base_jobposition" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_jobrole_company_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "jobrole_id" bigint NOT NULL REFERENCES "base_jobrole" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_mailboxintegration" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "provider" varchar(20) NOT NULL, "email_address" varchar(254) NOT NULL, "display_name" varchar(255) NOT NULL, "access_token" text NOT NULL, "refresh_token" text NOT NULL, "token_expires_at" datetime NULL, "scope" text NOT NULL, "is_active" bool NOT NULL, "last_used_at" datetime NULL, "last_error" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_multipleapprovalcondition" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "condition_field" varchar(255) NOT NULL, "condition_operator" varchar(255) NULL, "condition_value" varchar(100) NULL, "condition_start_value" varchar(100) NULL, "condition_end_value" varchar(100) NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "department_id" bigint NOT NULL REFERENCES "base_department" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_multipleapprovalmanagers" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "sequence" integer NOT NULL, "employee_id" integer NULL, "reporting_manager" varchar(100) NULL, "condition_id_id" bigint NOT NULL REFERENCES "base_multipleapprovalcondition" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_notificationsound" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "sound_enabled" bool NOT NULL, "employee_id" bigint NOT NULL UNIQUE REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_penaltyaccounts" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "minus_leaves" real NULL, "deduct_from_carry_forward" bool NOT NULL, "penalty_amount" real NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "late_early_id_id" integer NULL REFERENCES "attendance_attendancelatecomeearlyout" ("id") DEFERRABLE INITIALLY DEFERRED, "leave_request_id_id" integer NULL REFERENCES "leave_leaverequest" ("id") DEFERRABLE INITIALLY DEFERRED, "leave_type_id_id" integer NULL REFERENCES "leave_leavetype" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_rotatingshift" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "name" varchar(50) NOT NULL, "additional_data" text NULL CHECK ((JSON_VALID("additional_data") OR "additional_data" IS NULL)), "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "shift1_id" bigint NULL REFERENCES "base_employeeshift" ("id") DEFERRABLE INITIALLY DEFERRED, "shift2_id" bigint NULL REFERENCES "base_employeeshift" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_rotatingshiftassign" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "start_date" date NOT NULL, "next_change_date" date NULL, "based_on" varchar(10) NOT NULL, "rotate_after_day" integer NULL, "rotate_every_weekend" varchar(10) NULL, "rotate_every" varchar(10) NULL, "additional_data" text NULL CHECK ((JSON_VALID("additional_data") OR "additional_data" IS NULL)), "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "current_shift_id" bigint NULL REFERENCES "base_employeeshift" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "next_shift_id" bigint NULL REFERENCES "base_employeeshift" ("id") DEFERRABLE INITIALLY DEFERRED, "rotating_shift_id_id" bigint NOT NULL REFERENCES "base_rotatingshift" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_rotatingworktype" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "name" varchar(50) NOT NULL, "additional_data" text NULL CHECK ((JSON_VALID("additional_data") OR "additional_data" IS NULL)), "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "work_type1_id" bigint NOT NULL REFERENCES "base_worktype" ("id") DEFERRABLE INITIALLY DEFERRED, "work_type2_id" bigint NOT NULL REFERENCES "base_worktype" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_rotatingworktypeassign" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "start_date" date NOT NULL, "next_change_date" date NULL, "based_on" varchar(10) NOT NULL, "rotate_after_day" integer NOT NULL, "rotate_every_weekend" varchar(10) NULL, "rotate_every" varchar(10) NOT NULL, "additional_data" text NULL CHECK ((JSON_VALID("additional_data") OR "additional_data" IS NULL)), "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "current_work_type_id" bigint NULL REFERENCES "base_worktype" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "next_work_type_id" bigint NULL REFERENCES "base_worktype" ("id") DEFERRABLE INITIALLY DEFERRED, "rotating_work_type_id_id" bigint NOT NULL REFERENCES "base_rotatingworktype" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_shiftrequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "requested_date" date NULL, "reallocate_approved" bool NOT NULL, "reallocate_canceled" bool NOT NULL, "requested_till" date NULL, "description" text NULL, "is_permanent_shift" bool NOT NULL, "approved" bool NOT NULL, "canceled" bool NOT NULL, "shift_changed" bool NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "previous_shift_id_id" bigint NULL REFERENCES "base_employeeshift" ("id") DEFERRABLE INITIALLY DEFERRED, "reallocate_to_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "shift_id_id" bigint NOT NULL REFERENCES "base_employeeshift" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_shiftrequestcomment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "comment" text NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "request_id_id" bigint NOT NULL REFERENCES "base_shiftrequest" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_shiftrequestcomment_files" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "shiftrequestcomment_id" bigint NOT NULL REFERENCES "base_shiftrequestcomment" ("id") DEFERRABLE INITIALLY DEFERRED, "baserequestfile_id" bigint NOT NULL REFERENCES "base_baserequestfile" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(30) NOT NULL, "color" varchar(30) NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_tracklatecomeearlyout" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "is_enable" bool NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_worktype" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "work_type" varchar(50) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_worktype_company_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "worktype_id" bigint NOT NULL REFERENCES "base_worktype" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_worktyperequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "requested_date" date NULL, "requested_till" date NULL, "description" text NULL, "is_permanent_work_type" bool NOT NULL, "approved" bool NOT NULL, "canceled" bool NOT NULL, "work_type_changed" bool NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "previous_work_type_id_id" bigint NULL REFERENCES "base_worktype" ("id") DEFERRABLE INITIALLY DEFERRED, "work_type_id_id" bigint NOT NULL REFERENCES "base_worktype" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_worktyperequestcomment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "comment" text NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "request_id_id" bigint NOT NULL REFERENCES "base_worktyperequest" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "base_worktyperequestcomment_files" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "worktyperequestcomment_id" bigint NOT NULL REFERENCES "base_worktyperequestcomment" ("id") DEFERRABLE INITIALLY DEFERRED, "baserequestfile_id" bigint NOT NULL REFERENCES "base_baserequestfile" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "biometric_biometricdevices" ("created_at" datetime NULL, "is_active" bool NOT NULL, "id" char(32) NOT NULL PRIMARY KEY, "name" varchar(100) NOT NULL, "machine_type" varchar(18) NULL, "machine_ip" varchar(150) NULL, "port" integer NULL, "zk_password" varchar(100) NULL, "bio_username" varchar(100) NULL, "bio_password" varchar(100) NULL, "anviz_request_id" varchar(200) NULL, "api_url" varchar(200) NULL, "api_key" varchar(100) NULL, "api_secret" varchar(100) NULL, "api_token" varchar(500) NULL, "api_expires" varchar(100) NULL, "is_live" bool NOT NULL, "is_scheduler" bool NOT NULL, "scheduler_duration" varchar(10) NULL, "last_fetch_date" date NULL, "last_fetch_time" time NULL, "device_direction" varchar(50) NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "biometric_biometricemployees" ("id" char(32) NOT NULL PRIMARY KEY, "uid" integer NULL, "ref_user_id" integer NULL, "user_id" varchar(100) NOT NULL, "dahua_card_no" varchar(100) NULL, "device_id_id" char(32) NULL REFERENCES "biometric_biometricdevices" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "biometric_cosecattendancearguments" ("id" char(32) NOT NULL PRIMARY KEY, "last_fetch_roll_ovr_count" varchar(100) NULL, "last_fetch_seq_number" varchar(100) NULL, "device_id_id" char(32) NULL REFERENCES "biometric_biometricdevices" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "django_admin_log" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "object_id" text NULL, "object_repr" varchar(200) NOT NULL, "action_flag" smallint unsigned NOT NULL CHECK ("action_flag" >= 0), "change_message" text NOT NULL, "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "action_time" datetime NOT NULL);
CREATE TABLE "django_apscheduler_djangojob" ("id" varchar(255) NOT NULL PRIMARY KEY, "next_run_time" datetime NULL, "job_state" BLOB NOT NULL);
CREATE TABLE "django_apscheduler_djangojobexecution" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "status" varchar(50) NOT NULL, "run_time" datetime NOT NULL, "duration" decimal NULL, "finished" decimal NULL, "exception" varchar(1000) NULL, "traceback" text NULL, "job_id" varchar(255) NOT NULL REFERENCES "django_apscheduler_djangojob" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "unique_job_executions" UNIQUE ("job_id", "run_time"));
CREATE TABLE "django_content_type" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app_label" varchar(100) NOT NULL, "model" varchar(100) NOT NULL);
INSERT INTO "django_content_type" VALUES(1,'admin','logentry');
INSERT INTO "django_content_type" VALUES(2,'auth','permission');
INSERT INTO "django_content_type" VALUES(3,'auth','group');
INSERT INTO "django_content_type" VALUES(4,'auth','user');
INSERT INTO "django_content_type" VALUES(5,'contenttypes','contenttype');
INSERT INTO "django_content_type" VALUES(6,'sessions','session');
INSERT INTO "django_content_type" VALUES(7,'fits_audit','audittag');
INSERT INTO "django_content_type" VALUES(8,'fits_audit','historytrackingfields');
INSERT INTO "django_content_type" VALUES(9,'fits_audit','accountblockunblock');
INSERT INTO "django_content_type" VALUES(10,'accessibility','defaultaccessibility');
INSERT INTO "django_content_type" VALUES(11,'project','project');
INSERT INTO "django_content_type" VALUES(12,'attendance','gracetime');
INSERT INTO "django_content_type" VALUES(13,'attendance','attendancelatecomeearlyout');
INSERT INTO "django_content_type" VALUES(14,'leave','leavetype');
INSERT INTO "django_content_type" VALUES(15,'leave','leaverequest');
INSERT INTO "django_content_type" VALUES(16,'base','announcement');
INSERT INTO "django_content_type" VALUES(17,'base','announcementcomment');
INSERT INTO "django_content_type" VALUES(18,'base','announcementexpire');
INSERT INTO "django_content_type" VALUES(19,'base','announcementview');
INSERT INTO "django_content_type" VALUES(20,'base','attachment');
INSERT INTO "django_content_type" VALUES(21,'base','attendanceallowedip');
INSERT INTO "django_content_type" VALUES(22,'base','baserequestfile');
INSERT INTO "django_content_type" VALUES(23,'base','biometricattendance');
INSERT INTO "django_content_type" VALUES(24,'base','company');
INSERT INTO "django_content_type" VALUES(25,'base','companyleaves');
INSERT INTO "django_content_type" VALUES(26,'base','dashboardemployeecharts');
INSERT INTO "django_content_type" VALUES(27,'base','department');
INSERT INTO "django_content_type" VALUES(28,'base','driverviewed');
INSERT INTO "django_content_type" VALUES(29,'base','dynamicemailconfiguration');
INSERT INTO "django_content_type" VALUES(30,'base','dynamicpagination');
INSERT INTO "django_content_type" VALUES(31,'base','emaillog');
INSERT INTO "django_content_type" VALUES(32,'base','employeeshift');
INSERT INTO "django_content_type" VALUES(33,'base','employeeshiftday');
INSERT INTO "django_content_type" VALUES(34,'base','employeeshiftschedule');
INSERT INTO "django_content_type" VALUES(35,'base','employeetype');
INSERT INTO "django_content_type" VALUES(36,'base','fitsmailtemplate');
INSERT INTO "django_content_type" VALUES(37,'base','historicalrotatingshiftassign');
INSERT INTO "django_content_type" VALUES(38,'base','historicalrotatingworktypeassign');
INSERT INTO "django_content_type" VALUES(39,'base','historicalshiftrequest');
INSERT INTO "django_content_type" VALUES(40,'base','historicalworktyperequest');
INSERT INTO "django_content_type" VALUES(41,'base','holidays');
INSERT INTO "django_content_type" VALUES(42,'base','hruser');
INSERT INTO "django_content_type" VALUES(43,'base','jobposition');
INSERT INTO "django_content_type" VALUES(44,'base','jobrole');
INSERT INTO "django_content_type" VALUES(45,'base','multipleapprovalcondition');
INSERT INTO "django_content_type" VALUES(46,'base','multipleapprovalmanagers');
INSERT INTO "django_content_type" VALUES(47,'base','notificationsound');
INSERT INTO "django_content_type" VALUES(48,'base','penaltyaccounts');
INSERT INTO "django_content_type" VALUES(49,'base','rotatingshift');
INSERT INTO "django_content_type" VALUES(50,'base','rotatingshiftassign');
INSERT INTO "django_content_type" VALUES(51,'base','rotatingworktype');
INSERT INTO "django_content_type" VALUES(52,'base','rotatingworktypeassign');
INSERT INTO "django_content_type" VALUES(53,'base','shiftrequest');
INSERT INTO "django_content_type" VALUES(54,'base','shiftrequestcomment');
INSERT INTO "django_content_type" VALUES(55,'base','tags');
INSERT INTO "django_content_type" VALUES(56,'base','tracklatecomeearlyout');
INSERT INTO "django_content_type" VALUES(57,'base','worktype');
INSERT INTO "django_content_type" VALUES(58,'base','worktyperequest');
INSERT INTO "django_content_type" VALUES(59,'base','worktyperequestcomment');
INSERT INTO "django_content_type" VALUES(60,'base','mailboxintegration');
INSERT INTO "django_content_type" VALUES(61,'employee','actiontype');
INSERT INTO "django_content_type" VALUES(62,'employee','bonuspoint');
INSERT INTO "django_content_type" VALUES(63,'employee','employee');
INSERT INTO "django_content_type" VALUES(64,'employee','employeetag');
INSERT INTO "django_content_type" VALUES(65,'employee','employeeworkinformation');
INSERT INTO "django_content_type" VALUES(66,'employee','profileeditfeature');
INSERT INTO "django_content_type" VALUES(67,'employee','policymultiplefile');
INSERT INTO "django_content_type" VALUES(68,'employee','policy');
INSERT INTO "django_content_type" VALUES(69,'employee','notefiles');
INSERT INTO "django_content_type" VALUES(70,'employee','historicalemployeeworkinformation');
INSERT INTO "django_content_type" VALUES(71,'employee','historicalbonuspoint');
INSERT INTO "django_content_type" VALUES(72,'employee','employeesalaryhistory');
INSERT INTO "django_content_type" VALUES(73,'employee','employeenote');
INSERT INTO "django_content_type" VALUES(74,'employee','employeegeneralsetting');
INSERT INTO "django_content_type" VALUES(75,'employee','employeebankdetails');
INSERT INTO "django_content_type" VALUES(76,'employee','disciplinaryaction');
INSERT INTO "django_content_type" VALUES(77,'recruitment','approvalrule');
INSERT INTO "django_content_type" VALUES(78,'recruitment','approvalstep');
INSERT INTO "django_content_type" VALUES(79,'recruitment','candidate');
INSERT INTO "django_content_type" VALUES(80,'recruitment','evaluationcriteria');
INSERT INTO "django_content_type" VALUES(81,'recruitment','jobemailtemplate');
INSERT INTO "django_content_type" VALUES(82,'recruitment','linkedinaccount');
INSERT INTO "django_content_type" VALUES(83,'recruitment','manpowerrequest');
INSERT INTO "django_content_type" VALUES(84,'recruitment','offerlettertemplate');
INSERT INTO "django_content_type" VALUES(85,'recruitment','recruitment');
INSERT INTO "django_content_type" VALUES(86,'recruitment','skillzone');
INSERT INTO "django_content_type" VALUES(87,'recruitment','stage');
INSERT INTO "django_content_type" VALUES(88,'recruitment','stagefiles');
INSERT INTO "django_content_type" VALUES(89,'recruitment','surveytemplate');
INSERT INTO "django_content_type" VALUES(90,'recruitment','stagenote');
INSERT INTO "django_content_type" VALUES(91,'recruitment','skillzonecandidate');
INSERT INTO "django_content_type" VALUES(92,'recruitment','skill');
INSERT INTO "django_content_type" VALUES(93,'recruitment','resume');
INSERT INTO "django_content_type" VALUES(94,'recruitment','rejectreason');
INSERT INTO "django_content_type" VALUES(95,'recruitment','rejectedcandidate');
INSERT INTO "django_content_type" VALUES(96,'recruitment','recruitmentsurveyanswer');
INSERT INTO "django_content_type" VALUES(97,'recruitment','recruitmentsurvey');
INSERT INTO "django_content_type" VALUES(98,'recruitment','recruitmentgeneralsetting');
INSERT INTO "django_content_type" VALUES(99,'recruitment','recruitmentapprovaldelegation');
INSERT INTO "django_content_type" VALUES(100,'recruitment','recruitmentapproval');
INSERT INTO "django_content_type" VALUES(101,'recruitment','questionordering');
INSERT INTO "django_content_type" VALUES(102,'recruitment','parsedcvdata');
INSERT INTO "django_content_type" VALUES(103,'recruitment','offerletter');
INSERT INTO "django_content_type" VALUES(104,'recruitment','offerapproval');
INSERT INTO "django_content_type" VALUES(105,'recruitment','manpowerrequeststatuslog');
INSERT INTO "django_content_type" VALUES(106,'recruitment','manpowerapproval');
INSERT INTO "django_content_type" VALUES(107,'recruitment','jobapplication');
INSERT INTO "django_content_type" VALUES(108,'recruitment','interviewschedule');
INSERT INTO "django_content_type" VALUES(109,'recruitment','interviewevaluation');
INSERT INTO "django_content_type" VALUES(110,'recruitment','historicalrejectedcandidate');
INSERT INTO "django_content_type" VALUES(111,'recruitment','historicalcandidate');
INSERT INTO "django_content_type" VALUES(112,'recruitment','cvscreeninglog');
INSERT INTO "django_content_type" VALUES(113,'recruitment','cvparsingsettings');
INSERT INTO "django_content_type" VALUES(114,'recruitment','candidatescreeningprofile');
INSERT INTO "django_content_type" VALUES(115,'recruitment','candidatedocumentrequest');
INSERT INTO "django_content_type" VALUES(116,'recruitment','candidatedocument');
INSERT INTO "django_content_type" VALUES(117,'recruitment','evaluationscore');
INSERT INTO "django_content_type" VALUES(118,'recruitment','candidateskillmatch');
INSERT INTO "django_content_type" VALUES(119,'recruitment','candidaterating');
INSERT INTO "django_content_type" VALUES(120,'recruitment','candidaterankingscore');
INSERT INTO "django_content_type" VALUES(121,'recruitment','offerletterapproval');
INSERT INTO "django_content_type" VALUES(122,'recruitment','interviewround');
INSERT INTO "django_content_type" VALUES(123,'recruitment','medicallettertemplate');
INSERT INTO "django_content_type" VALUES(124,'recruitment','visalettertemplate');
INSERT INTO "django_content_type" VALUES(125,'recruitment','visaletter');
INSERT INTO "django_content_type" VALUES(126,'recruitment','medicalletter');
INSERT INTO "django_content_type" VALUES(127,'recruitment','offerletterstatuslog');
INSERT INTO "django_content_type" VALUES(128,'recruitment','medicalletterstatuslog');
INSERT INTO "django_content_type" VALUES(129,'recruitment','visaletterstatuslog');
INSERT INTO "django_content_type" VALUES(130,'recruitment','employmentproposal');
INSERT INTO "django_content_type" VALUES(131,'recruitment','proposalstatuslog');
INSERT INTO "django_content_type" VALUES(132,'recruitment','proposalroleassignment');
INSERT INTO "django_content_type" VALUES(133,'recruitment','proposalapproval');
INSERT INTO "django_content_type" VALUES(134,'recruitment','candidateportalupload');
INSERT INTO "django_content_type" VALUES(135,'auditlog','logentry');
INSERT INTO "django_content_type" VALUES(136,'attendance','attendancegeneralsetting');
INSERT INTO "django_content_type" VALUES(137,'base','docusignaccount');
INSERT INTO "django_content_type" VALUES(138,'base','adobesignaccount');
INSERT INTO "django_content_type" VALUES(139,'recruitment','onboardingdocument');
INSERT INTO "django_content_type" VALUES(140,'recruitment','bulkrequestline');
CREATE TABLE "django_migrations" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app" varchar(255) NOT NULL, "name" varchar(255) NOT NULL, "applied" datetime NOT NULL);
INSERT INTO "django_migrations" VALUES(1,'contenttypes','0001_initial','2026-05-29 10:17:59.663581');
INSERT INTO "django_migrations" VALUES(2,'auth','0001_initial','2026-05-29 10:17:59.668389');
INSERT INTO "django_migrations" VALUES(3,'admin','0001_initial','2026-05-29 10:17:59.670978');
INSERT INTO "django_migrations" VALUES(4,'admin','0002_logentry_remove_auto_add','2026-05-29 10:17:59.673817');
INSERT INTO "django_migrations" VALUES(5,'admin','0003_logentry_add_action_flag_choices','2026-05-29 10:17:59.675700');
INSERT INTO "django_migrations" VALUES(6,'attendance','0001_candidate_perf_indexes','2026-05-29 10:17:59.676653');
INSERT INTO "django_migrations" VALUES(7,'attendance','0002_candidate_perf_indexes','2026-05-29 10:17:59.677028');
INSERT INTO "django_migrations" VALUES(8,'auditlog','0001_initial','2026-05-29 10:17:59.679673');
INSERT INTO "django_migrations" VALUES(9,'auditlog','0002_auto_support_long_primary_keys','2026-05-29 10:17:59.682830');
INSERT INTO "django_migrations" VALUES(10,'auditlog','0003_logentry_remote_addr','2026-05-29 10:17:59.686726');
INSERT INTO "django_migrations" VALUES(11,'auditlog','0004_logentry_detailed_object_repr','2026-05-29 10:17:59.689933');
INSERT INTO "django_migrations" VALUES(12,'auditlog','0005_logentry_additional_data_verbose_name','2026-05-29 10:17:59.692622');
INSERT INTO "django_migrations" VALUES(13,'auditlog','0006_object_pk_index','2026-05-29 10:17:59.695919');
INSERT INTO "django_migrations" VALUES(14,'auditlog','0007_object_pk_type','2026-05-29 10:17:59.697952');
INSERT INTO "django_migrations" VALUES(15,'auditlog','0008_action_index','2026-05-29 10:17:59.701334');
INSERT INTO "django_migrations" VALUES(16,'auditlog','0009_alter_logentry_additional_data','2026-05-29 10:17:59.703287');
INSERT INTO "django_migrations" VALUES(17,'auditlog','0010_alter_logentry_timestamp','2026-05-29 10:17:59.706674');
INSERT INTO "django_migrations" VALUES(18,'auditlog','0011_logentry_serialized_data','2026-05-29 10:17:59.708984');
INSERT INTO "django_migrations" VALUES(19,'auditlog','0012_add_logentry_action_access','2026-05-29 10:17:59.711004');
INSERT INTO "django_migrations" VALUES(20,'auditlog','0013_alter_logentry_timestamp','2026-05-29 10:17:59.714406');
INSERT INTO "django_migrations" VALUES(21,'auditlog','0014_logentry_cid','2026-05-29 10:17:59.716915');
INSERT INTO "django_migrations" VALUES(22,'auditlog','0015_alter_logentry_changes','2026-05-29 10:17:59.723847');
INSERT INTO "django_migrations" VALUES(23,'auditlog','0016_logentry_remote_port','2026-05-29 10:17:59.727235');
INSERT INTO "django_migrations" VALUES(24,'auditlog','0017_add_actor_email','2026-05-29 10:17:59.729514');
INSERT INTO "django_migrations" VALUES(25,'contenttypes','0002_remove_content_type_name','2026-05-29 10:17:59.735630');
INSERT INTO "django_migrations" VALUES(26,'auth','0002_alter_permission_name_max_length','2026-05-29 10:17:59.738626');
INSERT INTO "django_migrations" VALUES(27,'auth','0003_alter_user_email_max_length','2026-05-29 10:17:59.743662');
INSERT INTO "django_migrations" VALUES(28,'auth','0004_alter_user_username_opts','2026-05-29 10:17:59.745630');
INSERT INTO "django_migrations" VALUES(29,'auth','0005_alter_user_last_login_null','2026-05-29 10:17:59.797011');
INSERT INTO "django_migrations" VALUES(30,'auth','0006_require_contenttypes_0002','2026-05-29 10:17:59.797693');
INSERT INTO "django_migrations" VALUES(31,'auth','0007_alter_validators_add_error_messages','2026-05-29 10:17:59.801193');
INSERT INTO "django_migrations" VALUES(32,'auth','0008_alter_user_username_max_length','2026-05-29 10:17:59.804372');
INSERT INTO "django_migrations" VALUES(33,'auth','0009_alter_user_last_name_max_length','2026-05-29 10:17:59.807292');
INSERT INTO "django_migrations" VALUES(34,'auth','0010_alter_group_name_max_length','2026-05-29 10:17:59.810158');
INSERT INTO "django_migrations" VALUES(35,'auth','0011_update_proxy_permissions','2026-05-29 10:17:59.812392');
INSERT INTO "django_migrations" VALUES(36,'auth','0012_alter_user_first_name_max_length','2026-05-29 10:17:59.815262');
INSERT INTO "django_migrations" VALUES(37,'auth','0013_add_is_new_employee','2026-05-29 10:17:59.818189');
INSERT INTO "django_migrations" VALUES(38,'leave','0001_candidate_perf_indexes','2026-05-29 10:17:59.819128');
INSERT INTO "django_migrations" VALUES(39,'fits_audit','0001_candidate_perf_indexes','2026-05-29 10:17:59.824367');
INSERT INTO "django_migrations" VALUES(40,'base','0001_candidate_perf_indexes','2026-05-29 10:17:59.845198');
INSERT INTO "django_migrations" VALUES(41,'employee','0001_candidate_perf_indexes','2026-05-29 10:17:59.988207');
INSERT INTO "django_migrations" VALUES(42,'base','0002_candidate_perf_indexes','2026-05-29 10:18:03.193002');
INSERT INTO "django_migrations" VALUES(43,'base','0003_mailbox_integration','2026-05-29 10:18:03.215236');
INSERT INTO "django_migrations" VALUES(44,'project','0001_candidate_project_fk','2026-05-29 10:18:03.216461');
INSERT INTO "django_migrations" VALUES(45,'recruitment','0001_candidate_perf_indexes','2026-05-29 10:18:05.324161');
INSERT INTO "django_migrations" VALUES(46,'recruitment','0002_add_justification_to_recruitment','2026-05-29 10:18:05.360351');
INSERT INTO "django_migrations" VALUES(47,'recruitment','0005_jobemailtemplate_offerlettertemplate_and_more','2026-05-29 10:18:06.765185');
INSERT INTO "django_migrations" VALUES(48,'recruitment','0006_interview_time_nullable','2026-05-29 10:18:06.807587');
INSERT INTO "django_migrations" VALUES(49,'recruitment','0007_seed_offer_letter_templates','2026-05-29 10:18:06.846347');
INSERT INTO "django_migrations" VALUES(50,'recruitment','0008_offerapproval_offerletter_approval_submitted_at_and_more','2026-05-29 10:18:06.847260');
INSERT INTO "django_migrations" VALUES(51,'recruitment','0009_add_num_rounds_to_interviewschedule','2026-05-29 10:18:06.886590');
INSERT INTO "django_migrations" VALUES(52,'recruitment','0010_add_signature_image_to_offerletterapproval','2026-05-29 10:18:06.912520');
INSERT INTO "django_migrations" VALUES(53,'recruitment','0011_add_medical_visa_letters','2026-05-29 10:18:07.026096');
INSERT INTO "django_migrations" VALUES(54,'recruitment','0012_seed_medical_visa_templates','2026-05-29 10:18:07.064818');
INSERT INTO "django_migrations" VALUES(55,'recruitment','0013_module9_doc_tracking','2026-05-29 10:18:07.475509');
INSERT INTO "django_migrations" VALUES(56,'recruitment','0011_candidate_project_fk','2026-05-29 10:18:07.705486');
INSERT INTO "django_migrations" VALUES(57,'recruitment','0014_merge_20260516_1233','2026-05-29 10:18:07.706210');
INSERT INTO "django_migrations" VALUES(58,'recruitment','0015_add_signature_image_to_offerapproval','2026-05-29 10:18:07.808160');
INSERT INTO "django_migrations" VALUES(59,'recruitment','0016_add_role_type_to_offerletter','2026-05-29 10:18:07.848732');
INSERT INTO "django_migrations" VALUES(60,'recruitment','0017_interviewround_per_round_fields','2026-05-29 10:18:07.954120');
INSERT INTO "django_migrations" VALUES(61,'recruitment','0018_recruitment_budget_fields','2026-05-29 10:18:08.073593');
INSERT INTO "django_migrations" VALUES(62,'recruitment','0019_jobapplication_hr_override_justification','2026-05-29 10:18:08.085948');
INSERT INTO "django_migrations" VALUES(63,'recruitment','0020_manpower_query_fields','2026-05-29 10:18:08.352417');
INSERT INTO "django_migrations" VALUES(64,'recruitment','0021_seed_hr_user','2026-05-29 10:18:08.447679');
INSERT INTO "django_migrations" VALUES(65,'recruitment','0022_recruitment_approval_queried_status','2026-05-29 10:18:08.540830');
INSERT INTO "django_migrations" VALUES(66,'recruitment','0023_seed_oneic_form_templates','2026-05-29 10:18:08.581483');
INSERT INTO "django_migrations" VALUES(67,'recruitment','0024_recruitment_job_id_and_fields','2026-05-29 10:18:08.985051');
INSERT INTO "django_migrations" VALUES(68,'recruitment','0025_employment_proposal','2026-05-29 10:18:09.248134');
INSERT INTO "django_migrations" VALUES(69,'recruitment','0026_candidate_portal','2026-05-29 10:18:09.531717');
INSERT INTO "django_migrations" VALUES(70,'recruitment','0027_jobapplication_skills_rejection','2026-05-29 10:18:09.576903');
INSERT INTO "django_migrations" VALUES(71,'recruitment','0028_alter_candidateportalupload_fields','2026-05-29 10:18:09.605059');
INSERT INTO "django_migrations" VALUES(72,'recruitment','0029_add_personal_fields_to_screening_profile','2026-05-29 10:18:10.123254');
INSERT INTO "django_migrations" VALUES(73,'sessions','0001_initial','2026-05-29 10:18:10.126057');
INSERT INTO "django_migrations" VALUES(74,'attendance','0003_stub_models','2026-05-29 10:25:34.438534');
INSERT INTO "django_migrations" VALUES(75,'base','0004_docusignaccount_adobesignaccount','2026-06-17 04:55:25.271956');
INSERT INTO "django_migrations" VALUES(76,'recruitment','0030_recruitmentapproval_signature_image','2026-06-17 04:55:25.323374');
INSERT INTO "django_migrations" VALUES(77,'recruitment','0031_add_oneic_scoring_fields','2026-06-17 04:55:25.458724');
INSERT INTO "django_migrations" VALUES(78,'recruitment','0032_add_hr_override_to_screening_profile','2026-06-17 04:55:25.524298');
INSERT INTO "django_migrations" VALUES(79,'recruitment','0033_interviewround_interviewers_m2m','2026-06-17 04:55:25.571958');
INSERT INTO "django_migrations" VALUES(80,'recruitment','0034_add_round_number_to_evaluation','2026-06-17 04:55:25.800303');
INSERT INTO "django_migrations" VALUES(81,'recruitment','0035_offerletter_add_location','2026-06-17 04:55:25.843719');
INSERT INTO "django_migrations" VALUES(82,'recruitment','0036_onboardingdocument','2026-06-17 04:55:25.891320');
INSERT INTO "django_migrations" VALUES(83,'recruitment','0037_recruitment_is_bulk_bulkrequestline','2026-06-17 04:55:25.983785');
INSERT INTO "django_migrations" VALUES(84,'recruitment','0038_offerletterapproval_esign_provider_and_more','2026-06-17 04:55:26.257894');
INSERT INTO "django_migrations" VALUES(85,'accessibility','0001_initial','2026-10-03 22:00:36.316257');
INSERT INTO "django_migrations" VALUES(86,'asset','0001_initial','2026-10-03 22:00:37.281221');
INSERT INTO "django_migrations" VALUES(87,'base','0005_add_is_new_employee_to_auth_user','2026-10-03 22:00:37.283317');
INSERT INTO "django_migrations" VALUES(88,'biometric','0001_initial','2026-10-03 22:00:37.471845');
INSERT INTO "django_migrations" VALUES(89,'django_apscheduler','0001_initial','2026-10-03 22:00:37.480737');
INSERT INTO "django_migrations" VALUES(90,'django_apscheduler','0002_auto_20180412_0758','2026-10-03 22:00:37.491179');
INSERT INTO "django_migrations" VALUES(91,'django_apscheduler','0003_auto_20200716_1632','2026-10-03 22:00:37.522411');
INSERT INTO "django_migrations" VALUES(92,'django_apscheduler','0004_auto_20200717_1043','2026-10-03 22:00:37.544129');
INSERT INTO "django_migrations" VALUES(93,'django_apscheduler','0005_migrate_name_to_id','2026-10-03 22:00:37.606005');
INSERT INTO "django_migrations" VALUES(94,'django_apscheduler','0006_remove_djangojob_name','2026-10-03 22:00:37.616085');
INSERT INTO "django_migrations" VALUES(95,'django_apscheduler','0007_auto_20200717_1404','2026-10-03 22:00:37.626631');
INSERT INTO "django_migrations" VALUES(96,'django_apscheduler','0008_remove_djangojobexecution_started','2026-10-03 22:00:37.638489');
INSERT INTO "django_migrations" VALUES(97,'django_apscheduler','0009_djangojobexecution_unique_job_executions','2026-10-03 22:00:37.648570');
INSERT INTO "django_migrations" VALUES(98,'expenses','0001_initial','2026-10-03 22:00:38.447317');
INSERT INTO "django_migrations" VALUES(99,'facedetection','0001_initial','2026-10-03 22:00:38.596376');
INSERT INTO "django_migrations" VALUES(100,'fits_automations','0001_initial','2026-10-03 22:00:38.786976');
INSERT INTO "django_migrations" VALUES(101,'fits_backup','0001_initial','2026-10-03 22:00:38.791418');
INSERT INTO "django_migrations" VALUES(102,'fits_documents','0001_initial','2026-10-03 22:00:38.926030');
INSERT INTO "django_migrations" VALUES(103,'fits_views','0001_initial','2026-10-03 22:00:39.405337');
INSERT INTO "django_migrations" VALUES(104,'geofencing','0001_initial','2026-10-03 22:00:39.494027');
INSERT INTO "django_migrations" VALUES(105,'helpdesk','0001_initial','2026-10-03 22:00:40.363100');
INSERT INTO "django_migrations" VALUES(106,'learning','0001_initial','2026-10-03 22:00:41.055089');
INSERT INTO "django_migrations" VALUES(107,'notifications','0001_initial','2026-10-03 22:00:41.257855');
INSERT INTO "django_migrations" VALUES(108,'offboarding','0001_initial','2026-10-03 22:00:42.850113');
INSERT INTO "django_migrations" VALUES(109,'omani_compliance','0001_initial','2026-10-03 22:00:43.086193');
INSERT INTO "django_migrations" VALUES(110,'onboarding','0001_initial','2026-10-03 22:00:43.983788');
INSERT INTO "django_migrations" VALUES(111,'payroll','0001_initial','2026-10-03 22:00:49.921132');
CREATE TABLE "django_session" ("session_key" varchar(40) NOT NULL PRIMARY KEY, "session_data" text NOT NULL, "expire_date" datetime NOT NULL);
INSERT INTO "django_session" VALUES('2a29vjtrq4ermab8fs34i7sokfqpiwnz','.eJxtkN1KxDAQhV9FcuHNrv1JmjYtLIt67TOUaTLdRtOkNIkoy767KRZU8HLmnPMNZ66khximPnpce61IR0py_L0bQL6h3QT1CvbiMulsWPWQbZZsV3324hSap937BzCBn1KaiUYyySgtG6h5XdMKW84rFLzhbChEU5WtGFvK20JUlMqxaIea0REpUkBZJahHgzKg6qWbF7CfiQrG_CP02voAViLpruTH_GjM3fM-HYlORdJyCmHxXZ5H_QDvEGD1qeGcw6Lzs4UZTyl12FP3W93L6qJVpxWscnPiBPwIO_z7lEa_4dPLbDTmdvsCQZB3aQ:1wSvzb:4c7_zbgZZ3PjCHPIFCj2YFrZjNP8Z84tVjDNQh3537w','2026-06-12 12:07:11.145107');
CREATE TABLE "employee_actiontype" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(50) NOT NULL, "action_type" varchar(30) NOT NULL, "block_option" bool NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_bonuspoint" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "points" integer NOT NULL, "encashment_condition" varchar(100) NULL, "redeeming_points" integer NULL, "reason" text NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NULL UNIQUE REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_disciplinaryaction" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "description" text NOT NULL, "unit_in" varchar(10) NOT NULL, "days" integer NULL, "hours" varchar(6) NULL, "start_date" date NULL, "attachment" varchar(100) NULL, "action_id" bigint NOT NULL REFERENCES "employee_actiontype" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_disciplinaryaction_employee_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "disciplinaryaction_id" bigint NOT NULL REFERENCES "employee_disciplinaryaction" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_employee" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "badge_id" varchar(50) NULL, "employee_first_name" varchar(200) NOT NULL, "employee_last_name" varchar(200) NULL, "employee_profile" varchar(100) NULL, "email" varchar(254) NOT NULL UNIQUE, "phone" varchar(25) NOT NULL, "address" text NULL, "country" varchar(100) NULL, "state" varchar(100) NULL, "city" varchar(30) NULL, "zip" varchar(20) NULL, "dob" date NULL, "gender" varchar(10) NULL, "qualification" varchar(50) NULL, "experience" integer NULL, "marital_status" varchar(50) NULL, "children" integer NULL, "emergency_contact" varchar(15) NULL, "emergency_contact_name" varchar(20) NULL, "emergency_contact_relation" varchar(20) NULL, "is_active" bool NOT NULL, "national_id" varchar(50) NULL, "passport_number" varchar(50) NULL, "work_permit_number" varchar(50) NULL, "last_appraisal_date" date NULL, "last_appraisal_rating" varchar(50) NULL, "nationality" varchar(100) NULL, "additional_info" text NULL CHECK ((JSON_VALID("additional_info") OR "additional_info" IS NULL)), "is_from_onboarding" bool NULL, "is_directly_converted" bool NULL, "employee_user_id_id" integer NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "employee_employee" VALUES(1,NULL,'HR','Manager','','hr@fits.com','+96890000099',NULL,NULL,NULL,NULL,NULL,NULL,'male',NULL,NULL,'single',NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
CREATE TABLE "employee_employeebankdetails" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "bank_name" varchar(50) NOT NULL, "account_number" varchar(50) NULL, "branch" varchar(50) NULL, "address" text NULL, "country" varchar(50) NULL, "state" varchar(50) NOT NULL, "city" varchar(50) NOT NULL, "any_other_code1" varchar(50) NULL, "any_other_code2" varchar(50) NULL, "additional_info" text NULL CHECK ((JSON_VALID("additional_info") OR "additional_info" IS NULL)), "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NULL UNIQUE REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_employeegeneralsetting" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "badge_id_prefix" varchar(5) NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_employeenote" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "description" text NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "updated_by_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_employeenote_note_files" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "employeenote_id" bigint NOT NULL REFERENCES "employee_employeenote" ("id") DEFERRABLE INITIALLY DEFERRED, "notefiles_id" bigint NOT NULL REFERENCES "employee_notefiles" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_employeesalaryhistory" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "effective_date" date NOT NULL, "basic_salary" decimal NOT NULL, "gross_salary" decimal NULL, "increment_reason" varchar(200) NOT NULL, "recorded_at" datetime NOT NULL, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "recorded_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_employeetag" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(50) NULL, "color" varchar(30) NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_employeeworkinformation" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "location" varchar(50) NULL, "email" varchar(254) NULL, "mobile" varchar(254) NULL, "date_joining" date NULL, "contract_end_date" date NULL, "basic_salary" integer NULL, "salary_hour" integer NULL, "additional_info" text NULL CHECK ((JSON_VALID("additional_info") OR "additional_info" IS NULL)), "experience" real NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "department_id_id" bigint NULL REFERENCES "base_department" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NULL UNIQUE REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_type_id_id" bigint NULL REFERENCES "base_employeetype" ("id") DEFERRABLE INITIALLY DEFERRED, "job_position_id_id" bigint NULL REFERENCES "base_jobposition" ("id") DEFERRABLE INITIALLY DEFERRED, "job_role_id_id" bigint NULL REFERENCES "base_jobrole" ("id") DEFERRABLE INITIALLY DEFERRED, "reporting_manager_id_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "shift_id_id" bigint NULL REFERENCES "base_employeeshift" ("id") DEFERRABLE INITIALLY DEFERRED, "work_type_id_id" bigint NULL REFERENCES "base_worktype" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "employee_employeeworkinformation" VALUES(1,NULL,NULL,NULL,NULL,NULL,0,0,NULL,0.0,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL);
CREATE TABLE "employee_employeeworkinformation_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "employeeworkinformation_id" bigint NOT NULL REFERENCES "employee_employeeworkinformation" ("id") DEFERRABLE INITIALLY DEFERRED, "employeetag_id" bigint NOT NULL REFERENCES "employee_employeetag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_historicalbonuspoint" ("id" bigint NOT NULL, "created_at" datetime NULL, "is_active" bool NOT NULL, "history_title" varchar(20) NULL, "history_description" text NULL, "history_highlight" bool NULL, "points" integer NOT NULL, "encashment_condition" varchar(100) NULL, "redeeming_points" integer NULL, "reason" text NULL, "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "history_date" datetime NOT NULL, "history_change_reason" varchar(100) NULL, "history_type" varchar(1) NOT NULL, "created_by_id" integer NULL, "employee_id_id" bigint NULL, "history_relation_id" bigint NOT NULL, "history_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL);
CREATE TABLE "employee_historicalbonuspoint_history_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "historicalbonuspoint_id" integer NOT NULL REFERENCES "employee_historicalbonuspoint" ("history_id") DEFERRABLE INITIALLY DEFERRED, "audittag_id" bigint NOT NULL REFERENCES "fits_audit_audittag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_historicalemployeeworkinformation" ("id" bigint NOT NULL, "history_title" varchar(20) NULL, "history_description" text NULL, "history_highlight" bool NULL, "location" varchar(50) NULL, "email" varchar(254) NULL, "mobile" varchar(254) NULL, "date_joining" date NULL, "contract_end_date" date NULL, "basic_salary" integer NULL, "salary_hour" integer NULL, "additional_info" text NULL CHECK ((JSON_VALID("additional_info") OR "additional_info" IS NULL)), "experience" real NULL, "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "history_date" datetime NOT NULL, "history_change_reason" varchar(100) NULL, "history_type" varchar(1) NOT NULL, "company_id_id" bigint NULL, "department_id_id" bigint NULL, "employee_id_id" bigint NULL, "employee_type_id_id" bigint NULL, "history_relation_id" bigint NOT NULL, "history_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "job_position_id_id" bigint NULL, "job_role_id_id" bigint NULL, "reporting_manager_id_id" bigint NULL, "shift_id_id" bigint NULL, "work_type_id_id" bigint NULL);
CREATE TABLE "employee_historicalemployeeworkinformation_history_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "historicalemployeeworkinformation_id" integer NOT NULL REFERENCES "employee_historicalemployeeworkinformation" ("history_id") DEFERRABLE INITIALLY DEFERRED, "audittag_id" bigint NOT NULL REFERENCES "fits_audit_audittag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_notefiles" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "files" varchar(100) NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_policy" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(50) NOT NULL, "body" text NOT NULL, "is_visible_to_all" bool NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_policy_attachments" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "policy_id" bigint NOT NULL REFERENCES "employee_policy" ("id") DEFERRABLE INITIALLY DEFERRED, "policymultiplefile_id" bigint NOT NULL REFERENCES "employee_policymultiplefile" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_policy_company_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "policy_id" bigint NOT NULL REFERENCES "employee_policy" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_policy_specific_employees" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "policy_id" bigint NOT NULL REFERENCES "employee_policy" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_policymultiplefile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "attachment" varchar(100) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "employee_profileeditfeature" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "is_enabled" bool NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "expenses_expensecategory" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "description" text NOT NULL, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "expenses_expenseclaim" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "description" text NOT NULL, "expense_date" date NOT NULL, "amount" decimal NOT NULL, "currency" varchar(3) NOT NULL, "exchange_rate" decimal NOT NULL, "local_amount" decimal NOT NULL, "status" varchar(20) NOT NULL, "submitted_date" datetime NOT NULL, "approval_date" datetime NULL, "payment_date" date NULL, "rejection_reason" text NOT NULL, "approved_by_finance_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "approved_by_manager_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "category_id" bigint NOT NULL REFERENCES "expenses_expensecategory" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "travel_request_id" bigint NULL REFERENCES "expenses_travelrequest" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "expenses_expensepolicy" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "policy_name" varchar(200) NOT NULL, "description" text NOT NULL, "max_amount" decimal NULL, "requires_receipt" bool NOT NULL, "requires_approval" bool NOT NULL, "approval_levels" integer unsigned NOT NULL CHECK ("approval_levels" >= 0), "is_active" bool NOT NULL, "category_id" bigint NOT NULL REFERENCES "expenses_expensecategory" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "expenses_expensereport" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "report_period_start" date NOT NULL, "report_period_end" date NOT NULL, "total_amount" decimal NOT NULL, "status" varchar(20) NOT NULL, "submitted_date" datetime NULL, "approved_date" datetime NULL, "paid_date" date NULL, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "expenses_expensereportitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "expense_claim_id" bigint NOT NULL REFERENCES "expenses_expenseclaim" ("id") DEFERRABLE INITIALLY DEFERRED, "expense_report_id" bigint NOT NULL REFERENCES "expenses_expensereport" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "expenses_perdiemrate" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "country" varchar(100) NOT NULL, "city" varchar(100) NOT NULL, "rate_amount" decimal NOT NULL, "currency" varchar(3) NOT NULL, "effective_date" date NOT NULL, "expiry_date" date NULL, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "expenses_receipt" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "receipt_file" varchar(100) NOT NULL, "description" varchar(200) NOT NULL, "amount" decimal NOT NULL, "receipt_date" date NOT NULL, "ocr_extracted_data" text NULL CHECK ((JSON_VALID("ocr_extracted_data") OR "ocr_extracted_data" IS NULL)), "uploaded_at" datetime NOT NULL, "expense_claim_id" bigint NOT NULL REFERENCES "expenses_expenseclaim" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "expenses_travelrequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "travel_type" varchar(20) NOT NULL, "purpose" text NOT NULL, "destination" varchar(200) NOT NULL, "departure_date" date NOT NULL, "return_date" date NOT NULL, "estimated_cost" decimal NOT NULL, "status" varchar(20) NOT NULL, "submitted_date" datetime NOT NULL, "approval_date" datetime NULL, "rejection_reason" text NOT NULL, "approved_by_finance_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "approved_by_manager_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "facedetection_employeefacedetection" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "image" varchar(100) NULL, "employee_id_id" bigint NOT NULL UNIQUE REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "facedetection_facedetection" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "start" bool NOT NULL, "company_id_id" bigint NULL UNIQUE REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "fits_audit_accountblockunblock" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "is_enabled" bool NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "fits_audit_audittag" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(20) NOT NULL, "highlight" bool NOT NULL);
CREATE TABLE "fits_audit_historytrackingfields" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "tracking_fields" text NULL CHECK ((JSON_VALID("tracking_fields") OR "tracking_fields" IS NULL)), "work_info_track" bool NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "fits_automations_mailautomation" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(256) NOT NULL UNIQUE, "method_title" varchar(100) NOT NULL, "model" varchar(100) NOT NULL, "mail_to" text NOT NULL, "mail_details" varchar(250) NOT NULL, "mail_detail_choice" text NOT NULL, "trigger" varchar(10) NOT NULL, "delivery_channel" varchar(50) NOT NULL, "condition_html" text NULL, "condition_querystring" text NULL, "condition" text NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "mail_template_id" bigint NULL REFERENCES "base_fitsmailtemplate" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "fits_automations_mailautomation_also_sent_to" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "mailautomation_id" bigint NOT NULL REFERENCES "fits_automations_mailautomation" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "fits_automations_mailautomation_template_attachments" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "mailautomation_id" bigint NOT NULL REFERENCES "fits_automations_mailautomation" ("id") DEFERRABLE INITIALLY DEFERRED, "fitsmailtemplate_id" bigint NOT NULL REFERENCES "base_fitsmailtemplate" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "fits_backup_googledrivebackup" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "oauth_credentials_file" varchar(100) NULL, "gdrive_folder_id" varchar(255) NOT NULL, "access_token" text NULL, "refresh_token" text NULL, "token_expiry" datetime NULL, "backup_media" bool NULL, "backup_db" bool NULL, "interval" bool NULL, "fixed" bool NULL, "seconds" integer NULL, "hour" integer NULL, "minute" integer NULL, "active" bool NOT NULL);
CREATE TABLE "fits_backup_localbackup" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "backup_path" varchar(255) NOT NULL, "backup_media" bool NULL, "backup_db" bool NULL, "interval" bool NULL, "fixed" bool NULL, "seconds" integer NULL, "hour" integer NULL, "minute" integer NULL, "active" bool NOT NULL);
CREATE TABLE "fits_documents_document" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(250) NOT NULL, "document" varchar(100) NULL, "status" varchar(10) NOT NULL, "reject_reason" text NULL, "issue_date" date NULL, "expiry_date" date NULL, "notify_before" integer NULL, "is_digital_asset" bool NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "document_request_id_id" bigint NULL REFERENCES "fits_documents_documentrequest" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "fits_documents_documentrequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(100) NOT NULL, "format" varchar(10) NOT NULL, "max_size" integer NULL, "description" text NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "fits_documents_documentrequest_employee_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "documentrequest_id" bigint NOT NULL REFERENCES "fits_documents_documentrequest" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "fits_views_activegroup" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "path" varchar(256) NOT NULL, "group_target" varchar(256) NOT NULL, "group_by_field" varchar(256) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "fits_views_activetab" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "path" varchar(256) NOT NULL, "tab_target" varchar(256) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "fits_views_activeview" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "path" varchar(256) NOT NULL, "type" varchar(50) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "fits_views_savedfilter" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(20) NULL, "color" varchar(10) NOT NULL, "is_default" bool NOT NULL, "filter" text NOT NULL, "urlencode" text NOT NULL, "path" varchar(256) NOT NULL, "referrer" varchar(256) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "fits_views_togglecolumn" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "path" varchar(256) NOT NULL, "excluded_columns" text NOT NULL CHECK ((JSON_VALID("excluded_columns") OR "excluded_columns" IS NULL)), "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "geofencing_geofencing" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "latitude" real NOT NULL, "longitude" real NOT NULL, "radius_in_meters" integer NOT NULL, "start" bool NOT NULL, "company_id_id" bigint NULL UNIQUE REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "helpdesk_attachment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "file" varchar(100) NOT NULL, "description" varchar(100) NULL, "format" varchar(50) NULL, "comment_id" bigint NULL REFERENCES "helpdesk_comment" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "ticket_id" bigint NULL REFERENCES "helpdesk_ticket" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "helpdesk_claimrequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "is_approved" bool NOT NULL, "is_rejected" bool NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "ticket_id_id" bigint NULL REFERENCES "helpdesk_ticket" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "helpdesk_comment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "comment" text NULL, "date" datetime NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "ticket_id" bigint NOT NULL REFERENCES "helpdesk_ticket" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "helpdesk_departmentmanager" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "department_id" bigint NOT NULL REFERENCES "base_department" ("id") DEFERRABLE INITIALLY DEFERRED, "manager_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "helpdesk_faq" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "question" varchar(255) NOT NULL, "answer" text NOT NULL, "category_id" bigint NOT NULL REFERENCES "helpdesk_faqcategory" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "helpdesk_faq_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "faq_id" bigint NOT NULL REFERENCES "helpdesk_faq" ("id") DEFERRABLE INITIALLY DEFERRED, "tags_id" bigint NOT NULL REFERENCES "base_tags" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "helpdesk_faqcategory" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(30) NOT NULL, "description" text NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "helpdesk_historicalticket" ("id" bigint NOT NULL, "created_at" datetime NULL, "is_active" bool NOT NULL, "history_title" varchar(20) NULL, "history_description" text NULL, "history_highlight" bool NULL, "title" varchar(50) NOT NULL, "description" text NOT NULL, "priority" varchar(100) NOT NULL, "created_date" date NOT NULL, "resolved_date" date NULL, "assigning_type" varchar(100) NOT NULL, "raised_on" varchar(100) NOT NULL, "deadline" date NULL, "status" varchar(50) NOT NULL, "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "history_date" datetime NOT NULL, "history_change_reason" varchar(100) NULL, "history_type" varchar(1) NOT NULL, "created_by_id" integer NULL, "employee_id_id" bigint NULL, "history_relation_id" bigint NOT NULL, "history_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL, "ticket_type_id" bigint NULL);
CREATE TABLE "helpdesk_historicalticket_history_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "historicalticket_id" integer NOT NULL REFERENCES "helpdesk_historicalticket" ("history_id") DEFERRABLE INITIALLY DEFERRED, "audittag_id" bigint NOT NULL REFERENCES "fits_audit_audittag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "helpdesk_ticket" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(50) NOT NULL, "description" text NOT NULL, "priority" varchar(100) NOT NULL, "created_date" date NOT NULL, "resolved_date" date NULL, "assigning_type" varchar(100) NOT NULL, "raised_on" varchar(100) NOT NULL, "deadline" date NULL, "status" varchar(50) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "ticket_type_id" bigint NOT NULL REFERENCES "helpdesk_tickettype" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "helpdesk_ticket_assigned_to" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ticket_id" bigint NOT NULL REFERENCES "helpdesk_ticket" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "helpdesk_ticket_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ticket_id" bigint NOT NULL REFERENCES "helpdesk_ticket" ("id") DEFERRABLE INITIALLY DEFERRED, "tags_id" bigint NOT NULL REFERENCES "base_tags" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "helpdesk_tickettype" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(100) NOT NULL UNIQUE, "type" varchar(50) NOT NULL, "prefix" varchar(3) NOT NULL UNIQUE, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "learning_certification" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(200) NOT NULL, "issuing_authority" varchar(100) NOT NULL, "description" text NOT NULL, "validity_period_months" integer unsigned NULL CHECK ("validity_period_months" >= 0));
CREATE TABLE "learning_coursecategory" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "description" text NOT NULL, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "learning_courseenrollment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "status" varchar(20) NOT NULL, "enrollment_date" date NOT NULL, "start_date" date NULL, "completion_date" date NULL, "progress_percentage" integer unsigned NOT NULL CHECK ("progress_percentage" >= 0), "final_score" decimal NULL, "certificate_issued" bool NOT NULL, "certificate_issue_date" date NULL, "notes" text NOT NULL, "course_id" bigint NOT NULL REFERENCES "learning_trainingcourse" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "learning_employeecertification" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "issue_date" date NOT NULL, "expiry_date" date NULL, "certificate_number" varchar(100) NOT NULL, "is_active" bool NOT NULL, "certification_id" bigint NOT NULL REFERENCES "learning_certification" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "learning_employeeskill" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "proficiency_level" varchar(20) NOT NULL, "years_experience" integer unsigned NOT NULL CHECK ("years_experience" >= 0), "last_used" date NULL, "verification_date" date NULL, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "skill_id" bigint NOT NULL REFERENCES "learning_skill" ("id") DEFERRABLE INITIALLY DEFERRED, "verified_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "learning_learningplan" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "description" text NOT NULL, "start_date" date NOT NULL, "end_date" date NOT NULL, "status" varchar(20) NOT NULL, "created_at" datetime NOT NULL, "created_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "learning_learningplanitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "description" text NOT NULL, "target_date" date NOT NULL, "completed" bool NOT NULL, "completion_date" date NULL, "course_id" bigint NULL REFERENCES "learning_trainingcourse" ("id") DEFERRABLE INITIALLY DEFERRED, "learning_plan_id" bigint NOT NULL REFERENCES "learning_learningplan" ("id") DEFERRABLE INITIALLY DEFERRED, "skill_id" bigint NULL REFERENCES "learning_skill" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "learning_skill" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "description" text NOT NULL, "category" varchar(50) NOT NULL);
CREATE TABLE "learning_trainingbudget" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "year" integer unsigned NOT NULL CHECK ("year" >= 0), "budget_amount" decimal NOT NULL, "allocated_amount" decimal NOT NULL, "remaining_amount" decimal NOT NULL, "department_id" bigint NOT NULL REFERENCES "base_department" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "learning_trainingcourse" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(200) NOT NULL, "description" text NOT NULL, "format" varchar(20) NOT NULL, "level" varchar(20) NOT NULL, "duration_hours" integer unsigned NOT NULL CHECK ("duration_hours" >= 0), "cost" decimal NOT NULL, "instructor" varchar(100) NOT NULL, "is_active" bool NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "category_id" bigint NOT NULL REFERENCES "learning_coursecategory" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "leave_leaverequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT);
CREATE TABLE "leave_leavetype" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL);
CREATE TABLE "notifications_notification" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "level" varchar(20) NOT NULL, "unread" bool NOT NULL, "actor_object_id" varchar(255) NOT NULL, "verb" varchar(255) NOT NULL, "description" text NULL, "target_object_id" varchar(255) NULL, "action_object_object_id" varchar(255) NULL, "timestamp" datetime NOT NULL, "public" bool NOT NULL, "deleted" bool NOT NULL, "emailed" bool NOT NULL, "data" text NULL CHECK ((JSON_VALID("data") OR "data" IS NULL)), "verb_en" varchar(255) NULL, "verb_ar" varchar(255) NULL, "verb_de" varchar(255) NULL, "verb_es" varchar(255) NULL, "verb_fr" varchar(255) NULL, "action_object_content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "actor_content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "recipient_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "target_content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_employeetask" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "status" varchar(20) NOT NULL, "description" text NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NULL REFERENCES "offboarding_offboardingemployee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "task_id_id" bigint NOT NULL REFERENCES "offboarding_offboardingtask" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_exitreason" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(50) NOT NULL, "description" text NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "offboarding_employee_id_id" bigint NOT NULL REFERENCES "offboarding_offboardingemployee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_exitreason_attachments" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "exitreason_id" bigint NOT NULL REFERENCES "offboarding_exitreason" ("id") DEFERRABLE INITIALLY DEFERRED, "offboardingstagemultiplefile_id" bigint NOT NULL REFERENCES "offboarding_offboardingstagemultiplefile" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_historicalemployeetask" ("id" bigint NOT NULL, "created_at" datetime NULL, "is_active" bool NOT NULL, "history_title" varchar(20) NULL, "history_description" text NULL, "history_highlight" bool NULL, "status" varchar(20) NOT NULL, "description" text NULL, "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "history_date" datetime NOT NULL, "history_change_reason" varchar(100) NULL, "history_type" varchar(1) NOT NULL, "created_by_id" integer NULL, "employee_id_id" bigint NULL, "history_relation_id" bigint NOT NULL, "history_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL, "task_id_id" bigint NULL);
CREATE TABLE "offboarding_historicalemployeetask_history_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "historicalemployeetask_id" integer NOT NULL REFERENCES "offboarding_historicalemployeetask" ("history_id") DEFERRABLE INITIALLY DEFERRED, "audittag_id" bigint NOT NULL REFERENCES "fits_audit_audittag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_offboarding" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(20) NOT NULL, "description" text NOT NULL, "status" varchar(10) NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_offboarding_managers" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "offboarding_id" bigint NOT NULL REFERENCES "offboarding_offboarding" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_offboardingemployee" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "notice_period" integer NULL, "unit" varchar(10) NULL, "notice_period_starts" date NULL, "notice_period_ends" date NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL UNIQUE REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "stage_id_id" bigint NULL REFERENCES "offboarding_offboardingstage" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_offboardinggeneralsetting" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "resignation_request" bool NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_offboardingnote" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "description" text NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NULL REFERENCES "offboarding_offboardingemployee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "note_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "stage_id_id" bigint NULL REFERENCES "offboarding_offboardingstage" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_offboardingnote_attachments" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "offboardingnote_id" bigint NOT NULL REFERENCES "offboarding_offboardingnote" ("id") DEFERRABLE INITIALLY DEFERRED, "offboardingstagemultiplefile_id" bigint NOT NULL REFERENCES "offboarding_offboardingstagemultiplefile" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_offboardingstage" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(20) NOT NULL, "type" varchar(13) NOT NULL, "sequence" integer NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "offboarding_id_id" bigint NOT NULL REFERENCES "offboarding_offboarding" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_offboardingstage_managers" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "offboardingstage_id" bigint NOT NULL REFERENCES "offboarding_offboardingstage" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_offboardingstagemultiplefile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "attachment" varchar(100) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_offboardingtask" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(30) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "stage_id_id" bigint NULL REFERENCES "offboarding_offboardingstage" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_offboardingtask_managers" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "offboardingtask_id" bigint NOT NULL REFERENCES "offboarding_offboardingtask" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "offboarding_resignationletter" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(100) NULL, "description" text NULL, "planned_to_leave_on" date NOT NULL, "status" varchar(10) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "offboarding_employee_id_id" bigint NULL REFERENCES "offboarding_offboardingemployee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "omani_compliance_omanicomplianceaudit" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "check_type" varchar(100) NOT NULL, "description" text NOT NULL, "status" varchar(20) NOT NULL, "details" text NOT NULL CHECK ((JSON_VALID("details") OR "details" IS NULL)), "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "omani_compliance_omanilabourlawconfig" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "annual_leave_days" integer NOT NULL, "sick_leave_full_pay_days" integer NOT NULL, "sick_leave_half_pay_days" integer NOT NULL, "sick_leave_unpaid_days" integer NOT NULL, "maternity_leave_days" integer NOT NULL, "hajj_leave_days" integer NOT NULL, "emergency_leave_days" integer NOT NULL, "daily_working_hours" integer NOT NULL, "weekly_working_hours" integer NOT NULL, "overtime_regular_rate" decimal NOT NULL, "overtime_holiday_rate" decimal NOT NULL, "gratuity_days_per_year" integer NOT NULL, "probation_period_months" integer NOT NULL, "pasi_enabled" bool NOT NULL, "pasi_employee_rate" decimal NOT NULL, "pasi_employer_rate" decimal NOT NULL, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "omani_compliance_omanitaxcalculation" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "month" date NOT NULL, "gross_salary" decimal NOT NULL, "taxable_income" decimal NOT NULL, "tax_amount" decimal NOT NULL, "tax_rate" decimal NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "onboarding_candidatestage" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "onboarding_end_date" date NULL, "sequence" integer NULL, "candidate_id_id" bigint NOT NULL UNIQUE REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "onboarding_stage_id_id" bigint NOT NULL REFERENCES "onboarding_onboardingstage" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "onboarding_candidatetask" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "status" varchar(50) NULL, "candidate_id_id" bigint NOT NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "onboarding_task_id_id" bigint NOT NULL REFERENCES "onboarding_onboardingtask" ("id") DEFERRABLE INITIALLY DEFERRED, "stage_id_id" bigint NULL REFERENCES "onboarding_onboardingstage" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "onboarding_historicalcandidatetask" ("id" bigint NOT NULL, "created_at" datetime NULL, "is_active" bool NOT NULL, "history_title" varchar(20) NULL, "history_description" text NULL, "history_highlight" bool NULL, "status" varchar(50) NULL, "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "history_date" datetime NOT NULL, "history_change_reason" varchar(100) NULL, "history_type" varchar(1) NOT NULL, "candidate_id_id" bigint NULL, "created_by_id" integer NULL, "history_relation_id" bigint NOT NULL, "history_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL, "onboarding_task_id_id" bigint NULL, "stage_id_id" bigint NULL);
CREATE TABLE "onboarding_historicalcandidatetask_history_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "historicalcandidatetask_id" integer NOT NULL REFERENCES "onboarding_historicalcandidatetask" ("history_id") DEFERRABLE INITIALLY DEFERRED, "audittag_id" bigint NOT NULL REFERENCES "fits_audit_audittag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "onboarding_onboardingportal" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "token" varchar(200) NOT NULL, "used" bool NOT NULL, "count" integer NOT NULL, "profile" varchar(100) NULL, "candidate_id_id" bigint NOT NULL UNIQUE REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "onboarding_onboardingstage" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "stage_title" varchar(200) NOT NULL, "sequence" integer NULL, "is_final_stage" bool NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "recruitment_id_id" bigint NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "onboarding_onboardingstage_employee_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "onboardingstage_id" bigint NOT NULL REFERENCES "onboarding_onboardingstage" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "onboarding_onboardingtask" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "task_title" varchar(200) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "stage_id_id" bigint NULL REFERENCES "onboarding_onboardingstage" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "onboarding_onboardingtask_candidates" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "onboardingtask_id" bigint NOT NULL REFERENCES "onboarding_onboardingtask" ("id") DEFERRABLE INITIALLY DEFERRED, "candidate_id" bigint NOT NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "onboarding_onboardingtask_employee_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "onboardingtask_id" bigint NOT NULL REFERENCES "onboarding_onboardingtask" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_allowance" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(255) NOT NULL, "one_time_date" date NULL, "include_active_employees" bool NOT NULL, "is_taxable" bool NOT NULL, "is_condition_based" bool NOT NULL, "field" varchar(255) NULL, "condition" varchar(255) NULL, "value" varchar(255) NULL, "is_fixed" bool NOT NULL, "amount" real NULL, "based_on" varchar(255) NULL, "rate" real NULL, "per_attendance_fixed_amount" real NULL, "per_children_fixed_amount" real NULL, "shift_per_attendance_amount" real NULL, "amount_per_one_hr" real NULL, "work_type_per_attendance_amount" real NULL, "has_max_limit" bool NOT NULL, "maximum_amount" real NULL, "maximum_unit" varchar(20) NULL, "if_choice" varchar(10) NOT NULL, "if_condition" varchar(10) NOT NULL, "if_amount" real NOT NULL, "start_range" real NULL, "end_range" real NULL, "only_show_under_employee" bool NOT NULL, "is_loan" bool NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "shift_id_id" bigint NULL REFERENCES "base_employeeshift" ("id") DEFERRABLE INITIALLY DEFERRED, "work_type_id_id" bigint NULL REFERENCES "base_worktype" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_allowance_exclude_employees" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "allowance_id" bigint NOT NULL REFERENCES "payroll_allowance" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_allowance_other_conditions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "allowance_id" bigint NOT NULL REFERENCES "payroll_allowance" ("id") DEFERRABLE INITIALLY DEFERRED, "multiplecondition_id" bigint NOT NULL REFERENCES "payroll_multiplecondition" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_allowance_specific_employees" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "allowance_id" bigint NOT NULL REFERENCES "payroll_allowance" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_contract" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "contract_name" varchar(250) NOT NULL, "contract_start_date" date NOT NULL, "contract_end_date" date NULL, "wage_type" varchar(250) NOT NULL, "pay_frequency" varchar(20) NULL, "wage" real NULL, "contract_status" varchar(250) NOT NULL, "notice_period_in_days" integer NOT NULL, "contract_document" varchar(100) NULL, "deduct_leave_from_basic_pay" bool NOT NULL, "calculate_daily_leave_amount" bool NOT NULL, "deduction_for_one_leave_amount" real NULL, "note" text NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "department_id" bigint NULL REFERENCES "base_department" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "filing_status_id" bigint NULL REFERENCES "payroll_filingstatus" ("id") DEFERRABLE INITIALLY DEFERRED, "job_position_id" bigint NULL REFERENCES "base_jobposition" ("id") DEFERRABLE INITIALLY DEFERRED, "job_role_id" bigint NULL REFERENCES "base_jobrole" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "shift_id" bigint NULL REFERENCES "base_employeeshift" ("id") DEFERRABLE INITIALLY DEFERRED, "work_type_id" bigint NULL REFERENCES "base_worktype" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_deduction" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(255) NOT NULL, "one_time_date" date NULL, "include_active_employees" bool NOT NULL, "is_tax" bool NOT NULL, "is_pretax" bool NOT NULL, "is_condition_based" bool NOT NULL, "field" varchar(255) NULL, "condition" varchar(255) NULL, "value" varchar(255) NULL, "update_compensation" varchar(10) NULL, "is_fixed" bool NOT NULL, "amount" real NULL, "based_on" varchar(255) NULL, "rate" real NULL, "employer_rate" real NOT NULL, "has_max_limit" bool NOT NULL, "maximum_amount" real NULL, "maximum_unit" varchar(20) NULL, "if_choice" varchar(10) NOT NULL, "if_condition" varchar(10) NOT NULL, "if_amount" real NOT NULL, "start_range" real NULL, "end_range" real NULL, "only_show_under_employee" bool NOT NULL, "is_installment" bool NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_deduction_exclude_employees" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "deduction_id" bigint NOT NULL REFERENCES "payroll_deduction" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_deduction_other_conditions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "deduction_id" bigint NOT NULL REFERENCES "payroll_deduction" ("id") DEFERRABLE INITIALLY DEFERRED, "multiplecondition_id" bigint NOT NULL REFERENCES "payroll_multiplecondition" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_deduction_specific_employees" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "deduction_id" bigint NOT NULL REFERENCES "payroll_deduction" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_encashmentgeneralsettings" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "bonus_amount" integer NOT NULL, "leave_amount" integer NULL);
CREATE TABLE "payroll_endofservicebenefit" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "separation_date" date NOT NULL, "separation_reason" varchar(50) NOT NULL, "initial_employment_date" date NOT NULL, "total_years_of_service" decimal NOT NULL, "total_months_of_service" decimal NOT NULL, "unpaid_leave_days" integer NOT NULL, "service_deduction_days" integer NOT NULL, "basic_salary" decimal NOT NULL, "monthly_fixed_allowances" decimal NOT NULL, "monthly_variable_allowances" decimal NOT NULL, "last_year_annual_bonus" decimal NOT NULL, "final_monthly_salary" decimal NOT NULL, "applicable_gratuity_rate" real NOT NULL, "gross_gratuity_amount" decimal NOT NULL, "outstanding_loan_balance" decimal NOT NULL, "outstanding_advance" decimal NOT NULL, "salary_adjustments" decimal NOT NULL, "other_deductions" decimal NOT NULL, "total_deductions" decimal NOT NULL, "net_eosb_amount" decimal NOT NULL, "status" varchar(20) NOT NULL, "calculated_date" datetime NULL, "hr_approval_date" datetime NULL, "director_approval_date" datetime NULL, "payment_method" varchar(50) NOT NULL, "payment_reference" varchar(255) NOT NULL, "paid_date" date NULL, "notes" text NULL, "hr_comments" text NULL, "director_comments" text NULL, "calculated_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "director_approved_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "hr_approved_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_eosbgratuitysettings" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "gratuity_less_than_3_years" real NOT NULL, "gratuity_3_to_5_years" real NOT NULL, "gratuity_5_to_20_years" real NOT NULL, "gratuity_20_plus_years" real NOT NULL, "consider_unpaid_leave" bool NOT NULL, "include_fixed_allowances" bool NOT NULL, "include_variable_allowances" bool NOT NULL, "include_last_bonus" bool NOT NULL, "auto_deduct_loans" bool NOT NULL, "auto_deduct_advances" bool NOT NULL, "requires_hr_approval" bool NOT NULL, "requires_director_approval" bool NOT NULL, "updated_at" datetime NOT NULL, "company_id" bigint NOT NULL UNIQUE REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_filingstatus" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "filing_status" varchar(30) NOT NULL, "based_on" varchar(255) NOT NULL, "use_py" bool NOT NULL, "python_code" text NULL, "description" text NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_glaccount" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "code" varchar(50) NOT NULL UNIQUE, "name" varchar(255) NOT NULL, "account_type" varchar(50) NOT NULL, "company_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_glmapping" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "mapping_type" varchar(50) NOT NULL, "component_id" integer NULL, "company_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "credit_account_id" bigint NOT NULL REFERENCES "payroll_glaccount" ("id") DEFERRABLE INITIALLY DEFERRED, "debit_account_id" bigint NOT NULL REFERENCES "payroll_glaccount" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_historicalcontract" ("id" bigint NOT NULL, "created_at" datetime NULL, "is_active" bool NOT NULL, "history_title" varchar(20) NULL, "history_description" text NULL, "history_highlight" bool NULL, "contract_name" varchar(250) NOT NULL, "contract_start_date" date NOT NULL, "contract_end_date" date NULL, "wage_type" varchar(250) NOT NULL, "pay_frequency" varchar(20) NULL, "wage" real NULL, "contract_status" varchar(250) NOT NULL, "notice_period_in_days" integer NOT NULL, "contract_document" text NULL, "deduct_leave_from_basic_pay" bool NOT NULL, "calculate_daily_leave_amount" bool NOT NULL, "deduction_for_one_leave_amount" real NULL, "note" text NULL, "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "history_date" datetime NOT NULL, "history_change_reason" varchar(100) NULL, "history_type" varchar(1) NOT NULL, "created_by_id" integer NULL, "department_id" bigint NULL, "employee_id_id" bigint NULL, "filing_status_id" bigint NULL, "history_relation_id" bigint NOT NULL, "history_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "job_position_id" bigint NULL, "job_role_id" bigint NULL, "modified_by_id" integer NULL, "shift_id" bigint NULL, "work_type_id" bigint NULL);
CREATE TABLE "payroll_historicalcontract_history_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "historicalcontract_id" integer NOT NULL REFERENCES "payroll_historicalcontract" ("history_id") DEFERRABLE INITIALLY DEFERRED, "audittag_id" bigint NOT NULL REFERENCES "fits_audit_audittag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_historicalpayslip" ("id" bigint NOT NULL, "created_at" datetime NULL, "is_active" bool NOT NULL, "history_title" varchar(20) NULL, "history_description" text NULL, "history_highlight" bool NULL, "group_name" varchar(50) NULL, "reference" varchar(255) NULL, "start_date" date NOT NULL, "end_date" date NOT NULL, "pay_head_data" text NOT NULL CHECK ((JSON_VALID("pay_head_data") OR "pay_head_data" IS NULL)), "contract_wage" real NULL, "basic_pay" real NULL, "gross_pay" real NULL, "deduction" real NULL, "net_pay" real NULL, "status" varchar(20) NULL, "sent_to_employee" bool NULL, "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "history_date" datetime NOT NULL, "history_change_reason" varchar(100) NULL, "history_type" varchar(1) NOT NULL, "created_by_id" integer NULL, "employee_id_id" bigint NULL, "history_relation_id" bigint NOT NULL, "history_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL);
CREATE TABLE "payroll_historicalpayslip_history_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "historicalpayslip_id" integer NOT NULL REFERENCES "payroll_historicalpayslip" ("history_id") DEFERRABLE INITIALLY DEFERRED, "audittag_id" bigint NOT NULL REFERENCES "fits_audit_audittag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_icbsconfig" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "bank_name" varchar(255) NOT NULL, "api_endpoint" varchar(200) NOT NULL, "client_id" varchar(255) NOT NULL, "client_secret" varchar(255) NOT NULL, "is_active" bool NOT NULL, "company_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_leaveencashment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "leave_count" decimal NOT NULL, "encashment_date" date NOT NULL, "daily_wage" decimal NOT NULL, "total_encashment_amount" decimal NULL, "tax_deducted" decimal NOT NULL, "other_deductions" decimal NOT NULL, "net_encashment_amount" decimal NULL, "status" varchar(20) NOT NULL, "approved_date" datetime NULL, "payment_date" date NULL, "payment_method" varchar(50) NOT NULL, "remarks" text NULL, "approved_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "calculated_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "leave_type_id" bigint NULL REFERENCES "leave_leavetype" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_loanaccount" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "type" varchar(15) NOT NULL, "title" varchar(20) NOT NULL, "loan_amount" real NOT NULL, "provided_date" date NOT NULL, "description" text NULL, "is_fixed" bool NOT NULL, "rate" real NOT NULL, "installment_amount" real NULL, "installments" integer NOT NULL, "installment_start_date" date NOT NULL, "apply_on" varchar(20) NOT NULL, "settled" bool NOT NULL, "settled_date" datetime NULL, "allowance_id_id" bigint NULL REFERENCES "payroll_allowance" ("id") DEFERRABLE INITIALLY DEFERRED, "asset_id_id" bigint NULL REFERENCES "asset_asset" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_loanaccount_deduction_ids" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "loanaccount_id" bigint NOT NULL REFERENCES "payroll_loanaccount" ("id") DEFERRABLE INITIALLY DEFERRED, "deduction_id" bigint NOT NULL REFERENCES "payroll_deduction" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_multiplecondition" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "field" varchar(255) NOT NULL, "condition" varchar(255) NULL, "value" varchar(255) NULL);
CREATE TABLE "payroll_overrideattendance" ("attendance_ptr_id" bigint NOT NULL PRIMARY KEY REFERENCES "attendance_attendance" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_overrideleaverequest" ("leaverequest_ptr_id" bigint NOT NULL PRIMARY KEY REFERENCES "leave_leaverequest" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_payrollgeneralsetting" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "notice_period" integer NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_payrollsettings" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "currency_symbol" varchar(5) NULL, "position" varchar(15) NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_payslip" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "group_name" varchar(50) NULL, "reference" varchar(255) NULL, "start_date" date NOT NULL, "end_date" date NOT NULL, "pay_head_data" text NOT NULL CHECK ((JSON_VALID("pay_head_data") OR "pay_head_data" IS NULL)), "contract_wage" real NULL, "basic_pay" real NULL, "gross_pay" real NULL, "deduction" real NULL, "net_pay" real NULL, "status" varchar(20) NULL, "sent_to_employee" bool NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_payslip_installment_ids" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "payslip_id" bigint NOT NULL REFERENCES "payroll_payslip" ("id") DEFERRABLE INITIALLY DEFERRED, "deduction_id" bigint NOT NULL REFERENCES "payroll_deduction" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_payslipautogenerate" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "generate_day" varchar(30) NOT NULL, "auto_generate" bool NOT NULL, "company_id_id" bigint NULL UNIQUE REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_reimbursement" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(50) NOT NULL, "type" varchar(16) NOT NULL, "allowance_on" date NOT NULL, "attachment" varchar(100) NULL, "ad_to_encash" real NOT NULL, "cfd_to_encash" real NOT NULL, "bonus_to_encash" integer NOT NULL, "amount" real NOT NULL, "status" varchar(10) NOT NULL, "description" text NULL, "allowance_id_id" bigint NULL REFERENCES "payroll_allowance" ("id") DEFERRABLE INITIALLY DEFERRED, "approved_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "leave_type_id_id" bigint NULL REFERENCES "leave_leavetype" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_reimbursement_other_attachments" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "reimbursement_id" bigint NOT NULL REFERENCES "payroll_reimbursement" ("id") DEFERRABLE INITIALLY DEFERRED, "reimbursementmultipleattachment_id" bigint NOT NULL REFERENCES "payroll_reimbursementmultipleattachment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_reimbursementfile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "file" varchar(100) NOT NULL);
CREATE TABLE "payroll_reimbursementmultipleattachment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "attachment" varchar(100) NOT NULL);
CREATE TABLE "payroll_reimbursementrequestcomment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "is_active" bool NOT NULL, "comment" text NULL, "created_at" datetime NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "request_id_id" bigint NOT NULL REFERENCES "payroll_reimbursement" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_reimbursementrequestcomment_files" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "reimbursementrequestcomment_id" bigint NOT NULL REFERENCES "payroll_reimbursementrequestcomment" ("id") DEFERRABLE INITIALLY DEFERRED, "reimbursementfile_id" bigint NOT NULL REFERENCES "payroll_reimbursementfile" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_salaryrevision" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "revision_reason" varchar(100) NOT NULL, "current_basic_salary" decimal NOT NULL, "new_basic_salary" decimal NOT NULL, "increment_percentage" decimal NULL, "current_gross_salary" decimal NULL, "new_gross_salary" decimal NULL, "effective_from" date NOT NULL, "status" varchar(20) NOT NULL, "submitted_date" datetime NULL, "approved_date" datetime NULL, "rejection_reason" text NULL, "justification" text NOT NULL, "new_contract" varchar(100) NULL, "approved_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "submitted_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_serviceaward" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "award_type" varchar(20) NOT NULL, "award_date" date NOT NULL, "award_amount" decimal NOT NULL, "description" text NULL, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_taxbracket" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "min_income" real NOT NULL, "max_income" real NULL, "tax_rate" real NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "filing_status_id_id" bigint NOT NULL REFERENCES "payroll_filingstatus" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_workrecord" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "record_name" varchar(250) NULL, "work_record_type" varchar(5) NULL, "date" date NULL, "at_work" varchar(5) NULL, "min_hour" varchar(5) NULL, "at_work_second" integer NULL, "min_hour_second" integer NULL, "note" text NOT NULL, "message" varchar(30) NULL, "is_attendance_record" bool NOT NULL, "is_leave_record" bool NOT NULL, "day_percentage" real NOT NULL, "last_update" datetime NULL, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_wpsauditlog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "action" varchar(30) NOT NULL, "timestamp" datetime NOT NULL, "details" text NULL, "user_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "wps_file_id" bigint NOT NULL REFERENCES "payroll_wpsperiodicfile" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_wpsglobalsettings" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "company_bank_name" varchar(100) NOT NULL, "company_bank_code" varchar(10) NOT NULL, "company_bank_account_number" varchar(20) NOT NULL, "company_bank_account_iban" varchar(34) NOT NULL, "company_cr_number" varchar(20) NOT NULL, "company_wps_code" varchar(20) NOT NULL, "enable_wps_processing" bool NOT NULL, "wps_submission_frequency" varchar(20) NOT NULL, "wps_format_version" varchar(10) NOT NULL, "auto_generate_wps_file" bool NOT NULL, "include_end_of_service" bool NOT NULL, "include_loans" bool NOT NULL, "requires_director_approval" bool NOT NULL, "digital_signature_required" bool NOT NULL, "updated_at" datetime NOT NULL, "company_id" bigint NOT NULL UNIQUE REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_wpspaymentexception" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "exception_type" varchar(30) NOT NULL, "error_description" text NOT NULL, "is_resolved" bool NOT NULL, "resolution_notes" text NULL, "created_date" datetime NOT NULL, "resolved_date" datetime NULL, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "wps_file_id" bigint NOT NULL REFERENCES "payroll_wpsperiodicfile" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "payroll_wpsperiodicfile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "payroll_period" varchar(20) NOT NULL, "payment_date" date NOT NULL, "file_reference_number" varchar(50) NOT NULL UNIQUE, "file_generation_date" datetime NOT NULL, "file_version" varchar(10) NOT NULL, "total_records" integer NOT NULL, "total_amount" decimal NOT NULL, "currency" varchar(3) NOT NULL, "employee_records" text NOT NULL CHECK ((JSON_VALID("employee_records") OR "employee_records" IS NULL)), "file_path" varchar(255) NOT NULL, "file_size_bytes" integer NOT NULL, "file_format" varchar(20) NOT NULL, "status" varchar(20) NOT NULL, "approval_date" datetime NULL, "approval_comments" text NULL, "submitted_date" datetime NULL, "bank_response_code" varchar(20) NOT NULL, "bank_response_message" text NULL, "bank_reference_number" varchar(50) NOT NULL, "processing_status" varchar(100) NOT NULL, "processing_date" datetime NULL, "rejection_reason" text NULL, "is_resubmitted" bool NOT NULL, "resubmission_date" datetime NULL, "notes" text NULL, "approved_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "company_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "generated_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "project_project" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL);
CREATE TABLE "recruitment_approvalrule" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "name" varchar(200) NOT NULL, "grade_min" varchar(50) NOT NULL, "grade_max" varchar(50) NOT NULL, "priority" integer unsigned NOT NULL CHECK ("priority" >= 0), "is_active" bool NOT NULL, "company_id_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "department_id" bigint NULL REFERENCES "base_department" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_approvalstep" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "sequence" integer unsigned NOT NULL CHECK ("sequence" >= 0), "approver_type" varchar(30) NOT NULL, "sla_hours" integer unsigned NOT NULL CHECK ("sla_hours" >= 0), "is_optional" bool NOT NULL, "approver_user_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "rule_id" bigint NOT NULL REFERENCES "recruitment_approvalrule" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_bulkrequestline" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(120) NOT NULL, "vacancy" integer unsigned NOT NULL CHECK ("vacancy" >= 0), "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "job_position_id" bigint NULL, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "published_recruitment_id" bigint NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED, "recruitment_id" bigint NOT NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_candidate" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "name" varchar(100) NULL, "profile" varchar(100) NULL, "portfolio" varchar(200) NOT NULL, "schedule_date" datetime NULL, "email" varchar(254) NOT NULL, "mobile" varchar(15) NOT NULL, "resume" varchar(100) NOT NULL, "address" text NULL, "country" varchar(30) NULL, "dob" date NULL, "state" varchar(30) NULL, "city" varchar(30) NULL, "zip" varchar(30) NULL, "gender" varchar(15) NULL, "source" varchar(20) NULL, "start_onboard" bool NOT NULL, "hired" bool NOT NULL, "canceled" bool NOT NULL, "converted" bool NOT NULL, "joining_date" date NULL, "sequence" integer NULL, "experience_years" decimal NOT NULL, "notice_period_days" integer unsigned NULL CHECK ("notice_period_days" >= 0), "availability_date" date NULL, "probation_end" date NULL, "offer_letter_status" varchar(10) NOT NULL, "last_updated" date NULL, "hired_date" date NULL, "converted_employee_id_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "job_position_id_id" bigint NULL REFERENCES "base_jobposition" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "recruitment_id_id" bigint NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED, "referral_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "stage_id_id" bigint NULL REFERENCES "recruitment_stage" ("id") DEFERRABLE INITIALLY DEFERRED, "cover_letter" varchar(100) NULL, "graduation_certificate" varchar(100) NULL, "promoted_to_onboarding" bool NOT NULL, "transcripts" varchar(100) NULL, "project_id_id" integer NULL REFERENCES "project_project" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_candidatedocument" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(250) NOT NULL, "document" varchar(100) NULL, "status" varchar(10) NOT NULL, "reject_reason" text NULL, "candidate_id_id" bigint NOT NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "document_request_id_id" bigint NULL REFERENCES "recruitment_candidatedocumentrequest" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_candidatedocumentrequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(100) NOT NULL, "format" varchar(10) NOT NULL, "max_size" integer NULL, "description" text NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_candidatedocumentrequest_candidate_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "candidatedocumentrequest_id" bigint NOT NULL REFERENCES "recruitment_candidatedocumentrequest" ("id") DEFERRABLE INITIALLY DEFERRED, "candidate_id" bigint NOT NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_candidateportalupload" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "offer_id" bigint NOT NULL REFERENCES "recruitment_offerletter" ("id") DEFERRABLE INITIALLY DEFERRED, "document_type" varchar(20) NOT NULL, "label" varchar(100) NOT NULL, "file" varchar(100) NOT NULL, "notes" text NOT NULL, "uploaded_at" datetime NOT NULL);
CREATE TABLE "recruitment_candidaterankingscore" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "skill_match_score" real NOT NULL, "experience_match_score" real NOT NULL, "education_match_score" real NOT NULL, "location_match_score" real NOT NULL, "overall_ranking_score" real NOT NULL, "ranking_category" varchar(30) NOT NULL, "recommendation_text" text NOT NULL, "action_taken" varchar(50) NOT NULL, "scoring_engine_version" varchar(20) NOT NULL, "scoring_date" datetime NOT NULL, "candidate_id" bigint NOT NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "recruitment_id" bigint NOT NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_candidaterating" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "rating" integer NOT NULL, "candidate_id_id" bigint NOT NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_candidatescreeningprofile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "extracted_skills" text NOT NULL CHECK ((JSON_VALID("extracted_skills") OR "extracted_skills" IS NULL)), "years_experience" integer NOT NULL, "education" text NOT NULL CHECK ((JSON_VALID("education") OR "education" IS NULL)), "previous_positions" text NOT NULL CHECK ((JSON_VALID("previous_positions") OR "previous_positions" IS NULL)), "matching_score" integer NOT NULL, "matching_skills" text NOT NULL CHECK ((JSON_VALID("matching_skills") OR "matching_skills" IS NULL)), "missing_skills" text NOT NULL CHECK ((JSON_VALID("missing_skills") OR "missing_skills" IS NULL)), "summary" text NULL, "status" varchar(20) NOT NULL, "recommendation" varchar(100) NULL, "screened_at" datetime NOT NULL, "ai_model" varchar(100) NULL, "candidate_id" bigint NOT NULL UNIQUE REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "screened_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "extracted_dob" date NULL, "extracted_driving_license" varchar(20) NOT NULL, "extracted_experience_local_years" decimal NULL, "extracted_experience_overseas_years" decimal NULL, "extracted_lang_arabic" bool NOT NULL, "extracted_lang_english" bool NOT NULL, "extracted_lang_others" varchar(200) NOT NULL, "extracted_marital_status" varchar(20) NOT NULL, "extracted_nationality" varchar(100) NOT NULL, "extracted_place_of_birth" varchar(120) NOT NULL, "extracted_present_employer" varchar(200) NOT NULL, "extracted_qualification_academic" varchar(200) NOT NULL, "extracted_qualification_professional" varchar(200) NOT NULL, "ai_reasoning" text NOT NULL, "oneic_grand_total" real NOT NULL, "oneic_percentage" real NOT NULL, "scoring_breakdown" text NOT NULL CHECK ((JSON_VALID("scoring_breakdown") OR "scoring_breakdown" IS NULL)), "hr_override" bool NOT NULL, "hr_override_justification" text NULL);
CREATE TABLE "recruitment_candidateskillmatch" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "required_skills" text NOT NULL CHECK ((JSON_VALID("required_skills") OR "required_skills" IS NULL)), "candidate_skills" text NOT NULL CHECK ((JSON_VALID("candidate_skills") OR "candidate_skills" IS NULL)), "matched_skills" text NOT NULL CHECK ((JSON_VALID("matched_skills") OR "matched_skills" IS NULL)), "missing_skills" text NOT NULL CHECK ((JSON_VALID("missing_skills") OR "missing_skills" IS NULL)), "extra_skills" text NOT NULL CHECK ((JSON_VALID("extra_skills") OR "extra_skills" IS NULL)), "skill_match_percentage" real NOT NULL, "skill_relevance_score" real NOT NULL, "candidate_id" bigint NOT NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "recruitment_id" bigint NOT NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_cvparsingsettings" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "enable_ai_screening" bool NOT NULL, "auto_parse_cv" bool NOT NULL, "auto_rank_candidates" bool NOT NULL, "pdf_parser_engine" varchar(20) NOT NULL, "ocr_enabled" bool NOT NULL, "skill_match_weight" real NOT NULL, "experience_weight" real NOT NULL, "education_weight" real NOT NULL, "location_weight" real NOT NULL, "min_skill_match_percentage" integer NOT NULL, "min_overall_score" integer NOT NULL, "auto_shortlist_above_score" integer NOT NULL, "auto_reject_below_score" integer NOT NULL, "updated_at" datetime NOT NULL, "company_id" bigint NOT NULL UNIQUE REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_cvscreeninglog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "action" varchar(30) NOT NULL, "timestamp" datetime NOT NULL, "details" text NOT NULL CHECK ((JSON_VALID("details") OR "details" IS NULL)), "error_message" text NULL, "candidate_id" bigint NOT NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "recruitment_id" bigint NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_employmentproposal" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "proposal_no" varchar(20) NOT NULL UNIQUE, "template_type" varchar(20) NOT NULL, "status" varchar(20) NOT NULL, "post_applied_for" varchar(200) NOT NULL, "grade_group" varchar(50) NOT NULL, "division_department" varchar(200) NOT NULL, "post_location" varchar(200) NOT NULL, "contractual" bool NOT NULL, "contract_name" varchar(200) NOT NULL, "contract_period_from" date NULL, "contract_period_to" date NULL, "job_no" varchar(50) NOT NULL, "reporting_to" varchar(200) NOT NULL, "reporting_staff_no" varchar(50) NOT NULL, "gsm_cpn_no" varchar(50) NOT NULL, "is_new_appointment" bool NOT NULL, "replacement_staff_no" varchar(50) NOT NULL, "candidate_referred" varchar(20) NOT NULL, "referral_staff_number" varchar(50) NOT NULL, "consultancy_reg" varchar(20) NOT NULL, "consultancy_other" varchar(120) NOT NULL, "employment_contract_type" varchar(20) NOT NULL, "employment_contract_months" integer unsigned NULL CHECK ("employment_contract_months" >= 0), "has_relative_in_company" bool NOT NULL, "relative_name" varchar(120) NOT NULL, "relative_staff_no" varchar(50) NOT NULL, "relative_location" varchar(120) NOT NULL, "application_date" date NULL, "interview_date" date NULL, "applicant_name" varchar(200) NOT NULL, "nationality" varchar(80) NOT NULL, "present_employer" varchar(200) NOT NULL, "local_transfer" bool NOT NULL, "marital_status" varchar(20) NOT NULL, "dob" date NULL, "place_of_birth" varchar(120) NOT NULL, "qualification_academic" varchar(200) NOT NULL, "qualification_professional" varchar(200) NOT NULL, "experience_local_years" decimal NULL, "experience_overseas_years" decimal NULL, "lang_arabic" bool NOT NULL, "lang_english" bool NOT NULL, "lang_others" varchar(200) NOT NULL, "driving_license" varchar(20) NOT NULL, "salary_budgeted" varchar(20) NOT NULL, "basic_salary" decimal NULL, "hra_allowance" decimal NULL, "transport_allowance" decimal NULL, "addl_resp_allowance" decimal NULL, "overtime_allowance" decimal NULL, "food_allowance" decimal NULL, "lsa_allowance" decimal NULL, "lsa_tier" varchar(20) NOT NULL, "gross_salary" decimal NULL, "salary_columns_json" text NOT NULL CHECK ((JSON_VALID("salary_columns_json") OR "salary_columns_json" IS NULL)), "air_passage_from" varchar(120) NOT NULL, "air_passage_to" varchar(120) NOT NULL, "air_passage_months" integer unsigned NULL CHECK ("air_passage_months" >= 0), "family_status" varchar(20) NOT NULL, "medical_clause" bool NOT NULL, "salary_increase_clause" text NOT NULL, "hod_comments" text NOT NULL, "remarks" text NOT NULL, "candidate_id" bigint NOT NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "interview_id" bigint NULL REFERENCES "recruitment_interviewschedule" ("id") DEFERRABLE INITIALLY DEFERRED, "manpower_request_id" bigint NULL REFERENCES "recruitment_manpowerrequest" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "recruitment_id" bigint NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_evaluationcriteria" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "description" text NOT NULL, "max_score" integer unsigned NOT NULL CHECK ("max_score" >= 0), "is_active" bool NOT NULL);
CREATE TABLE "recruitment_evaluationscore" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "score" integer unsigned NOT NULL CHECK ("score" >= 0), "comment" text NOT NULL, "criteria_id" bigint NOT NULL REFERENCES "recruitment_evaluationcriteria" ("id") DEFERRABLE INITIALLY DEFERRED, "evaluation_id" bigint NOT NULL REFERENCES "recruitment_interviewevaluation" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_historicalcandidate" ("id" bigint NOT NULL, "created_at" datetime NULL, "is_active" bool NOT NULL, "history_title" varchar(20) NULL, "history_description" text NULL, "history_highlight" bool NULL, "name" varchar(100) NULL, "profile" text NULL, "portfolio" varchar(200) NOT NULL, "schedule_date" datetime NULL, "email" varchar(254) NOT NULL, "mobile" varchar(15) NOT NULL, "resume" text NOT NULL, "address" text NULL, "country" varchar(30) NULL, "dob" date NULL, "state" varchar(30) NULL, "city" varchar(30) NULL, "zip" varchar(30) NULL, "gender" varchar(15) NULL, "source" varchar(20) NULL, "start_onboard" bool NOT NULL, "hired" bool NOT NULL, "canceled" bool NOT NULL, "converted" bool NOT NULL, "joining_date" date NULL, "sequence" integer NULL, "experience_years" decimal NOT NULL, "notice_period_days" integer unsigned NULL CHECK ("notice_period_days" >= 0), "availability_date" date NULL, "probation_end" date NULL, "offer_letter_status" varchar(10) NOT NULL, "last_updated" date NULL, "hired_date" date NULL, "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "history_date" datetime NOT NULL, "history_change_reason" varchar(100) NULL, "history_type" varchar(1) NOT NULL, "converted_employee_id_id" bigint NULL, "created_by_id" integer NULL, "history_relation_id" bigint NOT NULL, "history_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "job_position_id_id" bigint NULL, "modified_by_id" integer NULL, "recruitment_id_id" bigint NULL, "referral_id" bigint NULL, "stage_id_id" bigint NULL, "cover_letter" text NULL, "graduation_certificate" text NULL, "promoted_to_onboarding" bool NOT NULL, "transcripts" text NULL, "project_id_id" integer NULL);
CREATE TABLE "recruitment_historicalcandidate_history_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "historicalcandidate_id" integer NOT NULL REFERENCES "recruitment_historicalcandidate" ("history_id") DEFERRABLE INITIALLY DEFERRED, "audittag_id" bigint NOT NULL REFERENCES "fits_audit_audittag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_historicalrejectedcandidate" ("id" bigint NOT NULL, "created_at" datetime NULL, "is_active" bool NOT NULL, "history_title" varchar(20) NULL, "history_description" text NULL, "history_highlight" bool NULL, "description" text NOT NULL, "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "history_date" datetime NOT NULL, "history_change_reason" varchar(100) NULL, "history_type" varchar(1) NOT NULL, "candidate_id_id" bigint NULL, "created_by_id" integer NULL, "history_relation_id" bigint NOT NULL, "history_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL);
CREATE TABLE "recruitment_historicalrejectedcandidate_history_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "historicalrejectedcandidate_id" integer NOT NULL REFERENCES "recruitment_historicalrejectedcandidate" ("history_id") DEFERRABLE INITIALLY DEFERRED, "audittag_id" bigint NOT NULL REFERENCES "fits_audit_audittag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_interviewevaluation" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "overall_score" decimal NOT NULL, "recommendation" varchar(20) NOT NULL, "strengths" text NOT NULL, "weaknesses" text NOT NULL, "notes" text NOT NULL, "submitted_at" datetime NOT NULL, "candidate_id" bigint NOT NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "interview_id" bigint NOT NULL REFERENCES "recruitment_interviewschedule" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "panelist_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "round_number" integer unsigned NOT NULL CHECK ("round_number" >= 0));
CREATE TABLE "recruitment_interviewround" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "round_number" integer unsigned NOT NULL CHECK ("round_number" >= 0), "label" varchar(100) NOT NULL, "completed" bool NOT NULL, "completed_at" datetime NULL, "interview_id" bigint NOT NULL REFERENCES "recruitment_interviewschedule" ("id") DEFERRABLE INITIALLY DEFERRED, "interviewer_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "round_date" date NULL, "round_time" time NULL);
CREATE TABLE "recruitment_interviewround_interviewers" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "interviewround_id" bigint NOT NULL REFERENCES "recruitment_interviewround" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_interviewschedule" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "interview_date" date NOT NULL, "interview_time" time NULL, "description" text NOT NULL, "completed" bool NOT NULL, "online_meeting_link" varchar(200) NOT NULL, "meeting_provider" varchar(20) NOT NULL, "invite_sent_at" datetime NULL, "candidate_id_id" bigint NOT NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "num_rounds" integer unsigned NOT NULL CHECK ("num_rounds" >= 0));
CREATE TABLE "recruitment_interviewschedule_employee_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "interviewschedule_id" bigint NOT NULL REFERENCES "recruitment_interviewschedule" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_jobapplication" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(200) NOT NULL, "email" varchar(254) NOT NULL, "phone" varchar(30) NULL, "country" varchar(100) NULL, "experience" text NULL, "why_apply" text NULL, "resume_path" varchar(500) NULL, "status" varchar(20) NOT NULL, "score" integer NULL, "ai_reason" text NULL, "hr_override" bool NOT NULL, "excluded_by_second_filter" bool NOT NULL, "created_at" datetime NOT NULL, "recruitment_id" bigint NOT NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED, "hr_override_justification" text NULL, "skills" text NOT NULL CHECK ((JSON_VALID("skills") OR "skills" IS NULL)), "rejection_justification" text NULL, "rejection_email_sent" bool NOT NULL);
CREATE TABLE "recruitment_jobemailtemplate" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "selection_subject" varchar(200) NOT NULL, "selection_body" text NOT NULL, "rejection_subject" varchar(200) NOT NULL, "rejection_body" text NOT NULL, "is_default" bool NOT NULL);
CREATE TABLE "recruitment_linkedinaccount" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "username" varchar(250) NOT NULL, "email" varchar(254) NOT NULL, "api_token" varchar(500) NOT NULL, "sub_id" varchar(250) NOT NULL UNIQUE, "organization_id" varchar(250) NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_manpowerapproval" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "action" varchar(20) NOT NULL, "acted_at" datetime NULL, "due_at" datetime NULL, "comment" text NOT NULL, "acted_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "approver_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "request_id" bigint NOT NULL REFERENCES "recruitment_manpowerrequest" ("id") DEFERRABLE INITIALLY DEFERRED, "step_id" bigint NULL REFERENCES "recruitment_approvalstep" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_manpowerrequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "requisition_no" varchar(20) NOT NULL UNIQUE, "grade" varchar(50) NOT NULL, "positions_count" integer unsigned NOT NULL CHECK ("positions_count" >= 0), "justification" text NOT NULL, "budget_code" varchar(100) NOT NULL, "expected_join_date" date NULL, "employment_type" varchar(20) NOT NULL, "nationality_preference" varchar(10) NOT NULL, "status" varchar(20) NOT NULL, "requested_on" datetime NOT NULL, "closed_positions" integer unsigned NOT NULL CHECK ("closed_positions" >= 0), "company_id_id" bigint NOT NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "department_id" bigint NULL REFERENCES "base_department" ("id") DEFERRABLE INITIALLY DEFERRED, "job_position_id" bigint NULL REFERENCES "base_jobposition" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "requested_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "clarification_document" varchar(100) NULL, "last_query" text NOT NULL, "query_count" integer unsigned NOT NULL CHECK ("query_count" >= 0));
CREATE TABLE "recruitment_manpowerrequeststatuslog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "from_status" varchar(20) NOT NULL, "to_status" varchar(20) NOT NULL, "at" datetime NOT NULL, "note" text NOT NULL, "changed_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "request_id" bigint NOT NULL REFERENCES "recruitment_manpowerrequest" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_medicalletter" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content" text NOT NULL, "status" varchar(20) NOT NULL, "hr_signed" bool NOT NULL, "hr_signature" text NOT NULL, "hr_signed_at" datetime NULL, "created_at" datetime NOT NULL, "candidate_id_id" bigint NOT NULL UNIQUE REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "hr_signed_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "doc_no" varchar(20) NOT NULL UNIQUE);
CREATE TABLE "recruitment_medicalletterstatuslog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "from_status" varchar(30) NOT NULL, "to_status" varchar(30) NOT NULL, "note" text NOT NULL, "timestamp" datetime NOT NULL, "actor_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "medical_letter_id" bigint NOT NULL REFERENCES "recruitment_medicalletter" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_medicallettertemplate" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(200) NOT NULL, "body_html" text NOT NULL, "is_active" bool NOT NULL, "created_at" datetime NOT NULL);
INSERT INTO "recruitment_medicallettertemplate" VALUES(1,'Standard Medical Clearance Letter','To Whom It May Concern,

This is to certify that {{candidate_name}} has been assessed and found medically fit to undertake the role of {{position}} at {{company_name}}.

The candidate has completed all required pre-employment medical checks and has been declared medically fit for employment.

This clearance is valid for a period of three (3) months from the date of issuance.

Should you require any further information, please do not hesitate to contact us.

Yours sincerely,
Human Resources Department
{{company_name}}',1,'2026-05-29 10:18:07.063136');
INSERT INTO "recruitment_medicallettertemplate" VALUES(2,'Medical Clearance — Overseas Placement','RE: Medical Clearance for Overseas Employment

Dear Sir/Madam,

We are pleased to confirm that {{candidate_name}}, who has been selected for the position of {{position}} at {{company_name}}, has successfully completed all mandatory pre-employment medical examinations required for overseas deployment.

The results confirm that the candidate is in good health and is medically cleared for international travel and employment.

This letter is issued for official purposes only.

Yours faithfully,
Human Resources
{{company_name}}',1,'2026-05-29 10:18:07.063619');
CREATE TABLE "recruitment_offerapproval" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "action" varchar(20) NOT NULL, "acted_at" datetime NULL, "due_at" datetime NULL, "comment" text NOT NULL, "acted_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "approver_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "offer_id" bigint NOT NULL REFERENCES "recruitment_offerletter" ("id") DEFERRABLE INITIALLY DEFERRED, "step_id" bigint NULL REFERENCES "recruitment_approvalstep" ("id") DEFERRABLE INITIALLY DEFERRED, "signature_image" text NOT NULL);
CREATE TABLE "recruitment_offerletter" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "offer_no" varchar(20) NOT NULL UNIQUE, "position" varchar(100) NOT NULL, "department" varchar(100) NULL, "basic_salary" decimal NOT NULL, "gross_salary" decimal NULL, "currency" varchar(3) NOT NULL, "joining_date" date NOT NULL, "contract_duration" integer NULL, "probation_period" integer NOT NULL, "job_description" text NULL, "terms_conditions" text NULL, "letter_template" text NULL, "generated_letter" text NULL, "status" varchar(20) NOT NULL, "sent_date" datetime NULL, "accepted_date" datetime NULL, "rejected_date" datetime NULL, "rejection_reason" text NULL, "approval_submitted_at" datetime NULL, "medical_status" varchar(15) NOT NULL, "visa_status" varchar(15) NOT NULL, "labour_clearance_status" varchar(15) NOT NULL, "documents_completion_pct" integer unsigned NOT NULL CHECK ("documents_completion_pct" >= 0), "joining_status" varchar(15) NOT NULL, "medical_cleared_at" datetime NULL, "visa_cleared_at" datetime NULL, "labour_cleared_at" datetime NULL, "created_on" datetime NOT NULL, "modified_on" datetime NOT NULL, "candidate_id_id" bigint NOT NULL UNIQUE REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "role_type" varchar(20) NOT NULL, "candidate_signature_token" char(32) NOT NULL UNIQUE, "portal_token" char(32) NOT NULL UNIQUE, "candidate_signed_at" datetime NULL, "location" varchar(200) NULL);
CREATE TABLE "recruitment_offerletterapproval" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "sequence" integer unsigned NOT NULL CHECK ("sequence" >= 0), "status" varchar(20) NOT NULL, "feedback" text NOT NULL, "acted_at" datetime NULL, "approver_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "offer_letter_id" bigint NOT NULL REFERENCES "recruitment_offerletter" ("id") DEFERRABLE INITIALLY DEFERRED, "signature_image" text NOT NULL, "esign_provider" varchar(20) NULL, "esign_reference" varchar(120) NULL);
CREATE TABLE "recruitment_offerletterstatuslog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "from_status" varchar(30) NOT NULL, "to_status" varchar(30) NOT NULL, "note" text NOT NULL, "timestamp" datetime NOT NULL, "actor_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "offer_letter_id" bigint NOT NULL REFERENCES "recruitment_offerletter" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_offerlettertemplate" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(200) NOT NULL UNIQUE, "body_html" text NOT NULL, "is_active" bool NOT NULL, "created_at" datetime NOT NULL);
INSERT INTO "recruitment_offerlettertemplate" VALUES(1,'Standard Employment Offer','Dear {{candidate_name}},

We are delighted to offer you the position of <strong>{{position}}</strong>{% if department %} in the <strong>{{department}}</strong> department{% endif %} at <strong>{{company_name}}</strong>.

<strong>Key Terms of Employment:</strong>

• <strong>Position:</strong> {{position}}
• <strong>Department:</strong> {{department}}
• <strong>Joining Date:</strong> {{joining_date}}
• <strong>Basic Salary:</strong> OMR {{basic_salary}} per month

Your employment will be subject to the standard terms and conditions of employment as set out in the Employment Contract, which will be provided to you prior to your joining date.

Please confirm your acceptance of this offer by signing and returning a copy of this letter. If you have any questions, please do not hesitate to contact our HR department.

We look forward to welcoming you to our team.

Yours sincerely,
Human Resources Department
{{company_name}}',1,'2026-05-29 10:18:06.844691');
INSERT INTO "recruitment_offerlettertemplate" VALUES(2,'Senior Management Offer','Dear {{candidate_name}},

On behalf of the Leadership Team at <strong>{{company_name}}</strong>, we are pleased to extend this offer of employment for the senior role of <strong>{{position}}</strong>.

<strong>Position Details:</strong>

• <strong>Title:</strong> {{position}}
• <strong>Division / Department:</strong> {{department}}
• <strong>Commencement Date:</strong> {{joining_date}}
• <strong>Basic Monthly Remuneration:</strong> OMR {{basic_salary}}

In addition to your basic salary, you will be entitled to a comprehensive benefits package including health insurance, annual leave entitlement per Omani Labour Law, and performance-based incentives as outlined in the attached schedule.

This offer is contingent upon satisfactory reference checks and receipt of original academic and professional credentials.

We are confident that your expertise and leadership will make a significant contribution to our organisation. We look forward to your positive response.

Warmest regards,
Chief Executive Officer
{{company_name}}',1,'2026-05-29 10:18:06.845208');
INSERT INTO "recruitment_offerlettertemplate" VALUES(3,'Probationary Offer','Dear {{candidate_name}},

We are pleased to offer you the position of <strong>{{position}}</strong>{% if department %} within the <strong>{{department}}</strong> department{% endif %} at <strong>{{company_name}}</strong>, subject to a probationary period.

<strong>Employment Details:</strong>

• <strong>Position:</strong> {{position}}
• <strong>Department:</strong> {{department}}
• <strong>Start Date:</strong> {{joining_date}}
• <strong>Basic Salary:</strong> OMR {{basic_salary}} per month
• <strong>Probationary Period:</strong> Three (3) months from the date of joining

During the probationary period, your performance will be evaluated against set objectives. Upon successful completion, your employment will be confirmed and you will be entitled to the full benefits package as per company policy.

Either party may terminate employment during the probation period with one (1) week''s written notice.

Please sign and return this letter to confirm acceptance no later than 5 working days from the date of issue.

Kind regards,
Human Resources Department
{{company_name}}',1,'2026-05-29 10:18:06.845479');
INSERT INTO "recruitment_offerlettertemplate" VALUES(4,'Contract Employment Offer','Dear {{candidate_name}},

We are pleased to offer you a fixed-term contract position of <strong>{{position}}</strong>{% if department %} in the <strong>{{department}}</strong> department{% endif %} at <strong>{{company_name}}</strong>.

<strong>Contract Details:</strong>

• <strong>Position:</strong> {{position}}
• <strong>Department:</strong> {{department}}
• <strong>Contract Start Date:</strong> {{joining_date}}
• <strong>Contract Duration:</strong> One (1) year, renewable subject to performance and business needs
• <strong>Basic Monthly Salary:</strong> OMR {{basic_salary}}

This is a fixed-term engagement and does not imply any promise of permanent employment beyond the stated term. The contract may be renewed by mutual written agreement prior to expiry.

All other employment conditions shall be governed by the Omani Labour Law and the company''s internal policies applicable to contract employees.

Kindly confirm your acceptance of these terms within three (3) working days.

Regards,
Human Resources Department
{{company_name}}',1,'2026-05-29 10:18:06.845735');
INSERT INTO "recruitment_offerlettertemplate" VALUES(5,'Executive Offer Letter','Dear {{candidate_name}},

The Board of Directors and Executive Leadership of <strong>{{company_name}}</strong> are honoured to extend this offer of employment to you for the executive position of <strong>{{position}}</strong>.

<strong>Executive Appointment Details:</strong>

• <strong>Title:</strong> {{position}}
• <strong>Reporting Division:</strong> {{department}}
• <strong>Effective Date:</strong> {{joining_date}}
• <strong>Basic Monthly Salary:</strong> OMR {{basic_salary}}

<strong>Executive Benefits Include:</strong>
• Comprehensive private medical insurance (employee + dependants)
• Annual performance bonus (as per the Executive Incentive Plan)
• Company vehicle or vehicle allowance
• Annual leave as per Omani Labour Law plus additional executive entitlement
• Business travel and accommodation per company policy

This appointment is subject to board ratification, satisfactory completion of background screening, and execution of the Executive Service Agreement which will be provided separately.

We are excited about the strategic value you will bring to <strong>{{company_name}}</strong> and look forward to your formal acceptance.

With regards,
Chairman, Board of Directors
{{company_name}}',1,'2026-05-29 10:18:06.845998');
INSERT INTO "recruitment_offerlettertemplate" VALUES(6,'ONEIC — Employment Proposal Form (General)','
<div style="font-family: Arial, sans-serif; font-size: 11px; color:#000; max-width: 760px; margin:auto;">
  <div style="text-align:center; font-weight:bold;">
    <div style="font-size:13px;">الشركة الوطنية العمانية للهندسة و الاستثمار ( ش م ع ع )</div>
    <div style="font-size:13px;">Oman National Engineering &amp; Investment Company (SAOG)</div>
    <div style="font-size:14px; margin-top:6px;">EMPLOYMENT PROPOSAL FORM</div>
  </div>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:10px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;">
      <td colspan="4">General</td>
      <td style="width:60px;">05</td>
      <td style="width:60px;">2025</td>
    </tr>
    <tr>
      <td style="width:130px;">Post Applied for</td>
      <td colspan="3"><b>{{position}}</b></td>
      <td>Grade Group</td>
      <td>&nbsp;</td>
    </tr>
    <tr>
      <td>Div. / Dept.</td>
      <td colspan="3"><b>{{department}}</b></td>
      <td>Post Location</td>
      <td>&nbsp;</td>
    </tr>
    <tr>
      <td>Contractual</td>
      <td colspan="3">☐ YES &nbsp;&nbsp; ☑ NO</td>
      <td>Contract Name</td>
      <td>&nbsp;</td>
    </tr>
    <tr>
      <td>Contract Period</td>
      <td>From</td>
      <td>&nbsp;</td>
      <td>To</td>
      <td>Job No.</td>
      <td>83001</td>
    </tr>
    <tr>
      <td>Reporting to</td>
      <td colspan="3">{{reporting_to}}</td>
      <td>Staff No.</td>
      <td>&nbsp;</td>
    </tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="6">Brief (Recruitment)</td></tr>
    <tr>
      <td style="width:130px;">New Appointment</td>
      <td>☑ YES</td>
      <td>☐ NO</td>
      <td colspan="3">Replacement for Staff No. ___________</td>
    </tr>
    <tr>
      <td>Candidate Referred</td>
      <td>☐ Client</td>
      <td>☐ Consultancy</td>
      <td>☑ Direct</td>
      <td colspan="2">☐ Staff Number</td>
    </tr>
    <tr>
      <td>Consultancy Reg.</td>
      <td>☐ Voltech HR</td>
      <td>☐ Zen</td>
      <td>☐ Trehan</td>
      <td>☐ Sinclus</td>
      <td>☐ ALYousuf / ☐ Others</td>
    </tr>
    <tr>
      <td>Employment Contract</td>
      <td colspan="5">☐ Temporary ______ Months &nbsp;&nbsp; ☑ Permanent (Two years basis)</td>
    </tr>
    <tr>
      <td colspan="6">Does the Candidate have any relation working in the Company? ☐ YES &nbsp; ☑ NO<br/>
      If YES, mention Name: __________ ; Staff No: ______ ; Work Location: __________</td>
    </tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="4">Summary of Resume</td></tr>
    <tr><td>Application Date:</td><td>{{application_date}}</td><td>Interview Date:</td><td>{{interview_date}}</td></tr>
    <tr><td>Name of Applicant:</td><td><b>{{candidate_name}}</b></td><td>Nationality:</td><td>{{nationality}}</td></tr>
    <tr><td>Present Employer:</td><td>{{present_employer}}</td><td colspan="2">Local Transfer: ☑ YES &nbsp; ☐ NO</td></tr>
    <tr><td>Marital Status:</td><td colspan="3">☐ Single &nbsp; ☑ Married &nbsp; ☐ Divorced &nbsp; ☐ Widow &nbsp; ☐ Other</td></tr>
    <tr><td>Date of Birth:</td><td>{{dob}}</td><td>Place of Birth:</td><td>{{birth_place}}</td></tr>
    <tr><td>Qualification (Academic):</td><td colspan="3">Master of Business Administration &nbsp; / &nbsp; Professional/Technical: __________</td></tr>
    <tr><td>Experience:</td><td>Local: __________</td><td colspan="2">Overseas: __________</td></tr>
    <tr><td>Languages:</td><td colspan="3">☐ Arabic &nbsp; ☑ English &nbsp; ☐ Others &nbsp;&nbsp; Driving License: ☐ Omani ☐ GCC ☐ Other</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="4">SALARY RECOMMENDATION</td></tr>
    <tr style="background:#f6f6f6; font-weight:bold;">
      <td>Salary OMR — ☑ Budgeted R.O. &nbsp; ☐ Not Budgeted &nbsp; ☐ Contractual</td>
      <td>Proposed</td><td>HRC Suggestion</td><td>CEO Approval</td>
    </tr>
    <tr><td>Basic Salary</td><td>{{basic_salary}}</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>HRA (Inc. E&amp;W, Tel. &amp; GSM)</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Transport Allowance</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Additional Responsibility Allowance</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Overtime Allowance</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>FOOD ALLOWANCE</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Living Standard Allowance (LSA)<br/>
      ☐ RO 50 (&lt;300) &nbsp; ☐ RO (301–500) &nbsp; ☐ RO 30 (501–999) &nbsp; ☐ RO 20 (1000 &amp; Above)<br/>
      <i>LSA calculated as per Basic salary</i></td>
      <td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr style="font-weight:bold;"><td>Gross Salary →</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
  </table>

  <p style="font-size:10px;">* This allowance is part of gross salary and can be dissolved to adjust in basic and allowances during any compensation restructuring.</p>

  <div style="margin-top:6px;">
    <b>Notes:</b>
    <ul style="margin:4px 0 0 18px; padding:0;">
      <li>☐ Contract Period: ______ to ______ (Two years basis / Short Period)</li>
      <li>☑ Air passage Sector: From ______ to ______ (Entitlement: ☑ 12 months / ☐ 24 months)</li>
      <li>☐ Family status (Wife, 2 children up to 18 years age) &nbsp; ☑ Bachelor status</li>
      <li>☑ Medical (as per Company''s medical insurance policy and Oman Labour Law)</li>
      <li>☐ Increase Salary by RO ___ after ☐ 3 or ☐ 6 months in ☐ RO ___ in basic / ☐ RO ___ in Addl. Resp. Allow.</li>
    </ul>
    <p>HOD''s Comments (if any): ______________________________________________________</p>
  </div>

  <table border="1" cellspacing="0" cellpadding="6" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="3">Approvals by Circular – HRC</td></tr>
    <tr><td>Project Director</td><td>Member</td><td>__________________________</td></tr>
    <tr><td>Head Of Department</td><td>Member</td><td>__________________________</td></tr>
    <tr><td>Chief Operation Officer</td><td>Member</td><td>__________________________</td></tr>
    <tr><td>Legal Advisor</td><td>Member</td><td>__________________________</td></tr>
    <tr><td>General Manager HR&amp;A</td><td>Member</td><td>__________________________</td></tr>
  </table>

  <p>Remarks (if any): ______________________________________________________</p>

  <table border="1" cellspacing="0" cellpadding="10" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="2">FINAL APPROVAL</td></tr>
    <tr style="text-align:center;">
      <td><br/><br/>__________________________<br/><b>Chief Financial Officer</b><br/>HRC Chairman</td>
      <td><br/><br/>__________________________<br/><b>Chief Executive Officer</b></td>
    </tr>
  </table>

  <p style="font-size:10px; margin-top:6px;">
    Note: 1) "S&amp;O" Grade (Expat.) final approval by the Head of HR.<br/>
    2) Any change in this form must be signed by any 3 members at least, otherwise it is considered as void.
  </p>
  <p style="font-size:9px; text-align:right;">HR&amp;A/EPF/V3/R/July 2022</p>
</div>
',1,'2026-05-29 10:18:08.579632');
INSERT INTO "recruitment_offerlettertemplate" VALUES(7,'ONEIC — Employment Proposal Form (S-O-M Grade Contractual)','
<div style="font-family: Arial, sans-serif; font-size: 11px; color:#000; max-width:760px; margin:auto;">
  <div style="text-align:center; font-weight:bold;">
    <div style="font-size:13px;">الشركة الوطنية العمانية للهندسة و الاستثمار ( ش م ع ع )</div>
    <div style="font-size:13px;">Oman National Engineering &amp; Investment Company (SAOG)</div>
    <div style="font-size:14px; margin-top:6px;">EMPLOYMENT PROPOSAL FORM</div>
    <div style="font-size:12px;">("S-O-M" Grade — Contractual)</div>
    <div style="text-align:right; font-size:11px;">Date: __________ &nbsp; 2022</div>
  </div>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:10px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="4">General</td></tr>
    <tr><td>Post Applied for</td><td>{{position}}</td><td>Grade Group</td><td>&nbsp;</td></tr>
    <tr><td>Div. / Dept.</td><td>{{department}}</td><td>Post Location</td><td>&nbsp;</td></tr>
    <tr><td>Contractual</td><td>☐ YES &nbsp; ☐ NO</td><td>Contract Name</td><td>&nbsp;</td></tr>
    <tr><td>Contract Period</td><td>From _____ To _____</td><td>Job No.</td><td>&nbsp;</td></tr>
    <tr><td>Reporting to</td><td>{{reporting_to}}</td><td>Staff No. / GSM / CPN No.</td><td>&nbsp;</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="6">Brief (Recruitment)</td></tr>
    <tr><td>New Appointment</td><td>☐ YES</td><td>☐ NO</td><td colspan="3">Replacement for Staff No. ______</td></tr>
    <tr><td>Candidate Referred</td><td>☐ Client</td><td>☐ Consultancy</td><td>☐ Direct</td><td colspan="2">☐ Staff Number</td></tr>
    <tr><td>Consultancy Reg.</td><td>☐ Voltech HR</td><td>☐ Zen</td><td>☐ Trehan</td><td>☐ Sinclus</td><td>☐ ALYousuf / ☐ Others</td></tr>
    <tr><td>Employment Contract</td><td colspan="5">☐ Temporary _____ Months &nbsp; ☐ Permanent (______)</td></tr>
    <tr><td colspan="6">Does the Candidate have any relation working in the Company? ☐ YES &nbsp; ☐ NO<br/>If YES, mention Name: ______ ; Staff No: ______ ; Work Location: ______</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="4">Summary of Resume</td></tr>
    <tr><td>Application Date:</td><td>{{application_date}}</td><td>Interview Date:</td><td>{{interview_date}}</td></tr>
    <tr><td>Name of Applicant:</td><td><b>{{candidate_name}}</b></td><td>Nationality:</td><td>{{nationality}}</td></tr>
    <tr><td>Present Employer:</td><td>{{present_employer}}</td><td colspan="2">Local Transfer: ☐ YES ☐ NO</td></tr>
    <tr><td>Marital Status:</td><td colspan="3">✓ Single &nbsp; ☐ Married &nbsp; ☐ Divorced &nbsp; ☐ Widow &nbsp; ☐ Other</td></tr>
    <tr><td>Date of Birth:</td><td>{{dob}}</td><td>Place of Birth:</td><td>{{birth_place}}</td></tr>
    <tr><td>Qualification (Academic):</td><td colspan="3">__________ &nbsp; Professional/Technical: __________</td></tr>
    <tr><td>Experience:</td><td colspan="3">Overseas: ______ Years</td></tr>
    <tr><td>Languages:</td><td colspan="3">✓ Arabic &nbsp; ✓ English &nbsp; ☐ Others &nbsp;&nbsp; Driving License: ✓ Omani ☐ GCC ☐ Other</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="4">SALARY RECOMMENDATION</td></tr>
    <tr style="background:#f6f6f6; font-weight:bold;">
      <td>Salary OMR — ☐ Budgeted &nbsp; ☐ Not Budgeted &nbsp; ☐ Contractual</td>
      <td>Proposed</td><td>HR Suggestion</td><td>Remarks</td></tr>
    <tr><td>Basic Salary</td><td>{{basic_salary}}</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>HRA (Inc. E&amp;W, Tel. &amp; GSM)</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Transport Allowance</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Addl. Resp. Allowance</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Food Allowance</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Living Standard Allowance (LSA)<br/>
      ☐ RO 50 (&lt;300) ☐ RO (301–500) ☐ RO 30 (501–999) ☐ RO 20 (1000 &amp; Above)<br/>
      <i>LSA calculated as per Basic salary</i></td>
      <td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr style="font-weight:bold;"><td>Gross Salary →</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
  </table>

  <div style="margin-top:6px;">
    <b>Notes:</b>
    <ul style="margin:4px 0 0 18px; padding:0;">
      <li>☐ Contract Period: From ______ to ______ (Two years basis / Short Period)</li>
      <li>☐ Air passage Sector: From ______ to MUSCAT (Entitlement: ☐ 12 months ☐ 24 months)</li>
      <li>☐ Family status (Wife, 2 children up to 18 years age) &nbsp; ☐ Bachelor status</li>
      <li>☐ Medical (as per Company''s medical insurance policy and Oman Labour Law)</li>
      <li>☐ Increase Salary by RO ___ after ☐ 3 or ☐ 6 months in ☐ RO ___ in basic / ☐ RO ___ in Addl. Resp. Allow.</li>
    </ul>
    <p>HOD''s Comments (if any): ______________________________________________________</p>
  </div>

  <table border="1" cellspacing="0" cellpadding="6" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; font-weight:bold;"><td colspan="3">Approvals by Circular</td></tr>
    <tr><td>Head Of Department</td><td>Member</td><td>__________________________</td></tr>
    <tr><td>Chief Operation Officer</td><td>Member</td><td>__________________________</td></tr>
  </table>

  <p>Remarks (if any): ______________________________________________________</p>

  <table border="1" cellspacing="0" cellpadding="10" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td>FINAL APPROVAL</td></tr>
    <tr style="text-align:center;"><td><br/><br/>__________________________<br/><b>General Manager HR&amp;A</b></td></tr>
  </table>
  <p>Comments (if any): ______________________________________________________</p>

  <p style="font-size:10px;">
    Note: 1) "S – O – M" Grade: Final approval by the Head of HR for all contractual proposals.<br/>
    2) Any change in this form must be signed by any 3 members at least, otherwise it is considered as void.
  </p>
  <p style="font-size:9px; text-align:right;">HR&amp;A/EPF-S/V4/R/July 2022</p>
</div>
',1,'2026-05-29 10:18:08.580335');
CREATE TABLE "recruitment_onboardingdocument" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "doc_key" varchar(40) NOT NULL, "title" varchar(150) NOT NULL, "body_html" text NOT NULL, "batch" integer unsigned NOT NULL CHECK ("batch" >= 0), "sequence" integer unsigned NOT NULL CHECK ("sequence" >= 0), "released" bool NOT NULL, "candidate_signature" text NOT NULL, "candidate_signed_at" datetime NULL, "status" varchar(20) NOT NULL, "hr_note" text NOT NULL, "hr_acted_at" datetime NULL, "created_at" datetime NOT NULL, "hr_acted_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "offer_id" bigint NOT NULL REFERENCES "recruitment_offerletter" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_parsedcvdata" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "full_name" varchar(255) NOT NULL, "email" varchar(254) NOT NULL, "phone" varchar(20) NOT NULL, "location_city" varchar(100) NOT NULL, "location_country" varchar(100) NOT NULL, "education_json" text NOT NULL CHECK ((JSON_VALID("education_json") OR "education_json" IS NULL)), "highest_qualification" varchar(100) NOT NULL, "total_years_experience" decimal NOT NULL, "work_experience_json" text NOT NULL CHECK ((JSON_VALID("work_experience_json") OR "work_experience_json" IS NULL)), "current_job_title" varchar(255) NOT NULL, "current_company" varchar(255) NOT NULL, "extracted_skills" text NOT NULL CHECK ((JSON_VALID("extracted_skills") OR "extracted_skills" IS NULL)), "skill_categories" text NOT NULL CHECK ((JSON_VALID("skill_categories") OR "skill_categories" IS NULL)), "languages_spoken" text NOT NULL CHECK ((JSON_VALID("languages_spoken") OR "languages_spoken" IS NULL)), "certifications_json" text NOT NULL CHECK ((JSON_VALID("certifications_json") OR "certifications_json" IS NULL)), "parsing_engine" varchar(20) NOT NULL, "parsing_confidence" real NOT NULL, "parsing_date" datetime NOT NULL, "requires_manual_review" bool NOT NULL, "raw_cv_text" text NULL, "candidate_id" bigint NOT NULL UNIQUE REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_proposalapproval" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "role_key" varchar(40) NOT NULL, "role_label" varchar(120) NOT NULL, "sequence" integer unsigned NOT NULL CHECK ("sequence" >= 0), "status" varchar(20) NOT NULL, "feedback" text NOT NULL, "signature_image" text NOT NULL, "acted_at" datetime NULL, "approver_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "proposal_id" bigint NOT NULL REFERENCES "recruitment_employmentproposal" ("id") DEFERRABLE INITIALLY DEFERRED, "esign_provider" varchar(20) NULL, "esign_reference" varchar(120) NULL);
CREATE TABLE "recruitment_proposalroleassignment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "role_key" varchar(40) NOT NULL UNIQUE, "role_label" varchar(120) NOT NULL, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_proposalstatuslog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "action" varchar(40) NOT NULL, "note" text NOT NULL, "timestamp" datetime NOT NULL, "actor_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "proposal_id" bigint NOT NULL REFERENCES "recruitment_employmentproposal" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_questionordering" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "sequence" integer NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "question_id_id" bigint NOT NULL REFERENCES "recruitment_recruitmentsurvey" ("id") DEFERRABLE INITIALLY DEFERRED, "recruitment_id_id" bigint NOT NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_recruitment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(50) NULL, "description" text NULL, "is_event_based" bool NOT NULL, "closed" bool NOT NULL, "is_published" bool NOT NULL, "vacancy" integer NULL, "start_date" date NOT NULL, "end_date" date NULL, "linkedin_post_id" varchar(150) NULL, "published_to_linkedin" bool NOT NULL, "linkedin_posted_at" datetime NULL, "linkedin_external_id" varchar(50) NULL, "published_to_bayt" bool NOT NULL, "bayt_posted_at" datetime NULL, "bayt_external_id" varchar(50) NULL, "published_to_naukrigulf" bool NOT NULL, "naukrigulf_posted_at" datetime NULL, "naukrigulf_external_id" varchar(50) NULL, "publish_in_linkedin" bool NOT NULL, "optional_profile_image" bool NOT NULL, "optional_resume" bool NOT NULL, "is_public" bool NOT NULL, "public_slug" varchar(120) NOT NULL, "raised_from_employee" bool NOT NULL, "approval_status" varchar(20) NOT NULL, "hr_feedback" text NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "job_position_id_id" bigint NULL, "linkedin_account_id_id" bigint NULL REFERENCES "recruitment_linkedinaccount" ("id") DEFERRABLE INITIALLY DEFERRED, "manpower_request_id" bigint NULL UNIQUE REFERENCES "recruitment_manpowerrequest" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "raised_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "justification" text NULL, "posting_type" varchar(10) NOT NULL, "budget_available" bool NOT NULL, "budget_document" varchar(100) NULL, "job_id" varchar(20) NULL UNIQUE, "grade" varchar(30) NULL, "band" varchar(30) NULL, "budget" decimal NULL, "employment_type" varchar(20) NOT NULL, "expat_allowed" bool NOT NULL, "location" varchar(120) NULL, "is_bulk" bool NOT NULL);
CREATE TABLE "recruitment_recruitment_open_positions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "recruitment_id" bigint NOT NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED, "jobposition_id" bigint NOT NULL REFERENCES "base_jobposition" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_recruitment_recruitment_managers" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "recruitment_id" bigint NOT NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_recruitment_skills" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "recruitment_id" bigint NOT NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED, "skill_id" bigint NOT NULL REFERENCES "recruitment_skill" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_recruitment_survey_templates" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "recruitment_id" bigint NOT NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED, "surveytemplate_id" bigint NOT NULL REFERENCES "recruitment_surveytemplate" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_recruitmentapproval" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "sequence" integer unsigned NOT NULL CHECK ("sequence" >= 0), "status" varchar(20) NOT NULL, "approved_at" datetime NULL, "comments" text NULL, "approver_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "recruitment_id" bigint NOT NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED, "signature_image" text NOT NULL);
CREATE TABLE "recruitment_recruitmentapprovaldelegation" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "start_date" date NOT NULL, "end_date" date NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "delegate_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "delegator_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_recruitmentgeneralsetting" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "candidate_self_tracking" bool NOT NULL, "show_overall_rating" bool NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_recruitmentsurvey" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "is_mandatory" bool NOT NULL, "question" text NOT NULL, "sequence" integer NULL, "type" varchar(15) NOT NULL, "options" text NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_recruitmentsurvey_job_position_ids" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "recruitmentsurvey_id" bigint NOT NULL REFERENCES "recruitment_recruitmentsurvey" ("id") DEFERRABLE INITIALLY DEFERRED, "jobposition_id" bigint NOT NULL REFERENCES "base_jobposition" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_recruitmentsurvey_recruitment_ids" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "recruitmentsurvey_id" bigint NOT NULL REFERENCES "recruitment_recruitmentsurvey" ("id") DEFERRABLE INITIALLY DEFERRED, "recruitment_id" bigint NOT NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_recruitmentsurvey_template_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "recruitmentsurvey_id" bigint NOT NULL REFERENCES "recruitment_recruitmentsurvey" ("id") DEFERRABLE INITIALLY DEFERRED, "surveytemplate_id" bigint NOT NULL REFERENCES "recruitment_surveytemplate" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_recruitmentsurveyanswer" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "answer_json" text NOT NULL CHECK ((JSON_VALID("answer_json") OR "answer_json" IS NULL)), "attachment" varchar(100) NULL, "candidate_id_id" bigint NOT NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "job_position_id_id" bigint NULL REFERENCES "base_jobposition" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "recruitment_id_id" bigint NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_rejectedcandidate" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "description" text NOT NULL, "candidate_id_id" bigint NOT NULL UNIQUE REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_rejectedcandidate_reject_reason_id" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "rejectedcandidate_id" bigint NOT NULL REFERENCES "recruitment_rejectedcandidate" ("id") DEFERRABLE INITIALLY DEFERRED, "rejectreason_id" bigint NOT NULL REFERENCES "recruitment_rejectreason" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_rejectreason" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(50) NOT NULL, "description" text NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_resume" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "file" varchar(100) NOT NULL, "is_candidate" bool NOT NULL, "recruitment_id_id" bigint NOT NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_skill" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(100) NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_skillzone" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(50) NOT NULL, "description" text NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_skillzonecandidate" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "reason" varchar(200) NOT NULL, "added_on" date NOT NULL, "candidate_id_id" bigint NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "skill_zone_id_id" bigint NULL REFERENCES "recruitment_skillzone" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_stage" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "stage" varchar(50) NOT NULL, "stage_type" varchar(20) NOT NULL, "sequence" integer NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "recruitment_id_id" bigint NOT NULL REFERENCES "recruitment_recruitment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_stage_stage_managers" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "stage_id" bigint NOT NULL REFERENCES "recruitment_stage" ("id") DEFERRABLE INITIALLY DEFERRED, "employee_id" bigint NOT NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_stagefiles" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "files" varchar(100) NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_stagenote" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "description" text NOT NULL, "candidate_can_view" bool NOT NULL, "candidate_id_id" bigint NOT NULL REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "stage_id_id" bigint NOT NULL REFERENCES "recruitment_stage" ("id") DEFERRABLE INITIALLY DEFERRED, "updated_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_stagenote_stage_files" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "stagenote_id" bigint NOT NULL REFERENCES "recruitment_stagenote" ("id") DEFERRABLE INITIALLY DEFERRED, "stagefiles_id" bigint NOT NULL REFERENCES "recruitment_stagefiles" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_surveytemplate" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NULL, "is_active" bool NOT NULL, "title" varchar(50) NOT NULL UNIQUE, "description" text NULL, "is_general_template" bool NOT NULL, "company_id_id" bigint NULL REFERENCES "base_company" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "modified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_visaletter" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content" text NOT NULL, "status" varchar(20) NOT NULL, "hr_signed" bool NOT NULL, "hr_signature" text NOT NULL, "hr_signed_at" datetime NULL, "created_at" datetime NOT NULL, "candidate_id_id" bigint NOT NULL UNIQUE REFERENCES "recruitment_candidate" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "hr_signed_by_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "doc_no" varchar(20) NOT NULL UNIQUE);
CREATE TABLE "recruitment_visaletterstatuslog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "from_status" varchar(30) NOT NULL, "to_status" varchar(30) NOT NULL, "note" text NOT NULL, "timestamp" datetime NOT NULL, "actor_id" bigint NULL REFERENCES "employee_employee" ("id") DEFERRABLE INITIALLY DEFERRED, "visa_letter_id" bigint NOT NULL REFERENCES "recruitment_visaletter" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "recruitment_visalettertemplate" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(200) NOT NULL, "body_html" text NOT NULL, "is_active" bool NOT NULL, "created_at" datetime NOT NULL);
INSERT INTO "recruitment_visalettertemplate" VALUES(1,'Standard Visa Support Letter','To the Consular Officer,

RE: Visa Support Letter for {{candidate_name}}

We, {{company_name}}, hereby confirm that {{candidate_name}} has been offered and accepted the position of {{position}} with our organisation.

We respectfully request that a work visa / entry permit be granted to the above-named individual to allow them to commence their employment duties.

{{company_name}} accepts full responsibility for the candidate''s conduct and compliance with all applicable immigration laws during their stay.

Please feel free to contact our HR department for any further documentation or clarification required.

Yours sincerely,
Human Resources Department
{{company_name}}',1,'2026-05-29 10:18:07.064140');
INSERT INTO "recruitment_visalettertemplate" VALUES(2,'Visa Support Letter — Skilled Worker','To Whom It May Concern,

This letter serves as official confirmation that {{company_name}} has extended a formal offer of employment to {{candidate_name}} for the role of {{position}}.

The candidate possesses the requisite skills, qualifications and experience for this specialised role, and their employment is essential to our operations.

We kindly request the relevant authorities to process the work permit / visa application for {{candidate_name}} at the earliest convenience.

All supporting documentation will be provided upon request.

Warm regards,
Human Resources
{{company_name}}',1,'2026-05-29 10:18:07.064483');
INSERT INTO "recruitment_visalettertemplate" VALUES(3,'ONEIC — Visa Requisition Form','
<div style="font-family: Arial, sans-serif; font-size: 11px; color:#000; max-width:760px; margin:auto;">
  <div style="text-align:center; font-weight:bold;">
    <div style="font-size:13px;">الشركة الوطنية العمانية للهندسة و الاستثمار ( ش م ع ع )</div>
    <div style="font-size:13px;">Oman National Engineering &amp; Investment Company (SAOG)</div>
    <div style="font-size:14px; margin-top:6px; font-style:italic;">Visa Requisition Form</div>
    <div style="text-align:right; font-size:11px;">CV#: «CV_NO» &nbsp; Source: «Consultancy»</div>
  </div>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:10px;">
    <tr><td>Staff/Candidate Name</td><td><b>{{candidate_name}}</b></td><td>Date</td><td>{{today_date}}</td></tr>
    <tr><td>Staff No / PP No</td><td>«PP_ID_NO»</td><td>Designation</td><td>{{position}}</td></tr>
    <tr><td>Department</td><td><b>O&amp;M</b></td><td>Job No / Location</td><td>«Job_no» / «Job_Location»</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; font-weight:bold;"><td colspan="2">Type of Visa (Please ✓)</td></tr>
    <tr>
      <td>☐ Short Employment Visa<br/>Months ___ (4/6/9)</td>
      <td>☐ Medical report (attested) &nbsp; ☐ Salary Details &nbsp; ☐ Photographs &nbsp; ☐ Passport copy<br/>
          ☐ Degree/Diploma attested copy (Apostle) &nbsp; ☐ Govt./Semi Govt. Document — Contract with ONEIC</td>
    </tr>
    <tr>
      <td>☑ Employment Visa</td>
      <td>☑ Medical report (attested) &nbsp; ☑ Copy of Signed offer letter &nbsp; ☑ Photographs &nbsp; ☑ Passport copy<br/>
          ☐ Degree/Diploma attested copy (Apostle)</td>
    </tr>
  </table>

  <p style="margin-top:6px;">This Candidate Visa/Post is covered under the contract / project as per the below details:</p>
  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%;">
    <tr>
      <td style="width:50%;">☑ Existing &nbsp; &nbsp; Job No: «Job_no»</td>
      <td>☐ New &nbsp; &nbsp; Job No: __________</td>
    </tr>
    <tr><td>Project Period</td><td>From «Contract_Start_Date» &nbsp; To «Contract_End_Date»</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; font-weight:bold; text-align:center;">
      <td>Name of the Position</td><td>Requirement as per Contract / Manpower supply (nos)</td>
      <td>Replacement Post ☐ Y / ☐ N (if ''Y'' write Staff no)</td>
      <td>Additional Post Budgeted ☐ Y / ☐ N</td>
      <td>Existing / Available (Nos)</td><td>Shortage (Nos)</td><td>Remarks</td>
    </tr>
    <tr><td>{{position}}</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>«ReplS»</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr>
      <td style="width:30%;">☐ Family Visit Visa<br/><i>Mention the Relationship</i></td>
      <td>☐ Passport Copy &nbsp; ☐ Photographs &nbsp; ☐ Undertaking letter from Embassy (if necessity) &nbsp; ☐ Insurance (RO.2000 — if necessary)<br/>
          ____________________ &nbsp; Their Mother''s name ____________________</td>
    </tr>
    <tr>
      <td>☐ Family Joining Visa<br/><i>Mention the Relationship</i></td>
      <td>☐ Medical report (attested) &nbsp; ☐ Passport Copy &nbsp; ☐ Photographs &nbsp; ☐ Attested Marriage Certificate &nbsp; ☐ House Rental Agreement from Municipality &nbsp; ☐ Insurance (RO.2000)<br/>
          ____________________ &nbsp; Their Mother''s name ____________________</td>
    </tr>
    <tr>
      <td colspan="2">☑ Others: <b>EMPLOYMENT VISA</b> &nbsp; ☑ Passport Copy &nbsp; ☑ Photographs &nbsp; ☑ Medical report (attested)</td>
    </tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; font-weight:bold;"><td colspan="2">Undertaking for &nbsp; ☐ Visit Visa &nbsp; ☐ Family Joining Visa</td></tr>
    <tr><td colspan="2">I, ______________________ Staff No. ______ am accepting all the relevant expenses (visa charges, ticket, and medical expenses) for my ______________________ stay in Oman during the visit.</td></tr>
    <tr><td>Signature: ______________________</td><td>Date: ______________________</td></tr>
    <tr><td colspan="2"><i>Visit visa &amp; Family Joining Visa (if staff is not eligible), the undertaking is <b>Must</b>. Company is not responsible for staff''s relatives insurance.</i></td></tr>
  </table>

  <p>All relevant documents are enclosed.</p>

  <table border="1" cellspacing="0" cellpadding="6" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="text-align:center;">
      <td>__________________<br/>Requester Signature</td>
      <td>__________________<br/>Date</td>
    </tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="6" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; font-weight:bold; text-align:center;"><td colspan="4">Approved by</td></tr>
    <tr style="text-align:center;">
      <td>__________________<br/>Recommended by</td>
      <td>__________________<br/>Head of Div/Dept</td>
      <td>__________________<br/>General Manager (HR&amp;A)</td>
      <td>__________________<br/>Chief Executive Officer<br/>(for HODs)</td>
    </tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; font-weight:bold;"><td colspan="2">HR &amp; Admin Department</td></tr>
    <tr><td>Family Status: ☐ YES &nbsp; ☐ NO</td><td>☐ Staff Eligibility</td></tr>
    <tr><td colspan="2">☐ Accepted &nbsp; ☐ Rejected (Basis) — ☐ Salary &nbsp; ☐ ONEIC Experience &nbsp; ☐ Grade &nbsp; ☐ HRC Approval &nbsp; ☐ Less Salary &nbsp; ☐ Less Experience</td></tr>
    <tr><td>1 — I/C Admin Completed &amp; Forwarded on: __________</td><td>2 — I/C PRO Completed on: __________</td></tr>
    <tr><td>Visa Entered on Date: __________</td><td>Visa Issued on Date: __________ &nbsp; Visa Charges: RO. ________</td></tr>
    <tr><td colspan="2">Charge to ☐ SSR Account No __________ &nbsp; ☐ Job No __________</td></tr>
  </table>

  <p style="font-size:10px; margin-top:6px;">
    ♦ Pakistani Nationalities — Enclose 2<sup>nd</sup> Page of Passport with Mother Name &nbsp;&nbsp; ♦ Incomplete forms shall not be processed
  </p>
  <p style="font-size:9px; text-align:right; font-style:italic;">HR&amp;A/010/09/R1/11/R2/14</p>
</div>
',1,'2026-05-29 10:18:08.580946');
CREATE UNIQUE INDEX "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" ("group_id", "permission_id");
CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" ("group_id");
CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" ("permission_id");
CREATE UNIQUE INDEX "auth_user_groups_user_id_group_id_94350c0c_uniq" ON "auth_user_groups" ("user_id", "group_id");
CREATE INDEX "auth_user_groups_user_id_6a12ed8b" ON "auth_user_groups" ("user_id");
CREATE INDEX "auth_user_groups_group_id_97559544" ON "auth_user_groups" ("group_id");
CREATE UNIQUE INDEX "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq" ON "auth_user_user_permissions" ("user_id", "permission_id");
CREATE INDEX "auth_user_user_permissions_user_id_a95ead1b" ON "auth_user_user_permissions" ("user_id");
CREATE INDEX "auth_user_user_permissions_permission_id_1fbb5f2c" ON "auth_user_user_permissions" ("permission_id");
CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");
CREATE INDEX "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");
CREATE INDEX "auditlog_logentry_object_pk_6e3219c0" ON "auditlog_logentry" ("object_pk");
CREATE INDEX "auditlog_logentry_object_id_09c2eee8" ON "auditlog_logentry" ("object_id");
CREATE INDEX "auditlog_logentry_action_229afe39" ON "auditlog_logentry" ("action");
CREATE INDEX "auditlog_logentry_timestamp_37867bb0" ON "auditlog_logentry" ("timestamp");
CREATE INDEX "auditlog_logentry_actor_id_959271d2" ON "auditlog_logentry" ("actor_id");
CREATE INDEX "auditlog_logentry_content_type_id_75830218" ON "auditlog_logentry" ("content_type_id");
CREATE INDEX "auditlog_logentry_cid_9f467263" ON "auditlog_logentry" ("cid");
CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" ("app_label", "model");
CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" ("content_type_id", "codename");
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission" ("content_type_id");
CREATE INDEX "fits_audit_historytrackingfields_created_by_id_ddb5372d" ON "fits_audit_historytrackingfields" ("created_by_id");
CREATE INDEX "fits_audit_historytrackingfields_modified_by_id_312b5218" ON "fits_audit_historytrackingfields" ("modified_by_id");
CREATE INDEX "fits_audit_accountblockunblock_created_by_id_c4e7bbf3" ON "fits_audit_accountblockunblock" ("created_by_id");
CREATE INDEX "fits_audit_accountblockunblock_modified_by_id_0f233796" ON "fits_audit_accountblockunblock" ("modified_by_id");
CREATE INDEX "employee_actiontype_created_by_id_9cd886e5" ON "employee_actiontype" ("created_by_id");
CREATE INDEX "employee_actiontype_modified_by_id_ca03f5db" ON "employee_actiontype" ("modified_by_id");
CREATE INDEX "employee_employeetag_created_by_id_9bd7d192" ON "employee_employeetag" ("created_by_id");
CREATE INDEX "employee_employeetag_modified_by_id_c671878b" ON "employee_employeetag" ("modified_by_id");
CREATE INDEX "employee_employeeworkinformation_company_id_id_51e946d8" ON "employee_employeeworkinformation" ("company_id_id");
CREATE INDEX "employee_employeeworkinformation_department_id_id_31d2170f" ON "employee_employeeworkinformation" ("department_id_id");
CREATE INDEX "employee_employeeworkinformation_employee_type_id_id_f7707903" ON "employee_employeeworkinformation" ("employee_type_id_id");
CREATE INDEX "employee_employeeworkinformation_job_position_id_id_447a02c3" ON "employee_employeeworkinformation" ("job_position_id_id");
CREATE INDEX "employee_employeeworkinformation_job_role_id_id_b7032a1b" ON "employee_employeeworkinformation" ("job_role_id_id");
CREATE INDEX "employee_employeeworkinformation_reporting_manager_id_id_3f4c7fc4" ON "employee_employeeworkinformation" ("reporting_manager_id_id");
CREATE INDEX "employee_employeeworkinformation_shift_id_id_868ad7f1" ON "employee_employeeworkinformation" ("shift_id_id");
CREATE INDEX "employee_employeeworkinformation_work_type_id_id_e48fe5c7" ON "employee_employeeworkinformation" ("work_type_id_id");
CREATE UNIQUE INDEX "employee_employeeworkinformation_tags_employeeworkinformation_id_employeetag_id_f57a8e85_uniq" ON "employee_employeeworkinformation_tags" ("employeeworkinformation_id", "employeetag_id");
CREATE INDEX "employee_employeeworkinformation_tags_employeeworkinformation_id_adc704f0" ON "employee_employeeworkinformation_tags" ("employeeworkinformation_id");
CREATE INDEX "employee_employeeworkinformation_tags_employeetag_id_d877fd1d" ON "employee_employeeworkinformation_tags" ("employeetag_id");
CREATE INDEX "employee_profileeditfeature_created_by_id_91dbab11" ON "employee_profileeditfeature" ("created_by_id");
CREATE INDEX "employee_profileeditfeature_modified_by_id_a601d18a" ON "employee_profileeditfeature" ("modified_by_id");
CREATE INDEX "employee_policymultiplefile_created_by_id_ad34b84e" ON "employee_policymultiplefile" ("created_by_id");
CREATE INDEX "employee_policymultiplefile_modified_by_id_212f8be6" ON "employee_policymultiplefile" ("modified_by_id");
CREATE INDEX "employee_policy_created_by_id_9bd13cc9" ON "employee_policy" ("created_by_id");
CREATE INDEX "employee_policy_modified_by_id_30e119fc" ON "employee_policy" ("modified_by_id");
CREATE UNIQUE INDEX "employee_policy_attachments_policy_id_policymultiplefile_id_66acf84c_uniq" ON "employee_policy_attachments" ("policy_id", "policymultiplefile_id");
CREATE INDEX "employee_policy_attachments_policy_id_d1ac21df" ON "employee_policy_attachments" ("policy_id");
CREATE INDEX "employee_policy_attachments_policymultiplefile_id_5a893d6a" ON "employee_policy_attachments" ("policymultiplefile_id");
CREATE UNIQUE INDEX "employee_policy_company_id_policy_id_company_id_e633da71_uniq" ON "employee_policy_company_id" ("policy_id", "company_id");
CREATE INDEX "employee_policy_company_id_policy_id_76c891af" ON "employee_policy_company_id" ("policy_id");
CREATE INDEX "employee_policy_company_id_company_id_423bd625" ON "employee_policy_company_id" ("company_id");
CREATE UNIQUE INDEX "employee_policy_specific_employees_policy_id_employee_id_a94d13bd_uniq" ON "employee_policy_specific_employees" ("policy_id", "employee_id");
CREATE INDEX "employee_policy_specific_employees_policy_id_7a905ba6" ON "employee_policy_specific_employees" ("policy_id");
CREATE INDEX "employee_policy_specific_employees_employee_id_25986e79" ON "employee_policy_specific_employees" ("employee_id");
CREATE INDEX "employee_notefiles_created_by_id_52d05add" ON "employee_notefiles" ("created_by_id");
CREATE INDEX "employee_notefiles_modified_by_id_6f97580a" ON "employee_notefiles" ("modified_by_id");
CREATE INDEX "employee_historicalemployeeworkinformation_id_535f41ff" ON "employee_historicalemployeeworkinformation" ("id");
CREATE INDEX "employee_historicalemployeeworkinformation_history_date_280ba80b" ON "employee_historicalemployeeworkinformation" ("history_date");
CREATE INDEX "employee_historicalemployeeworkinformation_company_id_id_cff2a07a" ON "employee_historicalemployeeworkinformation" ("company_id_id");
CREATE INDEX "employee_historicalemployeeworkinformation_department_id_id_865f5100" ON "employee_historicalemployeeworkinformation" ("department_id_id");
CREATE INDEX "employee_historicalemployeeworkinformation_employee_id_id_aba4dc3f" ON "employee_historicalemployeeworkinformation" ("employee_id_id");
CREATE INDEX "employee_historicalemployeeworkinformation_employee_type_id_id_e9645a32" ON "employee_historicalemployeeworkinformation" ("employee_type_id_id");
CREATE INDEX "employee_historicalemployeeworkinformation_history_relation_id_a688dbcd" ON "employee_historicalemployeeworkinformation" ("history_relation_id");
CREATE INDEX "employee_historicalemployeeworkinformation_history_user_id_1977e79f" ON "employee_historicalemployeeworkinformation" ("history_user_id");
CREATE INDEX "employee_historicalemployeeworkinformation_job_position_id_id_f2def7a4" ON "employee_historicalemployeeworkinformation" ("job_position_id_id");
CREATE INDEX "employee_historicalemployeeworkinformation_job_role_id_id_1ddca879" ON "employee_historicalemployeeworkinformation" ("job_role_id_id");
CREATE INDEX "employee_historicalemployeeworkinformation_reporting_manager_id_id_e9aa69e5" ON "employee_historicalemployeeworkinformation" ("reporting_manager_id_id");
CREATE INDEX "employee_historicalemployeeworkinformation_shift_id_id_8e8623a6" ON "employee_historicalemployeeworkinformation" ("shift_id_id");
CREATE INDEX "employee_historicalemployeeworkinformation_work_type_id_id_bd1d8b2d" ON "employee_historicalemployeeworkinformation" ("work_type_id_id");
CREATE UNIQUE INDEX "employee_historicalemployeeworkinformation_history_tags_historicalemployeeworkinformation_id_audittag_id_ee12d2f8_uniq" ON "employee_historicalemployeeworkinformation_history_tags" ("historicalemployeeworkinformation_id", "audittag_id");
CREATE INDEX "employee_historicalemployeeworkinformation_history_tags_historicalemployeeworkinformation_id_ebf6f81c" ON "employee_historicalemployeeworkinformation_history_tags" ("historicalemployeeworkinformation_id");
CREATE INDEX "employee_historicalemployeeworkinformation_history_tags_audittag_id_b7e25442" ON "employee_historicalemployeeworkinformation_history_tags" ("audittag_id");
CREATE INDEX "employee_historicalbonuspoint_id_fe0a60ae" ON "employee_historicalbonuspoint" ("id");
CREATE INDEX "employee_historicalbonuspoint_history_date_c3debb07" ON "employee_historicalbonuspoint" ("history_date");
CREATE INDEX "employee_historicalbonuspoint_created_by_id_0b61cb56" ON "employee_historicalbonuspoint" ("created_by_id");
CREATE INDEX "employee_historicalbonuspoint_employee_id_id_e83d42fc" ON "employee_historicalbonuspoint" ("employee_id_id");
CREATE INDEX "employee_historicalbonuspoint_history_relation_id_407cc345" ON "employee_historicalbonuspoint" ("history_relation_id");
CREATE INDEX "employee_historicalbonuspoint_history_user_id_a529213d" ON "employee_historicalbonuspoint" ("history_user_id");
CREATE INDEX "employee_historicalbonuspoint_modified_by_id_438cff6e" ON "employee_historicalbonuspoint" ("modified_by_id");
CREATE UNIQUE INDEX "employee_historicalbonuspoint_history_tags_historicalbonuspoint_id_audittag_id_16ee8b1c_uniq" ON "employee_historicalbonuspoint_history_tags" ("historicalbonuspoint_id", "audittag_id");
CREATE INDEX "employee_historicalbonuspoint_history_tags_historicalbonuspoint_id_40f9c15d" ON "employee_historicalbonuspoint_history_tags" ("historicalbonuspoint_id");
CREATE INDEX "employee_historicalbonuspoint_history_tags_audittag_id_d2a36a4e" ON "employee_historicalbonuspoint_history_tags" ("audittag_id");
CREATE INDEX "employee_employeesalaryhistory_employee_id_dd2835c3" ON "employee_employeesalaryhistory" ("employee_id");
CREATE INDEX "employee_employeesalaryhistory_recorded_by_id_2439df6e" ON "employee_employeesalaryhistory" ("recorded_by_id");
CREATE INDEX "employee_employeenote_created_by_id_2ca9060d" ON "employee_employeenote" ("created_by_id");
CREATE INDEX "employee_employeenote_employee_id_id_b9fd028b" ON "employee_employeenote" ("employee_id_id");
CREATE INDEX "employee_employeenote_modified_by_id_eaeca7b4" ON "employee_employeenote" ("modified_by_id");
CREATE INDEX "employee_employeenote_updated_by_id_03758b94" ON "employee_employeenote" ("updated_by_id");
CREATE UNIQUE INDEX "employee_employeenote_note_files_employeenote_id_notefiles_id_73466035_uniq" ON "employee_employeenote_note_files" ("employeenote_id", "notefiles_id");
CREATE INDEX "employee_employeenote_note_files_employeenote_id_68e119b7" ON "employee_employeenote_note_files" ("employeenote_id");
CREATE INDEX "employee_employeenote_note_files_notefiles_id_4fff24b8" ON "employee_employeenote_note_files" ("notefiles_id");
CREATE INDEX "employee_employeegeneralsetting_company_id_id_6cf00960" ON "employee_employeegeneralsetting" ("company_id_id");
CREATE INDEX "employee_employeegeneralsetting_created_by_id_03d5751d" ON "employee_employeegeneralsetting" ("created_by_id");
CREATE INDEX "employee_employeegeneralsetting_modified_by_id_47e9b29b" ON "employee_employeegeneralsetting" ("modified_by_id");
CREATE INDEX "employee_employeebankdetails_created_by_id_eb03d5bb" ON "employee_employeebankdetails" ("created_by_id");
CREATE INDEX "employee_employeebankdetails_modified_by_id_8726ef48" ON "employee_employeebankdetails" ("modified_by_id");
CREATE INDEX "employee_disciplinaryaction_action_id_a7d291be" ON "employee_disciplinaryaction" ("action_id");
CREATE INDEX "employee_disciplinaryaction_created_by_id_7fc312af" ON "employee_disciplinaryaction" ("created_by_id");
CREATE INDEX "employee_disciplinaryaction_modified_by_id_7eaa64e1" ON "employee_disciplinaryaction" ("modified_by_id");
CREATE UNIQUE INDEX "employee_disciplinaryaction_employee_id_disciplinaryaction_id_employee_id_ba1d46a5_uniq" ON "employee_disciplinaryaction_employee_id" ("disciplinaryaction_id", "employee_id");
CREATE INDEX "employee_disciplinaryaction_employee_id_disciplinaryaction_id_e4d129d5" ON "employee_disciplinaryaction_employee_id" ("disciplinaryaction_id");
CREATE INDEX "employee_disciplinaryaction_employee_id_employee_id_c3b19929" ON "employee_disciplinaryaction_employee_id" ("employee_id");
CREATE INDEX "employee_bonuspoint_created_by_id_2ce413ab" ON "employee_bonuspoint" ("created_by_id");
CREATE UNIQUE INDEX "unique_badge_id" ON "employee_employee" ("badge_id") WHERE "badge_id" IS NOT NULL;
CREATE UNIQUE INDEX "employee_employee_employee_first_name_employee_last_name_email_b193a07f_uniq" ON "employee_employee" ("employee_first_name", "employee_last_name", "email");
CREATE INDEX "employee_bonuspoint_modified_by_id_3041354b" ON "employee_bonuspoint" ("modified_by_id");
CREATE UNIQUE INDEX "base_worktyperequestcomment_files_worktyperequestcomment_id_baserequestfile_id_11279360_uniq" ON "base_worktyperequestcomment_files" ("worktyperequestcomment_id", "baserequestfile_id");
CREATE INDEX "base_worktyperequestcomment_files_worktyperequestcomment_id_4f8ea110" ON "base_worktyperequestcomment_files" ("worktyperequestcomment_id");
CREATE INDEX "base_worktyperequestcomment_files_baserequestfile_id_56f0cad3" ON "base_worktyperequestcomment_files" ("baserequestfile_id");
CREATE INDEX "base_worktyperequestcomment_created_by_id_90ecf6c8" ON "base_worktyperequestcomment" ("created_by_id");
CREATE INDEX "base_worktyperequestcomment_employee_id_id_5f0b0e04" ON "base_worktyperequestcomment" ("employee_id_id");
CREATE INDEX "base_worktyperequestcomment_modified_by_id_ac63c417" ON "base_worktyperequestcomment" ("modified_by_id");
CREATE INDEX "base_worktyperequestcomment_request_id_id_802359b4" ON "base_worktyperequestcomment" ("request_id_id");
CREATE INDEX "base_worktyperequest_created_by_id_da875da8" ON "base_worktyperequest" ("created_by_id");
CREATE INDEX "base_worktyperequest_employee_id_id_d747036a" ON "base_worktyperequest" ("employee_id_id");
CREATE INDEX "base_worktyperequest_modified_by_id_cf5dcbb5" ON "base_worktyperequest" ("modified_by_id");
CREATE INDEX "base_worktyperequest_previous_work_type_id_id_0187b88f" ON "base_worktyperequest" ("previous_work_type_id_id");
CREATE INDEX "base_worktyperequest_work_type_id_id_cff6cd3f" ON "base_worktyperequest" ("work_type_id_id");
CREATE UNIQUE INDEX "base_worktype_company_id_worktype_id_company_id_b60b5273_uniq" ON "base_worktype_company_id" ("worktype_id", "company_id");
CREATE INDEX "base_worktype_company_id_worktype_id_29a81247" ON "base_worktype_company_id" ("worktype_id");
CREATE INDEX "base_worktype_company_id_company_id_d2d58a62" ON "base_worktype_company_id" ("company_id");
CREATE INDEX "base_worktype_created_by_id_bebc20f6" ON "base_worktype" ("created_by_id");
CREATE INDEX "base_worktype_modified_by_id_15d81354" ON "base_worktype" ("modified_by_id");
CREATE INDEX "base_tracklatecomeearlyout_created_by_id_998011af" ON "base_tracklatecomeearlyout" ("created_by_id");
CREATE INDEX "base_tracklatecomeearlyout_modified_by_id_ddef4b5e" ON "base_tracklatecomeearlyout" ("modified_by_id");
CREATE INDEX "base_tags_company_id_id_ec9a08f4" ON "base_tags" ("company_id_id");
CREATE INDEX "base_tags_created_by_id_16be081b" ON "base_tags" ("created_by_id");
CREATE INDEX "base_tags_modified_by_id_7e6e7fb2" ON "base_tags" ("modified_by_id");
CREATE UNIQUE INDEX "base_shiftrequestcomment_files_shiftrequestcomment_id_baserequestfile_id_3d088052_uniq" ON "base_shiftrequestcomment_files" ("shiftrequestcomment_id", "baserequestfile_id");
CREATE INDEX "base_shiftrequestcomment_files_shiftrequestcomment_id_ee9b60b3" ON "base_shiftrequestcomment_files" ("shiftrequestcomment_id");
CREATE INDEX "base_shiftrequestcomment_files_baserequestfile_id_7db65962" ON "base_shiftrequestcomment_files" ("baserequestfile_id");
CREATE INDEX "base_shiftrequestcomment_created_by_id_21ea5fad" ON "base_shiftrequestcomment" ("created_by_id");
CREATE INDEX "base_shiftrequestcomment_employee_id_id_48e54a2f" ON "base_shiftrequestcomment" ("employee_id_id");
CREATE INDEX "base_shiftrequestcomment_modified_by_id_18deac02" ON "base_shiftrequestcomment" ("modified_by_id");
CREATE INDEX "base_shiftrequestcomment_request_id_id_bd54b51e" ON "base_shiftrequestcomment" ("request_id_id");
CREATE INDEX "base_shiftrequest_created_by_id_bea31919" ON "base_shiftrequest" ("created_by_id");
CREATE INDEX "base_shiftrequest_employee_id_id_a5fa6bd9" ON "base_shiftrequest" ("employee_id_id");
CREATE INDEX "base_shiftrequest_modified_by_id_3062fe89" ON "base_shiftrequest" ("modified_by_id");
CREATE INDEX "base_shiftrequest_previous_shift_id_id_e5d96887" ON "base_shiftrequest" ("previous_shift_id_id");
CREATE INDEX "base_shiftrequest_reallocate_to_id_48ba7a4e" ON "base_shiftrequest" ("reallocate_to_id");
CREATE INDEX "base_shiftrequest_shift_id_id_c5024f4a" ON "base_shiftrequest" ("shift_id_id");
CREATE INDEX "base_rotatingworktypeassign_created_by_id_f70083f5" ON "base_rotatingworktypeassign" ("created_by_id");
CREATE INDEX "base_rotatingworktypeassign_current_work_type_id_011f4ef1" ON "base_rotatingworktypeassign" ("current_work_type_id");
CREATE INDEX "base_rotatingworktypeassign_employee_id_id_7df12772" ON "base_rotatingworktypeassign" ("employee_id_id");
CREATE INDEX "base_rotatingworktypeassign_modified_by_id_617a9333" ON "base_rotatingworktypeassign" ("modified_by_id");
CREATE INDEX "base_rotatingworktypeassign_next_work_type_id_51672d14" ON "base_rotatingworktypeassign" ("next_work_type_id");
CREATE INDEX "base_rotatingworktypeassign_rotating_work_type_id_id_25af494e" ON "base_rotatingworktypeassign" ("rotating_work_type_id_id");
CREATE INDEX "base_rotatingworktype_created_by_id_3e26c1b7" ON "base_rotatingworktype" ("created_by_id");
CREATE INDEX "base_rotatingworktype_modified_by_id_b561415c" ON "base_rotatingworktype" ("modified_by_id");
CREATE INDEX "base_rotatingworktype_work_type1_id_3db498c9" ON "base_rotatingworktype" ("work_type1_id");
CREATE INDEX "base_rotatingworktype_work_type2_id_c8539552" ON "base_rotatingworktype" ("work_type2_id");
CREATE INDEX "base_rotatingshiftassign_created_by_id_bc0c9b87" ON "base_rotatingshiftassign" ("created_by_id");
CREATE INDEX "base_rotatingshiftassign_current_shift_id_f546b96a" ON "base_rotatingshiftassign" ("current_shift_id");
CREATE INDEX "base_rotatingshiftassign_employee_id_id_2c62486a" ON "base_rotatingshiftassign" ("employee_id_id");
CREATE INDEX "base_rotatingshiftassign_modified_by_id_dbf1e1c7" ON "base_rotatingshiftassign" ("modified_by_id");
CREATE INDEX "base_rotatingshiftassign_next_shift_id_f32a9069" ON "base_rotatingshiftassign" ("next_shift_id");
CREATE INDEX "base_rotatingshiftassign_rotating_shift_id_id_04b24bbb" ON "base_rotatingshiftassign" ("rotating_shift_id_id");
CREATE INDEX "base_rotatingshift_created_by_id_9924e341" ON "base_rotatingshift" ("created_by_id");
CREATE INDEX "base_rotatingshift_modified_by_id_1bf62cb1" ON "base_rotatingshift" ("modified_by_id");
CREATE INDEX "base_rotatingshift_shift1_id_a18464b7" ON "base_rotatingshift" ("shift1_id");
CREATE INDEX "base_rotatingshift_shift2_id_14afc77b" ON "base_rotatingshift" ("shift2_id");
CREATE INDEX "base_penaltyaccounts_created_by_id_d2cde238" ON "base_penaltyaccounts" ("created_by_id");
CREATE INDEX "base_penaltyaccounts_employee_id_id_edbbe2bb" ON "base_penaltyaccounts" ("employee_id_id");
CREATE INDEX "base_penaltyaccounts_late_early_id_id_7a6389d6" ON "base_penaltyaccounts" ("late_early_id_id");
CREATE INDEX "base_penaltyaccounts_leave_request_id_id_015a796d" ON "base_penaltyaccounts" ("leave_request_id_id");
CREATE INDEX "base_penaltyaccounts_leave_type_id_id_9fbfde5e" ON "base_penaltyaccounts" ("leave_type_id_id");
CREATE INDEX "base_penaltyaccounts_modified_by_id_ee3da796" ON "base_penaltyaccounts" ("modified_by_id");
CREATE INDEX "base_multipleapprovalmanagers_condition_id_id_3f6be088" ON "base_multipleapprovalmanagers" ("condition_id_id");
CREATE INDEX "base_multipleapprovalcondition_company_id_id_d33471ce" ON "base_multipleapprovalcondition" ("company_id_id");
CREATE INDEX "base_multipleapprovalcondition_created_by_id_a833e417" ON "base_multipleapprovalcondition" ("created_by_id");
CREATE INDEX "base_multipleapprovalcondition_department_id_0123c893" ON "base_multipleapprovalcondition" ("department_id");
CREATE INDEX "base_multipleapprovalcondition_modified_by_id_0248a986" ON "base_multipleapprovalcondition" ("modified_by_id");
CREATE UNIQUE INDEX "base_jobrole_company_id_jobrole_id_company_id_bec196f7_uniq" ON "base_jobrole_company_id" ("jobrole_id", "company_id");
CREATE INDEX "base_jobrole_company_id_jobrole_id_0a5b1a10" ON "base_jobrole_company_id" ("jobrole_id");
CREATE INDEX "base_jobrole_company_id_company_id_00594b32" ON "base_jobrole_company_id" ("company_id");
CREATE INDEX "base_jobrole_created_by_id_295bd2e6" ON "base_jobrole" ("created_by_id");
CREATE INDEX "base_jobrole_job_position_id_id_e90dff92" ON "base_jobrole" ("job_position_id_id");
CREATE INDEX "base_jobrole_modified_by_id_0560dbfb" ON "base_jobrole" ("modified_by_id");
CREATE UNIQUE INDEX "base_jobposition_company_id_jobposition_id_company_id_3cc4d480_uniq" ON "base_jobposition_company_id" ("jobposition_id", "company_id");
CREATE INDEX "base_jobposition_company_id_jobposition_id_da6fae2f" ON "base_jobposition_company_id" ("jobposition_id");
CREATE INDEX "base_jobposition_company_id_company_id_c1803a10" ON "base_jobposition_company_id" ("company_id");
CREATE INDEX "base_jobposition_created_by_id_924524b6" ON "base_jobposition" ("created_by_id");
CREATE INDEX "base_jobposition_department_id_id_3a4e0e2c" ON "base_jobposition" ("department_id_id");
CREATE INDEX "base_jobposition_modified_by_id_e834fef8" ON "base_jobposition" ("modified_by_id");
CREATE INDEX "base_holidays_company_id_id_dcd70297" ON "base_holidays" ("company_id_id");
CREATE INDEX "base_holidays_created_by_id_0ddc62ec" ON "base_holidays" ("created_by_id");
CREATE INDEX "base_holidays_modified_by_id_a4e26e62" ON "base_holidays" ("modified_by_id");
CREATE INDEX "base_historicalworktyperequest_id_bb0da676" ON "base_historicalworktyperequest" ("id");
CREATE INDEX "base_historicalworktyperequest_history_date_dae1ccdb" ON "base_historicalworktyperequest" ("history_date");
CREATE INDEX "base_historicalworktyperequest_created_by_id_a814446c" ON "base_historicalworktyperequest" ("created_by_id");
CREATE INDEX "base_historicalworktyperequest_employee_id_id_8dcebf94" ON "base_historicalworktyperequest" ("employee_id_id");
CREATE INDEX "base_historicalworktyperequest_history_relation_id_991a4d9d" ON "base_historicalworktyperequest" ("history_relation_id");
CREATE UNIQUE INDEX "base_historicalworktyperequest_history_tags_historicalworktyperequest_id_audittag_id_9872c74a_uniq" ON "base_historicalworktyperequest_history_tags" ("historicalworktyperequest_id", "audittag_id");
CREATE INDEX "base_historicalworktyperequest_history_tags_historicalworktyperequest_id_0e0f338f" ON "base_historicalworktyperequest_history_tags" ("historicalworktyperequest_id");
CREATE INDEX "base_historicalworktyperequest_history_tags_audittag_id_e87dd597" ON "base_historicalworktyperequest_history_tags" ("audittag_id");
CREATE INDEX "base_historicalworktyperequest_history_user_id_93351399" ON "base_historicalworktyperequest" ("history_user_id");
CREATE INDEX "base_historicalworktyperequest_modified_by_id_31a4fe5e" ON "base_historicalworktyperequest" ("modified_by_id");
CREATE INDEX "base_historicalworktyperequest_previous_work_type_id_id_162e234d" ON "base_historicalworktyperequest" ("previous_work_type_id_id");
CREATE INDEX "base_historicalworktyperequest_work_type_id_id_532ab06d" ON "base_historicalworktyperequest" ("work_type_id_id");
CREATE INDEX "base_historicalshiftrequest_id_c79122c2" ON "base_historicalshiftrequest" ("id");
CREATE INDEX "base_historicalshiftrequest_history_date_6a85763e" ON "base_historicalshiftrequest" ("history_date");
CREATE INDEX "base_historicalshiftrequest_created_by_id_a7603569" ON "base_historicalshiftrequest" ("created_by_id");
CREATE INDEX "base_historicalshiftrequest_employee_id_id_aedfeaf3" ON "base_historicalshiftrequest" ("employee_id_id");
CREATE INDEX "base_historicalshiftrequest_history_relation_id_b55281a2" ON "base_historicalshiftrequest" ("history_relation_id");
CREATE UNIQUE INDEX "base_historicalshiftrequest_history_tags_historicalshiftrequest_id_audittag_id_f67984f8_uniq" ON "base_historicalshiftrequest_history_tags" ("historicalshiftrequest_id", "audittag_id");
CREATE INDEX "base_historicalshiftrequest_history_tags_historicalshiftrequest_id_847ea50e" ON "base_historicalshiftrequest_history_tags" ("historicalshiftrequest_id");
CREATE INDEX "base_historicalshiftrequest_history_tags_audittag_id_749e92d3" ON "base_historicalshiftrequest_history_tags" ("audittag_id");
CREATE INDEX "base_historicalshiftrequest_history_user_id_979ea896" ON "base_historicalshiftrequest" ("history_user_id");
CREATE INDEX "base_historicalshiftrequest_modified_by_id_30a46bb9" ON "base_historicalshiftrequest" ("modified_by_id");
CREATE INDEX "base_historicalshiftrequest_previous_shift_id_id_3beec7c0" ON "base_historicalshiftrequest" ("previous_shift_id_id");
CREATE INDEX "base_historicalshiftrequest_reallocate_to_id_b34570a9" ON "base_historicalshiftrequest" ("reallocate_to_id");
CREATE INDEX "base_historicalshiftrequest_shift_id_id_b10c3051" ON "base_historicalshiftrequest" ("shift_id_id");
CREATE INDEX "base_historicalrotatingworktypeassign_id_e461ed90" ON "base_historicalrotatingworktypeassign" ("id");
CREATE INDEX "base_historicalrotatingworktypeassign_history_date_59dde7ca" ON "base_historicalrotatingworktypeassign" ("history_date");
CREATE INDEX "base_historicalrotatingworktypeassign_created_by_id_7361b0d4" ON "base_historicalrotatingworktypeassign" ("created_by_id");
CREATE INDEX "base_historicalrotatingworktypeassign_current_work_type_id_3209eedc" ON "base_historicalrotatingworktypeassign" ("current_work_type_id");
CREATE INDEX "base_historicalrotatingworktypeassign_employee_id_id_ac747bf1" ON "base_historicalrotatingworktypeassign" ("employee_id_id");
CREATE INDEX "base_historicalrotatingworktypeassign_history_relation_id_aa9df2e0" ON "base_historicalrotatingworktypeassign" ("history_relation_id");
CREATE UNIQUE INDEX "base_historicalrotatingworktypeassign_history_tags_historicalrotatingworktypeassign_id_audittag_id_1a15b3ee_uniq" ON "base_historicalrotatingworktypeassign_history_tags" ("historicalrotatingworktypeassign_id", "audittag_id");
CREATE INDEX "base_historicalrotatingworktypeassign_history_tags_historicalrotatingworktypeassign_id_bbc5caa7" ON "base_historicalrotatingworktypeassign_history_tags" ("historicalrotatingworktypeassign_id");
CREATE INDEX "base_historicalrotatingworktypeassign_history_tags_audittag_id_fbfad6f7" ON "base_historicalrotatingworktypeassign_history_tags" ("audittag_id");
CREATE INDEX "base_historicalrotatingworktypeassign_history_user_id_28ca3275" ON "base_historicalrotatingworktypeassign" ("history_user_id");
CREATE INDEX "base_historicalrotatingworktypeassign_modified_by_id_24058264" ON "base_historicalrotatingworktypeassign" ("modified_by_id");
CREATE INDEX "base_historicalrotatingworktypeassign_next_work_type_id_0aafd1c2" ON "base_historicalrotatingworktypeassign" ("next_work_type_id");
CREATE INDEX "base_historicalrotatingworktypeassign_rotating_work_type_id_id_1070e4ee" ON "base_historicalrotatingworktypeassign" ("rotating_work_type_id_id");
CREATE INDEX "base_historicalrotatingshiftassign_id_493b78d7" ON "base_historicalrotatingshiftassign" ("id");
CREATE INDEX "base_historicalrotatingshiftassign_history_date_5e854fb5" ON "base_historicalrotatingshiftassign" ("history_date");
CREATE INDEX "base_historicalrotatingshiftassign_created_by_id_09d2123e" ON "base_historicalrotatingshiftassign" ("created_by_id");
CREATE INDEX "base_historicalrotatingshiftassign_current_shift_id_76c97d97" ON "base_historicalrotatingshiftassign" ("current_shift_id");
CREATE INDEX "base_historicalrotatingshiftassign_employee_id_id_991498a9" ON "base_historicalrotatingshiftassign" ("employee_id_id");
CREATE INDEX "base_historicalrotatingshiftassign_history_relation_id_f86808dd" ON "base_historicalrotatingshiftassign" ("history_relation_id");
CREATE UNIQUE INDEX "base_historicalrotatingshiftassign_history_tags_historicalrotatingshiftassign_id_audittag_id_2dc84adf_uniq" ON "base_historicalrotatingshiftassign_history_tags" ("historicalrotatingshiftassign_id", "audittag_id");
CREATE INDEX "base_historicalrotatingshiftassign_history_tags_historicalrotatingshiftassign_id_98c6b941" ON "base_historicalrotatingshiftassign_history_tags" ("historicalrotatingshiftassign_id");
CREATE INDEX "base_historicalrotatingshiftassign_history_tags_audittag_id_814369ae" ON "base_historicalrotatingshiftassign_history_tags" ("audittag_id");
CREATE INDEX "base_historicalrotatingshiftassign_history_user_id_0e47cd81" ON "base_historicalrotatingshiftassign" ("history_user_id");
CREATE INDEX "base_historicalrotatingshiftassign_modified_by_id_f292aff7" ON "base_historicalrotatingshiftassign" ("modified_by_id");
CREATE INDEX "base_historicalrotatingshiftassign_next_shift_id_369414f0" ON "base_historicalrotatingshiftassign" ("next_shift_id");
CREATE INDEX "base_historicalrotatingshiftassign_rotating_shift_id_id_3c076fe6" ON "base_historicalrotatingshiftassign" ("rotating_shift_id_id");
CREATE INDEX "base_fitsmailtemplate_company_id_id_6c354ab3" ON "base_fitsmailtemplate" ("company_id_id");
CREATE INDEX "base_fitsmailtemplate_created_by_id_ffad5466" ON "base_fitsmailtemplate" ("created_by_id");
CREATE INDEX "base_fitsmailtemplate_modified_by_id_d81bfdc4" ON "base_fitsmailtemplate" ("modified_by_id");
CREATE UNIQUE INDEX "base_employeetype_company_id_employeetype_id_company_id_fb19a24d_uniq" ON "base_employeetype_company_id" ("employeetype_id", "company_id");
CREATE INDEX "base_employeetype_company_id_employeetype_id_0aa55002" ON "base_employeetype_company_id" ("employeetype_id");
CREATE INDEX "base_employeetype_company_id_company_id_fb8006d6" ON "base_employeetype_company_id" ("company_id");
CREATE INDEX "base_employeetype_created_by_id_c6fe9642" ON "base_employeetype" ("created_by_id");
CREATE INDEX "base_employeetype_modified_by_id_cb5ba349" ON "base_employeetype" ("modified_by_id");
CREATE UNIQUE INDEX "base_employeeshiftschedule_company_id_employeeshiftschedule_id_company_id_e88d292f_uniq" ON "base_employeeshiftschedule_company_id" ("employeeshiftschedule_id", "company_id");
CREATE INDEX "base_employeeshiftschedule_company_id_employeeshiftschedule_id_e3a7a8a4" ON "base_employeeshiftschedule_company_id" ("employeeshiftschedule_id");
CREATE INDEX "base_employeeshiftschedule_company_id_company_id_df72d486" ON "base_employeeshiftschedule_company_id" ("company_id");
CREATE INDEX "base_employeeshiftschedule_created_by_id_5dda4d62" ON "base_employeeshiftschedule" ("created_by_id");
CREATE INDEX "base_employeeshiftschedule_day_id_3adbec28" ON "base_employeeshiftschedule" ("day_id");
CREATE INDEX "base_employeeshiftschedule_modified_by_id_4c4cf90a" ON "base_employeeshiftschedule" ("modified_by_id");
CREATE INDEX "base_employeeshiftschedule_shift_id_id_0b0b76ba" ON "base_employeeshiftschedule" ("shift_id_id");
CREATE UNIQUE INDEX "base_employeeshiftday_company_id_employeeshiftday_id_company_id_5986b684_uniq" ON "base_employeeshiftday_company_id" ("employeeshiftday_id", "company_id");
CREATE INDEX "base_employeeshiftday_company_id_employeeshiftday_id_a860dbad" ON "base_employeeshiftday_company_id" ("employeeshiftday_id");
CREATE INDEX "base_employeeshiftday_company_id_company_id_2c4eeb07" ON "base_employeeshiftday_company_id" ("company_id");
CREATE UNIQUE INDEX "base_employeeshift_company_id_employeeshift_id_company_id_f4e05bd4_uniq" ON "base_employeeshift_company_id" ("employeeshift_id", "company_id");
CREATE INDEX "base_employeeshift_company_id_employeeshift_id_196dad8a" ON "base_employeeshift_company_id" ("employeeshift_id");
CREATE INDEX "base_employeeshift_company_id_company_id_93281d0d" ON "base_employeeshift_company_id" ("company_id");
CREATE INDEX "base_employeeshift_created_by_id_dbf8a807" ON "base_employeeshift" ("created_by_id");
CREATE INDEX "base_employeeshift_grace_time_id_id_15569b8e" ON "base_employeeshift" ("grace_time_id_id");
CREATE INDEX "base_employeeshift_modified_by_id_9075134f" ON "base_employeeshift" ("modified_by_id");
CREATE INDEX "base_emaillog_company_id_id_ed759e09" ON "base_emaillog" ("company_id_id");
CREATE INDEX "base_dynamicemailconfiguration_created_by_id_52e9b73b" ON "base_dynamicemailconfiguration" ("created_by_id");
CREATE INDEX "base_dynamicemailconfiguration_modified_by_id_80c89277" ON "base_dynamicemailconfiguration" ("modified_by_id");
CREATE INDEX "base_driverviewed_user_id_78f9f2a5" ON "base_driverviewed" ("user_id");
CREATE UNIQUE INDEX "base_department_company_id_department_id_company_id_ccaa34c4_uniq" ON "base_department_company_id" ("department_id", "company_id");
CREATE INDEX "base_department_company_id_department_id_4aded189" ON "base_department_company_id" ("department_id");
CREATE INDEX "base_department_company_id_company_id_3e26ba00" ON "base_department_company_id" ("company_id");
CREATE INDEX "base_department_created_by_id_86fcb76a" ON "base_department" ("created_by_id");
CREATE INDEX "base_department_modified_by_id_2539afce" ON "base_department" ("modified_by_id");
CREATE INDEX "base_dashboardemployeecharts_created_by_id_7a6c88d1" ON "base_dashboardemployeecharts" ("created_by_id");
CREATE INDEX "base_dashboardemployeecharts_employee_id_af804f1a" ON "base_dashboardemployeecharts" ("employee_id");
CREATE INDEX "base_dashboardemployeecharts_modified_by_id_58988408" ON "base_dashboardemployeecharts" ("modified_by_id");
CREATE INDEX "base_companyleaves_company_id_id_59a8dee0" ON "base_companyleaves" ("company_id_id");
CREATE INDEX "base_companyleaves_created_by_id_c5d3ba1d" ON "base_companyleaves" ("created_by_id");
CREATE INDEX "base_companyleaves_modified_by_id_d98a6c67" ON "base_companyleaves" ("modified_by_id");
CREATE INDEX "base_company_created_by_id_0a5eae8c" ON "base_company" ("created_by_id");
CREATE INDEX "base_company_modified_by_id_7f84ef61" ON "base_company" ("modified_by_id");
CREATE INDEX "base_biometricattendance_company_id_id_79e0cd9e" ON "base_biometricattendance" ("company_id_id");
CREATE INDEX "base_announcementview_announcement_id_30dc6c43" ON "base_announcementview" ("announcement_id");
CREATE INDEX "base_announcementview_user_id_3de12961" ON "base_announcementview" ("user_id");
CREATE INDEX "base_announcementcomment_announcement_id_id_6b41613d" ON "base_announcementcomment" ("announcement_id_id");
CREATE INDEX "base_announcementcomment_created_by_id_4972b6e5" ON "base_announcementcomment" ("created_by_id");
CREATE INDEX "base_announcementcomment_employee_id_id_1aba795e" ON "base_announcementcomment" ("employee_id_id");
CREATE UNIQUE INDEX "base_jobrole_job_position_id_id_job_role_8e2fa70b_uniq" ON "base_jobrole" ("job_position_id_id", "job_role");
CREATE UNIQUE INDEX "base_employeeshiftschedule_shift_id_id_day_id_cb5c24e1_uniq" ON "base_employeeshiftschedule" ("shift_id_id", "day_id");
CREATE UNIQUE INDEX "base_companyleaves_based_on_week_based_on_week_day_ae1142e7_uniq" ON "base_companyleaves" ("based_on_week", "based_on_week_day");
CREATE UNIQUE INDEX "base_company_company_address_0205f120_uniq" ON "base_company" ("company", "address");
CREATE INDEX "base_announcementcomment_modified_by_id_cec87a65" ON "base_announcementcomment" ("modified_by_id");
CREATE UNIQUE INDEX "base_announcement_attachments_announcement_id_attachment_id_d0147299_uniq" ON "base_announcement_attachments" ("announcement_id", "attachment_id");
CREATE INDEX "base_announcement_attachments_announcement_id_28c89de7" ON "base_announcement_attachments" ("announcement_id");
CREATE INDEX "base_announcement_attachments_attachment_id_d426ada6" ON "base_announcement_attachments" ("attachment_id");
CREATE UNIQUE INDEX "base_announcement_company_id_announcement_id_company_id_544233be_uniq" ON "base_announcement_company_id" ("announcement_id", "company_id");
CREATE INDEX "base_announcement_company_id_announcement_id_88c3a5db" ON "base_announcement_company_id" ("announcement_id");
CREATE INDEX "base_announcement_company_id_company_id_3159799c" ON "base_announcement_company_id" ("company_id");
CREATE INDEX "base_announcement_created_by_id_60c3675f" ON "base_announcement" ("created_by_id");
CREATE UNIQUE INDEX "base_announcement_department_announcement_id_department_id_65aebed2_uniq" ON "base_announcement_department" ("announcement_id", "department_id");
CREATE INDEX "base_announcement_department_announcement_id_1fc854a1" ON "base_announcement_department" ("announcement_id");
CREATE INDEX "base_announcement_department_department_id_58667008" ON "base_announcement_department" ("department_id");
CREATE UNIQUE INDEX "base_announcement_employees_announcement_id_employee_id_fd08521b_uniq" ON "base_announcement_employees" ("announcement_id", "employee_id");
CREATE INDEX "base_announcement_employees_announcement_id_6420dc09" ON "base_announcement_employees" ("announcement_id");
CREATE INDEX "base_announcement_employees_employee_id_59b0c73f" ON "base_announcement_employees" ("employee_id");
CREATE UNIQUE INDEX "base_announcement_filtered_employees_announcement_id_employee_id_877070fd_uniq" ON "base_announcement_filtered_employees" ("announcement_id", "employee_id");
CREATE INDEX "base_announcement_filtered_employees_announcement_id_d818df54" ON "base_announcement_filtered_employees" ("announcement_id");
CREATE INDEX "base_announcement_filtered_employees_employee_id_6b6dcc8c" ON "base_announcement_filtered_employees" ("employee_id");
CREATE UNIQUE INDEX "base_announcement_job_position_announcement_id_jobposition_id_3abce70a_uniq" ON "base_announcement_job_position" ("announcement_id", "jobposition_id");
CREATE INDEX "base_announcement_job_position_announcement_id_733faa88" ON "base_announcement_job_position" ("announcement_id");
CREATE INDEX "base_announcement_job_position_jobposition_id_884b606d" ON "base_announcement_job_position" ("jobposition_id");
CREATE INDEX "base_announcement_modified_by_id_bd30f74b" ON "base_announcement" ("modified_by_id");
CREATE UNIQUE INDEX "base_mailboxintegration_user_id_provider_9c08718c_uniq" ON "base_mailboxintegration" ("user_id", "provider");
CREATE INDEX "base_mailboxintegration_user_id_73ee9860" ON "base_mailboxintegration" ("user_id");
CREATE INDEX "recruitment_approvalrule_company_id_id_575157c4" ON "recruitment_approvalrule" ("company_id_id");
CREATE INDEX "recruitment_approvalrule_created_by_id_5e0779c3" ON "recruitment_approvalrule" ("created_by_id");
CREATE INDEX "recruitment_approvalrule_department_id_502a0d2f" ON "recruitment_approvalrule" ("department_id");
CREATE INDEX "recruitment_approvalrule_modified_by_id_96f0af45" ON "recruitment_approvalrule" ("modified_by_id");
CREATE INDEX "recruitment_approvalstep_approver_user_id_6ffed9cf" ON "recruitment_approvalstep" ("approver_user_id");
CREATE INDEX "recruitment_approvalstep_created_by_id_f89c8d09" ON "recruitment_approvalstep" ("created_by_id");
CREATE INDEX "recruitment_approvalstep_modified_by_id_bc82a244" ON "recruitment_approvalstep" ("modified_by_id");
CREATE INDEX "recruitment_approvalstep_rule_id_b049d91b" ON "recruitment_approvalstep" ("rule_id");
CREATE INDEX "recruitment_linkedinaccount_company_id_id_92fc0d4f" ON "recruitment_linkedinaccount" ("company_id_id");
CREATE INDEX "recruitment_linkedinaccount_created_by_id_d4c65311" ON "recruitment_linkedinaccount" ("created_by_id");
CREATE INDEX "recruitment_linkedinaccount_modified_by_id_6f83d73b" ON "recruitment_linkedinaccount" ("modified_by_id");
CREATE UNIQUE INDEX "recruitment_recruitment_open_positions_recruitment_id_jobposition_id_dd7d1b27_uniq" ON "recruitment_recruitment_open_positions" ("recruitment_id", "jobposition_id");
CREATE INDEX "recruitment_recruitment_open_positions_recruitment_id_ecad5263" ON "recruitment_recruitment_open_positions" ("recruitment_id");
CREATE INDEX "recruitment_recruitment_open_positions_jobposition_id_b152ea09" ON "recruitment_recruitment_open_positions" ("jobposition_id");
CREATE UNIQUE INDEX "recruitment_recruitment_recruitment_managers_recruitment_id_employee_id_685bc030_uniq" ON "recruitment_recruitment_recruitment_managers" ("recruitment_id", "employee_id");
CREATE INDEX "recruitment_recruitment_recruitment_managers_recruitment_id_a4c3404a" ON "recruitment_recruitment_recruitment_managers" ("recruitment_id");
CREATE INDEX "recruitment_recruitment_recruitment_managers_employee_id_a7139bba" ON "recruitment_recruitment_recruitment_managers" ("employee_id");
CREATE INDEX "recruitment_skillzone_company_id_id_a5d93a16" ON "recruitment_skillzone" ("company_id_id");
CREATE INDEX "recruitment_skillzone_created_by_id_5d1ea287" ON "recruitment_skillzone" ("created_by_id");
CREATE INDEX "recruitment_skillzone_modified_by_id_e00c979e" ON "recruitment_skillzone" ("modified_by_id");
CREATE UNIQUE INDEX "recruitment_stage_recruitment_id_id_stage_41b4d1c0_uniq" ON "recruitment_stage" ("recruitment_id_id", "stage");
CREATE INDEX "recruitment_stage_created_by_id_93d9a4be" ON "recruitment_stage" ("created_by_id");
CREATE INDEX "recruitment_stage_modified_by_id_96c190ac" ON "recruitment_stage" ("modified_by_id");
CREATE INDEX "recruitment_stage_recruitment_id_id_d63ee32a" ON "recruitment_stage" ("recruitment_id_id");
CREATE UNIQUE INDEX "recruitment_stage_stage_managers_stage_id_employee_id_2ce70681_uniq" ON "recruitment_stage_stage_managers" ("stage_id", "employee_id");
CREATE INDEX "recruitment_stage_stage_managers_stage_id_6d61885b" ON "recruitment_stage_stage_managers" ("stage_id");
CREATE INDEX "recruitment_stage_stage_managers_employee_id_e7e5236a" ON "recruitment_stage_stage_managers" ("employee_id");
CREATE INDEX "recruitment_stagefiles_created_by_id_a3b5b93f" ON "recruitment_stagefiles" ("created_by_id");
CREATE INDEX "recruitment_stagefiles_modified_by_id_cb03fbd9" ON "recruitment_stagefiles" ("modified_by_id");
CREATE INDEX "recruitment_surveytemplate_company_id_id_5bae672b" ON "recruitment_surveytemplate" ("company_id_id");
CREATE INDEX "recruitment_surveytemplate_created_by_id_38b804e2" ON "recruitment_surveytemplate" ("created_by_id");
CREATE INDEX "recruitment_surveytemplate_modified_by_id_6311950c" ON "recruitment_surveytemplate" ("modified_by_id");
CREATE INDEX "recruitment_stagenote_candidate_id_id_d1383dd3" ON "recruitment_stagenote" ("candidate_id_id");
CREATE INDEX "recruitment_stagenote_created_by_id_b3a66e86" ON "recruitment_stagenote" ("created_by_id");
CREATE INDEX "recruitment_stagenote_modified_by_id_c57c24d3" ON "recruitment_stagenote" ("modified_by_id");
CREATE INDEX "recruitment_stagenote_stage_id_id_1a358085" ON "recruitment_stagenote" ("stage_id_id");
CREATE INDEX "recruitment_stagenote_updated_by_id_ed4ff558" ON "recruitment_stagenote" ("updated_by_id");
CREATE UNIQUE INDEX "recruitment_stagenote_stage_files_stagenote_id_stagefiles_id_2f931248_uniq" ON "recruitment_stagenote_stage_files" ("stagenote_id", "stagefiles_id");
CREATE INDEX "recruitment_stagenote_stage_files_stagenote_id_8a0b35b6" ON "recruitment_stagenote_stage_files" ("stagenote_id");
CREATE INDEX "recruitment_stagenote_stage_files_stagefiles_id_c02993d0" ON "recruitment_stagenote_stage_files" ("stagefiles_id");
CREATE INDEX "recruitment_skillzonecandidate_candidate_id_id_ac9e3998" ON "recruitment_skillzonecandidate" ("candidate_id_id");
CREATE INDEX "recruitment_skillzonecandidate_created_by_id_bea62548" ON "recruitment_skillzonecandidate" ("created_by_id");
CREATE INDEX "recruitment_skillzonecandidate_modified_by_id_a1ce64d0" ON "recruitment_skillzonecandidate" ("modified_by_id");
CREATE INDEX "recruitment_skillzonecandidate_skill_zone_id_id_f55c73fc" ON "recruitment_skillzonecandidate" ("skill_zone_id_id");
CREATE INDEX "recruitment_skill_created_by_id_fbf18ae8" ON "recruitment_skill" ("created_by_id");
CREATE INDEX "recruitment_skill_modified_by_id_32de1bd8" ON "recruitment_skill" ("modified_by_id");
CREATE INDEX "recruitment_resume_recruitment_id_id_00eb694d" ON "recruitment_resume" ("recruitment_id_id");
CREATE INDEX "recruitment_rejectreason_company_id_id_710f492e" ON "recruitment_rejectreason" ("company_id_id");
CREATE INDEX "recruitment_rejectreason_created_by_id_f79fee48" ON "recruitment_rejectreason" ("created_by_id");
CREATE INDEX "recruitment_rejectreason_modified_by_id_87e738ae" ON "recruitment_rejectreason" ("modified_by_id");
CREATE INDEX "recruitment_rejectedcandidate_created_by_id_0d2b6a1a" ON "recruitment_rejectedcandidate" ("created_by_id");
CREATE INDEX "recruitment_rejectedcandidate_modified_by_id_9bef5a46" ON "recruitment_rejectedcandidate" ("modified_by_id");
CREATE UNIQUE INDEX "recruitment_rejectedcandidate_reject_reason_id_rejectedcandidate_id_rejectreason_id_c4d4a5a0_uniq" ON "recruitment_rejectedcandidate_reject_reason_id" ("rejectedcandidate_id", "rejectreason_id");
CREATE INDEX "recruitment_rejectedcandidate_reject_reason_id_rejectedcandidate_id_0029fa4e" ON "recruitment_rejectedcandidate_reject_reason_id" ("rejectedcandidate_id");
CREATE INDEX "recruitment_rejectedcandidate_reject_reason_id_rejectreason_id_a5275520" ON "recruitment_rejectedcandidate_reject_reason_id" ("rejectreason_id");
CREATE INDEX "recruitment_recruitmentsurveyanswer_candidate_id_id_e1b0fedb" ON "recruitment_recruitmentsurveyanswer" ("candidate_id_id");
CREATE INDEX "recruitment_recruitmentsurveyanswer_created_by_id_163d2633" ON "recruitment_recruitmentsurveyanswer" ("created_by_id");
CREATE INDEX "recruitment_recruitmentsurveyanswer_job_position_id_id_97a8b004" ON "recruitment_recruitmentsurveyanswer" ("job_position_id_id");
CREATE INDEX "recruitment_recruitmentsurveyanswer_modified_by_id_1bfd6064" ON "recruitment_recruitmentsurveyanswer" ("modified_by_id");
CREATE INDEX "recruitment_recruitmentsurveyanswer_recruitment_id_id_56888b17" ON "recruitment_recruitmentsurveyanswer" ("recruitment_id_id");
CREATE INDEX "recruitment_recruitmentsurvey_created_by_id_1a345de1" ON "recruitment_recruitmentsurvey" ("created_by_id");
CREATE INDEX "recruitment_recruitmentsurvey_modified_by_id_3669d754" ON "recruitment_recruitmentsurvey" ("modified_by_id");
CREATE UNIQUE INDEX "recruitment_recruitmentsurvey_job_position_ids_recruitmentsurvey_id_jobposition_id_06322710_uniq" ON "recruitment_recruitmentsurvey_job_position_ids" ("recruitmentsurvey_id", "jobposition_id");
CREATE INDEX "recruitment_recruitmentsurvey_job_position_ids_recruitmentsurvey_id_75c9ce77" ON "recruitment_recruitmentsurvey_job_position_ids" ("recruitmentsurvey_id");
CREATE INDEX "recruitment_recruitmentsurvey_job_position_ids_jobposition_id_89704641" ON "recruitment_recruitmentsurvey_job_position_ids" ("jobposition_id");
CREATE UNIQUE INDEX "recruitment_recruitmentsurvey_recruitment_ids_recruitmentsurvey_id_recruitment_id_71c5480b_uniq" ON "recruitment_recruitmentsurvey_recruitment_ids" ("recruitmentsurvey_id", "recruitment_id");
CREATE INDEX "recruitment_recruitmentsurvey_recruitment_ids_recruitmentsurvey_id_711bd7eb" ON "recruitment_recruitmentsurvey_recruitment_ids" ("recruitmentsurvey_id");
CREATE INDEX "recruitment_recruitmentsurvey_recruitment_ids_recruitment_id_e1b93c79" ON "recruitment_recruitmentsurvey_recruitment_ids" ("recruitment_id");
CREATE UNIQUE INDEX "recruitment_recruitmentsurvey_template_id_recruitmentsurvey_id_surveytemplate_id_4062fb17_uniq" ON "recruitment_recruitmentsurvey_template_id" ("recruitmentsurvey_id", "surveytemplate_id");
CREATE INDEX "recruitment_recruitmentsurvey_template_id_recruitmentsurvey_id_45834a00" ON "recruitment_recruitmentsurvey_template_id" ("recruitmentsurvey_id");
CREATE INDEX "recruitment_recruitmentsurvey_template_id_surveytemplate_id_54a3a2e8" ON "recruitment_recruitmentsurvey_template_id" ("surveytemplate_id");
CREATE INDEX "recruitment_recruitmentgeneralsetting_company_id_id_32a2ecaf" ON "recruitment_recruitmentgeneralsetting" ("company_id_id");
CREATE INDEX "recruitment_recruitmentgeneralsetting_created_by_id_86a5f511" ON "recruitment_recruitmentgeneralsetting" ("created_by_id");
CREATE INDEX "recruitment_recruitmentgeneralsetting_modified_by_id_1e118681" ON "recruitment_recruitmentgeneralsetting" ("modified_by_id");
CREATE INDEX "recruitment_recruitmentapprovaldelegation_created_by_id_d545932e" ON "recruitment_recruitmentapprovaldelegation" ("created_by_id");
CREATE INDEX "recruitment_recruitmentapprovaldelegation_delegate_id_6086cbc7" ON "recruitment_recruitmentapprovaldelegation" ("delegate_id");
CREATE INDEX "recruitment_recruitmentapprovaldelegation_delegator_id_cd95c61f" ON "recruitment_recruitmentapprovaldelegation" ("delegator_id");
CREATE INDEX "recruitment_recruitmentapprovaldelegation_modified_by_id_dee95532" ON "recruitment_recruitmentapprovaldelegation" ("modified_by_id");
CREATE UNIQUE INDEX "recruitment_recruitment_skills_recruitment_id_skill_id_9d15d780_uniq" ON "recruitment_recruitment_skills" ("recruitment_id", "skill_id");
CREATE INDEX "recruitment_recruitment_skills_recruitment_id_c62ab337" ON "recruitment_recruitment_skills" ("recruitment_id");
CREATE INDEX "recruitment_recruitment_skills_skill_id_659ac48e" ON "recruitment_recruitment_skills" ("skill_id");
CREATE UNIQUE INDEX "recruitment_recruitment_survey_templates_recruitment_id_surveytemplate_id_9d52b3b1_uniq" ON "recruitment_recruitment_survey_templates" ("recruitment_id", "surveytemplate_id");
CREATE INDEX "recruitment_recruitment_survey_templates_recruitment_id_082d049d" ON "recruitment_recruitment_survey_templates" ("recruitment_id");
CREATE INDEX "recruitment_recruitment_survey_templates_surveytemplate_id_536c97fa" ON "recruitment_recruitment_survey_templates" ("surveytemplate_id");
CREATE INDEX "recruitment_questionordering_created_by_id_f8771bb5" ON "recruitment_questionordering" ("created_by_id");
CREATE INDEX "recruitment_questionordering_modified_by_id_0355a7a5" ON "recruitment_questionordering" ("modified_by_id");
CREATE INDEX "recruitment_questionordering_question_id_id_1b4adb1f" ON "recruitment_questionordering" ("question_id_id");
CREATE INDEX "recruitment_questionordering_recruitment_id_id_d35a120f" ON "recruitment_questionordering" ("recruitment_id_id");
CREATE INDEX "recruitment_parsedcvdata_created_by_id_edeb7885" ON "recruitment_parsedcvdata" ("created_by_id");
CREATE INDEX "recruitment_parsedcvdata_modified_by_id_191f2857" ON "recruitment_parsedcvdata" ("modified_by_id");
CREATE INDEX "recruitment_manpowerrequeststatuslog_changed_by_id_b72c3f3d" ON "recruitment_manpowerrequeststatuslog" ("changed_by_id");
CREATE INDEX "recruitment_manpowerrequeststatuslog_request_id_66cf8a9c" ON "recruitment_manpowerrequeststatuslog" ("request_id");
CREATE INDEX "recruitment_manpowerapproval_acted_by_id_285ce998" ON "recruitment_manpowerapproval" ("acted_by_id");
CREATE INDEX "recruitment_manpowerapproval_approver_id_2c190202" ON "recruitment_manpowerapproval" ("approver_id");
CREATE INDEX "recruitment_manpowerapproval_request_id_c35650ee" ON "recruitment_manpowerapproval" ("request_id");
CREATE INDEX "recruitment_manpowerapproval_step_id_a1847b45" ON "recruitment_manpowerapproval" ("step_id");
CREATE UNIQUE INDEX "recruitment_interviewschedule_employee_id_interviewschedule_id_employee_id_34c14bfc_uniq" ON "recruitment_interviewschedule_employee_id" ("interviewschedule_id", "employee_id");
CREATE INDEX "recruitment_interviewschedule_employee_id_interviewschedule_id_60873c42" ON "recruitment_interviewschedule_employee_id" ("interviewschedule_id");
CREATE INDEX "recruitment_interviewschedule_employee_id_employee_id_ccd9a309" ON "recruitment_interviewschedule_employee_id" ("employee_id");
CREATE INDEX "recruitment_historicalrejectedcandidate_id_30e1cc24" ON "recruitment_historicalrejectedcandidate" ("id");
CREATE INDEX "recruitment_historicalrejectedcandidate_history_date_cc4995db" ON "recruitment_historicalrejectedcandidate" ("history_date");
CREATE INDEX "recruitment_historicalrejectedcandidate_candidate_id_id_f590a22d" ON "recruitment_historicalrejectedcandidate" ("candidate_id_id");
CREATE INDEX "recruitment_historicalrejectedcandidate_created_by_id_ad5f645f" ON "recruitment_historicalrejectedcandidate" ("created_by_id");
CREATE INDEX "recruitment_historicalrejectedcandidate_history_relation_id_99021d48" ON "recruitment_historicalrejectedcandidate" ("history_relation_id");
CREATE INDEX "recruitment_historicalrejectedcandidate_history_user_id_ade3345e" ON "recruitment_historicalrejectedcandidate" ("history_user_id");
CREATE INDEX "recruitment_historicalrejectedcandidate_modified_by_id_9c81374f" ON "recruitment_historicalrejectedcandidate" ("modified_by_id");
CREATE UNIQUE INDEX "recruitment_historicalrejectedcandidate_history_tags_historicalrejectedcandidate_id_audittag_id_eb843d90_uniq" ON "recruitment_historicalrejectedcandidate_history_tags" ("historicalrejectedcandidate_id", "audittag_id");
CREATE INDEX "recruitment_historicalrejectedcandidate_history_tags_historicalrejectedcandidate_id_4765b9a4" ON "recruitment_historicalrejectedcandidate_history_tags" ("historicalrejectedcandidate_id");
CREATE INDEX "recruitment_historicalrejectedcandidate_history_tags_audittag_id_c5b10b47" ON "recruitment_historicalrejectedcandidate_history_tags" ("audittag_id");
CREATE UNIQUE INDEX "recruitment_historicalcandidate_history_tags_historicalcandidate_id_audittag_id_8a9083b7_uniq" ON "recruitment_historicalcandidate_history_tags" ("historicalcandidate_id", "audittag_id");
CREATE INDEX "recruitment_historicalcandidate_history_tags_historicalcandidate_id_8b4729d7" ON "recruitment_historicalcandidate_history_tags" ("historicalcandidate_id");
CREATE INDEX "recruitment_historicalcandidate_history_tags_audittag_id_18d229c0" ON "recruitment_historicalcandidate_history_tags" ("audittag_id");
CREATE INDEX "recruitment_cvscreeninglog_candidate_id_9a78fc6f" ON "recruitment_cvscreeninglog" ("candidate_id");
CREATE INDEX "recruitment_cvscreeninglog_recruitment_id_7ce0edfc" ON "recruitment_cvscreeninglog" ("recruitment_id");
CREATE INDEX "recruitment_candidatedocumentrequest_created_by_id_9aff83cf" ON "recruitment_candidatedocumentrequest" ("created_by_id");
CREATE INDEX "recruitment_candidatedocumentrequest_modified_by_id_0e961fa2" ON "recruitment_candidatedocumentrequest" ("modified_by_id");
CREATE UNIQUE INDEX "recruitment_candidatedocumentrequest_candidate_id_candidatedocumentrequest_id_candidate_id_287d5959_uniq" ON "recruitment_candidatedocumentrequest_candidate_id" ("candidatedocumentrequest_id", "candidate_id");
CREATE INDEX "recruitment_candidatedocumentrequest_candidate_id_candidatedocumentrequest_id_58411ac1" ON "recruitment_candidatedocumentrequest_candidate_id" ("candidatedocumentrequest_id");
CREATE INDEX "recruitment_candidatedocumentrequest_candidate_id_candidate_id_aa0c35ed" ON "recruitment_candidatedocumentrequest_candidate_id" ("candidate_id");
CREATE INDEX "recruitment_candidatedocument_candidate_id_id_e3f353e9" ON "recruitment_candidatedocument" ("candidate_id_id");
CREATE INDEX "recruitment_candidatedocument_created_by_id_b99ad3d5" ON "recruitment_candidatedocument" ("created_by_id");
CREATE INDEX "recruitment_candidatedocument_document_request_id_id_f57b6648" ON "recruitment_candidatedocument" ("document_request_id_id");
CREATE INDEX "recruitment_candidatedocument_modified_by_id_bf50b147" ON "recruitment_candidatedocument" ("modified_by_id");
CREATE UNIQUE INDEX "recruitment_evaluationscore_evaluation_id_criteria_id_f2fa4073_uniq" ON "recruitment_evaluationscore" ("evaluation_id", "criteria_id");
CREATE INDEX "recruitment_evaluationscore_criteria_id_a6df35fd" ON "recruitment_evaluationscore" ("criteria_id");
CREATE INDEX "recruitment_evaluationscore_evaluation_id_98d67e39" ON "recruitment_evaluationscore" ("evaluation_id");
CREATE UNIQUE INDEX "recruitment_candidateskillmatch_candidate_id_recruitment_id_dfe487b9_uniq" ON "recruitment_candidateskillmatch" ("candidate_id", "recruitment_id");
CREATE INDEX "recruitment_candidateskillmatch_candidate_id_14d4efd8" ON "recruitment_candidateskillmatch" ("candidate_id");
CREATE INDEX "recruitment_candidateskillmatch_created_by_id_74022123" ON "recruitment_candidateskillmatch" ("created_by_id");
CREATE INDEX "recruitment_candidateskillmatch_modified_by_id_04b54e70" ON "recruitment_candidateskillmatch" ("modified_by_id");
CREATE INDEX "recruitment_candidateskillmatch_recruitment_id_daf32433" ON "recruitment_candidateskillmatch" ("recruitment_id");
CREATE UNIQUE INDEX "recruitment_candidaterating_employee_id_id_candidate_id_id_1e72748e_uniq" ON "recruitment_candidaterating" ("employee_id_id", "candidate_id_id");
CREATE INDEX "recruitment_candidaterating_candidate_id_id_1ede0d1f" ON "recruitment_candidaterating" ("candidate_id_id");
CREATE INDEX "recruitment_candidaterating_created_by_id_0e9a4f8f" ON "recruitment_candidaterating" ("created_by_id");
CREATE INDEX "recruitment_candidaterating_employee_id_id_aa90a5e3" ON "recruitment_candidaterating" ("employee_id_id");
CREATE INDEX "recruitment_candidaterating_modified_by_id_3ab4f1fe" ON "recruitment_candidaterating" ("modified_by_id");
CREATE UNIQUE INDEX "recruitment_candidaterankingscore_candidate_id_recruitment_id_5fb6d14a_uniq" ON "recruitment_candidaterankingscore" ("candidate_id", "recruitment_id");
CREATE INDEX "recruitment_candidaterankingscore_candidate_id_aa04c842" ON "recruitment_candidaterankingscore" ("candidate_id");
CREATE INDEX "recruitment_candidaterankingscore_created_by_id_1d7e0072" ON "recruitment_candidaterankingscore" ("created_by_id");
CREATE INDEX "recruitment_candidaterankingscore_modified_by_id_aae66f7c" ON "recruitment_candidaterankingscore" ("modified_by_id");
CREATE INDEX "recruitment_candidaterankingscore_recruitment_id_2f82c450" ON "recruitment_candidaterankingscore" ("recruitment_id");
CREATE INDEX "recruitment_overall_b544ac_idx" ON "recruitment_candidaterankingscore" ("overall_ranking_score" DESC);
CREATE INDEX "recruitment_ranking_4d7dd0_idx" ON "recruitment_candidaterankingscore" ("ranking_category");
CREATE INDEX "recruitment_interviewround_interview_id_d04677d8" ON "recruitment_interviewround" ("interview_id");
CREATE UNIQUE INDEX "recruitment_candidate_email_recruitment_id_id_2d38a838_uniq" ON "recruitment_candidate" ("email", "recruitment_id_id");
CREATE INDEX "recruitment_candidate_converted_employee_id_id_aea3b89c" ON "recruitment_candidate" ("converted_employee_id_id");
CREATE INDEX "recruitment_candidate_created_by_id_e66d3f8b" ON "recruitment_candidate" ("created_by_id");
CREATE INDEX "recruitment_candidate_job_position_id_id_6d554ae7" ON "recruitment_candidate" ("job_position_id_id");
CREATE INDEX "recruitment_candidate_modified_by_id_ea175e4b" ON "recruitment_candidate" ("modified_by_id");
CREATE INDEX "recruitment_candidate_recruitment_id_id_3276947d" ON "recruitment_candidate" ("recruitment_id_id");
CREATE INDEX "recruitment_candidate_referral_id_0aaff040" ON "recruitment_candidate" ("referral_id");
CREATE INDEX "recruitment_candidate_stage_id_id_95c8b982" ON "recruitment_candidate" ("stage_id_id");
CREATE INDEX "recruitment_recruit_3b5d61_idx" ON "recruitment_candidate" ("recruitment_id_id", "stage_id_id");
CREATE INDEX "recruitment_job_pos_e2cb0c_idx" ON "recruitment_candidate" ("job_position_id_id", "stage_id_id");
CREATE INDEX "recruitment_is_acti_c3edb9_idx" ON "recruitment_candidate" ("is_active", "recruitment_id_id");
CREATE INDEX "recruitment_offer_l_014232_idx" ON "recruitment_candidate" ("offer_letter_status");
CREATE INDEX "recruitment_hired_31c289_idx" ON "recruitment_candidate" ("hired");
CREATE INDEX "recruitment_historicalcandidate_id_754f239c" ON "recruitment_historicalcandidate" ("id");
CREATE INDEX "recruitment_historicalcandidate_history_date_ab29a308" ON "recruitment_historicalcandidate" ("history_date");
CREATE INDEX "recruitment_historicalcandidate_converted_employee_id_id_539259f7" ON "recruitment_historicalcandidate" ("converted_employee_id_id");
CREATE INDEX "recruitment_historicalcandidate_created_by_id_e0d2d80b" ON "recruitment_historicalcandidate" ("created_by_id");
CREATE INDEX "recruitment_historicalcandidate_history_relation_id_04af0535" ON "recruitment_historicalcandidate" ("history_relation_id");
CREATE INDEX "recruitment_historicalcandidate_history_user_id_c56fecb3" ON "recruitment_historicalcandidate" ("history_user_id");
CREATE INDEX "recruitment_historicalcandidate_job_position_id_id_f6fadcbc" ON "recruitment_historicalcandidate" ("job_position_id_id");
CREATE INDEX "recruitment_historicalcandidate_modified_by_id_ffd9a8ac" ON "recruitment_historicalcandidate" ("modified_by_id");
CREATE INDEX "recruitment_historicalcandidate_recruitment_id_id_bf78daa8" ON "recruitment_historicalcandidate" ("recruitment_id_id");
CREATE INDEX "recruitment_historicalcandidate_referral_id_66a55772" ON "recruitment_historicalcandidate" ("referral_id");
CREATE INDEX "recruitment_historicalcandidate_stage_id_id_a5d26037" ON "recruitment_historicalcandidate" ("stage_id_id");
CREATE INDEX "recruitment_interviewschedule_candidate_id_id_bae2223f" ON "recruitment_interviewschedule" ("candidate_id_id");
CREATE INDEX "recruitment_interviewschedule_created_by_id_7ea3824e" ON "recruitment_interviewschedule" ("created_by_id");
CREATE INDEX "recruitment_interviewschedule_modified_by_id_d79442b1" ON "recruitment_interviewschedule" ("modified_by_id");
CREATE INDEX "recruitment_offerletterapproval_approver_id_f98db871" ON "recruitment_offerletterapproval" ("approver_id");
CREATE INDEX "recruitment_offerletterapproval_offer_letter_id_779914bc" ON "recruitment_offerletterapproval" ("offer_letter_id");
CREATE INDEX "recruitment_medicalletter_created_by_id_7873dab0" ON "recruitment_medicalletter" ("created_by_id");
CREATE INDEX "recruitment_medicalletter_hr_signed_by_id_b08a0a36" ON "recruitment_medicalletter" ("hr_signed_by_id");
CREATE INDEX "recruitment_visaletter_created_by_id_9f44b0f1" ON "recruitment_visaletter" ("created_by_id");
CREATE INDEX "recruitment_visaletter_hr_signed_by_id_48d5890c" ON "recruitment_visaletter" ("hr_signed_by_id");
CREATE INDEX "recruitment_offerletterstatuslog_actor_id_2c392fc7" ON "recruitment_offerletterstatuslog" ("actor_id");
CREATE INDEX "recruitment_offerletterstatuslog_offer_letter_id_b7c1d2b9" ON "recruitment_offerletterstatuslog" ("offer_letter_id");
CREATE INDEX "recruitment_medicalletterstatuslog_actor_id_311788f4" ON "recruitment_medicalletterstatuslog" ("actor_id");
CREATE INDEX "recruitment_medicalletterstatuslog_medical_letter_id_c34b9a20" ON "recruitment_medicalletterstatuslog" ("medical_letter_id");
CREATE INDEX "recruitment_visaletterstatuslog_actor_id_4b10d967" ON "recruitment_visaletterstatuslog" ("actor_id");
CREATE INDEX "recruitment_visaletterstatuslog_visa_letter_id_52304b39" ON "recruitment_visaletterstatuslog" ("visa_letter_id");
CREATE INDEX "recruitment_candidate_project_id_id_c2a9d14f" ON "recruitment_candidate" ("project_id_id");
CREATE INDEX "recruitment_historicalcandidate_project_id_id_532383f7" ON "recruitment_historicalcandidate" ("project_id_id");
CREATE INDEX "recruitment_offerapproval_acted_by_id_a061963f" ON "recruitment_offerapproval" ("acted_by_id");
CREATE INDEX "recruitment_offerapproval_approver_id_624390e1" ON "recruitment_offerapproval" ("approver_id");
CREATE INDEX "recruitment_offerapproval_offer_id_1f0c1d78" ON "recruitment_offerapproval" ("offer_id");
CREATE INDEX "recruitment_offerapproval_step_id_8a7f9d55" ON "recruitment_offerapproval" ("step_id");
CREATE INDEX "recruitment_interviewround_interviewer_id_8b1be98e" ON "recruitment_interviewround" ("interviewer_id");
CREATE INDEX "recruitment_manpowerrequest_company_id_id_2c084ad6" ON "recruitment_manpowerrequest" ("company_id_id");
CREATE INDEX "recruitment_manpowerrequest_created_by_id_d44d8f1a" ON "recruitment_manpowerrequest" ("created_by_id");
CREATE INDEX "recruitment_manpowerrequest_department_id_aad15e4d" ON "recruitment_manpowerrequest" ("department_id");
CREATE INDEX "recruitment_manpowerrequest_job_position_id_8cbf2f41" ON "recruitment_manpowerrequest" ("job_position_id");
CREATE INDEX "recruitment_manpowerrequest_modified_by_id_e1830c60" ON "recruitment_manpowerrequest" ("modified_by_id");
CREATE INDEX "recruitment_manpowerrequest_requested_by_id_eb0bea7c" ON "recruitment_manpowerrequest" ("requested_by_id");
CREATE INDEX "recruitment_employmentproposal_candidate_id_95511fe0" ON "recruitment_employmentproposal" ("candidate_id");
CREATE INDEX "recruitment_employmentproposal_created_by_id_e65c583b" ON "recruitment_employmentproposal" ("created_by_id");
CREATE INDEX "recruitment_employmentproposal_interview_id_26c93c49" ON "recruitment_employmentproposal" ("interview_id");
CREATE INDEX "recruitment_employmentproposal_manpower_request_id_55528f4c" ON "recruitment_employmentproposal" ("manpower_request_id");
CREATE INDEX "recruitment_employmentproposal_modified_by_id_2df125e7" ON "recruitment_employmentproposal" ("modified_by_id");
CREATE INDEX "recruitment_employmentproposal_recruitment_id_804adbcb" ON "recruitment_employmentproposal" ("recruitment_id");
CREATE INDEX "recruitment_proposalstatuslog_actor_id_cebcdc87" ON "recruitment_proposalstatuslog" ("actor_id");
CREATE INDEX "recruitment_proposalstatuslog_proposal_id_7e3e006b" ON "recruitment_proposalstatuslog" ("proposal_id");
CREATE INDEX "recruitment_proposalroleassignment_employee_id_3e369fd7" ON "recruitment_proposalroleassignment" ("employee_id");
CREATE INDEX "recruitment_proposalapproval_approver_id_29eb9365" ON "recruitment_proposalapproval" ("approver_id");
CREATE INDEX "recruitment_proposalapproval_proposal_id_0e0640c7" ON "recruitment_proposalapproval" ("proposal_id");
CREATE INDEX "recruitment_offerletter_created_by_id_91f615cf" ON "recruitment_offerletter" ("created_by_id");
CREATE INDEX "recruitment_offerletter_modified_by_id_0e46397c" ON "recruitment_offerletter" ("modified_by_id");
CREATE INDEX "recruitment_jobapplication_recruitment_id_f00e34eb" ON "recruitment_jobapplication" ("recruitment_id");
CREATE INDEX "recruitment_candidateportalupload_offer_id_fbbb00f7" ON "recruitment_candidateportalupload" ("offer_id");
CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");
CREATE INDEX "base_docusignaccount_user_id_298030d4" ON "base_docusignaccount" ("user_id");
CREATE INDEX "base_adobesignaccount_user_id_191f7e83" ON "base_adobesignaccount" ("user_id");
CREATE INDEX "recruitment_recruitmentapproval_approver_id_2c4f7fef" ON "recruitment_recruitmentapproval" ("approver_id");
CREATE INDEX "recruitment_recruitmentapproval_created_by_id_9acd4cdf" ON "recruitment_recruitmentapproval" ("created_by_id");
CREATE INDEX "recruitment_recruitmentapproval_modified_by_id_1a02107d" ON "recruitment_recruitmentapproval" ("modified_by_id");
CREATE INDEX "recruitment_recruitmentapproval_recruitment_id_1cd75752" ON "recruitment_recruitmentapproval" ("recruitment_id");
CREATE INDEX "recruitment_candidatescreeningprofile_screened_by_id_777c4bc0" ON "recruitment_candidatescreeningprofile" ("screened_by_id");
CREATE UNIQUE INDEX "recruitment_interviewround_interviewers_interviewround_id_employee_id_3573b8df_uniq" ON "recruitment_interviewround_interviewers" ("interviewround_id", "employee_id");
CREATE INDEX "recruitment_interviewround_interviewers_interviewround_id_5eecb261" ON "recruitment_interviewround_interviewers" ("interviewround_id");
CREATE INDEX "recruitment_interviewround_interviewers_employee_id_b4ef8b0f" ON "recruitment_interviewround_interviewers" ("employee_id");
CREATE INDEX "recruitment_interviewevaluation_candidate_id_e110261a" ON "recruitment_interviewevaluation" ("candidate_id");
CREATE INDEX "recruitment_interviewevaluation_created_by_id_57c0cbeb" ON "recruitment_interviewevaluation" ("created_by_id");
CREATE INDEX "recruitment_interviewevaluation_interview_id_f90464fa" ON "recruitment_interviewevaluation" ("interview_id");
CREATE INDEX "recruitment_interviewevaluation_modified_by_id_3c465729" ON "recruitment_interviewevaluation" ("modified_by_id");
CREATE INDEX "recruitment_interviewevaluation_panelist_id_974b1822" ON "recruitment_interviewevaluation" ("panelist_id");
CREATE UNIQUE INDEX "recruitment_interviewevaluation_interview_id_panelist_id_round_number_ef57780b_uniq" ON "recruitment_interviewevaluation" ("interview_id", "panelist_id", "round_number");
CREATE INDEX "recruitment_onboardingdocument_hr_acted_by_id_467a3f9f" ON "recruitment_onboardingdocument" ("hr_acted_by_id");
CREATE INDEX "recruitment_onboardingdocument_offer_id_9bbd0891" ON "recruitment_onboardingdocument" ("offer_id");
CREATE UNIQUE INDEX "recruitment_recruitment_job_position_id_id_start_date_company_id_id_5247efe7_uniq" ON "recruitment_recruitment" ("job_position_id_id", "start_date", "company_id_id");
CREATE UNIQUE INDEX "recruitment_recruitment_job_position_id_id_start_date_5785e5bf_uniq" ON "recruitment_recruitment" ("job_position_id_id", "start_date");
CREATE INDEX "recruitment_recruitment_public_slug_38391823" ON "recruitment_recruitment" ("public_slug");
CREATE INDEX "recruitment_recruitment_company_id_id_35c39ac1" ON "recruitment_recruitment" ("company_id_id");
CREATE INDEX "recruitment_recruitment_created_by_id_7487d8a1" ON "recruitment_recruitment" ("created_by_id");
CREATE INDEX "recruitment_recruitment_job_position_id_id_253cfce6" ON "recruitment_recruitment" ("job_position_id_id");
CREATE INDEX "recruitment_recruitment_linkedin_account_id_id_ed119e75" ON "recruitment_recruitment" ("linkedin_account_id_id");
CREATE INDEX "recruitment_recruitment_modified_by_id_3da7024d" ON "recruitment_recruitment" ("modified_by_id");
CREATE INDEX "recruitment_recruitment_raised_by_id_1c3bda64" ON "recruitment_recruitment" ("raised_by_id");
CREATE INDEX "recruitment_bulkrequestline_created_by_id_7086b2a3" ON "recruitment_bulkrequestline" ("created_by_id");
CREATE INDEX "recruitment_bulkrequestline_job_position_id_866636be" ON "recruitment_bulkrequestline" ("job_position_id");
CREATE INDEX "recruitment_bulkrequestline_modified_by_id_4ce5f301" ON "recruitment_bulkrequestline" ("modified_by_id");
CREATE INDEX "recruitment_bulkrequestline_published_recruitment_id_2fb36fb1" ON "recruitment_bulkrequestline" ("published_recruitment_id");
CREATE INDEX "recruitment_bulkrequestline_recruitment_id_5d9d8395" ON "recruitment_bulkrequestline" ("recruitment_id");
CREATE INDEX "accessibility_defaultaccessibility_created_by_id_ff9332a2" ON "accessibility_defaultaccessibility" ("created_by_id");
CREATE INDEX "accessibility_defaultaccessibility_modified_by_id_0b00d519" ON "accessibility_defaultaccessibility" ("modified_by_id");
CREATE UNIQUE INDEX "accessibility_defaultaccessibility_employees_defaultaccessibility_id_employee_id_ce4c5db1_uniq" ON "accessibility_defaultaccessibility_employees" ("defaultaccessibility_id", "employee_id");
CREATE INDEX "accessibility_defaultaccessibility_employees_defaultaccessibility_id_914de53f" ON "accessibility_defaultaccessibility_employees" ("defaultaccessibility_id");
CREATE INDEX "accessibility_defaultaccessibility_employees_employee_id_41ccfcfa" ON "accessibility_defaultaccessibility_employees" ("employee_id");
CREATE INDEX "asset_assetcategory_created_by_id_c99b90f0" ON "asset_assetcategory" ("created_by_id");
CREATE INDEX "asset_assetcategory_modified_by_id_bd92ea34" ON "asset_assetcategory" ("modified_by_id");
CREATE UNIQUE INDEX "asset_assetcategory_company_id_assetcategory_id_company_id_cd9193ab_uniq" ON "asset_assetcategory_company_id" ("assetcategory_id", "company_id");
CREATE INDEX "asset_assetcategory_company_id_assetcategory_id_bbbe3f1d" ON "asset_assetcategory_company_id" ("assetcategory_id");
CREATE INDEX "asset_assetcategory_company_id_company_id_61918643" ON "asset_assetcategory_company_id" ("company_id");
CREATE INDEX "asset_returnimages_created_by_id_593a7b20" ON "asset_returnimages" ("created_by_id");
CREATE INDEX "asset_returnimages_modified_by_id_9dcbbb09" ON "asset_returnimages" ("modified_by_id");
CREATE INDEX "asset_assetrequest_asset_category_id_id_818a04db" ON "asset_assetrequest" ("asset_category_id_id");
CREATE INDEX "asset_assetrequest_created_by_id_142e3757" ON "asset_assetrequest" ("created_by_id");
CREATE INDEX "asset_assetrequest_modified_by_id_ede6ba77" ON "asset_assetrequest" ("modified_by_id");
CREATE INDEX "asset_assetrequest_requested_employee_id_id_51386fae" ON "asset_assetrequest" ("requested_employee_id_id");
CREATE INDEX "asset_assetreport_asset_id_id_f03a6292" ON "asset_assetreport" ("asset_id_id");
CREATE INDEX "asset_assetreport_created_by_id_65f2a72b" ON "asset_assetreport" ("created_by_id");
CREATE INDEX "asset_assetreport_modified_by_id_bd66b671" ON "asset_assetreport" ("modified_by_id");
CREATE INDEX "asset_assetlot_created_by_id_67eb34f5" ON "asset_assetlot" ("created_by_id");
CREATE INDEX "asset_assetlot_modified_by_id_06990993" ON "asset_assetlot" ("modified_by_id");
CREATE UNIQUE INDEX "asset_assetlot_company_id_assetlot_id_company_id_f1b8a3fe_uniq" ON "asset_assetlot_company_id" ("assetlot_id", "company_id");
CREATE INDEX "asset_assetlot_company_id_assetlot_id_3625ff56" ON "asset_assetlot_company_id" ("assetlot_id");
CREATE INDEX "asset_assetlot_company_id_company_id_d784df99" ON "asset_assetlot_company_id" ("company_id");
CREATE INDEX "asset_assetdocuments_asset_report_id_5d283992" ON "asset_assetdocuments" ("asset_report_id");
CREATE INDEX "asset_assetdocuments_created_by_id_ed1eb431" ON "asset_assetdocuments" ("created_by_id");
CREATE INDEX "asset_assetdocuments_modified_by_id_2263fe64" ON "asset_assetdocuments" ("modified_by_id");
CREATE INDEX "asset_assetassignment_asset_id_id_40e00806" ON "asset_assetassignment" ("asset_id_id");
CREATE INDEX "asset_assetassignment_assigned_by_employee_id_id_0f42bd27" ON "asset_assetassignment" ("assigned_by_employee_id_id");
CREATE INDEX "asset_assetassignment_assigned_to_employee_id_id_79cc5925" ON "asset_assetassignment" ("assigned_to_employee_id_id");
CREATE INDEX "asset_assetassignment_created_by_id_d7b91bfa" ON "asset_assetassignment" ("created_by_id");
CREATE INDEX "asset_assetassignment_modified_by_id_f4f5446e" ON "asset_assetassignment" ("modified_by_id");
CREATE UNIQUE INDEX "asset_assetassignment_assign_images_assetassignment_id_returnimages_id_fce3fbc4_uniq" ON "asset_assetassignment_assign_images" ("assetassignment_id", "returnimages_id");
CREATE INDEX "asset_assetassignment_assign_images_assetassignment_id_27ad361a" ON "asset_assetassignment_assign_images" ("assetassignment_id");
CREATE INDEX "asset_assetassignment_assign_images_returnimages_id_cedd3c37" ON "asset_assetassignment_assign_images" ("returnimages_id");
CREATE UNIQUE INDEX "asset_assetassignment_return_images_assetassignment_id_returnimages_id_d09031a0_uniq" ON "asset_assetassignment_return_images" ("assetassignment_id", "returnimages_id");
CREATE INDEX "asset_assetassignment_return_images_assetassignment_id_f72aa0a3" ON "asset_assetassignment_return_images" ("assetassignment_id");
CREATE INDEX "asset_assetassignment_return_images_returnimages_id_b0ee2930" ON "asset_assetassignment_return_images" ("returnimages_id");
CREATE INDEX "asset_asset_asset_category_id_id_2d1f69ff" ON "asset_asset" ("asset_category_id_id");
CREATE INDEX "asset_asset_asset_lot_number_id_id_5b307bec" ON "asset_asset" ("asset_lot_number_id_id");
CREATE INDEX "asset_asset_created_by_id_3ee1315a" ON "asset_asset" ("created_by_id");
CREATE INDEX "asset_asset_modified_by_id_b605c1ff" ON "asset_asset" ("modified_by_id");
CREATE INDEX "asset_asset_owner_id_d2d14c87" ON "asset_asset" ("owner_id");
CREATE INDEX "biometric_biometricdevices_company_id_id_24f01059" ON "biometric_biometricdevices" ("company_id_id");
CREATE INDEX "biometric_biometricdevices_created_by_id_e53d3c02" ON "biometric_biometricdevices" ("created_by_id");
CREATE INDEX "biometric_biometricdevices_modified_by_id_4a3ba0a1" ON "biometric_biometricdevices" ("modified_by_id");
CREATE INDEX "biometric_cosecattendancearguments_device_id_id_d1307353" ON "biometric_cosecattendancearguments" ("device_id_id");
CREATE INDEX "biometric_biometricemployees_device_id_id_a109542b" ON "biometric_biometricemployees" ("device_id_id");
CREATE INDEX "biometric_biometricemployees_employee_id_id_f8a27dce" ON "biometric_biometricemployees" ("employee_id_id");
CREATE INDEX "django_apscheduler_djangojob_next_run_time_2f022619" ON "django_apscheduler_djangojob" ("next_run_time");
CREATE INDEX "django_apscheduler_djangojobexecution_run_time_16edd96b" ON "django_apscheduler_djangojobexecution" ("run_time");
CREATE INDEX "django_apscheduler_djangojobexecution_job_id_daf5090a" ON "django_apscheduler_djangojobexecution" ("job_id");
CREATE INDEX "expenses_expensecategory_company_id_dd19f548" ON "expenses_expensecategory" ("company_id");
CREATE INDEX "expenses_expenseclaim_approved_by_finance_id_f995d061" ON "expenses_expenseclaim" ("approved_by_finance_id");
CREATE INDEX "expenses_expenseclaim_approved_by_manager_id_43eb3782" ON "expenses_expenseclaim" ("approved_by_manager_id");
CREATE INDEX "expenses_expenseclaim_category_id_c86dde9f" ON "expenses_expenseclaim" ("category_id");
CREATE INDEX "expenses_expenseclaim_employee_id_7acbed91" ON "expenses_expenseclaim" ("employee_id");
CREATE INDEX "expenses_expensereport_employee_id_5cede0ee" ON "expenses_expensereport" ("employee_id");
CREATE INDEX "expenses_travelrequest_approved_by_finance_id_abbad67d" ON "expenses_travelrequest" ("approved_by_finance_id");
CREATE INDEX "expenses_travelrequest_approved_by_manager_id_4253b442" ON "expenses_travelrequest" ("approved_by_manager_id");
CREATE INDEX "expenses_travelrequest_employee_id_46bd2ae2" ON "expenses_travelrequest" ("employee_id");
CREATE INDEX "expenses_receipt_expense_claim_id_32ee1cef" ON "expenses_receipt" ("expense_claim_id");
CREATE INDEX "expenses_expensepolicy_category_id_983aac56" ON "expenses_expensepolicy" ("category_id");
CREATE INDEX "expenses_expensepolicy_company_id_71647334" ON "expenses_expensepolicy" ("company_id");
CREATE INDEX "expenses_expenseclaim_travel_request_id_3b02db8c" ON "expenses_expenseclaim" ("travel_request_id");
CREATE UNIQUE INDEX "expenses_perdiemrate_country_city_effective_date_c20b3829_uniq" ON "expenses_perdiemrate" ("country", "city", "effective_date");
CREATE INDEX "expenses_perdiemrate_company_id_f6cf51c9" ON "expenses_perdiemrate" ("company_id");
CREATE UNIQUE INDEX "expenses_expensereportitem_expense_report_id_expense_claim_id_7831701b_uniq" ON "expenses_expensereportitem" ("expense_report_id", "expense_claim_id");
CREATE INDEX "expenses_expensereportitem_expense_claim_id_9fba9e26" ON "expenses_expensereportitem" ("expense_claim_id");
CREATE INDEX "expenses_expensereportitem_expense_report_id_8da9dcb9" ON "expenses_expensereportitem" ("expense_report_id");
CREATE UNIQUE INDEX "unique_company_id_when_not_null_facedetection" ON "facedetection_facedetection" ("company_id_id") WHERE NOT ("company_id_id" IS NULL);
CREATE INDEX "fits_automations_mailautomation_created_by_id_928d9e6c" ON "fits_automations_mailautomation" ("created_by_id");
CREATE INDEX "fits_automations_mailautomation_mail_template_id_362b8176" ON "fits_automations_mailautomation" ("mail_template_id");
CREATE INDEX "fits_automations_mailautomation_modified_by_id_5974c5d0" ON "fits_automations_mailautomation" ("modified_by_id");
CREATE UNIQUE INDEX "fits_automations_mailautomation_also_sent_to_mailautomation_id_employee_id_92882ba0_uniq" ON "fits_automations_mailautomation_also_sent_to" ("mailautomation_id", "employee_id");
CREATE INDEX "fits_automations_mailautomation_also_sent_to_mailautomation_id_a050a285" ON "fits_automations_mailautomation_also_sent_to" ("mailautomation_id");
CREATE INDEX "fits_automations_mailautomation_also_sent_to_employee_id_e043fe08" ON "fits_automations_mailautomation_also_sent_to" ("employee_id");
CREATE UNIQUE INDEX "fits_automations_mailautomation_template_attachments_mailautomation_id_fitsmailtemplate_id_ece5c272_uniq" ON "fits_automations_mailautomation_template_attachments" ("mailautomation_id", "fitsmailtemplate_id");
CREATE INDEX "fits_automations_mailautomation_template_attachments_mailautomation_id_2a70358c" ON "fits_automations_mailautomation_template_attachments" ("mailautomation_id");
CREATE INDEX "fits_automations_mailautomation_template_attachments_fitsmailtemplate_id_aa908e23" ON "fits_automations_mailautomation_template_attachments" ("fitsmailtemplate_id");
CREATE INDEX "fits_documents_documentrequest_created_by_id_b7850a6c" ON "fits_documents_documentrequest" ("created_by_id");
CREATE INDEX "fits_documents_documentrequest_modified_by_id_b5b88513" ON "fits_documents_documentrequest" ("modified_by_id");
CREATE UNIQUE INDEX "fits_documents_documentrequest_employee_id_documentrequest_id_employee_id_62fd1a21_uniq" ON "fits_documents_documentrequest_employee_id" ("documentrequest_id", "employee_id");
CREATE INDEX "fits_documents_documentrequest_employee_id_documentrequest_id_47da59da" ON "fits_documents_documentrequest_employee_id" ("documentrequest_id");
CREATE INDEX "fits_documents_documentrequest_employee_id_employee_id_3f76d1a8" ON "fits_documents_documentrequest_employee_id" ("employee_id");
CREATE INDEX "fits_documents_document_created_by_id_c6b4bb43" ON "fits_documents_document" ("created_by_id");
CREATE INDEX "fits_documents_document_document_request_id_id_e90bfd9f" ON "fits_documents_document" ("document_request_id_id");
CREATE INDEX "fits_documents_document_employee_id_id_da99fd7e" ON "fits_documents_document" ("employee_id_id");
CREATE INDEX "fits_documents_document_modified_by_id_3a2498e5" ON "fits_documents_document" ("modified_by_id");
CREATE INDEX "fits_views_togglecolumn_created_by_id_e5455026" ON "fits_views_togglecolumn" ("created_by_id");
CREATE INDEX "fits_views_togglecolumn_modified_by_id_91a22aa1" ON "fits_views_togglecolumn" ("modified_by_id");
CREATE INDEX "fits_views_togglecolumn_user_id_id_d2c48f12" ON "fits_views_togglecolumn" ("user_id_id");
CREATE INDEX "fits_views_savedfilter_created_by_id_1d561a5a" ON "fits_views_savedfilter" ("created_by_id");
CREATE INDEX "fits_views_savedfilter_modified_by_id_ad0d0dd2" ON "fits_views_savedfilter" ("modified_by_id");
CREATE INDEX "fits_views_activeview_created_by_id_602bd98f" ON "fits_views_activeview" ("created_by_id");
CREATE INDEX "fits_views_activeview_modified_by_id_e79d9422" ON "fits_views_activeview" ("modified_by_id");
CREATE INDEX "fits_views_activetab_created_by_id_55d6662d" ON "fits_views_activetab" ("created_by_id");
CREATE INDEX "fits_views_activetab_modified_by_id_2ee0840c" ON "fits_views_activetab" ("modified_by_id");
CREATE INDEX "fits_views_activegroup_created_by_id_66f31c01" ON "fits_views_activegroup" ("created_by_id");
CREATE INDEX "fits_views_activegroup_modified_by_id_12042c8d" ON "fits_views_activegroup" ("modified_by_id");
CREATE UNIQUE INDEX "unique_company_id_when_not_null_geofencing" ON "geofencing_geofencing" ("company_id_id") WHERE NOT ("company_id_id" IS NULL);
CREATE INDEX "helpdesk_tickettype_company_id_id_79c589c3" ON "helpdesk_tickettype" ("company_id_id");
CREATE INDEX "helpdesk_tickettype_created_by_id_2cec5ee8" ON "helpdesk_tickettype" ("created_by_id");
CREATE INDEX "helpdesk_tickettype_modified_by_id_009acadd" ON "helpdesk_tickettype" ("modified_by_id");
CREATE INDEX "helpdesk_ticket_created_by_id_d27fab9b" ON "helpdesk_ticket" ("created_by_id");
CREATE INDEX "helpdesk_ticket_employee_id_id_8ee8c449" ON "helpdesk_ticket" ("employee_id_id");
CREATE INDEX "helpdesk_ticket_modified_by_id_89892e93" ON "helpdesk_ticket" ("modified_by_id");
CREATE INDEX "helpdesk_ticket_ticket_type_id_f444cfdc" ON "helpdesk_ticket" ("ticket_type_id");
CREATE UNIQUE INDEX "helpdesk_ticket_assigned_to_ticket_id_employee_id_56d49739_uniq" ON "helpdesk_ticket_assigned_to" ("ticket_id", "employee_id");
CREATE INDEX "helpdesk_ticket_assigned_to_ticket_id_63d4ab83" ON "helpdesk_ticket_assigned_to" ("ticket_id");
CREATE INDEX "helpdesk_ticket_assigned_to_employee_id_0bb736bc" ON "helpdesk_ticket_assigned_to" ("employee_id");
CREATE UNIQUE INDEX "helpdesk_ticket_tags_ticket_id_tags_id_154d805a_uniq" ON "helpdesk_ticket_tags" ("ticket_id", "tags_id");
CREATE INDEX "helpdesk_ticket_tags_ticket_id_ee2dfd5d" ON "helpdesk_ticket_tags" ("ticket_id");
CREATE INDEX "helpdesk_ticket_tags_tags_id_9964f9a6" ON "helpdesk_ticket_tags" ("tags_id");
CREATE INDEX "helpdesk_historicalticket_id_4ff77a58" ON "helpdesk_historicalticket" ("id");
CREATE INDEX "helpdesk_historicalticket_history_date_aad09962" ON "helpdesk_historicalticket" ("history_date");
CREATE INDEX "helpdesk_historicalticket_created_by_id_d412ca5c" ON "helpdesk_historicalticket" ("created_by_id");
CREATE INDEX "helpdesk_historicalticket_employee_id_id_897758d9" ON "helpdesk_historicalticket" ("employee_id_id");
CREATE INDEX "helpdesk_historicalticket_history_relation_id_633fb3cb" ON "helpdesk_historicalticket" ("history_relation_id");
CREATE INDEX "helpdesk_historicalticket_history_user_id_fe620449" ON "helpdesk_historicalticket" ("history_user_id");
CREATE INDEX "helpdesk_historicalticket_modified_by_id_1cbc35c2" ON "helpdesk_historicalticket" ("modified_by_id");
CREATE INDEX "helpdesk_historicalticket_ticket_type_id_1732560f" ON "helpdesk_historicalticket" ("ticket_type_id");
CREATE UNIQUE INDEX "helpdesk_historicalticket_history_tags_historicalticket_id_audittag_id_3bae2dc1_uniq" ON "helpdesk_historicalticket_history_tags" ("historicalticket_id", "audittag_id");
CREATE INDEX "helpdesk_historicalticket_history_tags_historicalticket_id_2e6a3113" ON "helpdesk_historicalticket_history_tags" ("historicalticket_id");
CREATE INDEX "helpdesk_historicalticket_history_tags_audittag_id_5fd5a887" ON "helpdesk_historicalticket_history_tags" ("audittag_id");
CREATE INDEX "helpdesk_faqcategory_company_id_id_804d6e9b" ON "helpdesk_faqcategory" ("company_id_id");
CREATE INDEX "helpdesk_faqcategory_created_by_id_551ed468" ON "helpdesk_faqcategory" ("created_by_id");
CREATE INDEX "helpdesk_faqcategory_modified_by_id_39f245eb" ON "helpdesk_faqcategory" ("modified_by_id");
CREATE INDEX "helpdesk_faq_category_id_df198307" ON "helpdesk_faq" ("category_id");
CREATE INDEX "helpdesk_faq_company_id_id_5d618d3f" ON "helpdesk_faq" ("company_id_id");
CREATE INDEX "helpdesk_faq_created_by_id_106edcde" ON "helpdesk_faq" ("created_by_id");
CREATE INDEX "helpdesk_faq_modified_by_id_95f51873" ON "helpdesk_faq" ("modified_by_id");
CREATE UNIQUE INDEX "helpdesk_faq_tags_faq_id_tags_id_d3ca2d3f_uniq" ON "helpdesk_faq_tags" ("faq_id", "tags_id");
CREATE INDEX "helpdesk_faq_tags_faq_id_fb60403b" ON "helpdesk_faq_tags" ("faq_id");
CREATE INDEX "helpdesk_faq_tags_tags_id_8bf80890" ON "helpdesk_faq_tags" ("tags_id");
CREATE INDEX "helpdesk_comment_created_by_id_07b33a87" ON "helpdesk_comment" ("created_by_id");
CREATE INDEX "helpdesk_comment_employee_id_id_09671cb9" ON "helpdesk_comment" ("employee_id_id");
CREATE INDEX "helpdesk_comment_modified_by_id_9cecf91c" ON "helpdesk_comment" ("modified_by_id");
CREATE INDEX "helpdesk_comment_ticket_id_c00da1fb" ON "helpdesk_comment" ("ticket_id");
CREATE INDEX "helpdesk_attachment_comment_id_91b1d9ce" ON "helpdesk_attachment" ("comment_id");
CREATE INDEX "helpdesk_attachment_created_by_id_1c9c4492" ON "helpdesk_attachment" ("created_by_id");
CREATE INDEX "helpdesk_attachment_modified_by_id_92fd74ee" ON "helpdesk_attachment" ("modified_by_id");
CREATE INDEX "helpdesk_attachment_ticket_id_9aa7f330" ON "helpdesk_attachment" ("ticket_id");
CREATE UNIQUE INDEX "helpdesk_departmentmanager_department_id_manager_id_a370e535_uniq" ON "helpdesk_departmentmanager" ("department_id", "manager_id");
CREATE INDEX "helpdesk_departmentmanager_company_id_id_4aa258db" ON "helpdesk_departmentmanager" ("company_id_id");
CREATE INDEX "helpdesk_departmentmanager_created_by_id_429ef9c3" ON "helpdesk_departmentmanager" ("created_by_id");
CREATE INDEX "helpdesk_departmentmanager_department_id_aec70b87" ON "helpdesk_departmentmanager" ("department_id");
CREATE INDEX "helpdesk_departmentmanager_manager_id_826b081d" ON "helpdesk_departmentmanager" ("manager_id");
CREATE INDEX "helpdesk_departmentmanager_modified_by_id_99acea72" ON "helpdesk_departmentmanager" ("modified_by_id");
CREATE UNIQUE INDEX "helpdesk_claimrequest_ticket_id_id_employee_id_id_2307c9fd_uniq" ON "helpdesk_claimrequest" ("ticket_id_id", "employee_id_id");
CREATE INDEX "helpdesk_claimrequest_created_by_id_b6780703" ON "helpdesk_claimrequest" ("created_by_id");
CREATE INDEX "helpdesk_claimrequest_employee_id_id_32aadd98" ON "helpdesk_claimrequest" ("employee_id_id");
CREATE INDEX "helpdesk_claimrequest_modified_by_id_7d52986e" ON "helpdesk_claimrequest" ("modified_by_id");
CREATE INDEX "helpdesk_claimrequest_ticket_id_id_d5306331" ON "helpdesk_claimrequest" ("ticket_id_id");
CREATE INDEX "learning_coursecategory_company_id_c33b5958" ON "learning_coursecategory" ("company_id");
CREATE INDEX "learning_learningplan_created_by_id_eed94443" ON "learning_learningplan" ("created_by_id");
CREATE INDEX "learning_learningplan_employee_id_9fd68a9a" ON "learning_learningplan" ("employee_id");
CREATE INDEX "learning_trainingcourse_category_id_3d834c1c" ON "learning_trainingcourse" ("category_id");
CREATE INDEX "learning_trainingcourse_company_id_70b6a087" ON "learning_trainingcourse" ("company_id");
CREATE INDEX "learning_learningplanitem_course_id_a4ca308b" ON "learning_learningplanitem" ("course_id");
CREATE INDEX "learning_learningplanitem_learning_plan_id_02920116" ON "learning_learningplanitem" ("learning_plan_id");
CREATE INDEX "learning_learningplanitem_skill_id_ed285ea7" ON "learning_learningplanitem" ("skill_id");
CREATE INDEX "learning_employeecertification_certification_id_d3081f4b" ON "learning_employeecertification" ("certification_id");
CREATE INDEX "learning_employeecertification_employee_id_9080f2de" ON "learning_employeecertification" ("employee_id");
CREATE UNIQUE INDEX "learning_trainingbudget_department_id_year_1dbaa008_uniq" ON "learning_trainingbudget" ("department_id", "year");
CREATE INDEX "learning_trainingbudget_department_id_3fe29e53" ON "learning_trainingbudget" ("department_id");
CREATE UNIQUE INDEX "learning_employeeskill_employee_id_skill_id_ba97a44a_uniq" ON "learning_employeeskill" ("employee_id", "skill_id");
CREATE INDEX "learning_employeeskill_employee_id_68823e73" ON "learning_employeeskill" ("employee_id");
CREATE INDEX "learning_employeeskill_skill_id_2e20b2c0" ON "learning_employeeskill" ("skill_id");
CREATE INDEX "learning_employeeskill_verified_by_id_16dff8e1" ON "learning_employeeskill" ("verified_by_id");
CREATE UNIQUE INDEX "learning_courseenrollment_employee_id_course_id_ec019149_uniq" ON "learning_courseenrollment" ("employee_id", "course_id");
CREATE INDEX "learning_courseenrollment_course_id_27446862" ON "learning_courseenrollment" ("course_id");
CREATE INDEX "learning_courseenrollment_employee_id_c1afe822" ON "learning_courseenrollment" ("employee_id");
CREATE INDEX "notifications_notification_unread_cce4be30" ON "notifications_notification" ("unread");
CREATE INDEX "notifications_notification_timestamp_6a797bad" ON "notifications_notification" ("timestamp");
CREATE INDEX "notifications_notification_public_1bc30b1c" ON "notifications_notification" ("public");
CREATE INDEX "notifications_notification_deleted_b32b69e6" ON "notifications_notification" ("deleted");
CREATE INDEX "notifications_notification_emailed_23a5ad81" ON "notifications_notification" ("emailed");
CREATE INDEX "notifications_notification_action_object_content_type_id_7d2b8ee9" ON "notifications_notification" ("action_object_content_type_id");
CREATE INDEX "notifications_notification_actor_content_type_id_0c69d7b7" ON "notifications_notification" ("actor_content_type_id");
CREATE INDEX "notifications_notification_recipient_id_d055f3f0" ON "notifications_notification" ("recipient_id");
CREATE INDEX "notifications_notification_target_content_type_id_ccb24d88" ON "notifications_notification" ("target_content_type_id");
CREATE INDEX "notifications_notification_recipient_id_unread_253aadc9_idx" ON "notifications_notification" ("recipient_id", "unread");
CREATE INDEX "offboarding_offboarding_company_id_id_6eb1a773" ON "offboarding_offboarding" ("company_id_id");
CREATE INDEX "offboarding_offboarding_created_by_id_08c743a3" ON "offboarding_offboarding" ("created_by_id");
CREATE INDEX "offboarding_offboarding_modified_by_id_64c7c296" ON "offboarding_offboarding" ("modified_by_id");
CREATE UNIQUE INDEX "offboarding_offboarding_managers_offboarding_id_employee_id_5c67fd17_uniq" ON "offboarding_offboarding_managers" ("offboarding_id", "employee_id");
CREATE INDEX "offboarding_offboarding_managers_offboarding_id_b2fa84b0" ON "offboarding_offboarding_managers" ("offboarding_id");
CREATE INDEX "offboarding_offboarding_managers_employee_id_bf56f847" ON "offboarding_offboarding_managers" ("employee_id");
CREATE INDEX "offboarding_offboardingemployee_created_by_id_948a3f67" ON "offboarding_offboardingemployee" ("created_by_id");
CREATE INDEX "offboarding_offboardingemployee_modified_by_id_26d15b17" ON "offboarding_offboardingemployee" ("modified_by_id");
CREATE INDEX "offboarding_offboardingstage_created_by_id_59a2c750" ON "offboarding_offboardingstage" ("created_by_id");
CREATE INDEX "offboarding_offboardingstage_modified_by_id_b077ba09" ON "offboarding_offboardingstage" ("modified_by_id");
CREATE INDEX "offboarding_offboardingstage_offboarding_id_id_da071a69" ON "offboarding_offboardingstage" ("offboarding_id_id");
CREATE UNIQUE INDEX "offboarding_offboardingstage_managers_offboardingstage_id_employee_id_4eb651fd_uniq" ON "offboarding_offboardingstage_managers" ("offboardingstage_id", "employee_id");
CREATE INDEX "offboarding_offboardingstage_managers_offboardingstage_id_717c52fc" ON "offboarding_offboardingstage_managers" ("offboardingstage_id");
CREATE INDEX "offboarding_offboardingstage_managers_employee_id_e0f30dcf" ON "offboarding_offboardingstage_managers" ("employee_id");
CREATE INDEX "offboarding_resignationletter_created_by_id_16bb92a5" ON "offboarding_resignationletter" ("created_by_id");
CREATE INDEX "offboarding_resignationletter_employee_id_id_2951a12b" ON "offboarding_resignationletter" ("employee_id_id");
CREATE INDEX "offboarding_resignationletter_modified_by_id_7b981cef" ON "offboarding_resignationletter" ("modified_by_id");
CREATE INDEX "offboarding_resignationletter_offboarding_employee_id_id_a1772643" ON "offboarding_resignationletter" ("offboarding_employee_id_id");
CREATE UNIQUE INDEX "offboarding_offboardingtask_title_stage_id_id_0b02fd34_uniq" ON "offboarding_offboardingtask" ("title", "stage_id_id");
CREATE INDEX "offboarding_offboardingtask_created_by_id_2bf9dfe4" ON "offboarding_offboardingtask" ("created_by_id");
CREATE INDEX "offboarding_offboardingtask_modified_by_id_ca2e6344" ON "offboarding_offboardingtask" ("modified_by_id");
CREATE INDEX "offboarding_offboardingtask_stage_id_id_da56fc56" ON "offboarding_offboardingtask" ("stage_id_id");
CREATE UNIQUE INDEX "offboarding_offboardingtask_managers_offboardingtask_id_employee_id_89c39d5e_uniq" ON "offboarding_offboardingtask_managers" ("offboardingtask_id", "employee_id");
CREATE INDEX "offboarding_offboardingtask_managers_offboardingtask_id_5b5b2ed8" ON "offboarding_offboardingtask_managers" ("offboardingtask_id");
CREATE INDEX "offboarding_offboardingtask_managers_employee_id_7bf8bbd0" ON "offboarding_offboardingtask_managers" ("employee_id");
CREATE INDEX "offboarding_offboardingstagemultiplefile_created_by_id_aeb6efb9" ON "offboarding_offboardingstagemultiplefile" ("created_by_id");
CREATE INDEX "offboarding_offboardingstagemultiplefile_modified_by_id_89479299" ON "offboarding_offboardingstagemultiplefile" ("modified_by_id");
CREATE INDEX "offboarding_offboardingnote_created_by_id_8fe36e26" ON "offboarding_offboardingnote" ("created_by_id");
CREATE INDEX "offboarding_offboardingnote_employee_id_id_91402889" ON "offboarding_offboardingnote" ("employee_id_id");
CREATE INDEX "offboarding_offboardingnote_modified_by_id_6ffcc05b" ON "offboarding_offboardingnote" ("modified_by_id");
CREATE INDEX "offboarding_offboardingnote_note_by_id_f52f0996" ON "offboarding_offboardingnote" ("note_by_id");
CREATE INDEX "offboarding_offboardingnote_stage_id_id_886a66b9" ON "offboarding_offboardingnote" ("stage_id_id");
CREATE UNIQUE INDEX "offboarding_offboardingnote_attachments_offboardingnote_id_offboardingstagemultiplefile_id_07700d00_uniq" ON "offboarding_offboardingnote_attachments" ("offboardingnote_id", "offboardingstagemultiplefile_id");
CREATE INDEX "offboarding_offboardingnote_attachments_offboardingnote_id_8fff891a" ON "offboarding_offboardingnote_attachments" ("offboardingnote_id");
CREATE INDEX "offboarding_offboardingnote_attachments_offboardingstagemultiplefile_id_4ecbaca9" ON "offboarding_offboardingnote_attachments" ("offboardingstagemultiplefile_id");
CREATE INDEX "offboarding_offboardinggeneralsetting_company_id_id_01502765" ON "offboarding_offboardinggeneralsetting" ("company_id_id");
CREATE INDEX "offboarding_offboardinggeneralsetting_created_by_id_5e2e2e96" ON "offboarding_offboardinggeneralsetting" ("created_by_id");
CREATE INDEX "offboarding_offboardinggeneralsetting_modified_by_id_51027037" ON "offboarding_offboardinggeneralsetting" ("modified_by_id");
CREATE INDEX "offboarding_offboardingemployee_stage_id_id_20811923" ON "offboarding_offboardingemployee" ("stage_id_id");
CREATE INDEX "offboarding_historicalemployeetask_id_2c7a8122" ON "offboarding_historicalemployeetask" ("id");
CREATE INDEX "offboarding_historicalemployeetask_history_date_d12662df" ON "offboarding_historicalemployeetask" ("history_date");
CREATE INDEX "offboarding_historicalemployeetask_created_by_id_843707b5" ON "offboarding_historicalemployeetask" ("created_by_id");
CREATE INDEX "offboarding_historicalemployeetask_employee_id_id_3980b221" ON "offboarding_historicalemployeetask" ("employee_id_id");
CREATE INDEX "offboarding_historicalemployeetask_history_relation_id_bba7ad24" ON "offboarding_historicalemployeetask" ("history_relation_id");
CREATE INDEX "offboarding_historicalemployeetask_history_user_id_321703d9" ON "offboarding_historicalemployeetask" ("history_user_id");
CREATE INDEX "offboarding_historicalemployeetask_modified_by_id_397df25d" ON "offboarding_historicalemployeetask" ("modified_by_id");
CREATE INDEX "offboarding_historicalemployeetask_task_id_id_36cec3fd" ON "offboarding_historicalemployeetask" ("task_id_id");
CREATE UNIQUE INDEX "offboarding_historicalemployeetask_history_tags_historicalemployeetask_id_audittag_id_f7313a04_uniq" ON "offboarding_historicalemployeetask_history_tags" ("historicalemployeetask_id", "audittag_id");
CREATE INDEX "offboarding_historicalemployeetask_history_tags_historicalemployeetask_id_2286f22e" ON "offboarding_historicalemployeetask_history_tags" ("historicalemployeetask_id");
CREATE INDEX "offboarding_historicalemployeetask_history_tags_audittag_id_699903e0" ON "offboarding_historicalemployeetask_history_tags" ("audittag_id");
CREATE INDEX "offboarding_exitreason_created_by_id_d6024369" ON "offboarding_exitreason" ("created_by_id");
CREATE INDEX "offboarding_exitreason_modified_by_id_da33e427" ON "offboarding_exitreason" ("modified_by_id");
CREATE INDEX "offboarding_exitreason_offboarding_employee_id_id_d148fca3" ON "offboarding_exitreason" ("offboarding_employee_id_id");
CREATE UNIQUE INDEX "offboarding_exitreason_attachments_exitreason_id_offboardingstagemultiplefile_id_c9d6b1c4_uniq" ON "offboarding_exitreason_attachments" ("exitreason_id", "offboardingstagemultiplefile_id");
CREATE INDEX "offboarding_exitreason_attachments_exitreason_id_187bf31f" ON "offboarding_exitreason_attachments" ("exitreason_id");
CREATE INDEX "offboarding_exitreason_attachments_offboardingstagemultiplefile_id_4bd29ac5" ON "offboarding_exitreason_attachments" ("offboardingstagemultiplefile_id");
CREATE INDEX "offboarding_employeetask_created_by_id_11277aff" ON "offboarding_employeetask" ("created_by_id");
CREATE INDEX "offboarding_employeetask_employee_id_id_d0c791ba" ON "offboarding_employeetask" ("employee_id_id");
CREATE INDEX "offboarding_employeetask_modified_by_id_564e145a" ON "offboarding_employeetask" ("modified_by_id");
CREATE INDEX "offboarding_employeetask_task_id_id_6f5a19ea" ON "offboarding_employeetask" ("task_id_id");
CREATE UNIQUE INDEX "offboarding_employeetask_employee_id_id_task_id_id_bcf65e60_uniq" ON "offboarding_employeetask" ("employee_id_id", "task_id_id");
CREATE INDEX "omani_compliance_omanitaxcalculation_created_by_id_8a7ec310" ON "omani_compliance_omanitaxcalculation" ("created_by_id");
CREATE INDEX "omani_compliance_omanitaxcalculation_employee_id_21cb18bc" ON "omani_compliance_omanitaxcalculation" ("employee_id");
CREATE INDEX "omani_compliance_omanitaxcalculation_modified_by_id_8c100e5e" ON "omani_compliance_omanitaxcalculation" ("modified_by_id");
CREATE INDEX "omani_compliance_omanilabourlawconfig_company_id_f909d3fe" ON "omani_compliance_omanilabourlawconfig" ("company_id");
CREATE INDEX "omani_compliance_omanilabourlawconfig_created_by_id_68ae2d9d" ON "omani_compliance_omanilabourlawconfig" ("created_by_id");
CREATE INDEX "omani_compliance_omanilabourlawconfig_modified_by_id_715b322a" ON "omani_compliance_omanilabourlawconfig" ("modified_by_id");
CREATE INDEX "omani_compliance_omanicomplianceaudit_created_by_id_65b11385" ON "omani_compliance_omanicomplianceaudit" ("created_by_id");
CREATE INDEX "omani_compliance_omanicomplianceaudit_employee_id_2741246a" ON "omani_compliance_omanicomplianceaudit" ("employee_id");
CREATE INDEX "omani_compliance_omanicomplianceaudit_modified_by_id_674564e2" ON "omani_compliance_omanicomplianceaudit" ("modified_by_id");
CREATE INDEX "onboarding_onboardingstage_created_by_id_025988ab" ON "onboarding_onboardingstage" ("created_by_id");
CREATE INDEX "onboarding_onboardingstage_modified_by_id_c77bd25e" ON "onboarding_onboardingstage" ("modified_by_id");
CREATE INDEX "onboarding_onboardingstage_recruitment_id_id_d1f224a7" ON "onboarding_onboardingstage" ("recruitment_id_id");
CREATE UNIQUE INDEX "onboarding_onboardingstage_employee_id_onboardingstage_id_employee_id_37a5f72a_uniq" ON "onboarding_onboardingstage_employee_id" ("onboardingstage_id", "employee_id");
CREATE INDEX "onboarding_onboardingstage_employee_id_onboardingstage_id_5afa9618" ON "onboarding_onboardingstage_employee_id" ("onboardingstage_id");
CREATE INDEX "onboarding_onboardingstage_employee_id_employee_id_a941974c" ON "onboarding_onboardingstage_employee_id" ("employee_id");
CREATE INDEX "onboarding_onboardingtask_created_by_id_cb6060a7" ON "onboarding_onboardingtask" ("created_by_id");
CREATE INDEX "onboarding_onboardingtask_modified_by_id_a4de5468" ON "onboarding_onboardingtask" ("modified_by_id");
CREATE INDEX "onboarding_onboardingtask_stage_id_id_9360b93d" ON "onboarding_onboardingtask" ("stage_id_id");
CREATE UNIQUE INDEX "onboarding_onboardingtask_candidates_onboardingtask_id_candidate_id_40a4bedb_uniq" ON "onboarding_onboardingtask_candidates" ("onboardingtask_id", "candidate_id");
CREATE INDEX "onboarding_onboardingtask_candidates_onboardingtask_id_19de8041" ON "onboarding_onboardingtask_candidates" ("onboardingtask_id");
CREATE INDEX "onboarding_onboardingtask_candidates_candidate_id_a2ad84c1" ON "onboarding_onboardingtask_candidates" ("candidate_id");
CREATE UNIQUE INDEX "onboarding_onboardingtask_employee_id_onboardingtask_id_employee_id_14e249fa_uniq" ON "onboarding_onboardingtask_employee_id" ("onboardingtask_id", "employee_id");
CREATE INDEX "onboarding_onboardingtask_employee_id_onboardingtask_id_55b23efb" ON "onboarding_onboardingtask_employee_id" ("onboardingtask_id");
CREATE INDEX "onboarding_onboardingtask_employee_id_employee_id_6e59c408" ON "onboarding_onboardingtask_employee_id" ("employee_id");
CREATE INDEX "onboarding_onboardingportal_created_by_id_c9caa2a3" ON "onboarding_onboardingportal" ("created_by_id");
CREATE INDEX "onboarding_onboardingportal_modified_by_id_b6ad8806" ON "onboarding_onboardingportal" ("modified_by_id");
CREATE INDEX "onboarding_historicalcandidatetask_id_ec19e8b7" ON "onboarding_historicalcandidatetask" ("id");
CREATE INDEX "onboarding_historicalcandidatetask_history_date_103f1570" ON "onboarding_historicalcandidatetask" ("history_date");
CREATE INDEX "onboarding_historicalcandidatetask_candidate_id_id_01d342a9" ON "onboarding_historicalcandidatetask" ("candidate_id_id");
CREATE INDEX "onboarding_historicalcandidatetask_created_by_id_8885c403" ON "onboarding_historicalcandidatetask" ("created_by_id");
CREATE INDEX "onboarding_historicalcandidatetask_history_relation_id_bcf7462b" ON "onboarding_historicalcandidatetask" ("history_relation_id");
CREATE INDEX "onboarding_historicalcandidatetask_history_user_id_a7e8bdf9" ON "onboarding_historicalcandidatetask" ("history_user_id");
CREATE INDEX "onboarding_historicalcandidatetask_modified_by_id_af88ba97" ON "onboarding_historicalcandidatetask" ("modified_by_id");
CREATE INDEX "onboarding_historicalcandidatetask_onboarding_task_id_id_10accdfd" ON "onboarding_historicalcandidatetask" ("onboarding_task_id_id");
CREATE INDEX "onboarding_historicalcandidatetask_stage_id_id_4fcfd9c0" ON "onboarding_historicalcandidatetask" ("stage_id_id");
CREATE UNIQUE INDEX "onboarding_historicalcandidatetask_history_tags_historicalcandidatetask_id_audittag_id_c5eeb41e_uniq" ON "onboarding_historicalcandidatetask_history_tags" ("historicalcandidatetask_id", "audittag_id");
CREATE INDEX "onboarding_historicalcandidatetask_history_tags_historicalcandidatetask_id_f452cc88" ON "onboarding_historicalcandidatetask_history_tags" ("historicalcandidatetask_id");
CREATE INDEX "onboarding_historicalcandidatetask_history_tags_audittag_id_032900d1" ON "onboarding_historicalcandidatetask_history_tags" ("audittag_id");
CREATE INDEX "onboarding_candidatetask_candidate_id_id_8b0eef2b" ON "onboarding_candidatetask" ("candidate_id_id");
CREATE INDEX "onboarding_candidatetask_created_by_id_e16f0e0b" ON "onboarding_candidatetask" ("created_by_id");
CREATE INDEX "onboarding_candidatetask_modified_by_id_c15234a2" ON "onboarding_candidatetask" ("modified_by_id");
CREATE INDEX "onboarding_candidatetask_onboarding_task_id_id_66c5c3d8" ON "onboarding_candidatetask" ("onboarding_task_id_id");
CREATE INDEX "onboarding_candidatetask_stage_id_id_2bc5e4af" ON "onboarding_candidatetask" ("stage_id_id");
CREATE INDEX "onboarding_candidatestage_created_by_id_778bf760" ON "onboarding_candidatestage" ("created_by_id");
CREATE INDEX "onboarding_candidatestage_modified_by_id_036edc7f" ON "onboarding_candidatestage" ("modified_by_id");
CREATE INDEX "onboarding_candidatestage_onboarding_stage_id_id_477080f9" ON "onboarding_candidatestage" ("onboarding_stage_id_id");
CREATE INDEX "payroll_wps_company_957f0e_idx" ON "payroll_wpsperiodicfile" ("company_id", "status");
CREATE INDEX "payroll_wps_payment_f85e0c_idx" ON "payroll_wpsperiodicfile" ("payment_date");
CREATE UNIQUE INDEX "payroll_wpsperiodicfile_company_id_payroll_period_30ce7ebf_uniq" ON "payroll_wpsperiodicfile" ("company_id", "payroll_period");
CREATE INDEX "payroll_end_employe_cd897e_idx" ON "payroll_endofservicebenefit" ("employee_id", "status");
CREATE INDEX "payroll_end_separat_0d5e95_idx" ON "payroll_endofservicebenefit" ("separation_date");
CREATE UNIQUE INDEX "payroll_contract_employee_id_id_contract_start_date_contract_end_date_eb2a98b3_uniq" ON "payroll_contract" ("employee_id_id", "contract_start_date", "contract_end_date");
CREATE UNIQUE INDEX "payroll_allowance_title_is_taxable_is_condition_based_field_condition_value_is_fixed_amount_based_on_rate_per__6fe89b5e_uniq" ON "payroll_allowance" ("title", "is_taxable", "is_condition_based", "field", "condition", "value", "is_fixed", "amount", "based_on", "rate", "per_attendance_fixed_amount", "shift_id_id", "shift_per_attendance_amount", "amount_per_one_hr", "work_type_id_id", "work_type_per_attendance_amount");
CREATE INDEX "payroll_allowance_company_id_id_5912bfe7" ON "payroll_allowance" ("company_id_id");
CREATE INDEX "payroll_allowance_created_by_id_1c73f9ba" ON "payroll_allowance" ("created_by_id");
CREATE INDEX "payroll_allowance_modified_by_id_947a87fd" ON "payroll_allowance" ("modified_by_id");
CREATE UNIQUE INDEX "payroll_allowance_exclude_employees_allowance_id_employee_id_1c31b105_uniq" ON "payroll_allowance_exclude_employees" ("allowance_id", "employee_id");
CREATE INDEX "payroll_allowance_exclude_employees_allowance_id_71401ad3" ON "payroll_allowance_exclude_employees" ("allowance_id");
CREATE INDEX "payroll_allowance_exclude_employees_employee_id_aa853e81" ON "payroll_allowance_exclude_employees" ("employee_id");
CREATE INDEX "payroll_contract_created_by_id_40695d65" ON "payroll_contract" ("created_by_id");
CREATE INDEX "payroll_contract_department_id_1ae8aa22" ON "payroll_contract" ("department_id");
CREATE INDEX "payroll_contract_employee_id_id_73b14d20" ON "payroll_contract" ("employee_id_id");
CREATE INDEX "payroll_deduction_company_id_id_d5546b8f" ON "payroll_deduction" ("company_id_id");
CREATE INDEX "payroll_deduction_created_by_id_433028c3" ON "payroll_deduction" ("created_by_id");
CREATE INDEX "payroll_deduction_modified_by_id_64c0dc3c" ON "payroll_deduction" ("modified_by_id");
CREATE UNIQUE INDEX "payroll_deduction_exclude_employees_deduction_id_employee_id_dc35ad86_uniq" ON "payroll_deduction_exclude_employees" ("deduction_id", "employee_id");
CREATE INDEX "payroll_deduction_exclude_employees_deduction_id_ab8324ba" ON "payroll_deduction_exclude_employees" ("deduction_id");
CREATE INDEX "payroll_deduction_exclude_employees_employee_id_f349f675" ON "payroll_deduction_exclude_employees" ("employee_id");
CREATE INDEX "payroll_filingstatus_company_id_id_c4edc643" ON "payroll_filingstatus" ("company_id_id");
CREATE INDEX "payroll_filingstatus_created_by_id_1585912b" ON "payroll_filingstatus" ("created_by_id");
CREATE INDEX "payroll_filingstatus_modified_by_id_8ee36489" ON "payroll_filingstatus" ("modified_by_id");
CREATE INDEX "payroll_glaccount_company_id_3f51f14a" ON "payroll_glaccount" ("company_id");
CREATE INDEX "payroll_glaccount_created_by_id_cac39217" ON "payroll_glaccount" ("created_by_id");
CREATE INDEX "payroll_glaccount_modified_by_id_699c10e9" ON "payroll_glaccount" ("modified_by_id");
CREATE INDEX "payroll_reimbursement_allowance_id_id_d4869beb" ON "payroll_reimbursement" ("allowance_id_id");
CREATE INDEX "payroll_reimbursement_approved_by_id_a5077a7b" ON "payroll_reimbursement" ("approved_by_id");
CREATE INDEX "payroll_reimbursement_created_by_id_faf47a67" ON "payroll_reimbursement" ("created_by_id");
CREATE INDEX "payroll_reimbursement_employee_id_id_caaaa190" ON "payroll_reimbursement" ("employee_id_id");
CREATE INDEX "payroll_reimbursement_leave_type_id_id_827b2717" ON "payroll_reimbursement" ("leave_type_id_id");
CREATE INDEX "payroll_reimbursement_modified_by_id_68fe469f" ON "payroll_reimbursement" ("modified_by_id");
CREATE INDEX "payroll_wpsperiodicfile_approved_by_id_e62a2baa" ON "payroll_wpsperiodicfile" ("approved_by_id");
CREATE INDEX "payroll_wpsperiodicfile_company_id_954ae81b" ON "payroll_wpsperiodicfile" ("company_id");
CREATE INDEX "payroll_wpsperiodicfile_created_by_id_77fcf248" ON "payroll_wpsperiodicfile" ("created_by_id");
CREATE INDEX "payroll_wpsperiodicfile_generated_by_id_722769ef" ON "payroll_wpsperiodicfile" ("generated_by_id");
CREATE INDEX "payroll_wpsperiodicfile_modified_by_id_761e3e03" ON "payroll_wpsperiodicfile" ("modified_by_id");
CREATE INDEX "payroll_wpspaymentexception_employee_id_d29825ab" ON "payroll_wpspaymentexception" ("employee_id");
CREATE INDEX "payroll_wpspaymentexception_wps_file_id_6c4a1918" ON "payroll_wpspaymentexception" ("wps_file_id");
CREATE INDEX "payroll_wpsauditlog_user_id_3c321496" ON "payroll_wpsauditlog" ("user_id");
CREATE INDEX "payroll_wpsauditlog_wps_file_id_8aa4cecb" ON "payroll_wpsauditlog" ("wps_file_id");
CREATE INDEX "payroll_workrecord_employee_id_id_193463e2" ON "payroll_workrecord" ("employee_id_id");
CREATE INDEX "payroll_taxbracket_created_by_id_9debe17b" ON "payroll_taxbracket" ("created_by_id");
CREATE INDEX "payroll_taxbracket_filing_status_id_id_44db05c3" ON "payroll_taxbracket" ("filing_status_id_id");
CREATE INDEX "payroll_taxbracket_modified_by_id_975491eb" ON "payroll_taxbracket" ("modified_by_id");
CREATE INDEX "payroll_serviceaward_company_id_83727057" ON "payroll_serviceaward" ("company_id");
CREATE INDEX "payroll_serviceaward_created_by_id_7050bedb" ON "payroll_serviceaward" ("created_by_id");
CREATE INDEX "payroll_serviceaward_employee_id_855b5e5f" ON "payroll_serviceaward" ("employee_id");
CREATE INDEX "payroll_serviceaward_modified_by_id_b5301b8d" ON "payroll_serviceaward" ("modified_by_id");
CREATE INDEX "payroll_salaryrevision_approved_by_id_1a48206b" ON "payroll_salaryrevision" ("approved_by_id");
CREATE INDEX "payroll_salaryrevision_created_by_id_96221e36" ON "payroll_salaryrevision" ("created_by_id");
CREATE INDEX "payroll_salaryrevision_employee_id_id_5e1d6ced" ON "payroll_salaryrevision" ("employee_id_id");
CREATE INDEX "payroll_salaryrevision_modified_by_id_85a1648b" ON "payroll_salaryrevision" ("modified_by_id");
CREATE INDEX "payroll_salaryrevision_submitted_by_id_5e48bd2b" ON "payroll_salaryrevision" ("submitted_by_id");
CREATE INDEX "payroll_reimbursementrequestcomment_created_by_id_bd8f0ee7" ON "payroll_reimbursementrequestcomment" ("created_by_id");
CREATE INDEX "payroll_reimbursementrequestcomment_employee_id_id_b1ed852c" ON "payroll_reimbursementrequestcomment" ("employee_id_id");
CREATE INDEX "payroll_reimbursementrequestcomment_modified_by_id_00a981b9" ON "payroll_reimbursementrequestcomment" ("modified_by_id");
CREATE INDEX "payroll_reimbursementrequestcomment_request_id_id_c5248113" ON "payroll_reimbursementrequestcomment" ("request_id_id");
CREATE UNIQUE INDEX "payroll_reimbursementrequestcomment_files_reimbursementrequestcomment_id_reimbursementfile_id_74c24a9a_uniq" ON "payroll_reimbursementrequestcomment_files" ("reimbursementrequestcomment_id", "reimbursementfile_id");
CREATE INDEX "payroll_reimbursementrequestcomment_files_reimbursementrequestcomment_id_a8d8524d" ON "payroll_reimbursementrequestcomment_files" ("reimbursementrequestcomment_id");
CREATE INDEX "payroll_reimbursementrequestcomment_files_reimbursementfile_id_346a9b2b" ON "payroll_reimbursementrequestcomment_files" ("reimbursementfile_id");
CREATE UNIQUE INDEX "payroll_reimbursement_other_attachments_reimbursement_id_reimbursementmultipleattachment_id_1f69f3e4_uniq" ON "payroll_reimbursement_other_attachments" ("reimbursement_id", "reimbursementmultipleattachment_id");
CREATE INDEX "payroll_reimbursement_other_attachments_reimbursement_id_0a9e691e" ON "payroll_reimbursement_other_attachments" ("reimbursement_id");
CREATE INDEX "payroll_reimbursement_other_attachments_reimbursementmultipleattachment_id_bb6e8ac8" ON "payroll_reimbursement_other_attachments" ("reimbursementmultipleattachment_id");
CREATE INDEX "payroll_payslip_created_by_id_c32cd835" ON "payroll_payslip" ("created_by_id");
CREATE INDEX "payroll_payslip_employee_id_id_f7edc1cc" ON "payroll_payslip" ("employee_id_id");
CREATE INDEX "payroll_payslip_modified_by_id_7fe374ca" ON "payroll_payslip" ("modified_by_id");
CREATE UNIQUE INDEX "payroll_payslip_installment_ids_payslip_id_deduction_id_35cc6afc_uniq" ON "payroll_payslip_installment_ids" ("payslip_id", "deduction_id");
CREATE INDEX "payroll_payslip_installment_ids_payslip_id_6872c6c5" ON "payroll_payslip_installment_ids" ("payslip_id");
CREATE INDEX "payroll_payslip_installment_ids_deduction_id_6ac3f4ed" ON "payroll_payslip_installment_ids" ("deduction_id");
CREATE INDEX "payroll_payrollsettings_company_id_id_d9a945a2" ON "payroll_payrollsettings" ("company_id_id");
CREATE INDEX "payroll_payrollsettings_created_by_id_6b62d3c9" ON "payroll_payrollsettings" ("created_by_id");
CREATE INDEX "payroll_payrollsettings_modified_by_id_6c104a36" ON "payroll_payrollsettings" ("modified_by_id");
CREATE INDEX "payroll_payrollgeneralsetting_company_id_id_e6427694" ON "payroll_payrollgeneralsetting" ("company_id_id");
CREATE INDEX "payroll_loanaccount_allowance_id_id_d01d19ed" ON "payroll_loanaccount" ("allowance_id_id");
CREATE INDEX "payroll_loanaccount_asset_id_id_b1a82434" ON "payroll_loanaccount" ("asset_id_id");
CREATE INDEX "payroll_loanaccount_created_by_id_c44cc155" ON "payroll_loanaccount" ("created_by_id");
CREATE INDEX "payroll_loanaccount_employee_id_id_aa0f9eef" ON "payroll_loanaccount" ("employee_id_id");
CREATE INDEX "payroll_loanaccount_modified_by_id_4b5d7154" ON "payroll_loanaccount" ("modified_by_id");
CREATE UNIQUE INDEX "payroll_loanaccount_deduction_ids_loanaccount_id_deduction_id_c7fe8d5b_uniq" ON "payroll_loanaccount_deduction_ids" ("loanaccount_id", "deduction_id");
CREATE INDEX "payroll_loanaccount_deduction_ids_loanaccount_id_f9fb1ae9" ON "payroll_loanaccount_deduction_ids" ("loanaccount_id");
CREATE INDEX "payroll_loanaccount_deduction_ids_deduction_id_1e7b9cf9" ON "payroll_loanaccount_deduction_ids" ("deduction_id");
CREATE INDEX "payroll_leaveencashment_approved_by_id_5860e068" ON "payroll_leaveencashment" ("approved_by_id");
CREATE INDEX "payroll_leaveencashment_calculated_by_id_462db1bc" ON "payroll_leaveencashment" ("calculated_by_id");
CREATE INDEX "payroll_leaveencashment_created_by_id_f6403aac" ON "payroll_leaveencashment" ("created_by_id");
CREATE INDEX "payroll_leaveencashment_employee_id_id_1a1317db" ON "payroll_leaveencashment" ("employee_id_id");
CREATE INDEX "payroll_leaveencashment_leave_type_id_8662118a" ON "payroll_leaveencashment" ("leave_type_id");
CREATE INDEX "payroll_leaveencashment_modified_by_id_4cfd5808" ON "payroll_leaveencashment" ("modified_by_id");
CREATE INDEX "payroll_icbsconfig_company_id_b61a039c" ON "payroll_icbsconfig" ("company_id");
CREATE INDEX "payroll_icbsconfig_created_by_id_923ee976" ON "payroll_icbsconfig" ("created_by_id");
CREATE INDEX "payroll_icbsconfig_modified_by_id_0d242fcb" ON "payroll_icbsconfig" ("modified_by_id");
CREATE INDEX "payroll_historicalpayslip_id_1a2e9086" ON "payroll_historicalpayslip" ("id");
CREATE INDEX "payroll_historicalpayslip_history_date_8f6a56d5" ON "payroll_historicalpayslip" ("history_date");
CREATE INDEX "payroll_historicalpayslip_created_by_id_3ebd6360" ON "payroll_historicalpayslip" ("created_by_id");
CREATE INDEX "payroll_historicalpayslip_employee_id_id_9d300a3a" ON "payroll_historicalpayslip" ("employee_id_id");
CREATE INDEX "payroll_historicalpayslip_history_relation_id_adad95a7" ON "payroll_historicalpayslip" ("history_relation_id");
CREATE INDEX "payroll_historicalpayslip_history_user_id_5ca3658a" ON "payroll_historicalpayslip" ("history_user_id");
CREATE INDEX "payroll_historicalpayslip_modified_by_id_c721f370" ON "payroll_historicalpayslip" ("modified_by_id");
CREATE UNIQUE INDEX "payroll_historicalpayslip_history_tags_historicalpayslip_id_audittag_id_eba05fac_uniq" ON "payroll_historicalpayslip_history_tags" ("historicalpayslip_id", "audittag_id");
CREATE INDEX "payroll_historicalpayslip_history_tags_historicalpayslip_id_f12f5ff1" ON "payroll_historicalpayslip_history_tags" ("historicalpayslip_id");
CREATE INDEX "payroll_historicalpayslip_history_tags_audittag_id_92f1fdad" ON "payroll_historicalpayslip_history_tags" ("audittag_id");
CREATE INDEX "payroll_historicalcontract_id_3115709d" ON "payroll_historicalcontract" ("id");
CREATE INDEX "payroll_historicalcontract_history_date_ae31cf09" ON "payroll_historicalcontract" ("history_date");
CREATE INDEX "payroll_historicalcontract_created_by_id_6912c2c8" ON "payroll_historicalcontract" ("created_by_id");
CREATE INDEX "payroll_historicalcontract_department_id_ba5c0ea2" ON "payroll_historicalcontract" ("department_id");
CREATE INDEX "payroll_historicalcontract_employee_id_id_ce631d33" ON "payroll_historicalcontract" ("employee_id_id");
CREATE INDEX "payroll_historicalcontract_filing_status_id_b1e556a3" ON "payroll_historicalcontract" ("filing_status_id");
CREATE INDEX "payroll_historicalcontract_history_relation_id_ac42ddee" ON "payroll_historicalcontract" ("history_relation_id");
CREATE INDEX "payroll_historicalcontract_history_user_id_60d308d1" ON "payroll_historicalcontract" ("history_user_id");
CREATE INDEX "payroll_historicalcontract_job_position_id_cff61233" ON "payroll_historicalcontract" ("job_position_id");
CREATE INDEX "payroll_historicalcontract_job_role_id_10059c7f" ON "payroll_historicalcontract" ("job_role_id");
CREATE INDEX "payroll_historicalcontract_modified_by_id_f9a8a752" ON "payroll_historicalcontract" ("modified_by_id");
CREATE INDEX "payroll_historicalcontract_shift_id_23264673" ON "payroll_historicalcontract" ("shift_id");
CREATE INDEX "payroll_historicalcontract_work_type_id_c38ff257" ON "payroll_historicalcontract" ("work_type_id");
CREATE UNIQUE INDEX "payroll_historicalcontract_history_tags_historicalcontract_id_audittag_id_076972f8_uniq" ON "payroll_historicalcontract_history_tags" ("historicalcontract_id", "audittag_id");
CREATE INDEX "payroll_historicalcontract_history_tags_historicalcontract_id_ce51a07a" ON "payroll_historicalcontract_history_tags" ("historicalcontract_id");
CREATE INDEX "payroll_historicalcontract_history_tags_audittag_id_ee2de581" ON "payroll_historicalcontract_history_tags" ("audittag_id");
CREATE INDEX "payroll_glmapping_company_id_7b3a8e20" ON "payroll_glmapping" ("company_id");
CREATE INDEX "payroll_glmapping_created_by_id_5974f178" ON "payroll_glmapping" ("created_by_id");
CREATE INDEX "payroll_glmapping_credit_account_id_2045c14c" ON "payroll_glmapping" ("credit_account_id");
CREATE INDEX "payroll_glmapping_debit_account_id_406de49c" ON "payroll_glmapping" ("debit_account_id");
CREATE INDEX "payroll_glmapping_modified_by_id_b6526c56" ON "payroll_glmapping" ("modified_by_id");
CREATE INDEX "payroll_endofservicebenefit_calculated_by_id_8bc0611e" ON "payroll_endofservicebenefit" ("calculated_by_id");
CREATE INDEX "payroll_endofservicebenefit_company_id_40b09d80" ON "payroll_endofservicebenefit" ("company_id");
CREATE INDEX "payroll_endofservicebenefit_created_by_id_5a801474" ON "payroll_endofservicebenefit" ("created_by_id");
CREATE INDEX "payroll_endofservicebenefit_director_approved_by_id_f97b31de" ON "payroll_endofservicebenefit" ("director_approved_by_id");
CREATE INDEX "payroll_endofservicebenefit_employee_id_7b9369da" ON "payroll_endofservicebenefit" ("employee_id");
CREATE INDEX "payroll_endofservicebenefit_hr_approved_by_id_d7c1cc1b" ON "payroll_endofservicebenefit" ("hr_approved_by_id");
CREATE INDEX "payroll_endofservicebenefit_modified_by_id_d88421d7" ON "payroll_endofservicebenefit" ("modified_by_id");
CREATE UNIQUE INDEX "payroll_deduction_other_conditions_deduction_id_multiplecondition_id_0c6b2fc2_uniq" ON "payroll_deduction_other_conditions" ("deduction_id", "multiplecondition_id");
CREATE INDEX "payroll_deduction_other_conditions_deduction_id_a96fe1ab" ON "payroll_deduction_other_conditions" ("deduction_id");
CREATE INDEX "payroll_deduction_other_conditions_multiplecondition_id_6f0081eb" ON "payroll_deduction_other_conditions" ("multiplecondition_id");
CREATE UNIQUE INDEX "payroll_deduction_specific_employees_deduction_id_employee_id_5a87e86f_uniq" ON "payroll_deduction_specific_employees" ("deduction_id", "employee_id");
CREATE INDEX "payroll_deduction_specific_employees_deduction_id_40142fb7" ON "payroll_deduction_specific_employees" ("deduction_id");
CREATE INDEX "payroll_deduction_specific_employees_employee_id_5a7d19b7" ON "payroll_deduction_specific_employees" ("employee_id");
CREATE INDEX "payroll_contract_filing_status_id_c62f4cc1" ON "payroll_contract" ("filing_status_id");
CREATE INDEX "payroll_contract_job_position_id_fa88268e" ON "payroll_contract" ("job_position_id");
CREATE INDEX "payroll_contract_job_role_id_41e136e0" ON "payroll_contract" ("job_role_id");
CREATE INDEX "payroll_contract_modified_by_id_afd91aba" ON "payroll_contract" ("modified_by_id");
CREATE INDEX "payroll_contract_shift_id_eda88904" ON "payroll_contract" ("shift_id");
CREATE INDEX "payroll_contract_work_type_id_82b0af54" ON "payroll_contract" ("work_type_id");
CREATE UNIQUE INDEX "payroll_allowance_other_conditions_allowance_id_multiplecondition_id_ff137d60_uniq" ON "payroll_allowance_other_conditions" ("allowance_id", "multiplecondition_id");
CREATE INDEX "payroll_allowance_other_conditions_allowance_id_91385ebf" ON "payroll_allowance_other_conditions" ("allowance_id");
CREATE INDEX "payroll_allowance_other_conditions_multiplecondition_id_c6d11700" ON "payroll_allowance_other_conditions" ("multiplecondition_id");
CREATE INDEX "payroll_allowance_shift_id_id_2a990c10" ON "payroll_allowance" ("shift_id_id");
CREATE UNIQUE INDEX "payroll_allowance_specific_employees_allowance_id_employee_id_00a48a04_uniq" ON "payroll_allowance_specific_employees" ("allowance_id", "employee_id");
CREATE INDEX "payroll_allowance_specific_employees_allowance_id_447cbbe6" ON "payroll_allowance_specific_employees" ("allowance_id");
CREATE INDEX "payroll_allowance_specific_employees_employee_id_8537de68" ON "payroll_allowance_specific_employees" ("employee_id");
CREATE INDEX "payroll_allowance_work_type_id_id_da9a0d44" ON "payroll_allowance" ("work_type_id_id");
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('django_migrations',111);
INSERT INTO "sqlite_sequence" VALUES('django_admin_log',0);
INSERT INTO "sqlite_sequence" VALUES('auditlog_logentry',4);
INSERT INTO "sqlite_sequence" VALUES('django_content_type',140);
INSERT INTO "sqlite_sequence" VALUES('auth_permission',570);
INSERT INTO "sqlite_sequence" VALUES('auth_group',0);
INSERT INTO "sqlite_sequence" VALUES('auth_user',2);
INSERT INTO "sqlite_sequence" VALUES('employee_bonuspoint',0);
INSERT INTO "sqlite_sequence" VALUES('base_worktyperequestcomment',0);
INSERT INTO "sqlite_sequence" VALUES('base_worktyperequest',0);
INSERT INTO "sqlite_sequence" VALUES('base_shiftrequestcomment',0);
INSERT INTO "sqlite_sequence" VALUES('base_shiftrequest',0);
INSERT INTO "sqlite_sequence" VALUES('base_rotatingworktypeassign',0);
INSERT INTO "sqlite_sequence" VALUES('base_rotatingworktype',0);
INSERT INTO "sqlite_sequence" VALUES('base_rotatingshiftassign',0);
INSERT INTO "sqlite_sequence" VALUES('base_rotatingshift',0);
INSERT INTO "sqlite_sequence" VALUES('base_notificationsound',0);
INSERT INTO "sqlite_sequence" VALUES('base_multipleapprovalmanagers',0);
INSERT INTO "sqlite_sequence" VALUES('base_multipleapprovalcondition',0);
INSERT INTO "sqlite_sequence" VALUES('base_jobrole',0);
INSERT INTO "sqlite_sequence" VALUES('base_jobposition',0);
INSERT INTO "sqlite_sequence" VALUES('base_hruser',1);
INSERT INTO "sqlite_sequence" VALUES('base_historicalworktyperequest',0);
INSERT INTO "sqlite_sequence" VALUES('base_historicalshiftrequest',0);
INSERT INTO "sqlite_sequence" VALUES('base_historicalrotatingworktypeassign',0);
INSERT INTO "sqlite_sequence" VALUES('base_historicalrotatingshiftassign',0);
INSERT INTO "sqlite_sequence" VALUES('base_employeeshiftschedule',0);
INSERT INTO "sqlite_sequence" VALUES('base_employeeshift',0);
INSERT INTO "sqlite_sequence" VALUES('base_dynamicpagination',0);
INSERT INTO "sqlite_sequence" VALUES('base_dynamicemailconfiguration',0);
INSERT INTO "sqlite_sequence" VALUES('base_driverviewed',0);
INSERT INTO "sqlite_sequence" VALUES('base_dashboardemployeecharts',0);
INSERT INTO "sqlite_sequence" VALUES('base_announcementview',0);
INSERT INTO "sqlite_sequence" VALUES('base_announcementcomment',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_candidate',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_historicalcandidate',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_offerlettertemplate',7);
INSERT INTO "sqlite_sequence" VALUES('recruitment_interviewschedule',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_offerletterapproval',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_medicallettertemplate',2);
INSERT INTO "sqlite_sequence" VALUES('recruitment_visalettertemplate',3);
INSERT INTO "sqlite_sequence" VALUES('recruitment_medicalletter',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_visaletter',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_offerapproval',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_manpowerrequest',0);
INSERT INTO "sqlite_sequence" VALUES('employee_employee',1);
INSERT INTO "sqlite_sequence" VALUES('employee_employeeworkinformation',1);
INSERT INTO "sqlite_sequence" VALUES('recruitment_offerletter',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_jobapplication',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_candidateportalupload',0);
INSERT INTO "sqlite_sequence" VALUES('base_employeeshiftday',7);
INSERT INTO "sqlite_sequence" VALUES('attendance_attendancelatecomeearlyout',0);
INSERT INTO "sqlite_sequence" VALUES('attendance_gracetime',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_recruitmentapproval',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_candidatescreeningprofile',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_interviewevaluation',0);
INSERT INTO "sqlite_sequence" VALUES('recruitment_recruitment',0);
INSERT INTO "sqlite_sequence" VALUES('asset_asset',0);
INSERT INTO "sqlite_sequence" VALUES('django_apscheduler_djangojobexecution',0);
INSERT INTO "sqlite_sequence" VALUES('offboarding_employeetask',0);
INSERT INTO "sqlite_sequence" VALUES('onboarding_candidatetask',0);
COMMIT;
