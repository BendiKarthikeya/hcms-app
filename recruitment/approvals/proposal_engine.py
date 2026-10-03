"""
recruitment/approvals/proposal_engine.py

Builds the sequential e-sign chain for an EmploymentProposal, mirroring the
offer-letter approval flow but using distinct chains per template (Permanent
vs Contractual) as printed on the ONEIC employment proposal forms.
"""

from django.contrib.auth.models import Permission, User
from django.utils import timezone

from employee.models import Employee
from recruitment.models_proposal import (
    CONTRACTUAL_CHAIN,
    EmploymentProposal,
    PERMANENT_CHAIN,
    ProposalApproval,
    ProposalRoleAssignment,
    ProposalStatusLog,
    ROLE_LABELS,
)


DEMO_PASSWORD = "demo@123"
_EMAIL_DOMAIN = "oneic.local"


def _notify_first_approver(proposal, step):
    """Send an in-app bell notification to the first (or next) approver."""
    if not step:
        return
    approver_emp = step.approver
    recipient_user = getattr(approver_emp, "employee_user_id", None)
    if not recipient_user:
        return
    try:
        from notifications.signals import notify
        notify.send(
            recipient_user,
            recipient=[recipient_user],
            verb=(
                f"Employment Proposal {proposal.proposal_no} is waiting for your e-signature."
            ),
            icon="people-circle",
            redirect="/recruitment/proposals/",
        )
    except Exception:
        pass
    # Also email the approver (mirror the dashboard notification).
    try:
        import threading
        from recruitment.email_utils import email_proposal_for_signature
        threading.Thread(
            target=email_proposal_for_signature,
            args=(proposal, approver_emp),
            daemon=True,
        ).start()
    except Exception:
        pass

PROPOSAL_PERMISSIONS = [
    "recruitment.view_employmentproposal",
    "recruitment.view_proposalapproval",
    "recruitment.change_proposalapproval",
]


def _grant_proposal_permissions(user):
    """Grant the minimum proposal module permissions to a User."""
    try:
        for perm_str in PROPOSAL_PERMISSIONS:
            app_label, codename = perm_str.split(".")
            perm = Permission.objects.filter(
                codename=codename,
                content_type__app_label=app_label,
            ).first()
            if perm:
                user.user_permissions.add(perm)
    except Exception:
        pass


def _notify(actor_user, recipient_user, verb, redirect_path=""):
    """Best-effort in-app notification using django-notifications."""
    if not recipient_user:
        return
    try:
        from notifications.signals import notify
        actor = actor_user or recipient_user
        notify.send(
            actor,
            recipient=[recipient_user],
            verb=verb,
            icon="people-circle",
            redirect=redirect_path,
        )
    except Exception:
        pass


def _ensure_role_employee(role_key):
    """Get or create a demo Employee + login User + ProposalRoleAssignment.

    Demo users are seeded with password ``demo@123`` and a stable
    ``<role_key>@oneic.local`` email, so each ONEIC signatory can log in and
    e-sign their step. The mapping is persisted via ProposalRoleAssignment.
    """
    existing = ProposalRoleAssignment.objects.filter(role_key=role_key).first()
    if existing and existing.employee and existing.employee.employee_user_id:
        # Make sure the linked user can still log in with the demo password.
        u = existing.employee.employee_user_id
        if not u.check_password(DEMO_PASSWORD):
            u.set_password(DEMO_PASSWORD)
            u.is_active = True
            u.save(update_fields=["password", "is_active"])
        return existing.employee

    label = ROLE_LABELS.get(role_key, role_key.replace("_", " ").title())
    email = f"{role_key}@{_EMAIL_DOMAIN}"

    user = User.objects.filter(username=email).first()
    if not user:
        user = User.objects.create_user(
            username=email,
            email=email,
            password=DEMO_PASSWORD,
            first_name=label,
        )
    else:
        user.set_password(DEMO_PASSWORD)
        user.is_active = True
        user.save(update_fields=["password", "is_active"])

    employee = Employee.objects.filter(email=email).first()
    if not employee:
        employee = Employee.objects.create(
            employee_user_id=user,
            employee_first_name=label,
            employee_last_name="(ONEIC)",
            email=email,
            phone="00000000",
            gender="male",
        )
    elif employee.employee_user_id_id != user.id:
        employee.employee_user_id = user
        employee.save(update_fields=["employee_user_id"])

    ProposalRoleAssignment.objects.update_or_create(
        role_key=role_key,
        defaults={"role_label": label, "employee": employee},
    )
    _grant_proposal_permissions(user)
    return employee


def _chain_for(proposal):
    if proposal.template_type == EmploymentProposal.TEMPLATE_PERMANENT:
        return PERMANENT_CHAIN
    return CONTRACTUAL_CHAIN


