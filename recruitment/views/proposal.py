"""
recruitment/views/proposal.py

Views for the Employment Proposal stage — list, create, detail, edit,
e-sign, reject, role mapping, and convert-to-offer-letter.
"""


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from employee.models import Employee
from recruitment.approvals.proposal_engine import (
    advance_after_signature,
    annotate_display_status,
    reject_proposal,
    route_proposal,
)
from recruitment.models import (
    InterviewSchedule,
)
from recruitment.models_proposal import (
    CONTRACTUAL_CHAIN,
    EmploymentProposal,
    PERMANENT_CHAIN,
    ProposalApproval,
    ProposalRoleAssignment,
    ProposalStatusLog,
    ROLE_LABELS,
)


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────
def _employee(user):
    return getattr(user, "employee_get", None)


def _prefill_from_interview(interview):
    """Build a dict of initial values for the proposal form using whatever the
    DB already knows about the candidate / recruitment / manpower request.
    """
    cand = interview.candidate_id if interview else None
    recruitment = getattr(cand, "recruitment_id", None) if cand else None
    mr = getattr(recruitment, "manpower_request", None) if recruitment else None

    data = {}
    if cand:
        data.update({
            "applicant_name": cand.name,
            "nationality": getattr(cand, "country", "") or "",
            "dob": getattr(cand, "dob", None),
            "application_date": cand.created_at.date() if cand.created_at else None,
        })
        ref_emp = getattr(cand, "referral", None)
        if ref_emp:
            data["candidate_referred"] = "staff_number"
            data["referral_staff_number"] = getattr(ref_emp, "badge_id", "") or ""
        elif getattr(cand, "source", "") == "consultancy":
            data["candidate_referred"] = "consultancy"

        exp = getattr(cand, "experience_years", None)
        if exp is not None:
            data["experience_overseas_years"] = exp

        # Pull AI-extracted personal details from screening profile
        sp = getattr(cand, "screening_profile", None)
        if sp:
            if sp.extracted_nationality:
                data["nationality"] = sp.extracted_nationality
            if sp.extracted_present_employer:
                data["present_employer"] = sp.extracted_present_employer
            if sp.extracted_marital_status:
                data["marital_status"] = sp.extracted_marital_status
            if sp.extracted_dob:
                data["dob"] = sp.extracted_dob
            if sp.extracted_place_of_birth:
                data["place_of_birth"] = sp.extracted_place_of_birth
            if sp.extracted_qualification_academic:
                data["qualification_academic"] = sp.extracted_qualification_academic
            if sp.extracted_qualification_professional:
                data["qualification_professional"] = sp.extracted_qualification_professional
            if sp.extracted_experience_local_years is not None:
                data["experience_local_years"] = sp.extracted_experience_local_years
            if sp.extracted_experience_overseas_years is not None:
                data["experience_overseas_years"] = sp.extracted_experience_overseas_years
            data["lang_arabic"] = sp.extracted_lang_arabic
            data["lang_english"] = sp.extracted_lang_english
            if sp.extracted_lang_others:
                data["lang_others"] = sp.extracted_lang_others
            if sp.extracted_driving_license:
                data["driving_license"] = sp.extracted_driving_license

    if recruitment:
        data.update({
            "post_applied_for": recruitment.title or "",
            "job_no": getattr(recruitment, "job_id", "") or "",
            "post_location": getattr(recruitment, "location", "") or "",
            "grade_group": getattr(recruitment, "grade", "") or "",
            # Contract period from Recruitment.start_date / end_date
            "contract_period_from": getattr(recruitment, "start_date", None),
            "contract_period_to": getattr(recruitment, "end_date", None),
            # HOD comments seeded from Recruitment.justification
            "hod_comments": getattr(recruitment, "justification", "") or "",
            # Employment type → Permanent (Full Time) vs Contractual mapping
            "employment_contract_type": (
                "permanent" if getattr(recruitment, "employment_type", "") == "full_time"
                else "temporary" if getattr(recruitment, "employment_type", "") in ("contract", "internship", "temporary")
                else ""
            ),
            # Budget availability → Budgeted flag
            "salary_budgeted": (
                "budgeted" if getattr(recruitment, "budget_available", False)
                else "not_budgeted"
            ),
            # Whether expat candidates are allowed (heuristic for "Local Transfer = No")
            "local_transfer": not bool(getattr(recruitment, "expat_allowed", False)),
        })
        # Use Recruitment.budget as a starting gross-salary hint
        budget = getattr(recruitment, "budget", None)
        if budget:
            data["gross_salary"] = budget

    if mr:
        data.setdefault("post_applied_for", str(getattr(mr, "post_title", "") or ""))
        dept = getattr(mr, "department", None)
        if dept:
            data["division_department"] = str(dept)
        requested_by = getattr(mr, "requested_by", None)
        if requested_by:
            data["reporting_to"] = requested_by.get_full_name()
            data["reporting_staff_no"] = getattr(requested_by, "badge_id", "") or ""

    if interview:
        data["interview_date"] = interview.interview_date

    return data


