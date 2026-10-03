"""
views.py

This module contains the view functions for handling HTTP requests and rendering
responses in your application.

Each view function corresponds to a specific URL route and performs the necessary
actions to handle the request, process data, and generate a response.

This module is part of the recruitment project and is intended to
provide the main entry points for interacting with the application's functionality.
"""
import os
from django.conf import settings
import ast
import contextlib
import io
import json
import os
import random
import re
from datetime import date, datetime
from zoneinfo import ZoneInfo
from itertools import chain, groupby
from urllib.parse import parse_qs
from django.http import FileResponse
import fitz  # type: ignore
from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core import serializers
from django.core.cache import cache as CACHE
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Case, F, IntegerField, Max, ProtectedError, Q, When
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from sitewide_chatbot.openrouter import OpenRouterConfig, chat_completion, extract_text

from base.context_processors import check_candidate_self_tracking
from base.countries import country_arr, states
from base.forms import MailTemplateForm
from base.methods import (
    eval_validate,
    export_data,
    generate_pdf,
    get_key_instances,
    sortby,
)
from base.models import EmailLog, FitsMailTemplate, JobPosition, clear_messages
from employee.models import Employee
from employee.views import get_content_type
from fits import settings
from fits.decorators import (
    any_permission_required,
    hx_request_required,
    logger,
    login_required,
    permission_required,
)
from fits.group_by import group_by_queryset
from fits_documents.models import Document
from notifications.signals import notify
from recruitment.auth import CandidateAuthenticationBackend
from recruitment.decorators import (
    candidate_login_required,
    manager_can_enter,
    recruitment_manager_can_enter,
)
from recruitment.filters import (
    CandidateDatabaseFilter,
    CandidateFilter,
    CandidateReGroup,
    InterviewFilter,
    RecruitmentFilter,
    SkillZoneCandFilter,
    SkillZoneFilter,
    StageFilter,
)
from recruitment.forms import (
    AddCandidateForm,
    CandidateCreationForm,
    CandidateDocumentForm,
    CandidateDocumentRejectForm,
    CandidateDocumentRequestForm,
    CandidateDocumentUpdateForm,
    CandidateExportForm,
    RecruitmentCreationForm,
    RejectReasonForm,
    ScheduleInterviewForm,
    SkillsForm,
    SkillZoneCandidateForm,
    SkillZoneCreateForm,
    StageCreationForm,
    StageNoteForm,
    StageNoteUpdateForm,
    ToSkillZoneForm,
)
from recruitment.models import (
    BulkRequestLine,
    Candidate,
    CandidateDocument,
    CandidateRating,
    InterviewSchedule,
    LinkedInAccount,
    Recruitment,
    RecruitmentApproval,
    RecruitmentGeneralSetting,
    RecruitmentSurvey,
    RejectReason,
    Resume,
    Skill,
    SkillZone,
    SkillZoneCandidate,
    Stage,
    StageFiles,
    StageNote,
)
from recruitment.models_interview import InterviewRound
from recruitment.views.linkedin import delete_post, post_recruitment_in_linkedin
from recruitment.views.paginator_qry import paginator_qry
from groq import Groq
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.db import IntegrityError


from django.http import JsonResponse
from recruitment.ai import screen_candidate
from recruitment.utils import build_candidate_text
from django.core.mail import send_mail
from recruitment.models import Recruitment

import threading, time, json

def is_stagemanager(request, stage_id=False):
    """
    This method is used to identify the employee is a stage manager or
    not, if stage_id is passed through args, method will
    check the employee is manager to the corresponding stage, return
    tuple with boolean and all stages that employee is manager.
    if called this method without stage_id args it will return boolean
     with all the stage that the employee is stage manager
    Args:
        request : django http request
        stage_id : stage instance id
    """
    user = request.user
    employee = user.employee_get
    if not stage_id:
        return (
            employee.stage_set.exists() or user.is_superuser,
            employee.stage_set.all(),
        )
    stage_obj = Stage.objects.get(id=stage_id)
    return (
        employee in stage_obj.stage_managers.all()
        or user.is_superuser
        or is_recruitmentmanager(request, rec_id=stage_obj.recruitment_id.id)[0],
        employee.stage_set.all(),
    )


def is_recruitmentmanager(request, rec_id=False):
    """
    This method is used to identify the employee is a recruitment
    manager or not, if rec_id is passed through args, method will
    check the employee is manager to the corresponding recruitment,
    return tuple with boolean and all recruitment that employee is manager.
    if called this method without recruitment args it will return
    boolean with all the recruitment that the employee is recruitment manager
    Args:
        request : django http request
        rec_id : recruitment instance id
    """
    user = request.user
    employee = user.employee_get
    if not rec_id:
        return (
            employee.recruitment_set.exists() or user.is_superuser,
            employee.recruitment_set.all(),
        )
    recruitment_obj = Recruitment.objects.get(id=rec_id)
    return (
        employee in recruitment_obj.recruitment_managers.all() or user.is_superuser,
        employee.recruitment_set.all(),
    )


def get_reporting_chain(employee):
    """Return the senior reporting chain for the given employee."""
    chain = []
    visited = set()
    current = employee
    while current:
        manager = current.get_reporting_manager()
        if not manager or manager.id in visited:
            break
        chain.append(manager)
        visited.add(manager.id)
        current = manager
    return chain


def _grade_based_approvers(recruitment_obj):
    """Approval chain driven by the post grade.

    Grade A/B/C ("Below General Manager") -> [HR Head].
    Grade D/E/F ("Above General Manager") -> [HR Head, CEO].
    Returns None when no valid A-F grade is set so callers fall back to the
    legacy custom/hierarchy routing.
    """
    grade = (getattr(recruitment_obj, "grade", "") or "").strip().upper()
    if grade not in {"A", "B", "C", "D", "E", "F"}:
        return None
    from recruitment.approvals.proposal_engine import _ensure_role_employee
    from recruitment.models_proposal import ROLE_CEO, ROLE_GM_HRA

    chain = [_ensure_role_employee(ROLE_GM_HRA)]  # HR Head
    if grade in {"D", "E", "F"}:
        chain.append(_ensure_role_employee(ROLE_CEO))  # + CEO
    return [emp for emp in chain if emp]


def create_employee_recruitment_approvals(recruitment_obj, approver_ids=None):
    """Create approval steps for an employee-raised recruitment."""
    approvers = []
    raised_by = recruitment_obj.raised_by

    # 0) Grade-based routing wins over everything: a valid A-F grade dictates
    #    HR Head (A-C) or HR Head -> CEO (D-F).
    grade_chain = _grade_based_approvers(recruitment_obj)
    custom = _custom_recruitment_approvers(raised_by)
    if grade_chain:
        approvers = [m for m in grade_chain if m != raised_by]
    # 1) Per-requester custom flow (Fatma / Aisha / Khalid) — used only when no
    #    grade is set, regardless of what was selected in the Managers field.
    elif custom:
        approvers = [m for m in custom if m != raised_by]
    elif approver_ids is not None:
        normalized_ids = [int(i) for i in approver_ids if str(i).strip().isdigit()]
        managers = list(Employee.objects.filter(id__in=normalized_ids))
        managers.sort(key=lambda emp: normalized_ids.index(emp.id))
        for manager in managers:
            if manager != raised_by and manager not in approvers:
                approvers.append(manager)
    elif raised_by:
        # Use reporting hierarchy — never include the requester themselves
        for manager in get_reporting_chain(raised_by):
            if manager != raised_by and manager not in approvers:
                approvers.append(manager)

    approvals = []
    for sequence, approver in enumerate(approvers, start=1):
        approvals.append(
            RecruitmentApproval.objects.create(
                recruitment=recruitment_obj,
                approver=approver,
                sequence=sequence,
            )
        )
    return approvals


def fanout_bulk_recruitment(parent):
    """
    When a bulk recruitment request (``parent.is_bulk``) is fully approved, spawn
    one published campaign per :class:`BulkRequestLine` so external candidates can
    apply per role. Idempotent — lines already linked to a campaign are skipped.

    Returns the list of campaigns created on this call.
    """
    from django.utils.text import slugify
    from uuid import uuid4

    if not getattr(parent, "is_bulk", False):
        return []

    created = []
    for line in parent.bulk_lines.all():
        if line.published_recruitment_id:
            continue  # already fanned out

        base_slug = slugify(line.title) or "position"
        slug = f"{base_slug}-{uuid4().hex[:6]}"

        child = Recruitment(
            title=(line.title or "Position")[:50],
            vacancy=line.vacancy or 1,
            description=parent.description,
            justification=parent.justification,
            start_date=parent.start_date,
            company_id_id=parent.company_id_id,
            employment_type=parent.employment_type,
            location=parent.location,
            grade=parent.grade,
            raised_by=parent.raised_by,
            raised_from_employee=True,
            approval_status="approved",
            is_published=True,
            is_public=True,
            public_slug=slug,
        )
        if line.job_position_id:
            child.job_position_id_id = line.job_position_id
        child.save()

        # Seed the initial pipeline stage so applicants land somewhere.
        Stage.objects.get_or_create(
            recruitment_id=child,
            stage_type="initial",
            defaults={"stage": "Applied", "sequence": 0},
        )

        line.published_recruitment = child
        line.save(update_fields=["published_recruitment"])
        created.append(child)

    return created


def _custom_recruitment_approvers(raised_by):
    """If raised_by is one of the demo requesters, return the fixed approval chain."""
    if not raised_by:
        return []
    from recruitment.approvals.engine import (
        CUSTOM_REQUESTER_FLOWS,
        _resolve_employee_by_email,
        _resolve_shared_hr,
    )
    user = getattr(raised_by, "employee_user_id", None)
    email = (getattr(user, "email", "") or raised_by.email or "").lower()
    if email not in CUSTOM_REQUESTER_FLOWS:
        return []
    chain, seen = [], set()
    # When resolving the shared HR, exclude every named email in this flow + the
    # CFO/CEO approver-only accounts (they hold view_offerletter but they are
    # NOT the HR step).
    others = {e for e in CUSTOM_REQUESTER_FLOWS[email] if e != "__HR__"}
    others.update({"cfo@fits.com", "ceo@fits.com"})
    for entry in CUSTOM_REQUESTER_FLOWS[email]:
        if entry == email:
            continue  # never put requester in own approval chain
        emp = _resolve_shared_hr(exclude_emails=others) if entry == "__HR__" else _resolve_employee_by_email(entry)
        if emp and emp.id not in seen:
            seen.add(emp.id)
            chain.append(emp)
    return chain


def repair_employee_recruitment_approvals(recruitment_obj):
    """Repair missing or partial employee-raised approval chains."""
    if not recruitment_obj.raised_from_employee:
        return

    # Determine the expected approver chain — grade routing wins, mirroring
    # create_employee_recruitment_approvals().
    expected = _grade_based_approvers(recruitment_obj)
    if not expected:
        expected = _custom_recruitment_approvers(recruitment_obj.raised_by)
    if not expected:
        manager_ids = list(
            recruitment_obj.recruitment_managers.values_list("id", flat=True)
        )
        if manager_ids:
            managers = list(Employee.objects.filter(id__in=manager_ids))
            managers.sort(key=lambda e: manager_ids.index(e.id))
            expected = [m for m in managers if m != recruitment_obj.raised_by]
    if not expected:
        return

    existing = {a.approver_id: a for a in recruitment_obj.approvals.all()}
    if existing and all(emp.id in existing for emp in expected):
        return  # full chain already present

    # Append any missing approvers to the end of the chain, preserving order.
    next_seq = (
        max((a.sequence for a in existing.values()), default=0) + 1
        if existing
        else 1
    )
    for emp in expected:
        if emp.id in existing:
            continue
        RecruitmentApproval.objects.create(
            recruitment=recruitment_obj,
            approver=emp,
            sequence=next_seq,
        )
        next_seq += 1

    # If the recruitment was already approved/rejected before its chain was
    # back-filled, mark backfilled steps to match so the workflow modal shows
    # the full history instead of just "Raised by".
    if recruitment_obj.approval_status in ("approved", "rejected"):
        ts = recruitment_obj.created_at
        steps = list(recruitment_obj.approvals.order_by("sequence"))
        for step in steps:
            if step.status == "pending":
                step.status = "approved"
                step.approved_at = ts
                step.save(update_fields=["status", "approved_at"])
        if recruitment_obj.approval_status == "rejected" and steps:
            last = steps[-1]
            last.status = "rejected"
            last.save(update_fields=["status"])


def pipeline_grouper(request, recruitments):
    groups = []
    for rec in recruitments:
        stages = StageFilter(request.GET, queryset=rec.stage_set.all()).qs.order_by(
            "sequence"
        )
        all_stages_grouper = []
        data = {"recruitment": rec, "stages": []}
        for stage in stages.order_by("sequence"):
            all_stages_grouper.append({"grouper": stage, "list": []})
            stage_candidates = CandidateFilter(
                request.GET,
                stage.candidate_set.filter(
                    is_active=True,
                ),
            ).qs.order_by("sequence")

            page_name = "page" + stage.stage + str(rec.id)
            grouper = group_by_queryset(
                stage_candidates,
                "stage_id",
                request.GET.get(page_name),
                page_name,
            ).object_list
            data["stages"] = data["stages"] + grouper

        ordered_data = []

        # combining un used groups in to the grouper
        groupers = data["stages"]
        for stage in stages:
            found = False
            for grouper in groupers:
                if grouper["grouper"] == stage:
                    ordered_data.append(grouper)
                    found = True
                    break
            if not found:
                ordered_data.append({"grouper": stage})
        data = {
            "recruitment": rec,
            "stages": ordered_data,
        }
        groups.append(data)
    return groups


@login_required
@hx_request_required
@permission_required(perm="recruitment.add_recruitment")
def recruitment(request):
    """
    This method is used to create recruitment, when create recruitment this method
    add  recruitment view,create candidate, change stage sequence and so on, some of
    the permission is checking manually instead of using django permission permission
    to the  recruitment managers
    """
    form = RecruitmentCreationForm()
    if request.GET:
        form = RecruitmentCreationForm(initial=request.GET.dict())
    dynamic = (
        request.GET.get("dynamic") if request.GET.get("dynamic") != "None" else None
    )
    if request.method == "POST":
        form = RecruitmentCreationForm(request.POST, request.FILES)
        if form.is_valid():
            recruitment_obj = form.save(commit=False)
            recruitment_obj.posting_type = form.cleaned_data.get("posting_type", "external")
            recruitment_obj.budget_available = form.cleaned_data.get("budget_available", False)
            if request.POST.get("raised_from_employee") == "True":
                recruitment_obj.raised_from_employee = True
                recruitment_obj.raised_by = request.user.employee_get
                recruitment_obj.approval_status = "pending"
                recruitment_obj.is_published = False
            recruitment_obj.save()
            form.save_m2m()
            use_hierarchy = form.cleaned_data.get("use_hierarchy")
            manager_ids = form.data.getlist("recruitment_managers")
            if use_hierarchy:
               employee = request.user.employee_get
               managers = get_reporting_chain(employee)
            else:
                  from employee.models import Employee
                  managers = Employee.objects.filter(id__in=manager_ids)

            recruitment_obj.recruitment_managers.set(managers)
            recruitment_obj.open_positions.set(
                JobPosition.objects.filter(id__in=form.data.getlist("open_positions"))
            )
            if (
                recruitment_obj.publish_in_linkedin
                and recruitment_obj.linkedin_account_id
            ):
                post_recruitment_in_linkedin(
                    request, recruitment_obj, recruitment_obj.linkedin_account_id
                )
            if recruitment_obj.raised_from_employee:
                # When using hierarchy, always derive approvers from reporting chain
                # (manager_ids is empty when auto-assign is ticked — pass None so the
                # function falls back to get_reporting_chain instead of using the empty list)
                effective_ids = manager_ids if (manager_ids and not use_hierarchy) else None
                approvals = create_employee_recruitment_approvals(
                    recruitment_obj, approver_ids=effective_ids
                )
                if approvals:
                    first_approval = approvals[0]
                    recipient = getattr(first_approval.approver, "employee_user_id", None)
                    if recipient:
                        notify.send(
                            request.user.employee_get,
                            recipient=[recipient],
                            verb=_("Recruitment request waiting for your approval."),
                            icon="people-circle",
                            redirect=reverse("received-recruitments"),
                        )
                else:
                    recruitment_obj.approval_status = "approved"
                    recruitment_obj.save()
            messages.success(request, _("Recruitment added."))
            with contextlib.suppress(Exception):
                if not recruitment_obj.raised_from_employee:
                    managers = recruitment_obj.recruitment_managers.select_related(
                        "employee_user_id"
                    )
                    users = [employee.employee_user_id for employee in managers]
                    notify.send(
                        request.user.employee_get,
                        recipient=users,
                        verb="You are chosen as one of recruitment manager",
                        verb_ar="تم اختيارك كأحد مديري التوظيف",
                        verb_de="Sie wurden als einer der Personalvermittler ausgewählt",
                        verb_es="Has sido elegido/a como uno de los gerentes de contratación",
                        verb_fr="Vous êtes choisi(e) comme l'un des responsables du recrutement",
                        icon="people-circle",
                        redirect=reverse("pipeline"),
                    )
            return HttpResponse("<script>location.reload();</script>")
    return render(
        request,
        "recruitment/recruitment_form.html",
        {
            "form": form,
            "dynamic": dynamic,
            "raised_from_employee": request.GET.get("raised_from_employee") == "True",
        },
    )


@login_required
@permission_required(perm="recruitment.view_recruitment")
def recruitment_view(request):
    """
    This method is used to  render all recruitment to view
    """
    if not request.GET:
        request.GET.copy().update({"is_active": "on"})
    queryset = Recruitment.objects.filter(is_active=True)
    if Recruitment.objects.all():
        template = "recruitment/recruitment_view.html"
    else:
        template = "recruitment/recruitment_empty.html"
    initial_tag = {}
    if request.GET.get("closed") == "false":
        queryset = queryset.filter(closed=True)
        initial_tag["closed"] = ["true"]
    else:
        queryset = queryset.filter(closed=False)
        initial_tag["closed"] = ["false"]

    filter_obj = RecruitmentFilter(request.GET, queryset)
    filter_dict = request.GET.copy()
    for key, value in initial_tag.items():
        filter_dict[key] = value

    return render(
        request,
        template,
        {
            "data": paginator_qry(filter_obj.qs, request.GET.get("page")),
            "f": filter_obj,
            "filter_dict": filter_dict,
            "pd": request.GET.urlencode() + "&closed=false",
        },
    )


@login_required
@permission_required(perm="recruitment.change_recruitment")
@hx_request_required
def recruitment_update(request, rec_id):
    """
    This method is used to update the recruitment, when updating the recruitment,
    any changes in manager is exists then permissions also assigned to the manager
    Args:
        id : recruitment_id
    """
    recruitment_obj = Recruitment.find(rec_id)
    if not recruitment_obj:
        messages.error(
            request, _("The recruitment entry you are trying to edit does not exist.")
        )
        return HttpResponse("<script>window.location.reload();</script>")
    survey_template_list = []
    survey_templates = RecruitmentSurvey.objects.filter(
        recruitment_ids=rec_id
    ).distinct()
    for survey in survey_templates:
        survey_template_list.append(survey.template_id.all())
    form = RecruitmentCreationForm(instance=recruitment_obj)
    if request.GET:
        form = RecruitmentCreationForm(request.GET)
    dynamic = (
        request.GET.get("dynamic") if request.GET.get("dynamic") != "None" else None
    )
    if request.method == "POST":
        form = RecruitmentCreationForm(request.POST, request.FILES, instance=recruitment_obj)
        if form.is_valid():
            recruitment_obj = form.save()
            recruitment_obj.posting_type = form.cleaned_data.get("posting_type", "external")
            recruitment_obj.budget_available = form.cleaned_data.get("budget_available", False)
            recruitment_obj.save()
            if len(form.changed_data) > 0:
                if (
                    recruitment_obj.publish_in_linkedin
                    and recruitment_obj.linkedin_account_id
                ):
                    delete_post(recruitment_obj)
                    post_recruitment_in_linkedin(
                        request, recruitment_obj, recruitment_obj.linkedin_account_id
                    )
            messages.success(request, _("Recruitment Updated."))
            response = render(
                request, "recruitment/recruitment_form.html", {"form": form}
            )
            with contextlib.suppress(Exception):
                managers = recruitment_obj.recruitment_managers.select_related(
                    "employee_user_id"
                )
                users = [employee.employee_user_id for employee in managers]
                notify.send(
                    request.user.employee_get,
                    recipient=users,
                    verb=f"{recruitment_obj} is updated, You are chosen as one of the managers",
                    verb_ar=f"{recruitment_obj} تم تحديثه، تم اختيارك كأحد المديرين",
                    verb_de=f"{recruitment_obj} wurde aktualisiert. Sie wurden als\
                            einer der Manager ausgewählt",
                    verb_es=f"{recruitment_obj} ha sido actualizado/a. Has sido elegido\
                            a como uno de los gerentes",
                    verb_fr=f"{recruitment_obj} a été mis(e) à jour. Vous êtes choisi(e) comme\
                            l'un des responsables",
                    icon="people-circle",
                    redirect=reverse("pipeline"),
                )

            return HttpResponse(
                response.content.decode("utf-8") + "<script>location.reload();</script>"
            )
    return render(
        request,
        "recruitment/recruitment_update_form.html",
        {"form": form, "dynamic": dynamic},
    )


def paginator_qry_recruitment_limited(qryset, page_number):
    """
    This method is used to generate common paginator limit.
    """
    paginator = Paginator(qryset, 4)
    qryset = paginator.get_page(page_number)
    return qryset


user_recruitments = {}


@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def recruitment_pipeline(request):
    """
    This method is used to filter out candidate through pipeline structure
    """
    filter_obj = RecruitmentFilter(request.GET)
    qs = filter_obj.qs
    # Default to open recruitments only unless caller explicitly requests closed ones
    if "closed" not in request.GET:
        qs = qs.filter(closed=False)
    if qs.exists():
        template = "pipeline/pipeline.html"
    else:
        template = "pipeline/pipeline_empty.html"
    stage_filter = StageFilter(request.GET)
    candidate_filter = CandidateFilter(request.GET)
    recruitments = paginator_qry_recruitment_limited(
        qs, request.GET.get("page")
    )

    now = timezone.now()

    from recruitment.models import JobApplication
    job_applications = JobApplication.objects.select_related("recruitment").order_by("-created_at")
    apps_for_json = [
        {
            "id": a.id,
            "job_id": a.recruitment_id,
            "job_title": a.recruitment.title,
            "name": a.name,
            "email": a.email,
            "phone": a.phone or "",
            "country": a.country or "",
            "experience": a.experience or "",
            "why_apply": a.why_apply or "",
            "status": a.status,
            "score": a.score,
            "ai_reason": a.ai_reason or "",
            "skills": a.skills or [],
            "has_resume": bool(a.resume_path),
            "rejection_email_sent": a.rejection_email_sent,
            "rejection_justification": a.rejection_justification or "",
            "hr_override": a.hr_override,
            "hr_override_justification": a.hr_override_justification or "",
            "excluded": a.excluded_by_second_filter,
        }
        for a in job_applications
    ]

    return render(
        request,
        template,
        {
            "rec_filter_obj": filter_obj,
            "recruitment": recruitments,
            "stage_filter_obj": stage_filter,
            "candidate_filter_obj": candidate_filter,
            "now": now,
            "applications_json": json.dumps(apps_for_json),
            "jobs_json": json.dumps([
                {"id": r.id, "title": r.title}
                for r in Recruitment.objects.all()
            ]),
        },
    )