def route_proposal(proposal):
    """Build the proposal e-sign chain.

    For each role on the template's chain, look up the assigned Employee via
    ProposalRoleAssignment. Unassigned roles are skipped (and logged). If
    every role is unassigned, the proposal stays in DRAFT and a warning log
    is written so HR can fix it.

    Returns "chain_built", "no_approvers", or None.
    """
    role_keys = _chain_for(proposal)
    assignments = {
        a.role_key: a.employee
        for a in ProposalRoleAssignment.objects.filter(role_key__in=role_keys)
    }

    proposal.approvals.all().delete()

    seq = 0
    skipped = []
    auto_provisioned = []
    for role_key in role_keys:
        emp = assignments.get(role_key)
        if not emp:
            emp = _ensure_role_employee(role_key)
            auto_provisioned.append(role_key)
        seq += 1
        ProposalApproval.objects.create(
            proposal=proposal,
            role_key=role_key,
            role_label=ROLE_LABELS.get(role_key, role_key),
            sequence=seq,
            approver=emp,
            status=ProposalApproval.STATUS_PENDING,
        )

    if seq == 0:
        ProposalStatusLog.objects.create(
            proposal=proposal,
            action="no_approvers",
            note=(
                "No approver mapped for this template chain. "
                "Assign roles at /recruitment/proposals/roles/ before re-routing."
            ),
        )
        return "no_approvers"

    if skipped:
        ProposalStatusLog.objects.create(
            proposal=proposal,
            action="chain_partial",
            note="Skipped unassigned roles: " + ", ".join(skipped),
        )

    if auto_provisioned:
        ProposalStatusLog.objects.create(
            proposal=proposal,
            action="chain_auto_provisioned",
            note=(
                "Auto-created placeholder approvers for unmapped roles: "
                + ", ".join(ROLE_LABELS.get(r, r) for r in auto_provisioned)
                + ". HR can reassign at /recruitment/proposals/roles/."
            ),
        )

    proposal.status = EmploymentProposal.STATUS_PENDING
    proposal.save(update_fields=["status"])
    ProposalStatusLog.objects.create(
        proposal=proposal,
        action="chain_built",
        note=f"E-sign chain built with {seq} step(s).",
    )

    # Notify the first approver (sequence=1) that they need to sign.
    first_step = proposal.approvals.order_by("sequence").first()
    _notify_first_approver(proposal, first_step)

    return "chain_built"


def advance_after_signature(proposal, current_step, actor_user=None):
    """Called after an approver signs a step. Marks proposal APPROVED if no
    more pending steps remain. Returns the next pending step or None.
    """
    cand_name = proposal.applicant_name or proposal.candidate.name
    total = proposal.approvals.count()

    next_step = proposal.approvals.filter(
        status=ProposalApproval.STATUS_PENDING
    ).order_by("sequence").first()

    if next_step:
        _notify_first_approver(proposal, next_step)
        return next_step

    proposal.status = EmploymentProposal.STATUS_APPROVED
    proposal.save(update_fields=["status"])
    ProposalStatusLog.objects.create(
        proposal=proposal,
        actor=actor_user,
        action="approved",
        note="All steps signed — proposal fully approved.",
        timestamp=timezone.now(),
    )
    # Notify the original submitter that the proposal is fully approved
    submitter = getattr(proposal, "created_by", None)
    _notify(
        actor_user,
        submitter,
        f"Employment proposal for {cand_name} has been fully approved by all signatories.",
        redirect_path="/recruitment/proposals/",
    )
    return None


def reject_proposal(proposal, rejecting_step, feedback, actor_user=None):
    """Mark the rejecting step rejected, cascade-reject remaining pending
    steps, and flip proposal status to REJECTED.
    """
    rejecting_step.status = ProposalApproval.STATUS_REJECTED
    rejecting_step.feedback = feedback
    rejecting_step.acted_at = timezone.now()
    rejecting_step.save(update_fields=["status", "feedback", "acted_at"])

    proposal.approvals.filter(
        status=ProposalApproval.STATUS_PENDING
    ).update(status=ProposalApproval.STATUS_REJECTED)

    proposal.status = EmploymentProposal.STATUS_REJECTED
    proposal.save(update_fields=["status"])

    ProposalStatusLog.objects.create(
        proposal=proposal,
        actor=actor_user,
        action="rejected",
        note=f"Rejected at step {rejecting_step.sequence} ({rejecting_step.role_label}). "
             f"Feedback: {feedback or 'None'}",
    )

    # Notify the original submitter
    cand_name = proposal.applicant_name or proposal.candidate.name
    submitter = getattr(proposal, "created_by", None)
    _notify(
        actor_user,
        submitter,
        f"Employment proposal for {cand_name} was rejected at Step {rejecting_step.sequence} "
        f"({rejecting_step.role_label}). Feedback: {feedback or 'None'}",
        redirect_path="/recruitment/proposals/",
    )
    # Also email the submitter.
    try:
        import threading
        from recruitment.email_utils import email_proposal_rejected
        threading.Thread(
            target=email_proposal_rejected,
            args=(proposal, feedback),
            daemon=True,
        ).start()
    except Exception:
        pass


def annotate_display_status(proposal):
    """Return the chain with `display_status` annotated on each step:
    first pending → active, later pending → waiting, else self status.
    Mirrors onboarding/views_letters.py:314-340.
    """
    chain = list(proposal.approvals.select_related("approver").order_by("sequence"))
    active_found = False
    for step in chain:
        if step.status == ProposalApproval.STATUS_PENDING and not active_found:
            step.display_status = "active"
            active_found = True
        elif step.status == ProposalApproval.STATUS_PENDING:
            step.display_status = "waiting"
        else:
            step.display_status = step.status
    return chain