# ────────────────────────────────────────────────────────────────────────────
# Picker (modal) — opens after "Create Proposal" click
# ────────────────────────────────────────────────────────────────────────────
@login_required
def proposal_picker(request, interview_id):
    """Render the two-card template picker modal (HTMX target)."""
    interview = get_object_or_404(InterviewSchedule, id=interview_id)
    return render(
        request,
        "recruitment/proposals/proposal_picker.html",
        {"interview": interview},
    )


# ────────────────────────────────────────────────────────────────────────────
# Create / Edit
# ────────────────────────────────────────────────────────────────────────────
@login_required
def proposal_create(request, interview_id):
    interview = get_object_or_404(InterviewSchedule, id=interview_id)
    template_type = request.GET.get("template") or request.POST.get("template_type")
    if template_type not in dict(EmploymentProposal.TEMPLATE_CHOICES):
        messages.error(request, _("Choose a proposal template first."))
        return redirect("interview-view")

    if request.method == "POST":
        proposal = _save_proposal_from_post(request, interview=interview,
                                            template_type=template_type)
        route_result = route_proposal(proposal)
        if route_result == "no_approvers":
            messages.warning(
                request,
                _("Proposal saved as draft — no approvers mapped. "
                  "Open Proposal Role Mapping to assign signatories."),
            )
        else:
            messages.success(request, _("Proposal submitted for e-sign approval."))
        return redirect("proposal-list")

    cand = interview.candidate_id
    initial = _prefill_from_interview(interview)
    recruitment_obj = getattr(cand, "recruitment_id", None)
    mr_obj = getattr(recruitment_obj, "manpower_request", None) if recruitment_obj else None
    return render(
        request,
        "recruitment/proposals/proposal_form.html",
        {
            "interview": interview,
            "candidate": cand,
            "recruitment_obj": recruitment_obj,
            "manpower_request": mr_obj,
            "template_type": template_type,
            "initial": initial,
            "is_edit": False,
            "MARITAL_CHOICES": EmploymentProposal.MARITAL_CHOICES,
            "REFERRAL_CHOICES": EmploymentProposal.REFERRAL_CHOICES,
            "CONSULTANCY_CHOICES": EmploymentProposal.CONSULTANCY_CHOICES,
            "CONTRACT_TYPE_CHOICES": EmploymentProposal.CONTRACT_TYPE_CHOICES,
            "LICENSE_CHOICES": EmploymentProposal.LICENSE_CHOICES,
            "SALARY_BUDGET_CHOICES": EmploymentProposal.SALARY_BUDGET_CHOICES,
            "LSA_TIER_CHOICES": EmploymentProposal.LSA_TIER_CHOICES,
            "FAMILY_STATUS_CHOICES": EmploymentProposal.FAMILY_STATUS_CHOICES,
        },
    )