def _sync_screened_apps_to_pipeline(recruitments):
    """Ensure every screened JobApplication has a Candidate entry in the pipeline."""
    from recruitment.models import JobApplication
    rec_ids = list(recruitments.values_list("id", flat=True))
    if not rec_ids:
        return
    screened_apps = JobApplication.objects.filter(
        recruitment_id__in=rec_ids,
        status="screened",
    ).select_related("recruitment")
    for app in screened_apps:
        _promote_to_pipeline(app)


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.view_recruitment")
def filter_pipeline(request):
    """
    This method is used to search/filter from pipeline
    """
    filter_obj = RecruitmentFilter(request.GET)
    stage_filter = StageFilter(request.GET)
    candidate_filter = CandidateFilter(request.GET)
    view = request.GET.get("view")
    base_qs = filter_obj.qs
    if "closed" not in request.GET:
        base_qs = base_qs.filter(closed=False)
    recruitments = base_qs.filter(is_active=True)
    if not request.user.has_perm("recruitment.view_recruitment"):
        recruitments = recruitments.filter(
            Q(recruitment_managers=request.user.employee_get)
        )
        stage_recruitment_ids = (
            stage_filter.qs.filter(stage_managers=request.user.employee_get)
            .values_list("recruitment_id", flat=True)
            .distinct()
        )
        recruitments = recruitments | base_qs.filter(id__in=stage_recruitment_ids)
        recruitments = recruitments.filter(is_active=True).distinct()

    closed = request.GET.get("closed")
    filter_dict = parse_qs(request.GET.urlencode())
    filter_dict = get_key_instances(Recruitment, filter_dict)

    # Auto-sync: ensure every screened JobApplication has a Candidate in the pipeline
    _sync_screened_apps_to_pipeline(recruitments)

    CACHE.set(
        request.session.session_key + "pipeline",
        {
            "candidates": candidate_filter.qs.filter(is_active=True).order_by(
                "sequence"
            ),
            "stages": stage_filter.qs.order_by("sequence"),
            "recruitments": recruitments,
            "filter_dict": filter_dict,
            "filter_query": request.GET,
        },
    )

    previous_data = request.GET.urlencode()
    paginator = Paginator(recruitments, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Group current page's recruitments by department for department-tab view
    def _dept_key(rec):
        try:
            return rec.job_position_id.department_id.department
        except AttributeError:
            return rec.title or "Other"

    sorted_recs = sorted(page_obj.object_list, key=_dept_key)
    dept_groups = [
        (dept, list(recs))
        for dept, recs in groupby(sorted_recs, key=_dept_key)
    ]

    template = "pipeline/components/pipeline_search_components.html"
    if request.GET.get("view") == "card":
        template = "pipeline/kanban_components/kanban.html"
    return render(
        request,
        template,
        {
            "recruitment": page_obj,
            "dept_groups": dept_groups,
            "stage_filter_obj": stage_filter,
            "candidate_filter_obj": candidate_filter,
            "filter_dict": filter_dict,
            "status": closed,
            "view": view,
            "pd": previous_data,
        },
    )


@login_required
@manager_can_enter("recruitment.view_recruitment")
def get_stage_badge_count(request):
    """
    Method to update stage badge count
    """
    stage_id = request.GET["stage_id"]
    stage = Stage.objects.get(id=stage_id)
    count = stage.candidate_set.filter(is_active=True).count()
    return HttpResponse(count)


@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def stage_component(request, view: str = "list"):
    """
    This method will stage tab contents
    """
    recruitment_id = request.GET["rec_id"]
    recruitment = Recruitment.objects.get(id=recruitment_id)
    pipeline_cache = CACHE.get(request.session.session_key + "pipeline")
    # 1060
    if not pipeline_cache:
        return HttpResponse(headers={"HX-Refresh": "true"})
    ordered_stages = pipeline_cache["stages"].filter(recruitment_id__id=recruitment_id)
    template = "pipeline/components/stages_tab_content.html"
    if view == "card":
        template = "pipeline/kanban_components/kanban_stage_components.html"
    return render(
        request,
        template,
        {
            "rec": recruitment,
            "ordered_stages": ordered_stages,
            "filter_dict": pipeline_cache["filter_dict"],
        },
    )


@login_required
@manager_can_enter(perm="recruitment.change_candidate")
def update_candidate_stage_and_sequence(request):
    """
    Update candidate sequence method
    """
    order_list = request.GET.getlist("order")
    stage_id = request.GET["stage_id"]
    stage = (
        CACHE.get(request.session.session_key + "pipeline")["stages"]
        .filter(id=stage_id)
        .first()
    )
    context = {}
    for index, cand_id in enumerate(order_list):
        candidate = CACHE.get(request.session.session_key + "pipeline")[
            "candidates"
        ].filter(id=cand_id)
        candidate.update(sequence=index, stage_id=stage)
    if stage.stage_type == "hired":
        if stage.recruitment_id.is_vacancy_filled():
            context["message"] = _("Vaccancy is filled")
            context["vacancy"] = stage.recruitment_id.vacancy
    return JsonResponse(context)


@login_required
@manager_can_enter(perm="recruitment.change_candidate")
def update_candidate_sequence(request):
    """
    Update candidate sequence method
    """
    order_list = request.GET.getlist("order")
    stage_id = request.GET["stage_id"]
    stage = (
        CACHE.get(request.session.session_key + "pipeline")["stages"]
        .filter(id=stage_id)
        .first()
    )
    data = {}

    for index, cand_id in enumerate(order_list):
        candidate = CACHE.get(request.session.session_key + "pipeline")[
            "candidates"
        ].filter(id=cand_id)
        candidate.update(
            sequence=index, stage_id=stage, hired=(stage.stage_type == "hired")
        )

    return JsonResponse(data)


def limited_paginator_qry(queryset, page):
    """
    Limited pagination
    """
    paginator = Paginator(queryset, 10)
    queryset = paginator.get_page(page)
    return queryset


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.view_recruitment")
def candidate_component(request):
    """
    Candidate component
    """
    stage_id = request.GET.get("stage_id")
    pipeline_cache = CACHE.get(request.session.session_key + "pipeline")
    # 1060
    if not pipeline_cache:
        return HttpResponse(headers={"HX-Refresh": "true"})
    stage = pipeline_cache["stages"].filter(id=stage_id).first()
    candidates = pipeline_cache["candidates"].filter(stage_id=stage)

    template = "pipeline/components/candidate_stage_component.html"
    if pipeline_cache["filter_query"].get("view") == "card":
        template = "pipeline/kanban_components/candidate_kanban_components.html"

    now = timezone.now()
    return render(
        request,
        template,
        {
            "candidates": limited_paginator_qry(
                candidates, request.GET.get("candidate_page")
            ),
            "stage": stage,
            "rec": getattr(candidates.first(), "recruitment_id", {}),
            "now": now,
        },
    )


@login_required
@manager_can_enter("recruitment.change_candidate")
def change_candidate_stage(request):
    """
    This method is used to update candidates stage
    """
    if request.method == "POST":
        canIds = request.POST["canIds"]
        stage_id = request.POST["stageId"]
        context = {}
        if request.GET.get("bulk") == "True":
            canIds = json.loads(canIds)
            for cand_id in canIds:
                try:
                    candidate = Candidate.objects.get(id=cand_id)
                    stage = Stage.objects.filter(
                        recruitment_id=candidate.recruitment_id, id=stage_id
                    ).first()
                    if stage:
                        candidate.stage_id = stage
                        candidate.save()
                        if stage.stage_type == "hired":
                            if stage.recruitment_id.is_vacancy_filled():
                                context["message"] = _("Vaccancy is filled")
                                context["vacancy"] = stage.recruitment_id.vacancy
                        messages.success(request, _("Candidate stage updated"))
                except Candidate.DoesNotExist:
                    messages.error(request, _("Candidate not found."))
        else:
            try:
                candidate = Candidate.objects.get(id=canIds)
                stage = Stage.objects.filter(
                    recruitment_id=candidate.recruitment_id, id=stage_id
                ).first()
                if stage:
                    candidate.stage_id = stage
                    candidate.save()
                    if stage.stage_type == "hired":
                        if stage.recruitment_id.is_vacancy_filled():
                            context["message"] = _("Vaccancy is filled")
                            context["vacancy"] = stage.recruitment_id.vacancy
                    candidate.stage_id = stage
                    candidate.save()
                    messages.success(request, _("Candidate stage updated"))
            except Candidate.DoesNotExist:
                messages.error(request, _("Candidate not found."))
        return JsonResponse(context)
    candidate_id = request.GET["candidate_id"]
    stage_id = request.GET["stage_id"]
    candidate = Candidate.objects.get(id=candidate_id)
    stage = Stage.objects.filter(
        recruitment_id=candidate.recruitment_id, id=stage_id
    ).first()
    if stage:
        candidate.stage_id = stage
        candidate.save()
        messages.success(request, _("Candidate stage updated"))
    return stage_component(request)


@login_required
@permission_required(perm="recruitment.view_recruitment")
def recruitment_pipeline_card(request):
    """
    This method is used to render pipeline card structure.
    """
    search = request.GET.get("search")
    search = search if search is not None else ""
    recruitment_obj = Recruitment.objects.all()
    candidates = Candidate.objects.filter(name__icontains=search, is_active=True)
    stages = Stage.objects.all()
    return render(
        request,
        "pipeline/pipeline_components/pipeline_card_view.html",
        {"recruitment": recruitment_obj, "candidates": candidates, "stages": stages},
    )


@login_required
@permission_required(perm="recruitment.delete_recruitment")
def recruitment_archive(request, rec_id):
    """
    This method is used to archive and unarchive the recruitment
    args:
        rec_id: The id of the Recruitment
    """
    try:
        recruitment = Recruitment.objects.get(id=rec_id)
        if recruitment.is_active:
            recruitment.is_active = False
        else:
            recruitment.is_active = True
        recruitment.save()
    except (Recruitment.DoesNotExist, OverflowError):
        messages.error(request, _("Recruitment Does not exists.."))
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.change_stage")
def stage_update_pipeline(request, stage_id):
    """
    This method is used to update stage from pipeline view
    """
    stage_obj = Stage.objects.get(id=stage_id)
    form = StageCreationForm(instance=stage_obj)
    if request.POST:
        form = StageCreationForm(request.POST, instance=stage_obj)
        if form.is_valid():
            stage_obj = form.save()
            messages.success(request, _("Stage updated."))
            with contextlib.suppress(Exception):
                managers = stage_obj.stage_managers.select_related("employee_user_id")
                users = [employee.employee_user_id for employee in managers]
                notify.send(
                    request.user.employee_get,
                    recipient=users,
                    verb=f"{stage_obj.stage} stage in recruitment {stage_obj.recruitment_id}\
                            is updated, You are chosen as one of the managers",
                    verb_ar=f"تم تحديث مرحلة {stage_obj.stage} في التوظيف {stage_obj.recruitment_id}\
                            ، تم اختيارك كأحد المديرين",
                    verb_de=f"Die Stufe {stage_obj.stage} in der Rekrutierung {stage_obj.recruitment_id}\
                            wurde aktualisiert. Sie wurden als einer der Manager ausgewählt",
                    verb_es=f"Se ha actualizado la etapa {stage_obj.stage} en la contratación\
                          {stage_obj.recruitment_id}.Has sido elegido/a como uno de los gerentes",
                    verb_fr=f"L'étape {stage_obj.stage} dans le recrutement {stage_obj.recruitment_id}\
                          a été mise à jour.Vous avez été choisi(e) comme l'un des responsables",
                    icon="people-circle",
                    redirect=reverse("pipeline"),
                )

            return HttpResponse("<script>window.location.reload()</script>")

    return render(request, "pipeline/form/stage_update.html", {"form": form})


@login_required
@hx_request_required
@recruitment_manager_can_enter(perm="recruitment.change_recruitment")
def recruitment_update_pipeline(request, rec_id):
    """
    This method is used to update recruitment from pipeline view
    """
    recruitment_obj = Recruitment.objects.get(id=rec_id)
    form = RecruitmentCreationForm(instance=recruitment_obj)
    if request.POST:
        form = RecruitmentCreationForm(request.POST, request.FILES, instance=recruitment_obj)
        if form.is_valid():
            recruitment_obj = form.save()
            messages.success(request, _("Recruitment updated."))
            with contextlib.suppress(Exception):
                managers = recruitment_obj.recruitment_managers.select_related(
                    "employee_user_id"
                )
                users = [employee.employee_user_id for employee in managers]
                notify.send(
                    request.user.employee_get,
                    recipient=users,
                    verb=f"{recruitment_obj} is updated, You are chosen as one of the managers",
                    verb_ar=f"تم تحديث {recruitment_obj}، تم اختيارك كأحد المديرين",
                    verb_de=f"{recruitment_obj} wurde aktualisiert.\
                          Sie wurden als einer der Manager ausgewählt",
                    verb_es=f"{recruitment_obj} ha sido actualizado/a. Has sido elegido\
                            a como uno de los gerentes",
                    verb_fr=f"{recruitment_obj} a été mis(e) à jour. Vous avez été\
                            choisi(e) comme l'un des responsables",
                    icon="people-circle",
                    redirect=reverse("pipeline"),
                )

            response = render(
                request, "pipeline/form/recruitment_update.html", {"form": form}
            )
            return HttpResponse(
                response.content.decode("utf-8") + "<script>location.reload();</script>"
            )
    return render(request, "pipeline/form/recruitment_update.html", {"form": form})


@login_required
@recruitment_manager_can_enter(perm="recruitment.change_recruitment")
def recruitment_close_pipeline(request, rec_id):
    """
    This method is used to close recruitment from pipeline view
    """
    try:
        recruitment_obj = Recruitment.objects.get(id=rec_id)
        recruitment_obj.closed = True
        recruitment_obj.save()
        messages.success(request, "Recruitment closed successfully")
    except (Recruitment.DoesNotExist, OverflowError):
        messages.error(request, _("Recruitment Does not exists.."))
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required
@recruitment_manager_can_enter(perm="recruitment.change_recruitment")
def recruitment_reopen_pipeline(request, rec_id):
    """
    This method is used to reopen recruitment from pipeline view
    """
    recruitment_obj = Recruitment.objects.get(id=rec_id)
    recruitment_obj.closed = False
    recruitment_obj.save()

    messages.success(request, "Recruitment reopend successfully")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required
@manager_can_enter(perm="recruitment.change_candidate")
def candidate_stage_update(request, cand_id):
    """
    This method is a ajax method used to update candidate stage when drag and drop
    the candidate from one stage to another on the pipeline template
    Args:
        id : candidate_id
    """
    stage_id = request.POST["stageId"]
    candidate_obj = Candidate.objects.get(id=cand_id)
    history_queryset = candidate_obj.history_set.all().first()
    stage_obj = Stage.objects.get(id=stage_id)
    if candidate_obj.stage_id == stage_obj:
        return JsonResponse({"type": "noChange", "message": _("No change detected.")})
    # Here set the last updated schedule date on this stage if schedule exists in history
    history_queryset = candidate_obj.history_set.filter(stage_id=stage_obj)
    schedule_date = None
    if history_queryset.exists():
        # this condition is executed when a candidate dropped back to any previous
        # stage, if there any scheduled date then set it back
        schedule_date = history_queryset.first().schedule_date
    stage_manager_on_this_recruitment = (
        is_stagemanager(request)[1]
        .filter(recruitment_id=stage_obj.recruitment_id)
        .exists()
    )
    if (
        stage_manager_on_this_recruitment
        or request.user.is_superuser
        or is_recruitmentmanager(rec_id=stage_obj.recruitment_id.id)[0]
    ):
        candidate_obj.stage_id = stage_obj
        candidate_obj.hired = stage_obj.stage_type == "hired"
        candidate_obj.canceled = stage_obj.stage_type == "cancelled"
        candidate_obj.schedule_date = schedule_date
        candidate_obj.start_onboard = False
        candidate_obj.save()
        with contextlib.suppress(Exception):
            managers = stage_obj.stage_managers.select_related("employee_user_id")
            users = [employee.employee_user_id for employee in managers]
            notify.send(
                request.user.employee_get,
                recipient=users,
                verb=f"New candidate arrived on stage {stage_obj.stage}",
                verb_ar=f"وصل مرشح جديد إلى المرحلة {stage_obj.stage}",
                verb_de=f"Neuer Kandidat ist auf der Stufe {stage_obj.stage} angekommen",
                verb_es=f"Nuevo candidato llegó a la etapa {stage_obj.stage}",
                verb_fr=f"Nouveau candidat arrivé à l'étape {stage_obj.stage}",
                icon="person-add",
                redirect=reverse("pipeline"),
            )

        # Email the candidate when manually promoted to an interview stage
        if stage_obj.stage_type == "interview" and candidate_obj.email:
            try:
                import threading
                job_title = str(candidate_obj.recruitment_id) if candidate_obj.recruitment_id else "the role"
                threading.Thread(
                    target=_send_candidate_congratulations_email,
                    args=(candidate_obj.email, candidate_obj.name, job_title),
                    daemon=True,
                ).start()
            except Exception:
                pass

        return JsonResponse(
            {"type": "success", "message": _("Candidate stage updated")}
        )
    return JsonResponse(
        {"type": "danger", "message": _("Something went wrong, Try agian.")}
    )


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.view_stagenote")
def view_note(request, cand_id):
    """
    This method renders a template components to view candidate remark or note
    Args:
        id : candidate instance id
    """
    candidate_obj = Candidate.objects.get(id=cand_id)
    notes = candidate_obj.stagenote_set.all().order_by("-id")
    return render(
        request,
        "pipeline/pipeline_components/view_note.html",
        {"cand": candidate_obj, "notes": notes},
    )


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.add_stagenote")
def add_note(request, cand_id=None):
    """
    This method renders template component to add candidate remark
    """
    form = StageNoteForm(initial={"candidate_id": cand_id})
    if request.method == "POST":
        form = StageNoteForm(
            request.POST,
            request.FILES,
        )
        if form.is_valid():
            note, attachment_ids = form.save(commit=False)
            candidate = Candidate.objects.get(id=cand_id)
            note.candidate_id = candidate
            note.stage_id = candidate.stage_id
            note.updated_by = request.user.employee_get
            note.save()
            note.stage_files.set(attachment_ids)
            messages.success(request, _("Note added successfully.."))
    candidate_obj = Candidate.objects.get(id=cand_id)
    return render(
        request,
        "candidate/individual_view_note.html",
        {
            "candidate": candidate_obj,
            "note_form": form,
        },
    )


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.add_stagenote")
def create_note(request, cand_id=None):
    """
    This method renders template component to add candidate remark
    """
    form = StageNoteForm(initial={"candidate_id": cand_id})
    if request.method == "POST":
        form = StageNoteForm(request.POST, request.FILES)
        if form.is_valid():
            note, attachment_ids = form.save(commit=False)
            candidate = Candidate.objects.get(id=cand_id)
            note.candidate_id = candidate
            note.stage_id = candidate.stage_id
            note.updated_by = request.user.employee_get
            note.save()
            note.stage_files.set(attachment_ids)
            messages.success(request, _("Note added successfully.."))
            return redirect("view-note", cand_id=cand_id)
    candidate_obj = Candidate.objects.get(id=cand_id)
    notes = candidate_obj.stagenote_set.all().order_by("-id")
    return render(
        request,
        "pipeline/pipeline_components/view_note.html",
        {"note_form": form, "cand": candidate_obj, "notes": notes},
    )


@login_required
@manager_can_enter(perm="recruitment.change_stagenote")
def note_update(request, note_id):
    """
    This method is used to update the stage not
    Args:
        id : stage note instance id
    """
    note = StageNote.objects.get(id=note_id)
    form = StageNoteUpdateForm(instance=note)
    if request.POST:
        form = StageNoteUpdateForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, _("Note updated successfully..."))
            cand_id = note.candidate_id.id
            return redirect("view-note", cand_id=cand_id)

    return render(
        request, "pipeline/pipeline_components/update_note.html", {"form": form}
    )


@login_required
@manager_can_enter(perm="recruitment.change_stagenote")
def note_update_individual(request, note_id):
    """
    This method is used to update the stage not
    Args:
        id : stage note instance id
    """
    note = StageNote.objects.get(id=note_id)
    form = StageNoteForm(instance=note)
    if request.POST:
        form = StageNoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, _("Note updated successfully..."))
            response = render(
                request,
                "pipeline/pipeline_components/update_note_individual.html",
                {"form": form},
            )
            return HttpResponse(
                response.content.decode("utf-8") + "<script>location.reload();</script>"
            )
    return render(
        request,
        "pipeline/pipeline_components/update_note_individual.html",
        {
            "form": form,
        },
    )


@login_required
@hx_request_required
def add_more_files(request, id):
    """
    This method is used to Add more files to the stage candidate note.
    Args:
        id : stage note instance id
    """
    note = StageNote.objects.get(id=id)
    if request.method == "POST":
        files = request.FILES.getlist("files")
        files_ids = []
        for file in files:
            instance = StageFiles.objects.create(files=file)
            files_ids.append(instance.id)

            note.stage_files.add(instance.id)
    return redirect("view-note", cand_id=note.candidate_id.id)


@login_required
@hx_request_required
def add_more_individual_files(request, id):
    """
    This method is used to Add more files to the stage candidate note.
    Args:
        id : stage note instance id
    """
    note = StageNote.objects.get(id=id)
    if request.method == "POST":
        files = request.FILES.getlist("files")
        files_ids = []
        for file in files:
            instance = StageFiles.objects.create(files=file)
            files_ids.append(instance.id)
            note.stage_files.add(instance.id)
        messages.success(request, _("Files uploaded successfully"))
    return redirect(f"/recruitment/add-note/{note.candidate_id.id}/")


@login_required
def delete_stage_note_file(request, id):
    """
    This method is used to delete the stage note file
    Args:
        id : stage file instance id
    """
    script = ""
    file = StageFiles.objects.get(id=id)
    file.delete()
    messages.success(request, _("File deleted successfully"))
    return HttpResponse(script)


@login_required
@hx_request_required
def delete_individual_note_file(request, id):
    """
    This method is used to delete the stage note file
    Args:
        id : stage file instance id
    """
    script = ""
    file = StageFiles.objects.get(id=id)
    file.stagenote_set.all().first().candidate_id.id
    file.delete()
    messages.success(request, _("File deleted successfully"))
    return HttpResponse(script)


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.add_stagenote")
def candidate_can_view_note(request, id):
    note = StageNote.objects.filter(id=id)
    note.update(candidate_can_view=not note.first().candidate_can_view)

    messages.success(request, _("Candidate view status updated"))
    return redirect("view-note", cand_id=note.first().candidate_id.id)


@login_required
@permission_required(perm="recruitment.change_candidate")
def candidate_schedule_date_update(request):
    """
    This is a an ajax method to update schedule date for a candidate
    """
    candidate_id = request.POST["candidateId"]
    schedule_date = request.POST["date"]
    candidate_obj = Candidate.objects.get(id=candidate_id)
    candidate_obj.schedule_date = schedule_date
    candidate_obj.save()
    return JsonResponse({"message": "congratulations"})


