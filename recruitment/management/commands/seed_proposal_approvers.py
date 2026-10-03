"""
Seed (or repair) the seven ONEIC employment-proposal approver accounts.

Each role gets a login user + Employee + ProposalRoleAssignment so the
Permanent and Contractual e-sign chains route end-to-end out of the box.

Permanent chain (7):
    Project Director → HOD → COO → Legal Advisor → GM HR&A → CFO → CEO

Contractual (S-O-M) chain (3):
    HOD → COO → GM HR&A

All users share password ``demo@123``. Idempotent — re-running resets the
password so demo credentials stay predictable.

Usage:
    python manage.py seed_proposal_approvers
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from recruitment.approvals.proposal_engine import (
    _ensure_role_employee,
    _grant_proposal_permissions,
    DEMO_PASSWORD,
)
from recruitment.models_proposal import (
    CONTRACTUAL_CHAIN,
    PERMANENT_CHAIN,
    ROLE_LABELS,
)


class Command(BaseCommand):
    help = "Create / repair the 7 ONEIC employment-proposal approver accounts."

    @transaction.atomic
    def handle(self, *args, **options):
        roles = list(dict.fromkeys(PERMANENT_CHAIN + CONTRACTUAL_CHAIN))
        for role_key in roles:
            emp = _ensure_role_employee(role_key)
            user = emp.employee_user_id
            _grant_proposal_permissions(user)
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ {ROLE_LABELS[role_key]:<30s}  {emp.email}  (pw: {DEMO_PASSWORD})"
            ))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(roles)} proposal approver accounts with proposal permissions."
        ))
        self.stdout.write("Permanent chain:    " + " → ".join(ROLE_LABELS[r] for r in PERMANENT_CHAIN))
        self.stdout.write("Contractual chain:  " + " → ".join(ROLE_LABELS[r] for r in CONTRACTUAL_CHAIN))
        self.stdout.write("")
        self.stdout.write("Permissions granted: view_employmentproposal, view_proposalapproval, change_proposalapproval")