@login_required
def proposal_edit(request, pk):
    proposal = get_object_or_404(EmploymentProposal, pk=pk)
    if proposal.is_terminal:
        messages.error(request, _("This proposal is finalised and cannot be edited."))
        return redirect("proposal-list")

    if request.method == "POST":
        _save_proposal_from_post(request, proposal=proposal,
                                 template_type=proposal.template_type)
        # If chain already exists and is unsigned, rebuild it from scratch
        if not proposal.approvals.filter(
            status__in=[ProposalApproval.STATUS_APPROVED, ProposalApproval.STATUS_REJECTED]
        ).exists():
            route_proposal(proposal)
        messages.success(request, _("Proposal updated."))
        return redirect("proposal-list")

    return render(
        request,
        "recruitment/proposals/proposal_form.html",
        {
            "proposal": proposal,
            "interview": proposal.interview,
            "candidate": proposal.candidate,
            "template_type": proposal.template_type,
            "initial": _proposal_to_initial(proposal),
            "is_edit": True,
            "MARITAL_CHOICES": EmploymentProposal.MARITAL_CHOICES,
            "REFERRAL_CHOICES": EmploymentProposal.REFERRAL_CHOICES,
            "CONSULTANCY_CHOICES": EmploymentProposal.CONSULTANCY_CHOICES,
            "CONTRACT_TYPE_CHOICES": EmploymentProposal.CONTRACT_TYPE_CHOICES,
            "LICENSE_CHOICES": EmploymentProposal.LICENSE_CHOICES,
            "SALARY_BUDGET_CHOICES": EmploymentProposal.SALARY_BUDGET_CHOICES,
            "LSA_TIER_CHOICES": EmploymentProposal.LSA_TIER_CHOICES,
            "FAMILY_STATUS_CHOICES": EmploymentProposal.FAMILY_STATUS_CHOICES,
        },
    )


def _proposal_to_initial(proposal):
    """Convert a saved EmploymentProposal to a dict suitable for the form template."""
    return {f.name: getattr(proposal, f.name) for f in proposal._meta.fields}


_DECIMAL_FIELDS = {
    "basic_salary", "hra_allowance", "transport_allowance", "addl_resp_allowance",
    "overtime_allowance", "food_allowance", "lsa_allowance", "gross_salary",
    "experience_local_years", "experience_overseas_years",
}
_INT_FIELDS = {"employment_contract_months", "air_passage_months"}
_DATE_FIELDS = {"contract_period_from", "contract_period_to",
                "application_date", "interview_date", "dob"}
_BOOL_FIELDS = {"contractual", "is_new_appointment", "has_relative_in_company",
                "local_transfer", "lang_arabic", "lang_english", "medical_clause"}


def _save_proposal_from_post(request, *, interview=None, proposal=None, template_type):
    """Persist POST data onto a new or existing EmploymentProposal."""
    post = request.POST
    if proposal is None:
        proposal = EmploymentProposal(
            candidate=interview.candidate_id,
            interview=interview,
            recruitment=getattr(interview.candidate_id, "recruitment_id", None),
            template_type=template_type,
        )
        recruitment_obj = proposal.recruitment
        if recruitment_obj is not None:
            proposal.manpower_request = getattr(recruitment_obj, "manpower_request", None)

    for f in proposal._meta.fields:
        name = f.name
        if name in ("id", "proposal_no", "status", "candidate", "interview",
                    "recruitment", "manpower_request", "template_type",
                    "created_at", "created_by", "modified_by", "is_active",
                    "salary_columns_json"):
            continue
        if name in _BOOL_FIELDS:
            setattr(proposal, name, post.get(name) in ("on", "true", "1", "yes"))
        elif name in _DATE_FIELDS:
            val = post.get(name) or None
            setattr(proposal, name, val if val else None)
        elif name in _DECIMAL_FIELDS:
            v = post.get(name, "").strip()
            setattr(proposal, name, v if v else None)
        elif name in _INT_FIELDS:
            v = post.get(name, "").strip()
            setattr(proposal, name, int(v) if v.isdigit() else None)
        elif name in post:
            setattr(proposal, name, post.get(name, "").strip())

    # Salary columns JSON — collect *_hrc and *_ceo columns
    rows = ["basic_salary", "hra_allowance", "transport_allowance",
            "addl_resp_allowance", "overtime_allowance", "food_allowance",
            "lsa_allowance", "gross_salary"]
    col_json = {}
    for r in rows:
        hrc = post.get(f"{r}_hrc", "").strip()
        ceo = post.get(f"{r}_ceo", "").strip()
        if hrc or ceo:
            col_json[r] = {"hrc": hrc, "ceo": ceo}
    proposal.salary_columns_json = col_json

    proposal.save()
    if not ProposalStatusLog.objects.filter(proposal=proposal, action="created").exists():
        ProposalStatusLog.objects.create(
            proposal=proposal, actor=request.user,
            action="created",
            note=f"Proposal {proposal.proposal_no} created ({proposal.get_template_type_display()}).",
        )
    return proposal