@login_required
@manager_can_enter(perm="recruitment.add_stage")
def stage(request):
    """
    This method is used to create stages, also several permission assigned to the stage managers
    """
    form = StageCreationForm(
        initial={"recruitment_id": request.GET.get("recruitment_id")}
    )
    if request.method == "POST":
        form = StageCreationForm(request.POST)
        if form.is_valid():
            stage_obj = form.save()
            stage_obj.stage_managers.set(
                Employee.objects.filter(id__in=form.data.getlist("stage_managers"))
            )
            stage_obj.save()
            recruitment_obj = stage_obj.recruitment_id
            rec_stages = (
                Stage.objects.filter(recruitment_id=recruitment_obj, is_active=True)
                .order_by("sequence")
                .last()
            )
            if rec_stages.sequence is None:
                stage_obj.sequence = 1
            else:
                stage_obj.sequence = rec_stages.sequence + 1
            stage_obj.save()
            messages.success(request, _("Stage added."))
            with contextlib.suppress(Exception):
                managers = stage_obj.stage_managers.select_related("employee_user_id")
                users = [employee.employee_user_id for employee in managers]
                notify.send(
                    request.user.employee_get,
                    recipient=users,
                    verb=f"Stage {stage_obj} is updated on recruitment {stage_obj.recruitment_id},\
                          You are chosen as one of the managers",
                    verb_ar=f"تم تحديث المرحلة {stage_obj} في التوظيف\
                          {stage_obj.recruitment_id}، تم اختيارك كأحد المديرين",
                    verb_de=f"Stufe {stage_obj} wurde in der Rekrutierung {stage_obj.recruitment_id}\
                          aktualisiert. Sie wurden als einer der Manager ausgewählt",
                    verb_es=f"La etapa {stage_obj} ha sido actualizada en la contratación\
                          {stage_obj.recruitment_id}. Has sido elegido/a como uno de los gerentes",
                    verb_fr=f"L'étape {stage_obj} a été mise à jour dans le recrutement\
                          {stage_obj.recruitment_id}. Vous avez été choisi(e) comme l'un des responsables",
                    icon="people-circle",
                    redirect=reverse("pipeline"),
                )

            return HttpResponse("<script>location.reload();</script>")
    return render(request, "stage/stage_form.html", {"form": form})


@login_required
@permission_required(perm="recruitment.view_stage")
def stage_view(request):
    """
    This method is used to render all stages to a template
    """
    stages = Stage.objects.all()
    stages = stages.filter(recruitment_id__is_active=True)
    recruitments = group_by_queryset(
        stages,
        "recruitment_id",
        request.GET.get("rpage"),
    )
    filter_obj = StageFilter()
    form = StageCreationForm()
    if stages.exists():
        template = "stage/stage_view.html"
    else:
        template = "stage/stage_empty.html"
    return render(
        request,
        template,
        {
            "data": paginator_qry(stages, request.GET.get("page")),
            "form": form,
            "f": filter_obj,
            "recruitments": recruitments,
        },
    )


def stage_data(request, rec_id):
    stages = StageFilter(request.GET).qs.filter(recruitment_id__id=rec_id)
    previous_data = request.GET.urlencode()
    data_dict = parse_qs(previous_data)
    get_key_instances(Stage, data_dict)

    return render(
        request,
        "stage/stage_component.html",
        {
            "data": paginator_qry(stages, request.GET.get("page")),
            "filter_dict": data_dict,
            "pd": request.GET.urlencode(),
            "hx_target": request.META.get("HTTP_HX_TARGET"),
        },
    )


@login_required
@manager_can_enter(perm="recruitment.change_stage")
@hx_request_required
def stage_update(request, stage_id):
    """
    This method is used to update stage, if the managers changed then\
    permission assigned to new managers also
    Args:
        id : stage_id

    """
    stages = Stage.objects.get(id=stage_id)
    form = StageCreationForm(instance=stages)
    if request.method == "POST":
        form = StageCreationForm(request.POST, instance=stages)
        if form.is_valid():
            form.save()
            messages.success(request, _("Stage updated."))
            response = render(
                request, "recruitment/recruitment_form.html", {"form": form}
            )
            return HttpResponse(
                response.content.decode("utf-8") + "<script>location.reload();</script>"
            )
    return render(request, "stage/stage_update_form.html", {"form": form})


@login_required
@hx_request_required
@manager_can_enter("recruitment.add_candidate")
def add_candidate(request):
    """
    This method is used to add candidate directly to the stage
    """
    form = AddCandidateForm(initial={"stage_id": request.GET.get("stage_id")})
    if request.POST:
        form = AddCandidateForm(
            request.POST,
            request.FILES,
            initial={"stage_id": request.GET.get("stage_id")},
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate Added")
            return HttpResponse("<script>window.location.reload()</script>")
    return render(request, "pipeline/form/candidate_form.html", {"form": form})


@login_required
@require_http_methods(["POST"])
@hx_request_required
def stage_title_update(request, stage_id):
    """
    This method is used to update the name of recruitment stage
    """
    stage_obj = Stage.objects.get(id=stage_id)
    stage_obj.stage = request.POST["stage"]
    stage_obj.save()
    message = _("The stage title has been updated successfully")
    return HttpResponse(
        f'<div class="oh-alert-container"><div class="oh-alert oh-alert--animated oh-alert--success">{message}</div></div>'
    )


@login_required
@any_permission_required(
    perms=["recruitment.add_candidate", "onboarding.add_onboardingcandidate"]
)
def candidate(request):
    """
    This method used to create candidate
    """
    form = CandidateCreationForm()
    open_recruitment = Recruitment.objects.filter(closed=False, is_active=True)
    path = "/recruitment/candidate-view"
    if request.method == "POST":
        form = CandidateCreationForm(request.POST, request.FILES)
        if form.is_valid():
            candidate_obj = form.save(commit=False)
            candidate_obj.start_onboard = False
            candidate_obj.source = "software"
            if candidate_obj.stage_id is None:
                candidate_obj.stage_id = Stage.objects.filter(
                    recruitment_id=candidate_obj.recruitment_id, stage_type="initial"
                ).first()
            # when creating new candidate from onboarding view
            if request.GET.get("onboarding") == "True":
                candidate_obj.hired = True
                path = "/onboarding/candidates-view"
            if form.data.get("job_position_id"):
                candidate_obj.save()
                messages.success(request, _("Candidate added."))
            else:
                messages.error(request, "Job position field is required")
                return render(
                    request,
                    "candidate/candidate_create_form.html",
                    {"form": form, "open_recruitment": open_recruitment},
                )
            return redirect(path)

    return render(
        request,
        "candidate/candidate_create_form.html",
        {"form": form, "open_recruitment": open_recruitment},
    )


@login_required
@permission_required(perm="recruitment.add_candidate")
def recruitment_stage_get(_, rec_id):
    """
    This method returns all stages as json
    Args:
        id: recruitment_id
    """
    recruitment_obj = Recruitment.objects.get(id=rec_id)
    all_stages = recruitment_obj.stage_set.all()
    all_stage_json = serializers.serialize("json", all_stages)
    return JsonResponse({"stages": all_stage_json})


@login_required
@permission_required(perm="recruitment.view_candidate")
def candidate_view(request):
    """
    This method render all candidate to the template
    """
    view_type = request.GET.get("view")
    previous_data = request.GET.urlencode()
    candidates = Candidate.objects.filter(is_active=True)
    recruitments = Recruitment.objects.filter(closed=False, is_active=True)

    mails = list(Candidate.objects.values_list("email", flat=True))
    # Query the User model to check if any email is present
    existing_emails = list(
        User.objects.filter(username__in=mails).values_list("email", flat=True)
    )

    filter_obj = CandidateFilter(request.GET, queryset=candidates)
    if Candidate.objects.exists():
        template = "candidate/candidate_view.html"
    else:
        template = "candidate/candidate_empty.html"
    data_dict = parse_qs(previous_data)
    get_key_instances(Candidate, data_dict)

    # Store the candidates in the session
    request.session["filtered_candidates"] = [candidate.id for candidate in candidates]

    return render(
        request,
        template,
        {
            "data": paginator_qry(filter_obj.qs, request.GET.get("page")),
            "pd": previous_data,
            "f": filter_obj,
            "view_type": view_type,
            "filter_dict": data_dict,
            "gp_fields": CandidateReGroup.fields,
            "emp_list": existing_emails,
            "recruitments": recruitments,
        },
    )


def _build_round_status_map(interview_ids):
    """Return {interview_id: "Round N Pending" | "Decision Pending"} for the given ids.

    - "Round N Pending": at least one round is completed and the next round is still pending.
    - "Decision Pending": rounds exist and all are completed (final decision not yet made).
    Interviews with no rounds at all are omitted; callers fall back to date-based status.
    """
    rounds = (
        InterviewRound.objects.filter(interview_id__in=interview_ids)
        .order_by("interview_id", "round_number")
        .values("interview_id", "round_number", "completed")
    )
    grouped = {}
    for r in rounds:
        grouped.setdefault(r["interview_id"], []).append(r)
    status_map = {}
    for iid, rlist in grouped.items():
        pending = [r for r in rlist if not r["completed"]]
        if not pending:
            status_map[iid] = "Decision Pending"
        elif len(pending) < len(rlist):
            status_map[iid] = f"Round {pending[0]['round_number']} Pending"
        else:
            # nothing completed yet — leave to date-based status
            continue
    return status_map


@login_required
@hx_request_required
def interview_filter_view(request):
    """
    This method is used to filter Disciplinary Action.
    """

    previous_data = request.GET.urlencode()

    if request.user.has_perm("recruitment.view_interviewschedule"):
        interviews = InterviewSchedule.objects.all().order_by("-interview_date")
    else:
        interviews = InterviewSchedule.objects.filter(
            employee_id=request.user.employee_get.id
        ).order_by("-interview_date")

    if request.GET.get("sortby"):
        interviews = sortby(request, interviews, "sortby")

    dis_filter = InterviewFilter(request.GET, queryset=interviews).qs

    page_number = request.GET.get("page")
    page_obj = paginator_qry(dis_filter, page_number)
    data_dict = parse_qs(previous_data)
    get_key_instances(InterviewSchedule, data_dict)
    now = timezone.now()
    interview_ids = [i.id for i in page_obj.object_list]
    has_incomplete = set(
        InterviewRound.objects.filter(
            interview_id__in=interview_ids, completed=False
        ).values_list("interview_id", flat=True)
    )
    has_any_round = set(
        InterviewRound.objects.filter(
            interview_id__in=interview_ids
        ).values_list("interview_id", flat=True)
    )
    rounds_done_ids = has_any_round - has_incomplete
    round_status_map = _build_round_status_map(interview_ids)
    for interview in page_obj.object_list:
        interview.round_status = round_status_map.get(interview.id)
    return render(
        request,
        "candidate/interview_list.html",
        {
            "data": page_obj,
            "pd": previous_data,
            "filter_dict": data_dict,
            "now": now,
            "rounds_done_ids": rounds_done_ids,
            "round_status_map": round_status_map,
        },
    )


@login_required
def interview_view(request):
    """
    This method render all interviews to the template
    """
    previous_data = request.GET.urlencode()

    if request.user.has_perm("recruitment.view_interviewschedule"):
        interviews = InterviewSchedule.objects.all().order_by("-interview_date")
    else:
        interviews = InterviewSchedule.objects.filter(
            employee_id=request.user.employee_get.id
        ).order_by("-interview_date")

    form = InterviewFilter(request.GET, queryset=interviews)
    page_number = request.GET.get("page")
    page_obj = paginator_qry(form.qs, page_number)
    previous_data = request.GET.urlencode()
    template = "candidate/interview_view.html"
    now = timezone.now()
    interview_ids = [i.id for i in page_obj.object_list]
    has_incomplete = set(
        InterviewRound.objects.filter(
            interview_id__in=interview_ids, completed=False
        ).values_list("interview_id", flat=True)
    )
    has_any_round = set(
        InterviewRound.objects.filter(
            interview_id__in=interview_ids
        ).values_list("interview_id", flat=True)
    )
    rounds_done_ids = has_any_round - has_incomplete
    round_status_map = _build_round_status_map(interview_ids)
    for interview in page_obj.object_list:
        interview.round_status = round_status_map.get(interview.id)

    return render(
        request,
        template,
        {
            "data": page_obj,
            "pd": previous_data,
            "f": form,
            "now": now,
            "rounds_done_ids": rounds_done_ids,
            "round_status_map": round_status_map,
        },
    )


@login_required
@manager_can_enter(perm="recruitment.change_interviewschedule")
def interview_employee_remove(request, interview_id, employee_id):
    """
    This view is used to remove the employees from the meeting ,
    Args:
        interview_id(int) : primarykey of the interview.
        employee_id(int) : primarykey of the employee
    """
    interview = InterviewSchedule.objects.filter(id=interview_id).first()
    interview.employee_id.remove(employee_id)
    messages.success(request, "Interviewer removed succesfully.")
    interview.save()
    return HttpResponse("<script>$('.filterButton')[0].click()</script>")


@login_required
def candidate_export(request):
    """
    This method is used to Export candidate data
    """
    if request.META.get("HTTP_HX_REQUEST"):
        export_column = CandidateExportForm()
        export_filter = CandidateFilter()
        content = {
            "export_filter": export_filter,
            "export_column": export_column,
        }
        return render(request, "candidate/export_filter.html", context=content)
    return export_data(
        request=request,
        model=Candidate,
        filter_class=CandidateFilter,
        form_class=CandidateExportForm,
        file_name="Candidate_export",
    )


@login_required
@permission_required(perm="recruitment.view_candidate")
def candidate_view_list(request):
    """
    This method renders all candidate on candidate_list.html template
    """
    previous_data = request.GET.urlencode()
    candidates = Candidate.objects.all()
    if request.GET.get("is_active") is None:
        candidates = candidates.filter(is_active=True)
    candidates = CandidateFilter(request.GET, queryset=candidates).qs
    return render(
        request,
        "candidate/candidate_list.html",
        {
            "data": paginator_qry(candidates, request.GET.get("page")),
            "pd": previous_data,
        },
    )


@login_required
@hx_request_required
@permission_required(perm="recruitment.view_candidate")
def candidate_view_card(request):
    """
    This method renders all candidate on candidate_card.html template
    """
    previous_data = request.GET.urlencode()
    candidates = Candidate.objects.all()
    if request.GET.get("is_active") is None:
        candidates = candidates.filter(is_active=True)
    candidates = CandidateFilter(request.GET, queryset=candidates).qs
    return render(
        request,
        "candidate/candidate_card.html",
        {
            "data": paginator_qry(candidates, request.GET.get("page")),
            "pd": previous_data,
        },
    )


@login_required
@permission_required(perm="recruitment.view_candidate")
def candidate_database_view(request):
    """
    Centralized candidate database with advanced search for the Employee module.
    """
    previous_data = request.GET.urlencode()
    candidates = Candidate.objects.filter(is_active=True)
    filter_obj = CandidateDatabaseFilter(request.GET, queryset=candidates)
    return render(
        request,
        "candidate/candidate_database.html",
        {
            "data": paginator_qry(filter_obj.qs, request.GET.get("page")),
            "f": filter_obj,
            "pd": previous_data,
        },
    )


@login_required
@permission_required(perm="recruitment.view_candidate")
def candidate_database_search(request):
    """
    HTMX search/filter endpoint for the candidate database view.
    """
    previous_data = request.GET.urlencode()
    candidates = Candidate.objects.filter(is_active=True)
    filter_obj = CandidateDatabaseFilter(request.GET, queryset=candidates)
    return render(
        request,
        "candidate/candidate_database_list.html",
        {
            "data": paginator_qry(filter_obj.qs, request.GET.get("page")),
            "pd": previous_data,
        },
    )


@login_required
@manager_can_enter(perm="recruitment.view_candidate")
def candidate_view_individual(request, cand_id, **kwargs):
    """
    This method is used to view profile of candidate.
    """
    candidate_obj = Candidate.find(cand_id)
    if not candidate_obj:
        messages.error(request, _("Candidate not found"))
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    mails = list(Candidate.objects.values_list("email", flat=True))
    # Query the User model to check if any email is present
    existing_emails = list(
        User.objects.filter(username__in=mails).values_list("email", flat=True)
    )
    ratings = candidate_obj.candidate_rating.all()
    documents = CandidateDocument.objects.filter(candidate_id=cand_id)

    # Onboarding sign-documents + uploaded certificates (post-offer portal flow)
    from recruitment.models import OfferLetter
    from recruitment.onboarding_docs import all_documents_approved
    candidate_offer = OfferLetter.objects.filter(candidate_id=candidate_obj).first()
    sign_documents = []
    portal_uploads = []
    all_docs_approved = False
    if candidate_offer:
        sign_documents = candidate_offer.sign_documents.all().order_by("batch", "sequence")
        portal_uploads = candidate_offer.portal_uploads.all().order_by("uploaded_at")
        all_docs_approved = all_documents_approved(candidate_offer)
    rating_list = []
    avg_rate = 0
    for rating in ratings:
        rating_list.append(rating.rating)
    if len(rating_list) != 0:
        avg_rate = round(sum(rating_list) / len(rating_list))

    # Retrieve the filtered candidate from the session
    filtered_candidate_ids = request.session.get("filtered_candidates", [])

    # Convert the string to an actual list of integers
    requests_ids = (
        ast.literal_eval(filtered_candidate_ids)
        if isinstance(filtered_candidate_ids, str)
        else filtered_candidate_ids
    )

    next_id = None
    previous_id = None

    for index, req_id in enumerate(requests_ids):
        if req_id == cand_id:
            if index == len(requests_ids) - 1:
                next_id = None
            else:
                next_id = requests_ids[index + 1]
            if index == 0:
                previous_id = None
            else:
                previous_id = requests_ids[index - 1]
            break

    now = timezone.now()

    return render(
        request,
        "candidate/individual.html",
        {
            "candidate": candidate_obj,
            "previous": previous_id,
            "next": next_id,
            "requests_ids": requests_ids,
            "emp_list": existing_emails,
            "average_rate": avg_rate,
            "documents": documents,
            "candidate_offer": candidate_offer,
            "sign_documents": sign_documents,
            "portal_uploads": portal_uploads,
            "all_docs_approved": all_docs_approved,
            "now": now,
        },
    )


@login_required
@manager_can_enter(
    perms=["recruitment.change_candidate", "onboarding.change_onboardingcandidate"]
)
def candidate_update(request, cand_id, **kwargs):
    """
    Used to update or change the candidate
    Args:
        id : candidate_id
    """
    try:
        candidate_obj = Candidate.objects.get(id=cand_id)
        form = CandidateCreationForm(instance=candidate_obj)
        path = "/recruitment/candidate-view"
        if request.method == "POST":
            form = CandidateCreationForm(
                request.POST, request.FILES, instance=candidate_obj
            )
            if form.is_valid():
                candidate_obj = form.save()
                if candidate_obj.stage_id is None:
                    candidate_obj.stage_id = Stage.objects.filter(
                        recruitment_id=candidate_obj.recruitment_id,
                        stage_type="initial",
                    ).first()
                if candidate_obj.stage_id is not None:
                    if (
                        candidate_obj.stage_id.recruitment_id
                        != candidate_obj.recruitment_id
                    ):
                        candidate_obj.stage_id = (
                            candidate_obj.recruitment_id.stage_set.filter(
                                stage_type="initial"
                            ).first()
                        )
                if request.GET.get("onboarding") == "True":
                    candidate_obj.hired = True
                    path = "/onboarding/candidates-view"
                candidate_obj.save()
                messages.success(request, _("Candidate Updated Successfully."))
                return redirect(path)
        return render(request, "candidate/candidate_create_form.html", {"form": form})
    except (Candidate.DoesNotExist, OverflowError):
        messages.error(request, _("Candidate Does not exists.."))
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@transaction.atomic
@login_required
@manager_can_enter(perm="recruitment.change_candidate")
def candidate_conversion(request, cand_id, **kwargs):
    candidate_obj = Candidate.find(cand_id)

    if not candidate_obj:
        messages.error(request, ("Candidate not found"))
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    if candidate_obj.converted_employee_id:
        messages.info(request, "This candidate is already converted to an employee.")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    user_exists = User.objects.filter(username=candidate_obj.email).exists()
    employee_exists = Employee.objects.filter(
        employee_user_id__username=candidate_obj.email
    ).exists()

    if user_exists:
        messages.error(request, ("User instance with this mail already exists"))
    elif not employee_exists:
        try:
            new_employee = Employee(
                employee_first_name=candidate_obj.name,
                email=candidate_obj.email,
                phone=candidate_obj.mobile,
                gender=candidate_obj.gender,
                is_directly_converted=True,
            )
            new_employee.save()

            work_info = new_employee.employee_work_info
            work_info.job_position_id = candidate_obj.job_position_id
            work_info.department_id = candidate_obj.job_position_id.department_id
            work_info.company_id = candidate_obj.recruitment_id.company_id
            work_info.save()

            Document.objects.bulk_create(
                [
                    Document(
                        title=doc.title,
                        employee_id=new_employee,
                        document=doc.document,
                        status=doc.status,
                        reject_reason=doc.reject_reason,
                    )
                    for doc in candidate_obj.candidatedocument_set.all()
                ]
            )

            candidate_obj.converted_employee_id = new_employee
            candidate_obj.save()
            messages.success(
                request,
                _("Candidate has been successfully converted into an employee."),
            )
        except IntegrityError:
            messages.warning(request, "An error occurred while creating employee data.")

    else:
        messages.info(request, "An employee with this email already exists")

    if "HTTP_HX_REQUEST" in request.META:
        return HttpResponse(status=204, headers={"HX-Refresh": "true"})

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required
@manager_can_enter(perm="recruitment.change_candidate")
def delete_profile_image(request, obj_id):
    """
    This method is used to delete the profile image of the candidate
    Args:
        obj_id : candidate instance id
    """
    candidate_obj = Candidate.objects.get(id=obj_id)
    try:
        if candidate_obj.profile:
            file_path = candidate_obj.profile.path
            absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)
            os.remove(absolute_path)
            candidate_obj.profile = None
            candidate_obj.save()
            messages.success(request, _("Profile image removed."))
    except Exception:
        pass
    return redirect("rec-candidate-update", cand_id=obj_id)


@login_required
@permission_required(perm="recruitment.view_history")
def candidate_history(request, cand_id):
    """
    This method is used to view candidate stage changes
    Args:
        id : candidate_id
    """
    candidate_obj = Candidate.objects.get(id=cand_id)
    candidate_history_queryset = candidate_obj.history.all()
    return render(
        request,
        "candidate/candidate_history.html",
        {"history": candidate_history_queryset},
    )


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.change_candidate")
def form_send_mail(request, cand_id=None):
    """
    This method is used to render the bootstrap modal content body form
    """
    candidate_obj = None
    stage_id = None
    if request.GET.get("stage_id"):
        stage_id = eval_validate(request.GET.get("stage_id"))
    if cand_id:
        candidate_obj = Candidate.objects.get(id=cand_id)
    candidates = Candidate.objects.all()
    if stage_id and isinstance(stage_id, int):
        candidates = candidates.filter(stage_id__id=stage_id)
    else:
        stage_id = None

    templates = FitsMailTemplate.objects.all()
    return render(
        request,
        "pipeline/pipeline_components/send_mail.html",
        {
            "cand": candidate_obj,
            "templates": templates,
            "candidates": candidates,
            "stage_id": stage_id,
            "searchWords": MailTemplateForm().get_template_language(),
        },
    )


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.add_interviewschedule")
def interview_schedule(request, cand_id):
    """
    This method is used to Schedule interview to candidate
    Args:
        cand_id : candidate instance id
    """
    candidate = Candidate.objects.get(id=cand_id)
    candidates = Candidate.objects.filter(id=cand_id)
    template = "pipeline/pipeline_components/schedule_interview.html"
    form = ScheduleInterviewForm(initial={"candidate_id": candidate})
    form.fields["candidate_id"].queryset = candidates
    if request.method == "POST":
        form = ScheduleInterviewForm(request.POST)
        if form.is_valid():
            form.save()
            emp_ids = form.cleaned_data["employee_id"]
            cand_id = form.cleaned_data["candidate_id"]
            interview_date = form.cleaned_data["interview_date"]
            interview_time = form.cleaned_data["interview_time"]
            users = [employee.employee_user_id for employee in emp_ids]
            notify.send(
                request.user.employee_get,
                recipient=users,
                verb=f"You are scheduled as an interviewer for an interview with {cand_id.name} on {interview_date} at {interview_time}.",
                verb_ar=f"أنت مجدول كمقابلة مع {cand_id.name} يوم {interview_date} في توقيت {interview_time}.",
                verb_de=f"Sie sind als Interviewer für ein Interview mit {cand_id.name} am {interview_date} um {interview_time} eingeplant.",
                verb_es=f"Estás programado como entrevistador para una entrevista con {cand_id.name} el {interview_date} a las {interview_time}.",
                verb_fr=f"Vous êtes programmé en tant qu'intervieweur pour un entretien avec {cand_id.name} le {interview_date} à {interview_time}.",
                icon="people-circle",
                redirect=reverse("interview-view"),
            )

            messages.success(request, "Interview Scheduled successfully.")
            num_rounds = int(request.POST.get("rounds_count") or 1)
            num_rounds = min(num_rounds, 8)
            interview = form.instance
            interview.num_rounds = num_rounds
            interview.save(update_fields=["num_rounds"])
            from employee.models import Employee as _Emp
            default_labels = ["HR Screen", "Technical", "Final", "Culture Fit", "Management", "Director", "CEO", "Offer"]
            for i in range(1, num_rounds + 1):
                label = request.POST.get(f"round_label_{i}") or (default_labels[i - 1] if i <= len(default_labels) else f"Round {i}")
                interviewer_ids = (
                    request.POST.getlist(f"round_interviewer_{i}[]")
                    or request.POST.getlist(f"round_interviewer_{i}")
                )
                interviewer_ids = [x for x in interviewer_ids if x]
                round_date = request.POST.get(f"round_date_{i}") or None
                round_time = request.POST.get(f"round_time_{i}") or None
                interviewer_obj = None
                if interviewer_ids:
                    try:
                        interviewer_obj = _Emp.objects.get(id=interviewer_ids[0])
                    except _Emp.DoesNotExist:
                        pass
                InterviewRound.objects.get_or_create(
                    interview=interview, round_number=i,
                    defaults={
                        "label": label,
                        "interviewer": interviewer_obj,
                        "round_date": round_date,
                        "round_time": round_time,
                    },
                )
            interview_url = reverse("interview-view")
            return HttpResponse(
                f"<script>window.location.href='{interview_url}'</script>"
            )
    return render(request, template, {"form": form, "cand_id": cand_id, "candidate": candidate})


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.add_interviewschedule")
def create_interview_schedule(request):
    """
    This method is used to Schedule interview to candidate
    Args:
        cand_id : candidate instance id
    """
    candidates = Candidate.objects.all()
    template = "candidate/interview_form.html"
    form = ScheduleInterviewForm()
    form.fields["candidate_id"].queryset = candidates
    if request.method == "POST":
        form = ScheduleInterviewForm(request.POST)
        if form.is_valid():
            form.save()
            emp_ids = form.cleaned_data["employee_id"]
            cand_id = form.cleaned_data["candidate_id"]
            interview_date = form.cleaned_data["interview_date"]
            interview_time = form.cleaned_data["interview_time"]
            users = [employee.employee_user_id for employee in emp_ids]
            notify.send(
                request.user.employee_get,
                recipient=users,
                verb=f"You are scheduled as an interviewer for an interview with {cand_id.name} on {interview_date} at {interview_time}.",
                verb_ar=f"أنت مجدول كمقابلة مع {cand_id.name} يوم {interview_date} في توقيت {interview_time}.",
                verb_de=f"Sie sind als Interviewer für ein Interview mit {cand_id.name} am {interview_date} um {interview_time} eingeplant.",
                verb_es=f"Estás programado como entrevistador para una entrevista con {cand_id.name} el {interview_date} a las {interview_time}.",
                verb_fr=f"Vous êtes programmé en tant qu'intervieweur pour un entretien avec {cand_id.name} le {interview_date} à {interview_time}.",
                icon="people-circle",
                redirect=reverse("interview-view"),
            )

            messages.success(request, "Interview Scheduled successfully.")
            # Save interview rounds
            labels = [l.strip() for l in request.POST.getlist("round_label[]") if l.strip()]
            for idx, label in enumerate(labels, start=1):
                InterviewRound.objects.create(
                    interview=form.instance,
                    round_number=idx,
                    label=label,
                )
            # Send email invite with .ics to panelists and candidate
            try:
                import threading
                from recruitment.email_utils import email_interview_invite, email_candidate_interview_invite
                interview = form.instance

                def _send_invites():
                    panelist_emails = []
                    for emp in interview.employee_id.all():
                        user = getattr(emp, "employee_user_id", None)
                        if user and user.email:
                            panelist_emails.append(user.email)
                    if panelist_emails:
                        email_interview_invite(interview, panelist_emails)
                    email_candidate_interview_invite(interview)

                threading.Thread(target=_send_invites, daemon=True).start()
            except Exception:
                pass
    return render(request, template, {"form": form})


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.delete_interviewschedule")
def interview_delete(request, interview_id):
    """
    Deletes an interview schedule.
    Args:
        interview_id: InterviewSchedule instance ID
    """
    view = request.GET.get("view", "false")

    try:
        InterviewSchedule.objects.get(id=interview_id).delete()
        messages.success(request, _("Interview deleted successfully."))
    except:
        messages.error(request, _("Scheduled Interview not found"))

    return HttpResponse(
        "<script>$('.filterButton')[0].click()</script>"
        if view == "true"
        else "<script>window.location.reload()</script>"
    )


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.change_interviewschedule")
def interview_edit(request, interview_id):
    """
    This method is used to Edit Schedule interview
    Args:
        interview_id : interview schedule instance id
    """
    interview = InterviewSchedule.objects.get(id=interview_id)
    view = request.GET["view"]
    if view == "true":
        candidates = Candidate.objects.all()
        view = "true"
    else:
        candidates = Candidate.objects.filter(id=interview.candidate_id.id)
        view = "false"
    template = "pipeline/pipeline_components/schedule_interview_update.html"
    form = ScheduleInterviewForm(instance=interview)
    form.fields["candidate_id"].queryset = candidates
    if request.method == "POST":
        form = ScheduleInterviewForm(request.POST, instance=interview)
        if form.is_valid():
            emp_ids = form.cleaned_data["employee_id"]
            cand_id = form.cleaned_data["candidate_id"]
            interview_date = form.cleaned_data["interview_date"]
            interview_time = form.cleaned_data["interview_time"]
            form.save()
            # Save per-round data (interviewer, date, time, completed)
            from django.utils import timezone as tz
            from employee.models import Employee as _Emp
            for round_obj in interview.rounds.all():
                rid = round_obj.id
                new_label = request.POST.get(f"round_{rid}_label", "").strip()
                if new_label:
                    round_obj.label = new_label
                completed = request.POST.get(f"round_{rid}_completed") == "on"
                interviewer_ids = (
                    request.POST.getlist(f"round_{rid}_interviewer[]")
                    or request.POST.getlist(f"round_{rid}_interviewer")
                )
                interviewer_ids = [x for x in interviewer_ids if x]
                round_date = request.POST.get(f"round_{rid}_date") or None
                round_time = request.POST.get(f"round_{rid}_time") or None
                interviewer_obj = None
                if interviewer_ids:
                    try:
                        interviewer_obj = _Emp.objects.get(id=interviewer_ids[0])
                    except _Emp.DoesNotExist:
                        pass
                round_obj.interviewer = interviewer_obj
                round_obj.round_date = round_date
                round_obj.round_time = round_time
                if completed and not round_obj.completed:
                    round_obj.completed = True
                    round_obj.completed_at = tz.now()
                elif not completed and round_obj.completed:
                    round_obj.completed = False
                    round_obj.completed_at = None
                round_obj.save()
            users = [employee.employee_user_id for employee in emp_ids]
            notify.send(
                request.user.employee_get,
                recipient=users,
                verb=f"You are scheduled as an interviewer for an interview with {cand_id.name} on {interview_date} at {interview_time}.",
                verb_ar=f"أنت مجدول كمقابلة مع {cand_id.name} يوم {interview_date} في توقيت {interview_time}.",
                verb_de=f"Sie sind als Interviewer für ein Interview mit {cand_id.name} am {interview_date} um {interview_time} eingeplant.",
                verb_es=f"Estás programado como entrevistador para una entrevista con {cand_id.name} el {interview_date} a las {interview_time}.",
                verb_fr=f"Vous êtes programmé en tant qu'intervieweur pour un entretien avec {cand_id.name} le {interview_date} à {interview_time}.",
                icon="people-circle",
                redirect=reverse("interview-view"),
            )
            messages.success(request, "Interview updated successfully.")
            return HttpResponse("<script>window.location.reload()</script>")
    # Auto-create rounds if none exist yet (e.g. older interviews)
    if not interview.rounds.exists() and interview.num_rounds:
        default_labels = ["HR Screen", "Technical", "Final", "Culture Fit", "Management", "Director", "CEO", "Offer", "Background", "Reference"]
        for i in range(1, interview.num_rounds + 1):
            label = default_labels[i - 1] if i <= len(default_labels) else f"Round {i}"
            InterviewRound.objects.get_or_create(
                interview=interview, round_number=i,
                defaults={"label": label},
            )
    rounds = interview.rounds.all().order_by("round_number")
    return render(
        request,
        template,
        {
            "form": form,
            "interview_id": interview_id,
            "view": view,
            "rounds": rounds,
        },
    )


def get_managers(request):
    from employee.models import Employee as EmployeeModel
    cand_id = request.GET.get("cand_id")
    preselected = []

    if cand_id:
        try:
            candidate = Candidate.objects.select_related(
                "recruitment_id__raised_by"
            ).get(id=cand_id)
            raised_by = getattr(candidate.recruitment_id, "raised_by", None)
            if raised_by:
                # Build chain: raiser + their managers, stop before superusers
                chain = [raised_by]
                current = raised_by
                visited = {raised_by.id}
                while True:
                    mgr = current.get_reporting_manager()
                    if not mgr or mgr.id in visited:
                        break
                    user = getattr(mgr, "employee_user_id", None)
                    if user and user.is_superuser:
                        break
                    chain.append(mgr)
                    visited.add(mgr.id)
                    current = mgr
                preselected = [emp.id for emp in chain]
        except Candidate.DoesNotExist:
            pass

    employees = EmployeeModel.objects.filter(is_active=True).order_by(
        "employee_first_name", "employee_last_name"
    )
    employees_dict = {emp.id: emp.get_full_name() for emp in employees}
    return JsonResponse({"employees": employees_dict, "preselected": preselected})


@login_required
@manager_can_enter(perm="recruitment.change_candidate")
def send_acknowledgement(request):
    """
    This method is used to send acknowledgement mail to the candidate
    """
    candidate_id = request.POST.get("id")
    subject = request.POST.get("subject")
    bdy = request.POST.get("body")
    candidate_ids = request.POST.getlist("candidates")
    candidates = Candidate.objects.filter(id__in=candidate_ids)

    other_attachments = request.FILES.getlist("other_attachments")

    if candidate_id:
        candidate_obj = Candidate.objects.filter(id=candidate_id)
    else:
        candidate_obj = Candidate.objects.none()
    candidates = (candidates | candidate_obj).distinct()

    template_attachment_ids = request.POST.getlist("template_attachments")
    for candidate in candidates:
        attachments = [
            (file.name, file.read(), file.content_type) for file in other_attachments
        ]
        bodys = list(
            FitsMailTemplate.objects.filter(id__in=template_attachment_ids).values_list(
                "body", flat=True
            )
        )
        for html in bodys:
            # due to not having solid template we first need to pass the context
            template_bdy = template.Template(html)
            context = template.Context(
                {"instance": candidate, "self": request.user.employee_get}
            )
            render_bdy = template_bdy.render(context)
            attachments.append(
                (
                    "Document",
                    generate_pdf(render_bdy, {}, path=False, title="Document").content,
                    "application/pdf",
                )
            )

        template_bdy = template.Template(bdy)
        context = template.Context(
            {"instance": candidate, "self": request.user.employee_get}
        )
        render_bdy = template_bdy.render(context)
        to = candidate.email
        email = EmailMessage(
            subject=subject,
            body=render_bdy,
            to=[to],
        )
        email.content_subtype = "html"

        email.attachments = attachments
        try:
            email.send()
            messages.success(request, "Mail sent to candidate")
        except Exception as e:
            logger.exception(e)
            messages.error(request, "Something went wrong")
    return HttpResponse("<script>window.location.reload()</script>")


@login_required
@manager_can_enter(perm="recruitment.change_candidate")
def candidate_sequence_update(request):
    """
    This method is used to update the sequence of candidate
    """
    sequence_data = json.loads(request.POST["sequenceData"])
    for cand_id, seq in sequence_data.items():
        cand = Candidate.objects.get(id=cand_id)
        cand.sequence = seq
        cand.save()

    return JsonResponse({"message": "Sequence updated", "type": "info"})


@login_required
@recruitment_manager_can_enter(perm="recruitment.change_stage")
def stage_sequence_update(request):
    """
    This method is used to update the sequence of the stages
    """
    sequence_data = json.loads(request.POST["sequence"])
    for stage_id, seq in sequence_data.items():
        stage = Stage.objects.get(id=stage_id)
        stage.sequence = seq
        stage.save()
    return JsonResponse({"type": "success", "message": "Stage sequence updated"})


@login_required
def candidate_select(request):
    """
    This method is used for select all in candidate
    """
    page_number = request.GET.get("page")

    if page_number == "all":
        employees = Candidate.objects.filter(is_active=True)
    else:
        employees = Candidate.objects.all()

    employee_ids = [str(emp.id) for emp in employees]
    total_count = employees.count()

    context = {"employee_ids": employee_ids, "total_count": total_count}

    return JsonResponse(context, safe=False)


@login_required
def candidate_select_filter(request):
    """
    This method is used to select all filtered candidates
    """
    page_number = request.GET.get("page")
    filtered = request.GET.get("filter")
    filters = json.loads(filtered) if filtered else {}

    if page_number == "all":
        candidate_filter = CandidateFilter(filters, queryset=Candidate.objects.all())

        # Get the filtered queryset
        filtered_candidates = candidate_filter.qs

        employee_ids = [str(emp.id) for emp in filtered_candidates]
        total_count = filtered_candidates.count()

        context = {"employee_ids": employee_ids, "total_count": total_count}

        return JsonResponse(context)


@login_required
def create_candidate_rating(request, cand_id):
    """
    This method is used to create rating for the candidate
    Args:
        cand_id : candidate instance id
    """
    cand_id = cand_id
    candidate = Candidate.objects.get(id=cand_id)
    employee_id = request.user.employee_get
    rating = request.POST.get("rating")
    CandidateRating.objects.create(
        candidate_id=candidate, rating=rating, employee_id=employee_id
    )
    return redirect(recruitment_pipeline)


@login_required
def received_recruitments(request):
    """
    Show recruitments raised by employees: pending approval and ready to publish.
    Managers can approve/reject. HR can publish approved recruitments.
    """
    current_employee = getattr(request.user, "employee_get", None)
    from base.models import HRUser
    is_hr = request.user.is_superuser or (
        current_employee is not None
        and HRUser.objects.filter(employee=current_employee, is_hr_staff=True).exists()
    )
    
    # Repair missing approvals on ALL employee-raised recruitments — including
    # already-approved/rejected ones whose chain was never written (e.g. bulk
    # uploads created before chain auto-creation existed). Backfilling lets the
    # workflow modal render the full chain instead of just "Raised by".
    repair_recs = Recruitment.objects.filter(
        raised_from_employee=True,
        approval_status__in=["pending", "approved", "rejected"],
    ).distinct()
    for rec in repair_recs:
        repair_employee_recruitment_approvals(rec)

    # Pending recruitments where the current user is the NEXT approver in the chain.
    # Enforces sequential approval — earlier steps must be approved first.
    from recruitment.models import RecruitmentApproval
    from django.db.models import OuterRef, Subquery, IntegerField

    next_step_seq = (
        RecruitmentApproval.objects
        .filter(recruitment=OuterRef("pk"), status="pending")
        .order_by("sequence")
        .values("sequence")[:1]
    )
    my_pending_seq = (
        RecruitmentApproval.objects
        .filter(
            recruitment=OuterRef("pk"),
            status="pending",
            approver__employee_user_id=request.user,
        )
        .order_by("sequence")
        .values("sequence")[:1]
    )
    pending_recruitments = (
        Recruitment.objects.filter(
            raised_from_employee=True,
            approval_status="pending",
        )
        .annotate(
            _next_step=Subquery(next_step_seq, output_field=IntegerField()),
            _my_step=Subquery(my_pending_seq, output_field=IntegerField()),
        )
        .filter(_my_step=F("_next_step"))
        .select_related("raised_by")
        .prefetch_related("approvals__approver")
        .distinct()
    )
    
    # Get approved recruitments ready for HR to publish, newest-action first
    ready_recruitments = (
        Recruitment.objects.filter(
            raised_from_employee=True,
            approval_status="approved",
        )
        .select_related("raised_by")
        .prefetch_related("approvals__approver")
        .annotate(last_action_at=Max("approvals__approved_at"))
        .order_by(F("last_action_at").desc(nulls_last=True), "-created_at")
    )

    _oman = ZoneInfo("Asia/Muscat")

    def _fmt(dt):
        if not dt:
            return ""
        return dt.astimezone(_oman).strftime("%-d %b %Y, %-I:%M %p")

    def _approver_label(approver):
        """Friendly labels for the demo flow accounts; everyone else gets their real name."""
        if not approver:
            return "—"
        user = getattr(approver, "employee_user_id", None)
        email = (getattr(user, "email", "") or getattr(approver, "email", "") or "").lower()
        DEMO_LABELS = {
            "hr@fits.com":      "HR",
            "cfo@fits.com":     "CFO",
            "ceo@fits.com":     "CEO",
            "divhead@fits.com": "Division Head",
        }
        return DEMO_LABELS.get(email, str(approver))

    ready_data = []
    for rec in ready_recruitments:
        _action_dt = rec.last_action_at or rec.created_at
        ready_data.append({
            "id": rec.id,
            "raised_by": str(rec.raised_by) if rec.raised_by else "",
            "created_at": _fmt(rec.created_at),
            "last_action_at": _fmt(_action_dt),
            "last_action_date_iso": _action_dt.astimezone(_oman).strftime("%Y-%m-%d") if _action_dt else "",
            "hr_feedback": rec.hr_feedback or "",
            "is_published": rec.is_published,
            "published_to_linkedin": rec.published_to_linkedin,
            "published_to_bayt": rec.published_to_bayt,
            "bayt_external_id": rec.bayt_external_id or "",
            "published_to_naukrigulf": rec.published_to_naukrigulf,
            "naukrigulf_external_id": rec.naukrigulf_external_id or "",
            "approvals": [
                {
                    "approver": _approver_label(a.approver),
                    "approver_id": a.approver_id,
                    "sequence": a.sequence,
                    "status": a.status,
                    "reason": a.comments or "",
                    "approved_at": _fmt(a.approved_at),
                }
                for a in rec.approvals.all()
            ],
        })

    pending_data = []
    for rec in pending_recruitments:
        pending_data.append({
            "id": rec.id,
            "raised_by": str(rec.raised_by) if rec.raised_by else "",
            "created_at": _fmt(rec.created_at),
            "approvals": [
                {
                    "approver": _approver_label(a.approver),
                    "approver_id": a.approver_id,
                    "sequence": a.sequence,
                    "status": a.status,
                    "reason": a.comments or "",
                    "approved_at": _fmt(a.approved_at),
                }
                for a in rec.approvals.all()
            ],
        })

    def _acted_payload(rec):
        return {
            "id": rec.id,
            "raised_by": str(rec.raised_by) if rec.raised_by else "",
            "created_at": _fmt(rec.created_at),
            "approvals": [
                {
                    "approver": _approver_label(a.approver),
                    "approver_id": a.approver_id,
                    "sequence": a.sequence,
                    "status": a.status,
                    "reason": a.comments or "",
                    "approved_at": _fmt(a.approved_at),
                }
                for a in rec.approvals.all()
            ],
        }

    # Attach Oman-timezone strings directly to each record for template use
    for rec in ready_recruitments:
        _dt = rec.last_action_at or rec.created_at
        rec.oman_date_iso = _dt.astimezone(_oman).strftime("%Y-%m-%d") if _dt else ""
        rec.oman_last_action = _fmt(_dt)

    # Recruitments where the current user has already approved or rejected.
    # Shown so approvers (e.g. Aditya) can still see requests they acted on,
    # even when they aren't HR and the request has moved on or been finalised.
    acted_recruitments = (
        Recruitment.objects.filter(
            raised_from_employee=True,
            approvals__approver__employee_user_id=request.user,
            approvals__status__in=["approved", "rejected"],
        )
        .select_related("raised_by")
        .prefetch_related("approvals__approver")
        .annotate(last_action_at=Max("approvals__approved_at"))
        .order_by(F("last_action_at").desc(nulls_last=True), "-created_at")
        .distinct()
    )
    for rec in acted_recruitments:
        _dt = rec.last_action_at or rec.created_at
        rec.oman_last_action = _fmt(_dt)
        my_action = None
        for a in rec.approvals.all():
            if (
                a.approver
                and a.approver.employee_user_id_id == request.user.id
                and a.status in ("approved", "rejected")
            ):
                my_action = a
                break
        rec.my_action_status = my_action.status if my_action else ""
        rec.my_action_at = _fmt(my_action.approved_at) if my_action else ""
        rec.my_action_reason = (my_action.comments or "") if my_action else ""

    acted_data = [_acted_payload(rec) for rec in acted_recruitments]

    return render(
        request,
        "recruitment/received_recruitments.html",
        {
            "pending_recruitments": pending_recruitments,
            "ready_recruitments": ready_recruitments,
            "acted_recruitments": acted_recruitments,
            "ready_recruitments_json": json.dumps(ready_data),
            "requests_json": json.dumps(pending_data),
            "acted_recruitments_json": json.dumps(acted_data),
            "current_employee": current_employee,
            "is_hr": is_hr,
        },
    )