# ────────────────────────────────────────────────────────────────────────────
# List + Detail
# ────────────────────────────────────────────────────────────────────────────
@login_required
def proposal_list(request):
    """Full page listing of all proposals with e-sign chain summary."""
    employee = _employee(request.user)

    # ONEIC role-holders (ProposalRoleAssignment) always get the filtered view —
    # they should only see proposals where it is currently their turn to sign,
    # regardless of any Django permissions they happen to hold.
    is_oneic_role = bool(
        employee and ProposalRoleAssignment.objects.filter(employee=employee).exists()
    )
    is_admin = not is_oneic_role and (
        request.user.is_superuser
        or request.user.has_perm("recruitment.view_employmentproposal")
    )

    proposals = EmploymentProposal.objects.select_related(
        "candidate", "interview", "recruitment"
    ).order_by("-id")

    rows = []
    for p in proposals:
        chain = annotate_display_status(p)
        if not chain and p.status in (
            EmploymentProposal.STATUS_DRAFT, EmploymentProposal.STATUS_PENDING
        ):
            route_proposal(p)
            chain = annotate_display_status(p)
        active = next((s for s in chain if s.display_status == "active"), None)
        is_my_turn = bool(active and employee and active.approver_id == employee.id)
        rows.append({
            "proposal": p,
            "chain": chain,
            "active": active,
            "is_my_turn": is_my_turn,
            "all_approved": p.status == EmploymentProposal.STATUS_APPROVED,
            "is_rejected": p.status == EmploymentProposal.STATUS_REJECTED,
            "is_converted": p.status == EmploymentProposal.STATUS_CONVERTED,
        })

    # ONEIC approvers only see proposals where it is currently their turn to sign.
    if not is_admin:
        rows = [r for r in rows if r["is_my_turn"]]

    # Filter view variant (HTMX partial) for the Proposals tab on interview view.
    if request.GET.get("partial") == "1":
        template = "recruitment/proposals/proposal_list_partial.html"
    else:
        template = "recruitment/proposals/proposal_list.html"

    return render(request, template, {"rows": rows, "is_admin": is_admin})


@login_required
def proposal_detail(request, pk):
    """Render the read-only template view (PDF-faithful) with the e-sign chain."""
    proposal = get_object_or_404(EmploymentProposal, pk=pk)
    chain = annotate_display_status(proposal)
    employee = _employee(request.user)
    active = next((s for s in chain if s.display_status == "active"), None)
    is_my_turn = bool(active and employee and active.approver_id == employee.id)
    logs = list(proposal.status_logs.order_by("timestamp"))

    template_name = (
        "recruitment/proposals/proposal_permanent.html"
        if proposal.template_type == EmploymentProposal.TEMPLATE_PERMANENT
        else "recruitment/proposals/proposal_contractual.html"
    )

    return render(request, template_name, {
        "proposal": proposal,
        "chain": chain,
        "active": active,
        "is_my_turn": is_my_turn,
        "logs": logs,
    })


# ────────────────────────────────────────────────────────────────────────────
# E-sign / reject
# ────────────────────────────────────────────────────────────────────────────
@login_required
@require_POST
def proposal_esign(request, pk):
    proposal = get_object_or_404(EmploymentProposal, pk=pk)
    if proposal.is_terminal:
        messages.error(request, _("This proposal is no longer accepting signatures."))
        return redirect("proposal-list")

    employee = _employee(request.user)
    step = proposal.approvals.filter(
        approver=employee, status=ProposalApproval.STATUS_PENDING
    ).order_by("sequence").first()
    if not step:
        messages.error(request, _("You don't have a pending signature step on this proposal."))
        return redirect("proposal-list")

    # Sequential enforcement — must be the first pending step.
    first_pending = proposal.approvals.filter(
        status=ProposalApproval.STATUS_PENDING
    ).order_by("sequence").first()
    if first_pending.id != step.id:
        messages.error(request, _("Waiting for earlier approvers to sign first."))
        return redirect("proposal-list")

    sig = request.POST.get("signature_data", "").strip()
    step.status = ProposalApproval.STATUS_APPROVED
    step.acted_at = timezone.now()
    if sig:
        step.signature_image = sig
    step.save(update_fields=["status", "acted_at", "signature_image"])

    ProposalStatusLog.objects.create(
        proposal=proposal, actor=request.user,
        action="signed",
        note=f"Step {step.sequence} ({step.role_label}) signed by {employee}.",
    )

    next_step = advance_after_signature(proposal, step, actor_user=request.user)
    if next_step:
        messages.success(
            request,
            _("Signed. Waiting for %(name)s.") % {"name": next_step.approver},
        )
    else:
        messages.success(request, _("All approvers signed. Proposal is fully approved."))
    return redirect("proposal-list")