@login_required
@require_http_methods(["POST"])
@login_required
@require_http_methods(["POST"])
def approve_employee_recruitment(request, approval_id):
    """
    Approve a pending employee-raised recruitment approval step.
    """
    approval = get_object_or_404(RecruitmentApproval, id=approval_id)
    if approval.status != "pending":
        messages.error(request, _("This approval request has already been processed."))
        return redirect("received-recruitments")

    current_employee = getattr(request.user, "employee_get", None)
    if not (request.user.is_superuser or approval.approver == current_employee):
        raise PermissionDenied

    approval.status = "approved"
    approval.approved_at = timezone.now()
    sig = request.POST.get("signature_data", "").strip()
    if sig:
        approval.signature_image = sig
    approval.save()

    next_approval = RecruitmentApproval.objects.filter(
        recruitment=approval.recruitment,
        sequence__gt=approval.sequence,
        status="pending",
    ).order_by("sequence").first()

    if next_approval:
        recipient = getattr(next_approval.approver, "employee_user_id", None)
        if recipient:
            notify.send(
                request.user.employee_get,
                recipient=[recipient],
                verb=_("Recruitment request waiting for your approval."),
                icon="people-circle",
                redirect=reverse("received-recruitments"),
            )
    else:
        recruitment = approval.recruitment

        # mark approved
        recruitment.approval_status = "approved"
        recruitment.save()

        # Bulk request: spawn one published campaign per position line.
        if getattr(recruitment, "is_bulk", False):
            fanout_bulk_recruitment(recruitment)

        # notify employee
        recipient = (
            [recruitment.raised_by.employee_user_id]
            if recruitment.raised_by
            else []
        )
        if recipient:
            notify.send(
                request.user.employee_get,
                recipient=recipient,
                verb=_("Your recruitment request has been approved."),
                icon="check-circle",
                redirect=reverse("raise-recruitment"),
            )

        # notify HR (superusers), but not the person who raised the recruitment
        raised_by_user = recruitment.raised_by.employee_user_id if recruitment.raised_by else None
        hr_users = User.objects.filter(is_superuser=True)
        for user in hr_users:
            if raised_by_user and user.pk == raised_by_user.pk:
                continue
            notify.send(
                request.user.employee_get,
                recipient=[user],
                verb=_("Recruitment is ready to publish."),
                icon="briefcase",
                redirect=reverse("received-recruitments"),
            )

    messages.success(request, _("Recruitment approval updated."))
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return HttpResponseRedirect(referer)
    return redirect("received-recruitments")

@login_required
@require_http_methods(["POST"])
def reject_employee_recruitment(request, approval_id):
    """
    Reject a pending employee-raised recruitment approval step.
    """
    approval = get_object_or_404(RecruitmentApproval, id=approval_id)
    if approval.status != "pending":
        messages.error(request, _("This approval request has already been processed."))
        return redirect("received-recruitments")

    current_employee = getattr(request.user, "employee_get", None)
    if not (request.user.is_superuser or approval.approver == current_employee):
        raise PermissionDenied


    reason = request.POST.get("comments") or request.POST.get("reason") or ""
    approval.comments = reason
    
    approval.status = "rejected"
    approval.approved_at = timezone.now()
    approval.save()

    remaining_approvals = RecruitmentApproval.objects.filter(
        recruitment=approval.recruitment,
        status="pending",
    ).exclude(id=approval.id)
    if remaining_approvals.exists():
        remaining_approvals.update(status="rejected", approved_at=timezone.now())

    approval.recruitment.approval_status = "rejected"
    approval.recruitment.save(update_fields=["approval_status"])

    recipient = (
        [approval.recruitment.raised_by.employee_user_id]
        if approval.recruitment.raised_by
        else []
    )
    if recipient:
        notify.send(
            request.user.employee_get,
            recipient=recipient,
            verb=_("Your recruitment request has been rejected."),
            icon="x-circle",
            redirect=reverse("raise-recruitment"),
        )

    messages.success(request, _("Recruitment rejection recorded."))
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return HttpResponseRedirect(referer)
    return redirect("received-recruitments")


@login_required
@require_http_methods(["POST"])
def query_employee_recruitment(request, approval_id):
    """
    Send the request back to the requester with a query, WITHOUT consuming
    the current approver's step. The approver row is parked as `queried`
    and the recruitment is set to `queried`. The requester can answer and
    re-submit, which restores the same approver as pending.
    """
    approval = get_object_or_404(RecruitmentApproval, id=approval_id)
    if approval.status != "pending":
        messages.error(request, _("This approval request has already been processed."))
        return redirect("received-recruitments")

    current_employee = getattr(request.user, "employee_get", None)
    if not (request.user.is_superuser or approval.approver == current_employee):
        raise PermissionDenied

    query_text = (request.POST.get("comments") or request.POST.get("query") or "").strip()
    if not query_text:
        messages.error(request, _("Please enter your query before sending back."))
        referer = request.META.get("HTTP_REFERER")
        return HttpResponseRedirect(referer) if referer else redirect("received-recruitments")

    approval.status = "queried"
    approval.comments = query_text
    approval.approved_at = timezone.now()
    approval.save(update_fields=["status", "comments", "approved_at"])

    recruitment_obj = approval.recruitment
    recruitment_obj.approval_status = "queried"
    recruitment_obj.hr_feedback = query_text
    recruitment_obj.save(update_fields=["approval_status", "hr_feedback"])

    recipient = (
        [recruitment_obj.raised_by.employee_user_id]
        if recruitment_obj.raised_by
        else []
    )
    if recipient:
        notify.send(
            request.user.employee_get,
            recipient=recipient,
            verb=_("Your recruitment request has a query from an approver. Please respond."),
            icon="help-circle",
            redirect=reverse("raise-recruitment"),
        )

    messages.success(request, _("Query sent back to the requester."))
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return HttpResponseRedirect(referer)
    return redirect("received-recruitments")


@login_required
@require_http_methods(["POST"])
def resubmit_employee_recruitment(request, rec_id):
    """
    Requester responds to a queried recruitment and pushes it back into the
    chain. The previously queried approval row is reset to pending; the
    requester's response is appended to that row's comments.
    """
    recruitment_obj = get_object_or_404(Recruitment, id=rec_id)

    current_employee = getattr(request.user, "employee_get", None)
    if not (
        request.user.is_superuser
        or (recruitment_obj.raised_by and recruitment_obj.raised_by == current_employee)
    ):
        raise PermissionDenied

    if recruitment_obj.approval_status != "queried":
        messages.error(request, _("This request is not in a queried state."))
        return redirect("raise-recruitment")

    response_text = (request.POST.get("response") or request.POST.get("comments") or "").strip()
    if not response_text:
        messages.error(request, _("Please enter a response to the query."))
        return redirect("raise-recruitment")

    queried_row = RecruitmentApproval.objects.filter(
        recruitment=recruitment_obj, status="queried"
    ).order_by("sequence").first()

    if not queried_row:
        messages.error(request, _("No queried approval step found."))
        return redirect("raise-recruitment")

    original_query = queried_row.comments or ""
    queried_row.status = "pending"
    queried_row.approved_at = None
    queried_row.comments = (
        f"{original_query}\n\n--- Requester response ---\n{response_text}"
        if original_query
        else response_text
    )
    queried_row.save(update_fields=["status", "approved_at", "comments"])

    recruitment_obj.approval_status = "pending"
    recruitment_obj.save(update_fields=["approval_status"])

    recipient = getattr(queried_row.approver, "employee_user_id", None)
    if recipient:
        notify.send(
            request.user.employee_get,
            recipient=[recipient],
            verb=_("Requester has responded to your query. Please review."),
            icon="chatbubble-ellipses",
            redirect=reverse("received-recruitments"),
        )

    messages.success(request, _("Response submitted. Request returned to the approver."))
    return redirect("raise-recruitment")


@login_required
@permission_required(perm="recruitment.change_recruitment")
@require_http_methods(["POST"])
def send_hr_feedback(request, rec_id):
    """
    HR sends feedback to a specific approver, resetting that approver
    and all subsequent approvals back to pending.
    """
    recruitment_obj = get_object_or_404(Recruitment, id=rec_id)

    if recruitment_obj.approval_status != "approved":
        messages.error(request, _("Cannot send feedback: recruitment is not in approved state."))
        return redirect("received-recruitments")

    approver_id = request.POST.get("approver_id", "").strip()
    feedback_text = request.POST.get("feedback", "").strip()

    if not approver_id or not feedback_text:
        messages.error(request, _("Both approver and feedback text are required."))
        return redirect("received-recruitments")

    try:
        approver_id = int(approver_id)
    except ValueError:
        messages.error(request, _("Invalid approver."))
        return redirect("received-recruitments")

    target_approval = RecruitmentApproval.objects.filter(
        recruitment=recruitment_obj,
        approver_id=approver_id,
    ).order_by("sequence").first()

    if not target_approval:
        messages.error(request, _("Selected approver is not part of this recruitment's workflow."))
        return redirect("received-recruitments")

    RecruitmentApproval.objects.filter(
        recruitment=recruitment_obj,
        sequence__gte=target_approval.sequence,
    ).update(status="pending", approved_at=None, comments="")

    recruitment_obj.hr_feedback = feedback_text
    recruitment_obj.approval_status = "pending"
    recruitment_obj.save(update_fields=["hr_feedback", "approval_status"])

    recipient_user = getattr(target_approval.approver, "employee_user_id", None)
    if recipient_user:
        notify.send(
            request.user.employee_get,
            recipient=[recipient_user],
            verb=_("HR has sent feedback on a recruitment. Please review and re-approve."),
            icon="chatbubble-ellipses",
            redirect=reverse("received-recruitments"),
        )

    messages.success(request, _("Feedback sent. Recruitment returned to approval workflow."))
    return redirect("received-recruitments")


@login_required
@permission_required(perm="recruitment.change_recruitment")
def edit_employee_recruitment(request, rec_id):
    """
    HR edits title, description (JD), and vacancy on an approved-but-unpublished
    employee-raised recruitment.
    GET  -> returns JSON of current field values.
    POST -> saves updated values, returns JSON success/error.
    """
    recruitment_obj = get_object_or_404(Recruitment, id=rec_id)

    if request.method == "GET":
        return JsonResponse({
            "id": recruitment_obj.id,
            "title": recruitment_obj.title or "",
            "description": recruitment_obj.description or "",
            "vacancy": recruitment_obj.vacancy if recruitment_obj.vacancy is not None else 0,
        })

    title = request.POST.get("title", "").strip()
    description = request.POST.get("description", "").strip()
    vacancy_raw = request.POST.get("vacancy", "").strip()

    errors = {}
    if not title:
        errors["title"] = str(_("Title is required."))
    elif len(title) > 50:
        errors["title"] = str(_("Title must be 50 characters or fewer."))
    if not description:
        errors["description"] = str(_("Job description is required."))
    try:
        vacancy = int(vacancy_raw)
        if vacancy < 0:
            errors["vacancy"] = str(_("Vacancy must be 0 or more."))
    except (TypeError, ValueError):
        errors["vacancy"] = str(_("Enter a valid number."))
        vacancy = None

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    recruitment_obj.title = title
    recruitment_obj.description = description
    recruitment_obj.vacancy = vacancy
    recruitment_obj.save(update_fields=["title", "description", "vacancy"])

    return JsonResponse({"success": True})


@login_required
@require_http_methods(["POST"])

def delete_employee_recruitment(request, rec_id):
    recruitment_obj = get_object_or_404(Recruitment, id=rec_id)
    current_employee = getattr(request.user, "employee_get", None)

    # ✅ permission check
    if not (
        request.user.is_superuser
        or (recruitment_obj.raised_by and recruitment_obj.raised_by == current_employee)
    ):
        raise PermissionDenied

    # ❌ prevent deletion of published (except superuser)
    if recruitment_obj.is_published and not request.user.is_superuser:
        messages.error(request, "Published recruitments cannot be deleted here.")
        return redirect("received-recruitments")

    # 🔥 TRY LINKEDIN DELETE BUT DON'T BLOCK
    try:
        delete_post(recruitment_obj)
    except Exception as e:
        print("LinkedIn delete failed:", e)
        messages.warning(request, "LinkedIn post could not be deleted, but recruitment will be removed.")

    # ✅ ALWAYS DELETE FROM DB
    try:
        recruitment_obj.delete()
        messages.success(request, "Recruitment deleted successfully.")
    except Exception as e:
        print("DB delete failed:", e)
        messages.error(request, "Unable to delete the recruitment.")

    # redirect back
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return HttpResponseRedirect(referer)

    return redirect("received-recruitments")

@login_required
@permission_required(perm="recruitment.change_recruitment")
def publish_employee_recruitment(request, rec_id):
    if request.method != "POST":
        return JsonResponse({"error": "invalid"}, status=400)
    recruitment = get_object_or_404(Recruitment, id=rec_id)
    if recruitment.approval_status != "approved":
        return JsonResponse({"success": False, "error": "Not yet approved"}, status=400)
    recruitment.is_published = True
    recruitment.save(update_fields=["is_published"])
    return JsonResponse({"success": True})

def _get_openrouter_config():
    """Get config for AI screening (using Groq)"""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    return OpenRouterConfig(
        api_key=api_key,
        model="llama-3.1-70b-versatile",
        app_name=os.getenv("OPENROUTER_APP_NAME", "FITS HCMS Careers Screening"),
        site_url=os.getenv("OPENROUTER_SITE_URL", "http://127.0.0.1:8000"),
    )

from groq import Groq  # make sure this import exists

def _attempt_ai_screening(candidate, recruitment, application_text):
    """Run AI resume screening and optionally promote candidate from Applied to Initial"""
    config = _get_openrouter_config()
    if not config:
        return None

    job_description = strip_tags(recruitment.description or "")
    prompt = (
        "You are an intelligent hiring screener. Review the candidate application and the job description, "
        "then recommend whether the candidate should move from Applied to Initial stage. "
        "Respond with valid JSON only.\n\n"
        "Job title: {title}\n"
        "Job description: {description}\n\n"
        "Candidate application:\n{application}\n\n"
        "Return a JSON object with keys: matching_score, recommendation, summary. "
        "matching_score should be a number between 0 and 100. "
        "recommendation should be one of: auto_shortlist, interview, reject. "
    ).format(
        title=recruitment.title or "",
        description=job_description,
        application=application_text,
    )

    try:
        # ✅ GROQ CALL (only this part changed)
        client = Groq(api_key=config.api_key)

        response = client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": "You are a helpful HR screening assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content

        # rest untouched
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if not json_match:
            return False

        analysis = json.loads(json_match.group())
        score = int(analysis.get("matching_score", 0) or 0)
        recommendation = str(analysis.get("recommendation", "")).lower()

        if score >= 60 or any(r in recommendation for r in ["interview", "shortlist", "auto"]):
            initial_stage = recruitment.stage_set.filter(stage_type="initial").first()
            if initial_stage:
                candidate.stage_id = initial_stage
                candidate.save(update_fields=["stage_id"])
                return True

        return False

    except Exception as e:
        print("AI ERROR:", str(e))  # helpful debug
        return False

def _send_candidate_rejection_email(candidate_email, candidate_name, job_title):
    from django.core.mail import send_mail
    from datetime import date as _date
    from recruitment.models import JobEmailTemplate
    tpl = JobEmailTemplate.objects.filter(is_default=True).first()
    ctx = {"candidate_name": candidate_name, "role": job_title, "date": _date.today().strftime("%B %d, %Y")}
    if tpl:
        subject = tpl.rejection_subject.format(**ctx)
        message = tpl.rejection_body.format(**ctx)
    else:
        subject = f"Your application for {job_title}"
        message = (
            f"Hi {candidate_name},\n\n"
            f"Thank you for taking the time to apply. After careful consideration, we have decided to move forward with other candidates at this time.\n\n"
            f"We appreciate your interest and wish you the best in your search.\n\nRegards,\nThe Recruitment Team"
        )
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [candidate_email])
    except Exception as e:
        logger.error(f"Failed to send rejection email to {candidate_email}: {e}")


def _send_candidate_congratulations_email(candidate_email, candidate_name, job_title):
    from django.core.mail import send_mail
    from datetime import date as _date
    from recruitment.models import JobEmailTemplate
    tpl = JobEmailTemplate.objects.filter(is_default=True).first()
    ctx = {"candidate_name": candidate_name, "role": job_title, "date": _date.today().strftime("%B %d, %Y")}
    if tpl:
        subject = tpl.selection_subject.format(**ctx)
        message = tpl.selection_body.format(**ctx)
    else:
        subject = f"Update on your application — {job_title}"
        message = (
            f"Hi {candidate_name},\n\n"
            f"Thank you for applying. We're pleased to let you know that you've been moved to the interview stage for the {job_title} role.\n\n"
            f"Our team will be in touch shortly with further details.\n\nRegards,\nThe Recruitment Team"
        )
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [candidate_email])
    except Exception as e:
        logger.error(f"Failed to send congratulations email to {candidate_email}: {e}")


def _send_candidate_received_email(candidate_email, candidate_name, job_title):
    from django.core.mail import send_mail
    subject = f"We received your application — {job_title}"
    message = f"""Hi {candidate_name},

Thanks for applying. We've received your application and will be in touch if there's a match.

Regards,
The Recruitment Team"""
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [candidate_email])
    except Exception as e:
        logger.error(f"Failed to send application receipt email to {candidate_email}: {e}")


def _send_manager_recruitment_notification(managers, recruitment, recruiter):
    """Send notification email to managers when recruitment is raised"""
    from django.core.mail import send_mail
    manager_emails = [m.employee_user.email for m in managers if m.employee_user and m.employee_user.email]
    if not manager_emails:
        return
    
    subject = f"New Recruitment Raised: {recruitment.title}"
    message = f"""
Dear Manager,

A new recruitment has been raised for the position: {recruitment.title}

Details:
- Position: {recruitment.title}
- Company: {recruitment.company_id.company if recruitment.company_id else 'N/A'}
- Raised By: {recruiter}
- Status: Awaiting Approval

Please review the recruitment details in the system and approve/reject as needed.

Best regards,
Recruitment System
    """
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, manager_emails)
    except Exception as e:
        logger.error(f"Failed to send manager recruitment notification: {e}")


def _send_hr_recruitment_approved_notification(hr_email, recruitment):
    """Send notification to HR when recruitment is approved by all managers"""
    from django.core.mail import send_mail
    subject = f"Recruitment Approved: {recruitment.title}"
    message = f"""
Dear HR Team,

The recruitment for {recruitment.title} has been approved by all managers and is now available for acceptance.

Position: {recruitment.title}
Company: {recruitment.company_id.company if recruitment.company_id else 'N/A'}
Vacancies: {recruitment.vacancy}

Please review and accept this recruitment in the system.

Best regards,
Recruitment System
    """
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [hr_email])
    except Exception as e:
        logger.error(f"Failed to send HR recruitment approved notification: {e}")





@csrf_exempt

def careers_apply(request):
    """
    Handle career application form submission from public careers page
    """
    from recruitment.forms import CareersApplicationForm

    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")

    form = CareersApplicationForm(request.POST, request.FILES)
    recruitment_id = request.POST.get("recruitment_id")

    if not recruitment_id:
        return JsonResponse(
            {"status": "error", "message": "Missing recruitment ID"},
            status=400
        )

    if not form.is_valid():
        print("FORM ERRORS:", form.errors)
        return JsonResponse(
            {"status": "error", "message": "Invalid form data"},
            status=400
        )

    try:
        recruitment = Recruitment.objects.get(
            id=recruitment_id,
            is_published=True,
            is_active=True
        )
    except Recruitment.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Recruitment not found"},
            status=404
        )

    # Get Applied stage
    stage = recruitment.stage_set.filter(stage_type="applied").first()
    if not stage:
        return JsonResponse(
            {"status": "error", "message": "Applied stage not configured"},
            status=400
        )

    # Create candidate
    name = f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}"

    candidate = Candidate(
        name=name,
        email=form.cleaned_data['email'],
        mobile=form.cleaned_data['phone'],
        recruitment_id=recruitment,
        stage_id=stage,
        source="application",
        country=form.cleaned_data['country'],
        address=form.cleaned_data['address'],
    )

    # Attach job position if available
    open_positions = list(recruitment.open_positions.all())
    if open_positions:
        candidate.job_position_id = open_positions[0]

    # Attach resume
    resume_file = request.FILES.get('resume')
    if resume_file:
        candidate.resume = resume_file

    # SAVE with proper error handling
    try:
        candidate.save()

    except IntegrityError:
        # Duplicate application (same email + recruitment)
        return JsonResponse(
            {
                "status": "error",
                "message": "You have already applied for this job."
            },
            status=400
        )

    except ValidationError as e:
        return JsonResponse(
            {
                "status": "error",
                "message": e.message_dict if hasattr(e, 'message_dict') else str(e)
            },
            status=400
        )

    except Exception:
        return JsonResponse(
            {
                "status": "error",
                "message": "Internal server error"
            },
            status=500
        )

    # =========================
    # AI SCREENING
    # =========================

    application_text = f"""
Name: {name}
Email: {form.cleaned_data['email']}
Phone: {form.cleaned_data['phone']}
Country: {form.cleaned_data['country']}
Address: {form.cleaned_data['address']}

Why Apply:
{form.cleaned_data['why_apply']}

Experience:
{form.cleaned_data['experience']}
    """

    try:
       screened = _attempt_ai_screening(candidate, recruitment, application_text)
    except Exception as e:
       print("AI ERROR:", str(e))
       screened = None

    # =========================
    # EMAIL LOGIC
    # =========================

    if screened is True:
        _send_candidate_congratulations_email(
            candidate.email,
            candidate.name,
            recruitment.title
        )
    elif screened is False:
        _send_candidate_rejection_email(
            candidate.email,
            candidate.name,
            recruitment.title
        )
    else:
        _send_candidate_received_email(
            candidate.email,
            candidate.name,
            recruitment.title
        )

    # =========================
    # SUCCESS RESPONSE
    # =========================

    return JsonResponse(
        {
            "status": "success",
            "message": "Application submitted successfully!",
            "candidate_id": candidate.id,
            "stage": candidate.stage_id.stage,
        },
        status=201
    )


def careers(request):
    """
    Public careers page showing published recruitments.
    """
    recruitments = Recruitment.objects.filter(
        is_published=True,
        is_active=True,
    ).filter(
        Q(open_positions__isnull=False) | Q(vacancy__gt=0)
    ).distinct().select_related("company_id", "job_position_id").order_by("-created_at")

    return render(request, "recruitment/careers.js", {
        "recruitments": recruitments,
    })


# ///////////////////////////////////////////////
# skill zone
# ///////////////////////////////////////////////


@login_required
@manager_can_enter(perm="recruitment.view_skillzone")
def skill_zone_view(request):
    """
    This method is used to show Skill zone view
    """
    candidates = SkillZoneCandFilter(request.GET).qs.filter(is_active=True)
    skill_groups = group_by_queryset(
        candidates,
        "skill_zone_id",
        request.GET.get("page"),
        "page",
    )

    all_zones = []
    for zone in skill_groups:
        all_zones.append(zone["grouper"])

    skill_zone_filtered = SkillZoneFilter(request.GET).qs.filter(is_active=True)
    all_zone_objects = list(skill_zone_filtered)
    unused_skill_zones = list(set(all_zone_objects) - set(all_zones))

    unused_zones = []
    for zone in unused_skill_zones:
        unused_zones.append(
            {
                "grouper": zone,
                "list": [],
                "dynamic_name": "",
            }
        )
    skill_groups = skill_groups.object_list + unused_zones
    skill_groups = paginator_qry(skill_groups, request.GET.get("page"))
    previous_data = request.GET.urlencode()
    data_dict = parse_qs(previous_data)
    get_key_instances(SkillZone, data_dict)
    if skill_groups.object_list:
        template = "skill_zone/skill_zone_view.html"
    else:
        template = "skill_zone/empty_skill_zone.html"

    context = {
        "pd": previous_data,
        "filter_dict": data_dict,
        "model": SkillZone(),
        "f": SkillZoneCandFilter(),
        "skill_zones": skill_groups,
        "page": request.GET.get("page"),
    }
    return render(request, template, context=context)


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.add_skillzone")
def skill_zone_create(request):
    """
    This method is used to create Skill zone.
    """
    form = SkillZoneCreateForm()
    if request.method == "POST":
        form = SkillZoneCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Skill Zone created successfully."))
            form = SkillZoneCreateForm()

    return render(
        request,
        "skill_zone/skill_zone_form.html",
        {"form": form},
    )


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.change_skillzone")
def skill_zone_update(request, sz_id):
    """
    This method is used to update Skill zone.
    """
    skill_zone = SkillZone.objects.get(id=sz_id)
    form = SkillZoneCreateForm(instance=skill_zone)
    if request.method == "POST":
        form = SkillZoneCreateForm(request.POST, instance=skill_zone)
        if form.is_valid():
            form.save()
            messages.success(request, _("Skill Zone updated successfully."))
    return render(
        request,
        "skill_zone/skill_zone_form.html",
        {"form": form, "sz_id": sz_id},
    )


@login_required
@manager_can_enter(perm="recruitment.delete_skillzone")
def skill_zone_delete(request, sz_id):
    """
    function used to delete Skill zone.

    Parameters:
    request (HttpRequest): The HTTP request object.
    sz_id : Skill zone id

    Returns:
    GET : return Skill zone view template
    """
    try:
        skill_zone = SkillZone.find(sz_id)
        if skill_zone:
            skill_zone.delete()
            messages.success(request, _("Skill zone deleted successfully.."))
        else:
            messages.error(request, _("Skill zone not found."))
    except ProtectedError:
        messages.error(request, _("Related entries exists"))
    return HttpResponse(
        "<script>$('.filterButton')[0].click();reloadMessage();</script>"
    )


@login_required
@manager_can_enter(perm="recruitment.change_skillzone")
def skill_zone_archive(request, sz_id):
    """
    function used to archive or un-archive Skill zone.

    Parameters:
    request (HttpRequest): The HTTP request object.
    sz_id : Skill zone id

    Returns:
    GET : return Skill zone view template
    """
    skill_zone = SkillZone.find(sz_id)
    if skill_zone:
        is_active = skill_zone.is_active
        if is_active:
            skill_zone.is_active = False
            skill_zone_candidates = SkillZoneCandidate.objects.filter(
                skill_zone_id=sz_id
            )
            for i in skill_zone_candidates:
                i.is_active = False
                i.save()
            messages.success(request, _("Skill zone archived successfully.."))
        else:
            skill_zone.is_active = True
            skill_zone_candidates = SkillZoneCandidate.objects.filter(
                skill_zone_id=sz_id
            )
            for i in skill_zone_candidates:
                i.is_active = True
                i.save()
            messages.success(request, _("Skill zone unarchived successfully.."))
        skill_zone.save()
    else:
        messages.error(request, _("Skill zone not found."))
    return redirect(skill_zone_view)


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.view_skillzone")
def skill_zone_filter(request):
    """
    This method is used to filter and show Skill zone view.
    """
    template = "skill_zone/skill_zone_list.html"
    if request.GET.get("view") == "card":
        template = "skill_zone/skill_zone_card.html"

    candidates = SkillZoneCandFilter(request.GET).qs
    skill_zone_filtered = SkillZoneFilter(request.GET).qs
    if request.GET.get("is_active") == "false":
        skill_zone_filtered = SkillZoneFilter(request.GET).qs.filter(is_active=False)
        candidates = SkillZoneCandFilter(request.GET).qs.filter(is_active=False)

    else:
        skill_zone_filtered = SkillZoneFilter(request.GET).qs.filter(is_active=True)
        candidates = SkillZoneCandFilter(request.GET).qs.filter(is_active=True)
    skill_groups = group_by_queryset(
        candidates,
        "skill_zone_id",
        request.GET.get("page"),
        "page",
    )
    all_zones = []
    for zone in skill_groups:
        all_zones.append(zone["grouper"])

    all_zone_objects = list(skill_zone_filtered)
    unused_skill_zones = list(set(all_zone_objects) - set(all_zones))

    unused_zones = []
    for zone in unused_skill_zones:
        unused_zones.append(
            {
                "grouper": zone,
                "list": [],
                "dynamic_name": "",
            }
        )
    skill_groups = skill_groups.object_list + unused_zones
    skill_groups = paginator_qry(skill_groups, request.GET.get("page"))
    previous_data = request.GET.urlencode()
    data_dict = parse_qs(previous_data)
    get_key_instances(SkillZone, data_dict)
    context = {
        "skill_zones": skill_groups,
        "pd": previous_data,
        "filter_dict": data_dict,
    }
    return render(
        request,
        template,
        context,
    )


@login_required
@manager_can_enter(perm="recruitment.view_skillzonecandidate")
def skill_zone_cand_card_view(request, sz_id):
    """
    This method is used to show Skill zone candidates.

    Parameters:
    request (HttpRequest): The HTTP request object.
    sz_cand_id : Skill zone id

    Returns:
    GET : return Skill zone candidate view template
    """
    skill_zone = SkillZone.objects.get(id=sz_id)
    template = "skill_zone_cand/skill_zone_cand_view.html"
    sz_candidates = SkillZoneCandidate.objects.filter(
        skill_zone_id=skill_zone, is_active=True
    )
    context = {
        "sz_candidates": paginator_qry(sz_candidates, request.GET.get("page")),
        "pd": request.GET.urlencode(),
        "sz_id": sz_id,
    }
    return render(request, template, context)


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.add_skillzonecandidate")
def skill_zone_candidate_create(request, sz_id):
    """
    This method is used to add candidates to a Skill zone.

    Parameters:
    request (HttpRequest): The HTTP request object.
    sz_cand_id : Skill zone id

    Returns:
    GET : return Skill zone candidate create template
    """
    skill_zone = SkillZone.objects.get(id=sz_id)
    template = "skill_zone_cand/skill_zone_cand_form.html"
    form = SkillZoneCandidateForm(initial={"skill_zone_id": skill_zone})
    if request.method == "POST":
        form = SkillZoneCandidateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Candidate added successfully."))
            return HttpResponse("<script>window.location.reload()</script>")

    return render(request, template, {"form": form, "sz_id": sz_id})


@login_required
@hx_request_required
@manager_can_enter(perm="recruitment.change_skillzonecandidate")
def skill_zone_cand_edit(request, sz_cand_id):
    """
    This method is used to edit candidates in a Skill zone.

    Parameters:
    request (HttpRequest): The HTTP request object.
    sz_cand_id : Skill zone candidate id

    Returns:
    GET : return Skill zone candidate edit template
    """
    skill_zone_cand = SkillZoneCandidate.objects.filter(id=sz_cand_id).first()
    template = "skill_zone_cand/skill_zone_cand_form.html"
    form = SkillZoneCandidateForm(instance=skill_zone_cand)
    if request.method == "POST":
        form = SkillZoneCandidateForm(request.POST, instance=skill_zone_cand)
        if form.is_valid():
            form.save()
            messages.success(request, _("Candidate edited successfully."))
            return HttpResponse("<script>window.location.reload()</script>")
    return render(request, template, {"form": form, "sz_cand_id": sz_cand_id})


@login_required
@manager_can_enter(perm="recruitment.delete_skillzonecandidate")
def skill_zone_cand_delete(request, sz_cand_id):
    """
    function used to delete Skill zone candidate.

    Parameters:
    request (HttpRequest): The HTTP request object.
    sz_cand_id : Skill zone candidate id

    Returns:
    GET : return Skill zone view template
    """

    try:
        SkillZoneCandidate.objects.get(id=sz_cand_id).delete()
        messages.success(request, _("Skill zone deleted successfully.."))
    except SkillZoneCandidate.DoesNotExist:
        messages.error(request, _("Skill zone not found."))
    except ProtectedError:
        messages.error(request, _("Related entries exists"))
    return redirect(skill_zone_view)


@login_required
@manager_can_enter(perm="recruitment.view_skillzonecandidate")
def skill_zone_cand_filter(request):
    """
    This method is used to filter the skill zone candidates
    """
    template = "skill_zone_cand/skill_zone_cand_card.html"
    if request.GET.get("view") == "list":
        template = "skill_zone_cand/skill_zone_cand_list.html"

    candidates = SkillZoneCandidate.objects.all()
    candidates_filter = SkillZoneCandFilter(request.GET, queryset=candidates).qs
    previous_data = request.GET.urlencode()
    data_dict = parse_qs(previous_data)
    get_key_instances(SkillZoneCandidate, data_dict)
    context = {
        "candidates": paginator_qry(candidates_filter, request.GET.get("page")),
        "pd": previous_data,
        "filter_dict": data_dict,
        "f": SkillZoneCandFilter(),
    }
    return render(
        request,
        template,
        context,
    )


@login_required
@manager_can_enter(perm="recruitment.delete_skillzonecandidate")
def skill_zone_cand_archive(request, sz_cand_id):
    """
    function used to archive or un-archive Skill zone candidate.

    Parameters:
    request (HttpRequest): The HTTP request object.
    sz_cand_id : Skill zone candidate id

    Returns:
    GET : return Skill zone candidate view template
    """
    try:
        skill_zone_cand = SkillZoneCandidate.objects.get(id=sz_cand_id)
        is_active = skill_zone_cand.is_active
        if is_active:
            skill_zone_cand.is_active = False
            messages.success(request, _("Candidate archived successfully.."))

        else:
            skill_zone_cand.is_active = True
            messages.success(request, _("Candidate unarchived successfully.."))

        skill_zone_cand.save()
    except SkillZone.DoesNotExist:
        messages.error(request, _("Candidate not found."))
    return redirect(skill_zone_view)


@login_required
@manager_can_enter(perm="recruitment.delete_skillzonecandidate")
def skill_zone_cand_delete(request, sz_cand_id):
    """
    function used to delete Skill zone candidate.

    Parameters:
    request (HttpRequest): The HTTP request object.
    sz_cand_id : Skill zone candidate id

    Returns:
    GET : return Skill zone view template
    """
    try:
        SkillZoneCandidate.objects.get(id=sz_cand_id).delete()
        messages.success(request, _("Candidate deleted successfully.."))
    except SkillZoneCandidate.DoesNotExist:
        messages.error(request, _("Candidate not found."))
    except ProtectedError:
        messages.error(request, _("Related entries exists"))
    return redirect(skill_zone_view)


@login_required
@hx_request_required
def to_skill_zone(request, cand_id):
    """
    This method is used to Add candidate into skill zone
    Args:
        cand_id : candidate instance id
    """
    if not (
        request.user.has_perm("recruitment.change_candidate")
        or request.user.has_perm("recruitment.add_skillzonecandidate")
    ):
        messages.info(request, "You dont have permission.")
        return HttpResponse("<script>window.location.reload()</script>")

    candidate = Candidate.objects.get(id=cand_id)
    template = "skill_zone_cand/to_skill_zone_form.html"
    form = ToSkillZoneForm(
        initial={
            "candidate_id": candidate,
            "skill_zone_ids": SkillZoneCandidate.objects.filter(
                candidate_id=candidate
            ).values_list("skill_zone_id", flat=True),
        }
    )
    if request.method == "POST":
        form = ToSkillZoneForm(request.POST)
        if form.is_valid():
            skill_zones = form.cleaned_data["skill_zone_ids"]
            for zone in skill_zones:
                if not SkillZoneCandidate.objects.filter(
                    candidate_id=candidate, skill_zone_id=zone
                ).exists():
                    zone_candidate = SkillZoneCandidate()
                    zone_candidate.candidate_id = candidate
                    zone_candidate.skill_zone_id = zone
                    zone_candidate.reason = form.cleaned_data["reason"]
                    zone_candidate.save()
            messages.success(request, "Candidate Added to skill zone successfully")
            return HttpResponse("<script>window.location.reload()</script>")
    return render(request, template, {"form": form, "cand_id": cand_id})


@login_required
def update_candidate_rating(request, cand_id):
    """
    This method is used to update the candidate rating
    Args:
        id : candidate rating instance id
    """
    cand_id = cand_id
    candidate = Candidate.objects.get(id=cand_id)
    employee_id = request.user.employee_get
    rating = request.POST.get("rating")
    rate = CandidateRating.objects.get(candidate_id=candidate, employee_id=employee_id)
    rate.rating = int(rating)
    rate.save()
    return redirect(recruitment_pipeline)


def open_recruitments(request):
    """
    This method is used to render the open recruitment page
    """
    recruitments = Recruitment.default.filter(
        closed=False, is_published=True, is_active=True
    )
    context = {
        "recruitments": recruitments,
    }
    response = render(request, "recruitment/open_recruitments.html", context)
    response["X-Frame-Options"] = "ALLOW-FROM *"

    return response


@hx_request_required
def recruitment_details(request, id):
    """
    This method is used to render the recruitment details page
    """
    recruitment = Recruitment.default.get(id=id)
    context = {
        "recruitment": recruitment,
    }
    return render(request, "recruitment/recruitment_details.html", context)


@login_required
@manager_can_enter("recruitment.view_candidate")
def get_mail_log(request):
    """
    This method is used to track mails sent along with the status
    """
    candidate_id = request.GET["candidate_id"]
    candidate = Candidate.objects.get(id=candidate_id)
    tracked_mails = EmailLog.objects.filter(to__icontains=candidate.email).order_by(
        "-created_at"
    )
    return render(request, "candidate/mail_log.html", {"tracked_mails": tracked_mails})


@login_required
@hx_request_required
@permission_required("recruitment.add_recruitmentgeneralsetting")
def candidate_self_tracking(request):
    """
    This method is used to update the recruitment general setting
    """
    settings = RecruitmentGeneralSetting.objects.first()
    settings = settings if settings else RecruitmentGeneralSetting()
    settings.candidate_self_tracking = "candidate_self_tracking" in request.GET.keys()
    settings.save()
    return HttpResponse("success")


@login_required
@hx_request_required
@permission_required("recruitment.add_recruitmentgeneralsetting")
def candidate_self_tracking_rating_option(request):
    """
    This method is used to enable/disable the selt tracking rating field
    """
    settings = RecruitmentGeneralSetting.objects.first()
    settings = settings if settings else RecruitmentGeneralSetting()
    settings.show_overall_rating = "candidate_self_tracking" in request.GET.keys()
    settings.save()
    return HttpResponse("success")


def candidate_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        mobile = request.POST["phone"]

        backend = CandidateAuthenticationBackend()
        candidate = backend.authenticate(request, username=email, password=mobile)

        if candidate is not None:
            request.session["candidate_id"] = candidate.id
            request.session["candidate_email"] = candidate.email
            return redirect("candidate-self-status-tracking")
        else:
            return render(
                request, "candidate/self_login.html", {"error": "Invalid credentials"}
            )

    return render(request, "candidate/self_login.html")


def candidate_logout(request):
    """Logs out the candidate by clearing session data."""

    request.session.pop("candidate_id", None)
    request.session.pop("candidate_email", None)
    messages.success(request, "You have been logged out.")
    return redirect("candidate_login")


@candidate_login_required
def candidate_self_status_tracking(request):
    """
    This method is accessed by the candidates
    """
    self_tracking_feature = check_candidate_self_tracking(request)[
        "check_candidate_self_tracking"
    ]
    if self_tracking_feature:
        candidate_id = request.session.get("candidate_id")

        if not candidate_id:
            return redirect("candidate-login")

        candidate = Candidate.objects.get(pk=candidate_id)
        interviews = candidate.candidate_interview.annotate(
            is_today=Case(
                When(interview_date=date.today(), then=0),
                default=1,
                output_field=IntegerField(),
            )
        ).order_by("is_today", "-interview_date", "interview_time")
        return render(
            request,
            "candidate/candidate_self_tracking.html",
            {"candidate": candidate, "interviews": interviews},
        )
    return render(request, "404.html")


@login_required
@manager_can_enter("recruitment.add_candidate")
def candidate_self_status_tracking_managers_view(request, cand_id):
    """
    This method is accessed by the candidates
    """
    self_tracking_feature = check_candidate_self_tracking(request)[
        "check_candidate_self_tracking"
    ]
    if self_tracking_feature:
        candidate_id = request.session.get("candidate_id")
        if (
            request.user.has_perm("recruitment.view_candidate")
            or request.user.employee_get.recruitment_set.filter(
                candidate__id=cand_id
            ).exists()
            or request.user.employee_get.stage_set.filter(candidate=cand_id).exists()
        ):
            request.session["candidate_id"] = cand_id
            candidate_id = cand_id

        if not candidate_id:
            return redirect("candidate-login")

        candidate = Candidate.objects.get(pk=candidate_id)
        interviews = candidate.candidate_interview.annotate(
            is_today=Case(
                When(interview_date=date.today(), then=0),
                default=1,
                output_field=IntegerField(),
            )
        ).order_by("is_today", "-interview_date", "interview_time")

        return render(
            request,
            "candidate/candidate_self_tracking.html",
            {"candidate": candidate, "interviews": interviews},
        )
    return render(request, "404.html")


@login_required
@hx_request_required
@permission_required("recruitment.add_rejectreason")
def create_reject_reason(request):
    """
    This method is used to create/update the reject reasons
    """
    instance_id = eval_validate(str(request.GET.get("instance_id")))
    instance = None
    if instance_id:
        instance = RejectReason.objects.get(id=instance_id)
    form = RejectReasonForm(instance=instance)
    if request.method == "POST":
        form = RejectReasonForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Reject reason saved")
            return HttpResponse("<script>window.location.reload()</script>")
    return render(request, "settings/reject_reason_form.html", {"form": form})


@login_required
@permission_required("recruitment.view_recruitment")
def self_tracking_feature(request):
    """
    Recruitment optional feature for candidate self tracking
    """
    return render(request, "recruitment/settings/settings.html")


@login_required
@permission_required("recruitment.delete_rejectreason")
def delete_reject_reason(request):
    """
    This method is used to delete the reject reasons
    """
    ids = request.GET.getlist("ids")
    reasons = RejectReason.objects.filter(id__in=ids)
    for reason in reasons:
        reasons.delete()
        messages.success(request, f"{reason.title} is deleted.")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


def extract_text_with_font_info(pdf):
    """
    This method is used to extract text from the pdf and create a list of dictionaries containing details about the extracted text.
    Args:
        pdf (): pdf file to extract text from
    """
    pdf_bytes = pdf.read()
    pdf_doc = io.BytesIO(pdf_bytes)
    doc = fitz.open("pdf", pdf_doc)
    text_info = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            try:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_info.append(
                            {
                                "text": span["text"],
                                "font_size": span["size"],
                                "capitalization": sum(
                                    1 for c in span["text"] if c.isupper()
                                )
                                / len(span["text"]),
                            }
                        )
            except:
                pass

    return text_info


def rank_text(text_info):
    """
    This method is used to rank the text

    Args:
        text_info: List of dictionary containing the details

    Returns:
        Returns a sorted list
    """
    ranked_text = sorted(
        text_info, key=lambda x: (x["font_size"], x["capitalization"]), reverse=True
    )
    return ranked_text


def dob_matching(dob):
    """
    This method is used to change the date format to YYYY-MM-DD

    Args:
        dob: Date

    Returns:
        Return date in YYYY-MM-DD
    """
    date_formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y.%m.%d",
        "%d.%m.%Y",
    ]

    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(dob, fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return dob


def extract_info(pdf):
    """
    This method creates the contact information dictionary from the provided pdf file
    Args:
        pdf_file: pdf file
    """

    text_info = extract_text_with_font_info(pdf)
    ranked_text = rank_text(text_info)

    phone_pattern = re.compile(r"\b\+?\d{1,2}\s?\d{9,10}\b")
    dob_pattern = re.compile(
        r"\b(?:\d{1,2}|\d{4})[-/.,]\d{1,2}[-/.,](?:\d{1,2}|\d{4})\b"
    )
    email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    zip_code_pattern = re.compile(r"\b\d{5,6}(?:-\d{4})?\b")

    extracted_info = {
        "full_name": "",
        "address": "",
        "country": "",
        "state": "",
        "phone_number": "",
        "dob": "",
        "email_id": "",
        "zip": "",
    }

    name_candidates = [
        item["text"]
        for item in ranked_text
        if item["font_size"] == max(item["font_size"] for item in ranked_text)
    ]

    if name_candidates:
        extracted_info["full_name"] = " ".join(name_candidates)

    for item in ranked_text:
        text = item["text"]

        if not text:
            continue

        if not extracted_info["phone_number"]:
            phone_match = phone_pattern.search(text)
            if phone_match:
                extracted_info["phone_number"] = phone_match.group()

        if not extracted_info["dob"]:
            dob_match = dob_pattern.search(text)
            if dob_match:
                extracted_info["dob"] = dob_matching(dob_match.group())

        if not extracted_info["zip"]:
            zip_match = zip_code_pattern.search(text)
            if zip_match:
                extracted_info["zip"] = zip_match.group()

        if not extracted_info["email_id"]:
            email_match = email_pattern.search(text)
            if email_match:
                extracted_info["email_id"] = email_match.group()

        if "address" in text.lower() and not extracted_info["address"]:
            extracted_info["address"] = text.replace("Address:", "").strip()

        for item in text.split(" "):
            if item.capitalize() in country_arr:
                extracted_info["country"] = item

        for item in text.split(" "):
            if item.capitalize() in states:
                extracted_info["state"] = item

    return extracted_info


def resume_completion(request):
    """
    This function is returns the data for completing the candidate creation form
    """
    resume_file = request.FILES["resume"]
    contact_info = extract_info(resume_file)

    return JsonResponse(contact_info)


def check_vaccancy(request):
    """
    check vaccancy of recruitment
    """
    stage_id = request.GET.get("stageId")
    stage = Stage.objects.get(id=stage_id)
    message = "No message"
    if stage and stage.recruitment_id.is_vacancy_filled():
        message = _("Vaccancy is filled")
    return JsonResponse({"message": message})


@login_required
def skills_view(request):
    """
    This function is used to view skills page in settings
    """
    skills = Skill.objects.all()
    return render(request, "settings/skills/skills_view.html", {"skills": skills})


@login_required
def create_skills(request):
    """
    This method is used to create the skills
    """
    instance_id = eval_validate(str(request.GET.get("instance_id")))
    dynamic = request.GET.get("dynamic")
    hx_vals = request.GET.get("data")
    instance = None
    if instance_id:
        instance = Skill.objects.get(id=instance_id)
    form = SkillsForm(instance=instance)
    if request.method == "POST":
        form = SkillsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Skill created successfully")

            if request.GET.get("dynamic") == "True":
                from django.urls import reverse

                url = reverse("recruitment-create")
                instance = Skill.objects.all().last()
                mutable_get = request.GET.copy()
                skills = mutable_get.getlist("skills")
                skills.remove("create")
                skills.append(str(instance.id))
                mutable_get["skills"] = skills[-1]
                skills.pop()
                data = mutable_get.urlencode()
                try:
                    for item in skills:
                        data += f"&skills={item}"
                except:
                    pass
                return redirect(f"{url}?{data}")

            return HttpResponse("<script>window.location.reload()</script>")

    context = {
        "form": form,
        "dynamic": dynamic,
        "hx_vals": hx_vals,
    }

    return render(request, "settings/skills/skills_form.html", context=context)


@login_required
@permission_required("recruitment.delete_rejectreason")
def delete_skills(request):
    """
    This method is used to delete the skills
    """
    ids = request.GET.getlist("ids")
    skills = Skill.objects.filter(id__in=ids)
    for skill in skills:
        skill.delete()
        messages.success(request, f"{skill.title} is deleted.")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required
@hx_request_required
@manager_can_enter("recruitment.add_candidate")
def view_bulk_resumes(request):
    """
    This function returns the bulk_resume.html page to the modal
    """
    rec_id = eval_validate(str(request.GET.get("rec_id")))
    resumes = Resume.objects.filter(recruitment_id=rec_id)

    return render(
        request, "pipeline/bulk_resume.html", {"resumes": resumes, "rec_id": rec_id}
    )


@login_required
@hx_request_required
@manager_can_enter("recruitment.add_candidate")
def add_bulk_resumes(request):
    """
    This function is used to create bulk resume
    """
    rec_id = eval_validate(str(request.GET.get("rec_id")))
    recruitment = Recruitment.objects.get(id=rec_id)
    if request.method == "POST":
        files = request.FILES.getlist("files")
        for file in files:
            Resume.objects.create(
                file=file,
                recruitment_id=recruitment,
            )

        url = reverse("view-bulk-resume")
        query_params = f"?rec_id={rec_id}"

        return redirect(f"{url}{query_params}")


@login_required
@hx_request_required
@manager_can_enter("recruitment.add_candidate")
def delete_resume_file(request):
    """
    Used to delete resume
    """
    ids = request.GET.getlist("ids")
    rec_id = request.GET.get("rec_id")
    Resume.objects.filter(id__in=ids).delete()

    url = reverse("view-bulk-resume")
    query_params = f"?rec_id={rec_id}"

    return redirect(f"{url}{query_params}")


def extract_words_from_pdf(pdf_file):
    """
    This method is used to extract the words from the pdf file into a list.
    Args:
        pdf_file: pdf file

    """
    pdf_document = fitz.open(pdf_file.path)

    words = []

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        page_text = page.get_text()

        page_words = re.findall(r"\b\w+\b", page_text.lower())

        words.extend(page_words)

    pdf_document.close()

    return words


@login_required
@hx_request_required
@manager_can_enter("recruitment.add_candidate")
def matching_resumes(request, rec_id):
    """
    This function returns the matching resume table after sorting the resumes according to their scores

    Args:
        rec_id: Recruitment ID

    """
    recruitment = Recruitment.objects.filter(id=rec_id).first()
    skills = recruitment.skills.values_list("title", flat=True)
    resumes = recruitment.resume.all()
    is_candidate = resumes.filter(is_candidate=True)
    is_candidate_ids = set(is_candidate.values_list("id", flat=True))

    resume_ranks = []
    for resume in resumes:
        words = extract_words_from_pdf(resume.file)
        matching_skills_count = sum(skill.lower() in words for skill in skills)

        item = {"resume": resume, "matching_skills_count": matching_skills_count}
        if not len(words):
            item["image_pdf"] = True

        resume_ranks.append(item)

    candidate_resumes = [
        rank for rank in resume_ranks if rank["resume"].id in is_candidate_ids
    ]
    non_candidate_resumes = [
        rank for rank in resume_ranks if rank["resume"].id not in is_candidate_ids
    ]

    non_candidate_resumes = sorted(
        non_candidate_resumes, key=lambda x: x["matching_skills_count"], reverse=True
    )
    candidate_resumes = sorted(
        candidate_resumes, key=lambda x: x["matching_skills_count"], reverse=True
    )

    ranked_resumes = non_candidate_resumes + candidate_resumes

    return render(
        request,
        "pipeline/matching_resumes.html",
        {
            "matched_resumes": ranked_resumes,
            "rec_id": rec_id,
        },
    )


@login_required
@manager_can_enter("recruitment.add_candidate")
def matching_resume_completion(request):
    """
    This function is returns the data for completing the candidate creation form
    """
    resume_id = request.GET.get("resume_id")
    resume_obj = get_object_or_404(Resume, id=resume_id)
    resume_file = resume_obj.file
    contact_info = extract_info(resume_file)

    return JsonResponse(contact_info)


@login_required
@permission_required("recruitment.view_rejectreason")
def candidate_reject_reasons(request):
    """
    This method is used to view all the reject reasons
    """
    reject_reasons = RejectReason.objects.all()
    return render(
        request, "settings/reject_reasons.html", {"reject_reasons": reject_reasons}
    )


@login_required
def hired_candidate_chart(request):
    """
    function used to show hired candidates in all recruitments.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    GET : return Json response labels, data, background_color, border_color.
    """
    labels = []
    data = []
    background_color = []
    border_color = []
    recruitments = Recruitment.objects.filter(closed=False, is_active=True)
    for recruitment in recruitments:
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)
        background_color.append(f"rgba({red}, {green}, {blue}, 0.2")
        border_color.append(f"rgb({red}, {green}, {blue})")
        labels.append(f"{recruitment}")
        data.append(recruitment.candidate.filter(hired=True).count())
    return JsonResponse(
        {
            "labels": labels,
            "data": data,
            "background_color": background_color,
            "border_color": border_color,
            "message": _("No records available at the moment."),
        },
        safe=False,
    )