@login_required
@require_POST
def proposal_reject(request, pk):
    proposal = get_object_or_404(EmploymentProposal, pk=pk)
    if proposal.is_terminal:
        messages.error(request, _("This proposal is no longer accepting actions."))
        return redirect("proposal-list")

    employee = _employee(request.user)
    step = proposal.approvals.filter(
        approver=employee, status=ProposalApproval.STATUS_PENDING
    ).order_by("sequence").first()
    if not step:
        messages.error(request, _("You don't have a pending signature step on this proposal."))
        return redirect("proposal-list")

    feedback = request.POST.get("feedback", "").strip()
    reject_proposal(proposal, step, feedback, actor_user=request.user)
    messages.warning(request, _("Proposal rejected. HR has been notified."))
    return redirect("proposal-list")


# ────────────────────────────────────────────────────────────────────────────
# Convert to Offer Letter (post-approval)
# ────────────────────────────────────────────────────────────────────────────
@login_required
def proposal_convert_to_offer(request, pk):
    """Mark the proposal as converted and hand the user to the existing
    offer-letter create page (prefill is handled by stashing data on session).
    """
    proposal = get_object_or_404(EmploymentProposal, pk=pk)
    if proposal.status != EmploymentProposal.STATUS_APPROVED:
        messages.error(request, _("Only fully approved proposals can become offer letters."))
        return redirect("proposal-list")

    proposal.status = EmploymentProposal.STATUS_CONVERTED
    proposal.save(update_fields=["status"])
    ProposalStatusLog.objects.create(
        proposal=proposal, actor=request.user,
        action="converted",
        note="Proposal converted into offer letter.",
    )

    request.session["proposal_prefill"] = {
        "proposal_id": proposal.id,
        "basic_salary": str(proposal.basic_salary or ""),
        "gross_salary": str(proposal.gross_salary or ""),
        "contract_period_from": proposal.contract_period_from.isoformat() if proposal.contract_period_from else "",
        "contract_period_to": proposal.contract_period_to.isoformat() if proposal.contract_period_to else "",
        "job_position": proposal.post_applied_for,
    }

    messages.success(request, _("Proposal converted. Continue with the offer letter below."))
    return redirect(reverse("offer-create", kwargs={"cand_id": proposal.candidate_id}))


# ────────────────────────────────────────────────────────────────────────────
# Role mapping admin
# ────────────────────────────────────────────────────────────────────────────
@login_required
def proposal_role_mapping(request):
    if request.method == "POST":
        for role_key in PERMANENT_CHAIN:
            emp_id = request.POST.get(f"role_{role_key}") or ""
            if emp_id.isdigit():
                emp = Employee.objects.filter(id=int(emp_id)).first()
                if emp:
                    ProposalRoleAssignment.objects.update_or_create(
                        role_key=role_key,
                        defaults={"role_label": ROLE_LABELS[role_key], "employee": emp},
                    )
            else:
                ProposalRoleAssignment.objects.filter(role_key=role_key).delete()
        messages.success(request, _("Proposal role mapping saved."))
        return redirect("proposal-roles")

    current = {
        a.role_key: a.employee_id
        for a in ProposalRoleAssignment.objects.all()
    }
    roles = [{
        "key": k,
        "label": ROLE_LABELS[k],
        "in_permanent": k in PERMANENT_CHAIN,
        "in_contractual": k in CONTRACTUAL_CHAIN,
        "selected_id": current.get(k, ""),
    } for k in PERMANENT_CHAIN]

    employees = Employee.objects.filter(is_active=True).order_by("employee_first_name")
    return render(request, "recruitment/proposals/proposal_role_mapping.html", {
        "roles": roles,
        "employees": employees,
    })