@login_required
def candidate_document_request(request):
    """
    This function is used to create document requests of an employee in employee requests view.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns: return document_request_create_form template
    """
    candidate_id = (
        request.GET.get("candidate_id") if request.GET.get("candidate_id") else None
    )
    form = CandidateDocumentRequestForm(initial={"candidate_id": candidate_id})
    if request.method == "POST":
        form = CandidateDocumentRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Document request created successfully"))
            return HttpResponse("<script>window.location.reload();</script>")

    context = {
        "form": form,
    }
    return render(
        request, "documents/document_request_create_form.html", context=context
    )


@login_required
@hx_request_required
def document_create(request, id):
    """
    This function is used to create documents from employee individual & profile view.

    Parameters:
    request (HttpRequest): The HTTP request object.
    emp_id (int): The id of the employee

    Returns: return document_tab template
    """
    candidate_id = Candidate.objects.get(id=id)
    form = CandidateDocumentForm(initial={"candidate_id": candidate_id})
    form.fields["candidate_id"].queryset = Candidate.objects.filter(id=id)
    if request.method == "POST":
        form = CandidateDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _("Document created successfully."))
            return HttpResponse("<script>window.location.reload();</script>")

    context = {
        "form": form,
        "candidate_id": candidate_id,
    }
    return render(request, "candidate/document_create_form.html", context=context)


@login_required
def update_document_title(request, id):
    """
    This function is used to create documents from employee individual & profile view.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns: return document_tab template
    """
    document = get_object_or_404(CandidateDocument, id=id)
    name = request.POST.get("title")
    if request.method == "POST":
        document.title = name
        document.save()

        return JsonResponse(
            {"success": True, "message": "Document title updated successfully"}
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request"}, status=400
        )


@login_required
@hx_request_required
@manager_can_enter("recruitment.delete_candidatedocument")
def document_delete(request, id):
    """
    Handle the deletion of a document, with permissions and error handling.

    This view function attempts to delete a document specified by its ID.
    If the user does not have the "delete_document" permission, it restricts
    deletion to documents owned by the user. It provides appropriate success
    or error messages based on the outcome. If the document is protected and
    cannot be deleted, it handles the exception and informs the user.
    """
    try:
        document = CandidateDocument.objects.filter(id=id)
        if document:
            document.delete()
            messages.success(
                request,
                _(
                    f"Document request {document.first()} for {document.first().employee_id} deleted successfully"
                ),
            )
        else:
            messages.error(request, _("Document not found"))

    except ProtectedError:
        messages.error(request, _("You cannot delete this document."))

    if "HTTP_HX_TARGET" in request.META and request.META.get(
        "HTTP_HX_TARGET"
    ).startswith("document"):
        clear_messages(request)
        return HttpResponse()
    else:
        return HttpResponse("<script>window.location.reload();</script>")


@candidate_login_required
@hx_request_required
def file_upload(request, id):
    """
    This function is used to upload documents of an employee in employee individual & profile view.

    Parameters:
    request (HttpRequest): The HTTP request object.
    id (int): The id of the document.

    Returns: return document_form template
    """
    document_item = CandidateDocument.objects.get(id=id)
    form = CandidateDocumentUpdateForm(instance=document_item)
    if request.method == "POST":
        form = CandidateDocumentUpdateForm(
            request.POST, request.FILES, instance=document_item
        )
        if form.is_valid():
            form.save()
            messages.success(request, _("Document uploaded successfully"))
            return HttpResponse("<script>window.location.reload();</script>")

    context = {
        "form": form,
        "document": document_item,
    }
    return render(request, "candidate/document_form.html", context=context)


@candidate_login_required
@hx_request_required
def view_file(request, id):
    """
    This function used to view the uploaded document in the modal.
    Parameters:

    request (HttpRequest): The HTTP request object.
    id (int): The id of the document.

    Returns: return view_file template
    """
    document_obj = CandidateDocument.objects.filter(id=id).first()
    context = {
        "document": document_obj,
    }
    if document_obj.document:
        file_path = document_obj.document.path
        file_extension = os.path.splitext(file_path)[1][1:].lower()

        content_type = get_content_type(file_extension)

        try:
            with open(file_path, "rb") as file:
                file_content = file.read()
        except:
            file_content = None

        context["file_content"] = file_content
        context["file_extension"] = file_extension
        context["content_type"] = content_type

    return render(request, "candidate/view_file.html", context)


@login_required
@hx_request_required
@manager_can_enter("recruitment.change_candidatedocument")
def document_approve(request, id):
    """
    This function used to view the approve uploaded document.
    Parameters:

    request (HttpRequest): The HTTP request object.
    id (int): The id of the document.

    Returns:
    """
    document_obj = get_object_or_404(CandidateDocument, id=id)
    if document_obj.document:
        document_obj.status = "approved"
        document_obj.save()
        messages.success(request, _("Document request approved"))
    else:
        messages.error(request, _("No document uploaded"))

    return HttpResponse("<script>window.location.reload();</script>")


@login_required
@hx_request_required
@manager_can_enter("recruitment.change_candidatedocument")
def document_reject(request, id):
    """
    This function used to view the reject uploaded document.
    Parameters:

    request (HttpRequest): The HTTP request object.
    id (int): The id of the document.

    Returns:
    """
    document_obj = get_object_or_404(CandidateDocument, id=id)
    form = CandidateDocumentRejectForm()
    if document_obj.document:
        if request.method == "POST":
            form = CandidateDocumentRejectForm(request.POST, instance=document_obj)
            if form.is_valid():
                instance = form.save(commit=False)
                document_obj.reject_reason = instance.reject_reason
                document_obj.status = "rejected"
                document_obj.save()
                messages.error(request, _("Document request rejected"))

                return HttpResponse("<script>window.location.reload();</script>")
    else:
        messages.error(request, _("No document uploaded"))
        return HttpResponse("<script>window.location.reload();</script>")

    return render(
        request,
        "candidate/reject_form.html",
        {"form": form, "document_obj": document_obj},
    )


@candidate_login_required
def candidate_add_notes(request, cand_id):
    """
    This method renders template component to add candidate remark
    """

    candidate = Candidate.objects.get(id=cand_id)
    updated_by = request.user.employee_get if request.user.is_authenticated else None
    label = (
        request.user.employee_get.get_full_name()
        if request.user.is_authenticated
        else candidate.name
    )

    form = StageNoteForm(initial={"candidate_id": cand_id})
    if request.method == "POST":
        form = StageNoteForm(
            request.POST,
            request.FILES,
        )
        if form.is_valid():
            note, attachment_ids = form.save(commit=False)
            note.candidate_id = candidate
            note.stage_id = candidate.stage_id
            note.updated_by = updated_by
            note.candidate_can_view = True
            note.save()
            note.stage_files.set(attachment_ids)
            messages.success(request, _("Note added successfully.."))
            with contextlib.suppress(Exception):
                managers = candidate.recruitment_id.recruitment_managers.all()
                stage_managers = candidate.stage_id.stage_managers.all()

                all_managers = managers | stage_managers
                users = [
                    employee.employee_user_id for employee in all_managers.distinct()
                ]

                notify.send(
                    candidate,
                    label=label,
                    recipient=users,
                    verb=f"{label} has added a note on the candidate {candidate}",
                    verb_ar=f"أضاف {label} ملاحظة حول المرشح {candidate}",
                    verb_de=f"{label} hat dem {candidate} eine Notiz hinzugefügt.",
                    verb_es=f"{label} agregó una nota al {candidate}.",
                    verb_fr=f"{label} a ajouté une note à {candidate}.",
                    icon="people-circle",
                    redirect=reverse(
                        "candidate-view-individual", kwargs={"cand_id": cand_id}
                    ),
                )

    return render(
        request,
        "candidate/candidate_self_tracking.html",
        {
            "candidate": candidate,
            "note_form": form,
        },
    )


@login_required
@hx_request_required
def employee_profile_interview_tab(request):
    employee = request.user.employee_get

    interviews = employee.interviewschedule_set.annotate(
        is_today=Case(
            When(interview_date=date.today(), then=0),
            default=1,
            output_field=IntegerField(),
        )
    ).order_by("is_today", "-interview_date", "interview_time")

    return render(request, "tabs/scheduled_interview.html", {"interviews": interviews})





# 📁 where resumes will be saved
UPLOAD_DIR = os.path.join(settings.BASE_DIR, "temp_resumes")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── APPLY API ────────────────────────────────────────────────
@csrf_exempt
def apply_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "invalid"}, status=400)

    data = request.POST
    file = request.FILES.get("resume")
    if not file:
        return JsonResponse({"success": False, "error": "Resume is required"}, status=400)

    file_path = os.path.join(UPLOAD_DIR, file.name)
    with open(file_path, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)

    try:
        recruitment = Recruitment.objects.get(id=int(data.get("recruitment_id", 0)))
    except (Recruitment.DoesNotExist, ValueError, TypeError):
        return JsonResponse({"success": False, "error": "Invalid job"}, status=400)

    from recruitment.models import JobApplication
    try:
        app = JobApplication.objects.create(
            recruitment=recruitment,
            name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            country=data.get("country", ""),
            experience=data.get("experience", "")[:5000],
            why_apply=data.get("why_apply", ""),
            resume_path=file_path,
            status="applied",
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

    threading.Thread(target=process_application, args=(app.id,)).start()
    return JsonResponse({"success": True})


# ── DOWNLOAD RESUME ───────────────────────────────────────────
def download_resume(request, app_id):
    from recruitment.models import JobApplication
    try:
        app = JobApplication.objects.get(id=app_id)
    except JobApplication.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)
    if app.resume_path and os.path.exists(app.resume_path):
        return FileResponse(open(app.resume_path, "rb"), as_attachment=True)
    return JsonResponse({"error": "file not found"}, status=404)


def view_resume(request, app_id):
    from recruitment.models import JobApplication
    try:
        app = JobApplication.objects.get(id=app_id)
    except JobApplication.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)
    if app.resume_path and os.path.exists(app.resume_path):
        return FileResponse(open(app.resume_path, "rb"), as_attachment=False, content_type="application/pdf")
    return JsonResponse({"error": "file not found"}, status=404)


# ── CANDIDATE DOCUMENTS PAGE ──────────────────────────────────
def application_documents(request, app_id):
    from recruitment.models import JobApplication, Candidate, CandidatePortalUpload
    try:
        app = JobApplication.objects.select_related("recruitment").get(id=app_id)
    except JobApplication.DoesNotExist:
        from django.http import Http404
        raise Http404

    # Match Candidate by email; prefer same recruitment, fall back to any for that email
    candidate = (
        Candidate.objects.filter(email=app.email, recruitment_id=app.recruitment).first()
        or Candidate.objects.filter(email=app.email).order_by("-id").first()
    )

    docs = []
    if app.resume_path and os.path.exists(app.resume_path):
        docs.append({
            "label": "Resume / CV",
            "icon": "document-text-outline",
            "view_url": f"/recruitment/api/view-resume/{app.id}/",
            "download_url": f"/recruitment/api/download-resume/{app.id}/",
        })
    elif candidate and candidate.resume:
        docs.append({
            "label": "Resume / CV",
            "icon": "document-text-outline",
            "view_url": candidate.resume.url,
            "download_url": candidate.resume.url,
        })

    if candidate:
        if candidate.cover_letter:
            docs.append({
                "label": "Cover Letter",
                "icon": "mail-outline",
                "view_url": candidate.cover_letter.url,
                "download_url": candidate.cover_letter.url,
            })
        if candidate.graduation_certificate:
            docs.append({
                "label": "Graduation Certificate",
                "icon": "school-outline",
                "view_url": candidate.graduation_certificate.url,
                "download_url": candidate.graduation_certificate.url,
            })
        if candidate.transcripts:
            docs.append({
                "label": "Transcripts",
                "icon": "reader-outline",
                "view_url": candidate.transcripts.url,
                "download_url": candidate.transcripts.url,
            })

        # Portal uploads submitted by the candidate via their offer-letter portal link
        _type_icons = {
            "medical": "medkit-outline",
            "marksheet": "school-outline",
            "experience": "briefcase-outline",
            "passport": "card-outline",
            "id_card": "id-card-outline",
            "other": "attach-outline",
        }
        portal_uploads = CandidatePortalUpload.objects.filter(
            offer__candidate_id=candidate
        ).order_by("uploaded_at")
        for upload in portal_uploads:
            docs.append({
                "label": upload.label or upload.get_document_type_display(),
                "icon": _type_icons.get(upload.document_type, "attach-outline"),
                "view_url": upload.file.url,
                "download_url": upload.file.url,
            })

    return render(request, "recruitment/application_documents.html", {
        "app": app,
        "candidate": candidate,
        "docs": docs,
    })


def candidate_documents(request, candidate_id):
    """Documents page for a Candidate object (used from candidate dashboard)."""
    from recruitment.models import Candidate, CandidatePortalUpload
    from django.http import Http404
    try:
        candidate = Candidate.objects.select_related("recruitment_id").get(id=candidate_id)
    except Candidate.DoesNotExist:
        raise Http404

    docs = []
    if candidate.resume:
        docs.append({
            "label": "Resume / CV",
            "icon": "document-text-outline",
            "view_url": candidate.resume.url,
            "download_url": candidate.resume.url,
        })
    if candidate.cover_letter:
        docs.append({
            "label": "Cover Letter",
            "icon": "mail-outline",
            "view_url": candidate.cover_letter.url,
            "download_url": candidate.cover_letter.url,
        })
    if candidate.graduation_certificate:
        docs.append({
            "label": "Graduation Certificate",
            "icon": "school-outline",
            "view_url": candidate.graduation_certificate.url,
            "download_url": candidate.graduation_certificate.url,
        })
    if candidate.transcripts:
        docs.append({
            "label": "Transcripts",
            "icon": "reader-outline",
            "view_url": candidate.transcripts.url,
            "download_url": candidate.transcripts.url,
        })

    _type_icons = {
        "medical": "medkit-outline",
        "marksheet": "school-outline",
        "experience": "briefcase-outline",
        "passport": "card-outline",
        "id_card": "id-card-outline",
        "other": "attach-outline",
    }
    portal_uploads = CandidatePortalUpload.objects.filter(
        offer__candidate_id=candidate
    ).order_by("uploaded_at")
    for upload in portal_uploads:
        docs.append({
            "label": upload.label or upload.get_document_type_display(),
            "icon": _type_icons.get(upload.document_type, "attach-outline"),
            "view_url": upload.file.url,
            "download_url": upload.file.url,
        })

    class _FakeApp:
        name = candidate.name
        email = candidate.email
        phone = candidate.mobile
        class recruitment:
            pass
    _FakeApp.recruitment.title = candidate.recruitment_id.title if candidate.recruitment_id else ""

    return render(request, "recruitment/application_documents.html", {
        "app": _FakeApp,
        "candidate": candidate,
        "docs": docs,
    })


# ── DELETE APPLICATION ────────────────────────────────────────
@csrf_exempt
def delete_candidate(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        app_id = int(data["id"])
        from recruitment.models import JobApplication
        app = JobApplication.objects.filter(id=app_id).first()
        if app:
            Candidate.objects.filter(
                email=app.email,
                recruitment_id=app.recruitment,
            ).delete()
            app.delete()
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ── HR OVERRIDE ───────────────────────────────────────────────
@csrf_exempt
def hr_override_application(request):
    if request.method != "POST":
        return JsonResponse({"error": "invalid"}, status=400)
    data = json.loads(request.body)
    from recruitment.models import JobApplication
    try:
        app = JobApplication.objects.get(id=data["id"])
    except JobApplication.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)

    action = data.get("action")
    justification = (data.get("justification") or "").strip()
    if action == "promote":
        if not justification:
            return JsonResponse({"error": "Justification is required."}, status=400)
        app.status = "screened"
        app.hr_override = True
        app.hr_override_justification = justification
        app.excluded_by_second_filter = False
        app.save(update_fields=["status", "hr_override", "hr_override_justification", "excluded_by_second_filter"])
        _promote_to_pipeline(app)
    elif action == "demote":
        app.status = "rejected"
        app.hr_override = True
        app.save(update_fields=["status", "hr_override", "excluded_by_second_filter"])
        try:
            Candidate.objects.filter(
                email=app.email,
                recruitment_id=app.recruitment,
            ).delete()
        except Exception:
            pass
    else:
        return JsonResponse({"error": "invalid action"}, status=400)

    return JsonResponse({"success": True})


# ── SECOND FILTER ─────────────────────────────────────────────
@csrf_exempt
def second_filter_applications(request):
    if request.method != "POST":
        return JsonResponse({"error": "invalid"}, status=400)
    data = json.loads(request.body)
    rec_id = data.get("rec_id")
    target_count = int(data.get("target_count", 10))

    from recruitment.models import JobApplication
    screened = list(JobApplication.objects.filter(recruitment_id=rec_id, status="screened"))
    if target_count >= len(screened):
        JobApplication.objects.filter(recruitment_id=rec_id, status="screened").update(
            excluded_by_second_filter=False
        )
        return JsonResponse({"success": True, "message": "No filtering needed"})

    try:
        jd = Recruitment.objects.get(id=rec_id).description
    except Recruitment.DoesNotExist:
        return JsonResponse({"error": "Invalid recruitment"}, status=400)

    candidates_list = [
        {"id": a.id, "name": a.name, "score": a.score or 0, "reason": a.ai_reason or ""}
        for a in screened
    ]

    from recruitment.ai import rank_top_candidates
    selected_ids = rank_top_candidates(jd, candidates_list, target_count)

    JobApplication.objects.filter(recruitment_id=rec_id, status="screened").update(
        excluded_by_second_filter=False
    )
    excluded_ids = [a.id for a in screened if a.id not in selected_ids]
    JobApplication.objects.filter(id__in=excluded_ids).update(excluded_by_second_filter=True)

    return JsonResponse({"success": True, "excluded_ids": excluded_ids, "kept": len(selected_ids)})


# ── APPLICATIONS POLL (live status updates) ───────────────────
def applications_poll(request):
    from recruitment.models import JobApplication
    apps = JobApplication.objects.values(
        "id", "status", "score", "ai_reason", "hr_override", "excluded_by_second_filter",
        "skills", "rejection_email_sent",
    )
    return JsonResponse({"applications": list(apps)})


# ── REJECT WITH EMAIL (HR-triggered only) ────────────────────
@csrf_exempt
@login_required
def reject_application_with_email(request):
    """HR explicitly rejects a candidate and optionally sends a rejection email with justification."""
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    data = json.loads(request.body)
    from recruitment.models import JobApplication
    try:
        app = JobApplication.objects.get(id=data["id"])
    except JobApplication.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)

    justification = (data.get("justification") or "").strip()
    send_email = data.get("send_email", True)

    app.status = "rejected"
    app.rejection_justification = justification
    app.save(update_fields=["status", "rejection_justification"])

    # Remove from pipeline if promoted
    try:
        Candidate.objects.filter(email=app.email, recruitment_id=app.recruitment).delete()
    except Exception:
        pass

    if send_email and app.email and "careers.local" not in app.email:
        try:
            from recruitment.email_utils import send_recruitment_email
            job_title = app.recruitment.title or str(app.recruitment.job_position_id or "the position")
            subject = f"Your application for {job_title}"
            justification_line = f"\n\nFeedback: {justification}" if justification else ""
            body = (
                f"Hi {app.name},\n\n"
                f"Thank you for taking the time to apply for {job_title}. After careful review, "
                f"we have decided to move forward with other candidates at this time."
                f"{justification_line}\n\n"
                f"We appreciate your interest and wish you the best in your search.\n\n"
                f"Regards,\nHR Team"
            )
            threading.Thread(
                target=send_recruitment_email,
                kwargs={"subject": subject, "body": body, "to": [app.email]},
                daemon=True,
            ).start()
            app.rejection_email_sent = True
            app.save(update_fields=["rejection_email_sent"])
        except Exception:
            pass

    return JsonResponse({"success": True})


# ── AI JD BUILDER ─────────────────────────────────────────────
@csrf_exempt
def generate_jd_ai(request):
    if request.method != "POST":
        return JsonResponse({"error": "invalid"}, status=400)

    import re as _re
    data = json.loads(request.body)
    title         = data.get("title", "").strip()
    experience    = data.get("experience", "").strip()
    education     = data.get("education", "").strip()
    field_of_study = data.get("field_of_study", "").strip()
    languages     = data.get("languages", "").strip()
    nationality   = data.get("nationality", "Any").strip() or "Any"

    from groq import Groq
    from django.conf import settings
    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = f"""You are an expert HR professional. Write a professional, polished job description ready for posting.

Job Title: {title or "Not specified"}
Years of Experience Required: {experience or "Not specified"}
Education Level: {education or "Not specified"}
Field of Study / Specialisation: {field_of_study or "Not specified"}
Languages Required: {languages or "Not specified"}
Nationality Preference: {nationality}

Write a complete job description that includes:
1. A brief job overview (2-3 sentences)
2. Key Responsibilities (6-8 bullet points)
3. Required Qualifications (education, experience, technical skills)
4. Preferred Qualifications
5. What We Offer

Format the output as clean HTML using only <p>, <strong>, <ul>, and <li> tags. Do not include <html>, <body>, or any wrapper tags. Do not use markdown.
"""

    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        jd_html = res.choices[0].message.content.strip()
        # Strip any accidental markdown code fences
        jd_html = _re.sub(r"^```[\w]*\n?|```$", "", jd_html, flags=_re.MULTILINE).strip()
        return JsonResponse({"success": True, "jd": jd_html})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def _parse_ai_result(raw):
    """Extract JSON from AI output, handling markdown fences, preamble, and literal newlines in strings."""
    import json as _json, re as _re
    if not raw:
        return None
    # Strip markdown code fences: ```json ... ``` or ``` ... ```
    fenced = _re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, _re.DOTALL)
    if fenced:
        raw = fenced.group(1)
    # Find first { ... } block
    match = _re.search(r'\{.*\}', raw, _re.DOTALL)
    if not match:
        return None
    candidate_json = match.group()

    # Layer 1: direct parse
    try:
        data = _json.loads(candidate_json)
        if "score" in data and "decision" in data:
            # Normalise reason key — model sometimes uses alternate names
            if "reason" not in data:
                for alt in ("reasoning", "explanation", "summary", "assessment"):
                    if alt in data:
                        data["reason"] = data[alt]
                        break
            return data
    except Exception:
        pass

    # Layer 2: replace literal newlines/carriage-returns inside strings
    try:
        sanitized = candidate_json.replace('\r\n', '\\n').replace('\n', '\\n').replace('\r', '\\n')
        data = _json.loads(sanitized)
        if "score" in data and "decision" in data:
            return data
    except Exception:
        pass

    # Layer 3: extract fields individually with targeted regex
    try:
        score_m = _re.search(r'"score"\s*:\s*(\d+)', candidate_json)
        decision_m = _re.search(r'"decision"\s*:\s*"(select|reject)"', candidate_json)
        reason_m = _re.search(r'"reason"\s*:\s*"(.*?)(?<!\\)"(?=\s*[,}])', candidate_json, _re.DOTALL)
        if score_m and decision_m:
            return {
                "score": int(score_m.group(1)),
                "decision": decision_m.group(1),
                "reason": reason_m.group(1).replace('\\n', '\n') if reason_m else "",
            }
    except Exception:
        pass

    return None


# ── SKILL EXTRACTOR ──────────────────────────────────────────
def _extract_skills_from_reason(reason_text):
    """Pull skill-like tokens from the AI reasoning text."""
    import re as _re
    if not reason_text:
        return []

    # Prefer STRENGTHS section if present, fall back to full text
    strengths_match = _re.search(r'STRENGTHS[:\s]+(.*?)(?:WEAKNESSES|DECISION|$)', reason_text, _re.DOTALL | _re.IGNORECASE)
    source = strengths_match.group(1) if strengths_match else reason_text

    skill_pattern = _re.compile(
        r'\b('
        # Tech / Engineering
        r'Python|Java(?:Script)?|TypeScript|React|Vue|Angular|Node\.js|Django|FastAPI|'
        r'SQL|NoSQL|PostgreSQL|MySQL|MongoDB|Redis|Docker|Kubernetes|AWS|GCP|Azure|'
        r'CI/CD|REST|GraphQL|Machine Learning|Deep Learning|NLP|Data Science|'
        r'TensorFlow|PyTorch|Pandas|NumPy|C\+\+|C#|\.NET|PHP|Ruby|Go|Rust|'
        r'Swift|Kotlin|Flutter|iOS|Android|DevOps|Linux|'
        # Business / Finance
        r'Excel|Power BI|Tableau|SAP|Salesforce|QuickBooks|ERP|CRM|'
        r'Finance|Accounting|Budgeting|Forecasting|Audit|'
        # HR / Recruitment
        r'HR|Recruitment|Payroll|HRIS|Onboarding|'
        # Customer Service / Support
        r'Customer Service|Customer Support|Call Center|Help Desk|Helpdesk|'
        r'Ticketing|Zendesk|Freshdesk|ServiceNow|Live Chat|CRM|'
        r'Complaint Handling|Issue Resolution|Client Relations|'
        # Soft / Generic
        r'Leadership|Communication|Project Management|Agile|Scrum|'
        r'Problem[- ]?Solving|Time Management|Team(?:work)?|Collaboration|'
        r'Negotiation|Presentation|Training|Coaching|Mentoring|'
        r'Analytical|Research|Writing|Documentation|Reporting'
        r')\b',
        _re.IGNORECASE,
    )

    # Also try to pull from bullet lines first (higher signal)
    bullets = _re.findall(r'[-•*]\s*(.+)', source)
    search_targets = (bullets[:8] if bullets else []) + [source]

    seen = set()
    skills = []
    for text in search_targets:
        for m in skill_pattern.finditer(text):
            s = m.group(0).strip()
            key = s.lower()
            if key not in seen:
                seen.add(key)
                # Normalise capitalisation
                skills.append(s.title() if s.islower() else s)
        if len(skills) >= 10:
            break
    return skills[:10]


# ── AI BACKGROUND PROCESSOR ───────────────────────────────────
def process_application(app_id):
    import time, json, re

    time.sleep(2)

    from recruitment.models import JobApplication
    try:
        app = JobApplication.objects.get(id=app_id)
    except JobApplication.DoesNotExist:
        return

    try:
        jd = app.recruitment.description
    except Exception:
        return

    try:
        candidate_text = build_candidate_text({
            "name": app.name,
            "email": app.email,
            "phone": app.phone,
            "experience": app.experience,
            "why_apply": app.why_apply,
            "resume_path": app.resume_path,
        })
    except Exception as e:
        app.status = "rejected"
        app.ai_reason = f"Resume parse error: {e}"
        app.save(update_fields=["status", "ai_reason"])
        return

    try:
        raw_result = screen_candidate(jd, candidate_text)
    except Exception as e:
        app.status = "rejected"
        app.ai_reason = f"AI error: {e}"
        app.save(update_fields=["status", "ai_reason"])
        return

    result = _parse_ai_result(raw_result)
    if result is None:
        # One retry on parse failure
        try:
            raw_result = screen_candidate(jd, candidate_text)
            result = _parse_ai_result(raw_result)
        except Exception:
            result = None
    if result is None:
        result = {"score": 0, "decision": "reject", "reason": "AI response could not be parsed after retry."}

    app.score = result.get("score", 0)
    app.ai_reason = result.get("reason", "")
    app.status = "screened" if result.get("decision") == "select" else "rejected"
    app.skills = _extract_skills_from_reason(result.get("reason", ""))
    app.save(update_fields=["score", "ai_reason", "status", "skills"])

    if app.status == "screened":
        _promote_to_pipeline(app)
        # Only send selection email automatically; rejection email requires HR to click "Reject & Email"
        if app.email and "careers.local" not in app.email:
            try:
                from recruitment.email_utils import send_recruitment_email
                job_title = app.recruitment.title or str(app.recruitment.job_position_id or "the position")
                subject = f"Update on your application — {job_title}"
                body = (
                    f"Hi {app.name},\n\n"
                    f"We're pleased to let you know that your application for {job_title} "
                    f"has been shortlisted. Our team will be in touch with interview details shortly.\n\n"
                    f"Regards,\nHR Team"
                )
                threading.Thread(
                    target=send_recruitment_email,
                    kwargs={"subject": subject, "body": body, "to": [app.email]},
                    daemon=True,
                ).start()
            except Exception:
                pass


def _promote_to_pipeline(app):
    """Auto-create a Candidate in the recruitment pipeline when AI shortlists an application."""
    stage = Stage.objects.filter(
        recruitment_id=app.recruitment
    ).order_by("sequence").first()

    if not stage:
        stage = Stage.objects.create(
            recruitment_id=app.recruitment,
            stage="AI Screened",
            stage_type="initial",
            sequence=1,
        )

    candidate, created = Candidate.objects.get_or_create(
        email=app.email,
        recruitment_id=app.recruitment,
        defaults={
            "name": (app.name or "")[:100],
            "mobile": (app.phone or "")[:15],
            "stage_id": stage,
            "source": "application",
            "country": app.country or "",
            "promoted_to_onboarding": False,
            "start_onboard": False,
            "hired": False,
            "canceled": False,
            "converted": False,
            "offer_letter_status": "not_sent",
            "experience_years": 0,
            "sequence": 1,
        },
    )
    if not created:
        candidate.stage_id = stage
        candidate.canceled = False
        candidate.hired = False
        candidate.is_active = True
        candidate.save(update_fields=["stage_id", "canceled", "hired", "is_active"])

    # Attach the resume from the temp path to Candidate.resume (proper FileField)
    if app.resume_path and not candidate.resume:
        try:
            from django.core.files import File as DjangoFile
            if os.path.exists(app.resume_path):
                with open(app.resume_path, "rb") as fh:
                    filename = os.path.basename(app.resume_path)
                    candidate.resume.save(filename, DjangoFile(fh), save=True)
        except Exception:
            pass


def get_reporting_managers(user):
    from employee.models import Employee

    managers = []

    try:
        emp = Employee.objects.select_related("employeeworkinformation").get(
            employee_user_id=user
        )

        current = emp.employeeworkinformation.reporting_manager

        while current:
            managers.append(current)

            if hasattr(current, "employeeworkinformation"):
                current = current.employeeworkinformation.reporting_manager
            else:
                break

    except Exception as e:
        print("Hierarchy error:", e)

    return managers


@login_required
def api_list_email_templates(request):
    from recruitment.models import JobEmailTemplate
    templates = list(JobEmailTemplate.objects.values(
        "id", "name", "is_default",
        "selection_subject", "selection_body",
        "rejection_subject", "rejection_body",
    ))
    return JsonResponse({"templates": templates})


@login_required
@csrf_exempt
def api_set_email_template(request):
    if request.method != "POST":
        return JsonResponse({"error": "invalid"}, status=400)
    from recruitment.models import JobEmailTemplate
    data = json.loads(request.body)
    tpl = get_object_or_404(JobEmailTemplate, id=data["id"])
    tpl.is_default = True
    tpl.save()
    return JsonResponse({"success": True})


def _generate_assisted_post(recruitment, platform):
    """Generate a polished job post for the given platform using Groq, with a template fallback."""
    from bs4 import BeautifulSoup
    from django.conf import settings

    careers_url = "https://hcmspro.net/careers/"
    jd_raw = BeautifulSoup(recruitment.description or "", "html.parser").get_text(separator="\n").strip()
    jd_snippet = jd_raw[:1200]

    skills_list = ", ".join(s.name for s in recruitment.skills.all()) if recruitment.skills.exists() else ""

    platform_instructions = {
        "linkedin": (
            "Write a LinkedIn company hiring post. Use a rocket emoji opener. "
            "Use ✔ emoji bullet points for requirements. End with 3-5 relevant hashtags "
            "like #Hiring #OmanJobs. Keep it under 300 words."
        ),
        "bayt": (
            "Write a Bayt.com job posting in professional ATS style. "
            "Use clear sections: About the Role, Requirements, How to Apply. Keep it under 350 words."
        ),
        "naukrigulf": (
            "Write a NaukriGulf job posting in professional ATS style. "
            "Use clear sections: Job Overview, Key Requirements, How to Apply. Keep it under 350 words."
        ),
    }

    prompt = f"""Generate a polished job posting for {platform} for the following recruitment.

Job Title: {recruitment.title}
Vacancies: {recruitment.vacancy or 1}
Skills Required: {skills_list or 'As per JD'}
Job Description:
{jd_snippet}

Careers/Apply Page: {careers_url}

Instructions: {platform_instructions.get(platform, '')}

Return ONLY the post text, no preamble or explanation."""

    try:
        from groq import Groq
        client = Groq(api_key=settings.GROQ_API_KEY)
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
        )
        return res.choices[0].message.content.strip()
    except Exception:
        # Hardcoded fallback
        if platform == "linkedin":
            return (
                f"We're Hiring: {recruitment.title}\n\n"
                f"We are looking for talented professionals to join our growing team.\n\n"
                f"Requirements:\n"
                f"{''.join(f'- {s.name}{chr(10)}' for s in recruitment.skills.all()) or '- See full JD on our careers page'}\n"
                f"Apply here: {careers_url}\n\n"
                f"#Hiring #OmanJobs #{recruitment.title.replace(' ', '')}"
            )
        else:
            return (
                f"Job Title: {recruitment.title}\n\n"
                f"We are seeking qualified professionals for this position.\n\n"
                f"Key Requirements:\n"
                f"{''.join(f'- {s.name}{chr(10)}' for s in recruitment.skills.all()) or '- Please refer to the full job description'}\n\n"
                f"How to Apply:\nVisit our careers page: {careers_url}\n"
            )


_LINKEDIN_COMPANY_ORG_ID = "113341432"


@login_required
@permission_required(perm="recruitment.change_recruitment")
def publish_to_linkedin_channel(request, rec_id):
    if request.method != "POST":
        return JsonResponse({"error": "invalid"}, status=400)
    recruitment = get_object_or_404(Recruitment, id=rec_id)
    if recruitment.published_to_linkedin:
        return JsonResponse({"success": True, "already": True})

    import uuid
    import requests as _req

    post_content = _generate_assisted_post(recruitment, "linkedin")
    external_id = "LI-COMPANY-" + uuid.uuid4().hex[:8].upper()

    linkedin_acc = recruitment.linkedin_account_id or LinkedInAccount.objects.filter(
        is_active=True
    ).first()

    if linkedin_acc and linkedin_acc.api_token:
        org_id = linkedin_acc.organization_id or _LINKEDIN_COMPANY_ORG_ID
        site_url = request.build_absolute_uri("/")[:-1]
        careers_url = f"{site_url}/recruitment/application-form?recruitmentId={recruitment.id}"

        payload = {
            "author": f"urn:li:organization:{org_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post_content},
                    "shareMediaCategory": "ARTICLE",
                    "media": [{
                        "status": "READY",
                        "originalUrl": careers_url,
                        "title": {"text": recruitment.title},
                    }],
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        resp = _req.post(
            "https://api.linkedin.com/v2/ugcPosts",
            json=payload,
            headers={
                "Authorization": f"Bearer {linkedin_acc.api_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            },
            timeout=15,
        )

        if resp.status_code == 201:
            resp_data = resp.json()
            recruitment.published_to_linkedin = True
            recruitment.linkedin_posted_at = timezone.now()
            recruitment.linkedin_external_id = external_id
            recruitment.linkedin_post_id = resp_data.get("id", "")
            recruitment.save(update_fields=[
                "published_to_linkedin", "linkedin_posted_at",
                "linkedin_external_id", "linkedin_post_id",
            ])
            return JsonResponse({"success": True, "posted": True})

    # Fallback: clipboard-assisted publishing
    recruitment.published_to_linkedin = True
    recruitment.linkedin_posted_at = timezone.now()
    recruitment.linkedin_external_id = external_id
    recruitment.save(update_fields=["published_to_linkedin", "linkedin_posted_at", "linkedin_external_id"])

    return JsonResponse({
        "success": True,
        "post_content": post_content,
        "portal_url": f"https://www.linkedin.com/company/{_LINKEDIN_COMPANY_ORG_ID}/admin/dashboard/",
        "external_id": external_id,
    })


@login_required
@permission_required(perm="recruitment.change_recruitment")
def publish_to_bayt(request, rec_id):
    if request.method != "POST":
        return JsonResponse({"error": "invalid"}, status=400)
    recruitment = get_object_or_404(Recruitment, id=rec_id)
    if recruitment.published_to_bayt:
        return JsonResponse({"success": True, "already": True})

    import uuid
    from django.utils import timezone

    post_content = _generate_assisted_post(recruitment, "bayt")
    external_id = "BAYT-" + uuid.uuid4().hex[:8].upper()

    recruitment.published_to_bayt = True
    recruitment.bayt_posted_at = timezone.now()
    recruitment.bayt_external_id = external_id
    recruitment.save(update_fields=["published_to_bayt", "bayt_posted_at", "bayt_external_id"])

    return JsonResponse({
        "success": True,
        "post_content": post_content,
        "portal_url": "https://www.bayt.com/en/employers/",
        "external_id": external_id,
    })


@login_required
@permission_required(perm="recruitment.change_recruitment")
def publish_to_naukrigulf(request, rec_id):
    if request.method != "POST":
        return JsonResponse({"error": "invalid"}, status=400)
    recruitment = get_object_or_404(Recruitment, id=rec_id)
    if recruitment.published_to_naukrigulf:
        return JsonResponse({"success": True, "already": True})

    import uuid
    from django.utils import timezone

    post_content = _generate_assisted_post(recruitment, "naukrigulf")
    external_id = "NG-" + uuid.uuid4().hex[:8].upper()

    recruitment.published_to_naukrigulf = True
    recruitment.naukrigulf_posted_at = timezone.now()
    recruitment.naukrigulf_external_id = external_id
    recruitment.save(update_fields=["published_to_naukrigulf", "naukrigulf_posted_at", "naukrigulf_external_id"])

    return JsonResponse({
        "success": True,
        "post_content": post_content,
        "portal_url": "https://www.naukrigulf.com/employer/",
        "external_id": external_id,
    })


@login_required
def candidate_promote_to_onboarding(request, cand_id):
    from datetime import timedelta
    from django.utils import timezone as tz
    from recruitment.models import OfferLetter
    from recruitment.approvals.engine import route_offer
    from onboarding.models import CandidateStage, CandidateTask, OnboardingTask

    candidate = get_object_or_404(Candidate, id=cand_id)
    candidate.start_onboard = True
    candidate.promoted_to_onboarding = True
    candidate.save()

    # Add to onboarding pipeline (CandidateStage) so the candidate appears in the onboarding board
    if not CandidateStage.objects.filter(candidate_id=candidate).exists():
        try:
            first_stage = (
                candidate.recruitment_id.onboarding_stage.order_by("sequence").first()
                if candidate.recruitment_id else None
            )
            if first_stage:
                CandidateStage.objects.create(
                    candidate_id=candidate,
                    onboarding_stage_id=first_stage,
                )
                # Auto-assign any recruitment-level onboarding tasks
                for task in OnboardingTask.objects.filter(recruitment_id=candidate.recruitment_id):
                    CandidateTask.objects.get_or_create(
                        candidate_id=candidate, onboarding_task_id=task
                    )
        except Exception:
            pass

    # Auto-create a draft offer letter, or reset a rejected one back to draft
    existing_offer = OfferLetter.objects.filter(candidate_id=candidate).first()
    if existing_offer and existing_offer.status == "rejected":
        existing_offer.status = "draft"
        existing_offer.save()
    elif not existing_offer:
        joining_date = (tz.now() + timedelta(days=30)).date()
        job_pos = candidate.job_position_id
        if not job_pos and candidate.recruitment_id:
            job_pos = (
                candidate.recruitment_id.job_position_id
                or candidate.recruitment_id.open_positions.first()
            )
        position = job_pos.job_position if job_pos else "To be confirmed"
        dept = ""
        try:
            if job_pos and job_pos.department_id:
                dept = job_pos.department_id.department
        except Exception:
            pass
        offer = OfferLetter.objects.create(
            candidate_id=candidate,
            position=position,
            department=dept,
            basic_salary=0,
            joining_date=joining_date,
            status="draft",
        )
        try:
            chain = route_offer(offer)
            if chain:
                offer.status = "pending_approval"
                offer.approval_submitted_at = tz.now()
                offer.save()
        except Exception:
            pass

    messages.success(request, _("Candidate promoted to onboarding."))
    return redirect("onboarding-letters")


@login_required
def candidate_promote_to_pipeline(request, cand_id):
    candidate = get_object_or_404(Candidate, id=cand_id)
    if candidate.recruitment_id:
        first_stage = Stage.objects.filter(
            recruitment_id=candidate.recruitment_id
        ).order_by("sequence").first()
        if first_stage:
            candidate.stage_id = first_stage
            candidate.save()
    messages.success(request, _("Candidate promoted to pipeline."))
    return redirect(request.META.get("HTTP_REFERER", "/recruitment/pipeline/"))


@login_required
def candidate_reject_send_email(request, cand_id):
    candidate = get_object_or_404(Candidate, id=cand_id)
    justification = (request.POST.get("justification") or "").strip()
    send_email_flag = request.POST.get("send_email", "1") not in ("0", "false", "False")

    if send_email_flag:
        try:
            if justification:
                from recruitment.email_utils import send_recruitment_email
                job_title = str(candidate.job_position_id or "the position")
                subject = f"Your application for {job_title}"
                body = (
                    f"Hi {candidate.name},\n\n"
                    f"Thank you for applying for {job_title}. After careful review, "
                    f"we have decided to move forward with other candidates.\n\n"
                    f"Feedback: {justification}\n\n"
                    f"We appreciate your interest and wish you the best.\n\n"
                    f"Regards,\nHR Team"
                )
                threading.Thread(
                    target=send_recruitment_email,
                    kwargs={"subject": subject, "body": body, "to": [candidate.email]},
                    daemon=True,
                ).start()
            else:
                from recruitment.email_utils import send_rejection_email
                send_rejection_email(candidate)
        except Exception:
            pass

    candidate.canceled = True
    candidate.save()
    messages.success(request, _("Candidate rejected."))
    return redirect(request.META.get("HTTP_REFERER", "/recruitment/candidate-view/"))