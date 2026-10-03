"""
Leave Request Approval Service Layer
Handles complex business logic for approval workflows
Location: leave/services/approval_service.py
"""
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings

from leave.models_enhanced_approvals import (
    ApprovalPolicy,
    ApprovalRequest,
    ApprovalDelegation,
    ApprovalOverride,
    ApprovalSLAAlert,
)
from leave.models import LeaveRequest, LeaveRequestConditionApproval
from employee.models import Employee
from base.models import MultipleApprovalCondition


class ApprovalWorkflowService:
    """
    Service class for managing leave request approval workflows.
    Handles parallel/sequential approvals, SLA escalation, auto-approval.
    """

    def __init__(self, leave_request):
        self.leave_request = leave_request
        self.company = leave_request.employee_id.employee_work_info.company_id
        self.policy = self._get_policy()

    def _get_policy(self):
        """Retrieve active approval policy for company"""
        return ApprovalPolicy.objects.filter(
            company=self.company, is_active=True
        ).first()

    def create_approval_pipeline(self):
        """
        Creates approval pipeline based on policy and MultipleApprovalCondition.
        Handles parallel/sequential setup.
        """
        if not self.policy:
            return []

        # Get approval conditions based on days requested
        conditions = MultipleApprovalCondition.objects.filter(
            department=self.leave_request.employee_id.employee_work_info.department_id,
            company_id=self.company,
        ).order_by("condition_value")

        managers = []
        applicable_condition = None

        # Find applicable condition
        for condition in conditions:
            if self._matches_condition(condition):
                applicable_condition = condition
                break

        if not applicable_condition:
            return []

        # Get managers from condition
        approvers = applicable_condition.approval_managers()

        # Check for delegation
        now = timezone.now()
        for idx, approver in enumerate(approvers, 1):
            actual_approver = ApprovalDelegation.get_current_approver(approver, now)

            # Create approval request
            sla_deadline = now + timedelta(hours=self.policy.sla_hours)
            escalation_deadline = now + timedelta(hours=self.policy.escalation_hours)

            approval_type = (
                "parallel" if self.policy.allow_parallel_approvals else "sequential"
            )

            approval_req = ApprovalRequest.objects.create(
                leave_request=self.leave_request,
                approver=actual_approver,
                sequence_order=idx,
                approval_type=approval_type,
                sla_deadline=sla_deadline,
                escalation_deadline=escalation_deadline,
            )

            managers.append(approval_req)

            # Send initial notification
            self._send_approval_notification(approval_req)

        return managers

    def _matches_condition(self, condition):
        """Check if leave request matches approval condition"""
        requested_days = self.leave_request.requested_days

        if condition.condition_operator == "range":
            start = float(condition.condition_start_value)
            end = float(condition.condition_end_value)
            return start <= requested_days <= end

        # Handle other operators
        from leave.models import operator_mapping

        operator_func = operator_mapping.get(condition.condition_operator)
        if operator_func:
            condition_value = type(requested_days)(condition.condition_value)
            return operator_func(requested_days, condition_value)

        return False

    def check_auto_approval(self):
        """
        Check if leave should be auto-approved based on policy threshold.
        Returns True if auto-approved.
        """
        if not self.policy or not self.policy.auto_approve_threshold_days:
            return False

        if self.leave_request.requested_days <= self.policy.auto_approve_threshold_days:
            # Auto-approve
            ApprovalRequest.objects.filter(leave_request=self.leave_request).update(
                status="auto_approved",
                auto_approved=True,
                confirmation_required=self.policy.require_manager_confirmation,
            )
            return True

        return False

    def process_approvals(self):
        """
        Process approval pipeline.
        For parallel: all must approve
        For sequential: one by one
        """
        if self.policy.allow_parallel_approvals:
            return self._process_parallel_approvals()
        else:
            return self._process_sequential_approvals()

    def _process_parallel_approvals(self):
        """All approvers must approve in parallel"""
        pending_approvals = ApprovalRequest.objects.filter(
            leave_request=self.leave_request, status="pending"
        )

        all_approved = pending_approvals.count() == 0
        any_rejected = ApprovalRequest.objects.filter(
            leave_request=self.leave_request, status="rejected"
        ).exists()

        if any_rejected:
            self.leave_request.status = "rejected"
        elif all_approved:
            self.leave_request.status = "approved"

        self.leave_request.save()
        return self.leave_request.status

    def _process_sequential_approvals(self):
        """Process sequential approval chain"""
        approvals = ApprovalRequest.objects.filter(
            leave_request=self.leave_request
        ).order_by("sequence_order")

        for approval in approvals:
            if approval.status == "pending":
                return "pending"  # Stop at first pending
            elif approval.status == "rejected":
                self.leave_request.status = "rejected"
                self.leave_request.save()
                return "rejected"

        # All approved
        self.leave_request.status = "approved"
        self.leave_request.save()
        return "approved"

    def check_and_escalate_sla(self):
        """
        Check for SLA breaches and escalate if needed.
        Called by Celery task periodically.
        """
        pending_requests = ApprovalRequest.objects.filter(
            leave_request__company=self.company, status="pending"
        )

        escalated_count = 0

        for approval in pending_requests:
            # Check if escalation is due
            if approval.is_escalation_due():
                escalated_to = self._get_escalation_target(approval)
                if escalated_to:
                    approval.escalate(escalated_to, reason="sla_breach")
                    escalated_count += 1

                    # Create alert
                    ApprovalSLAAlert.objects.create(
                        approval_request=approval,
                        alert_type="escalated",
                        escalation_triggered=True,
                    )

                    # Notify escalation
                    self._send_escalation_notification(approval, escalated_to)

            # Check for warning alerts
            elif approval.days_until_sla_breach() < 2:  # Less than 2 days
                ApprovalSLAAlert.objects.create(
                    approval_request=approval, alert_type="critical"
                )
                approval.send_reminder()

        return escalated_count

    def _get_escalation_target(self, approval_request):
        """Determine who to escalate to"""
        # Escalate to next manager in chain
        next_approval = ApprovalRequest.objects.filter(
            leave_request=approval_request.leave_request,
            sequence_order__gt=approval_request.sequence_order,
        ).first()

        if next_approval:
            return next_approval.approver

        # Or escalate to HR
        # TODO: Determine HR approver from company settings
        return None

    def override_approval(self, override_by, action, reason):
        """
        Allow HR/Admin to override approval decision.
        Maintains audit trail.
        """
        if not self.policy or not self.policy.allow_override:
            raise PermissionError("Overrides not allowed by policy")

        # Check override count
        override_count = ApprovalOverride.objects.filter(
            leave_request=self.leave_request
        ).count()

        if override_count >= self.policy.max_override_count:
            raise PermissionError(
                f"Maximum overrides ({self.policy.max_override_count}) reached"
            )

        # Get latest approval request
        latest_approval = (
            ApprovalRequest.objects.filter(leave_request=self.leave_request)
            .order_by("-sequence_order")
            .first()
        )

        old_status = self.leave_request.status

        # Update leave request status
        if action == "approve":
            self.leave_request.status = "approved"
        elif action == "reject":
            self.leave_request.status = "rejected"
            self.leave_request.reject_reason = reason
        else:  # reset
            self.leave_request.status = "requested"

        self.leave_request.save()

        # Record override
        ApprovalOverride.objects.create(
            leave_request=self.leave_request,
            original_status=old_status,
            new_status=self.leave_request.status,
            action=action,
            overridden_by=override_by,
            reason=reason,
            approval_request=latest_approval,
        )

        # Notify affected parties
        self._send_override_notification(override_by, action, reason)

    def delegate_approval(self, from_manager, to_manager, start_date, end_date, reason):
        """
        Create approval delegation for absent manager.
        """
        delegation = ApprovalDelegation.objects.create(
            delegating_manager=from_manager,
            delegated_to=to_manager,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )

        # Update any pending approvals from delegating manager
        ApprovalRequest.objects.filter(approver=from_manager, status="pending").update(
            approver=to_manager
        )

        return delegation

    def bulk_approve(self, approver, leave_request_ids):
        """
        Allow manager to approve multiple leave requests at once.
        """
        approved_count = 0

        for request_id in leave_request_ids:
            try:
                leave = LeaveRequest.objects.get(id=request_id)
                approval = ApprovalRequest.objects.filter(
                    leave_request=leave, approver=approver, status="pending"
                ).first()

                if approval:
                    approval.approve(approver, "Bulk approved")
                    approved_count += 1

            except LeaveRequest.DoesNotExist:
                continue

        return approved_count

    def _send_approval_notification(self, approval_request):
        """Send email notification to approver"""
        # TODO: Implement email sending
        pass

    def _send_escalation_notification(self, approval_request, escalated_to):
        """Send escalation notification"""
        # TODO: Implement email sending
        pass

    def _send_override_notification(self, override_by, action, reason):
        """Send override notification"""
        # TODO: Implement email sending
        pass


class ApprovalAnalyticsService:
    """
    Service for generating approval analytics and metrics.
    """

    @staticmethod
    def calculate_monthly_metrics(company):
        """
        Calculate approval metrics for current month.
        """
        from datetime import date
        from dateutil.relativedelta import relativedelta
        from leave.models_enhanced_approvals import ApprovalMetrics

        # Get first day of current month
        today = date.today()
        period_date = date(today.year, today.month, 1)

        # Query approval requests for this company
        approvals = ApprovalRequest.objects.filter(
            leave_request__employee_id__employee_work_info__company_id=company
        )

        # Calculate metrics
        metrics = {
            "total_requests": approvals.count(),
            "approved_count": approvals.filter(status="approved").count(),
            "rejected_count": approvals.filter(status="rejected").count(),
            "pending_count": approvals.filter(status="pending").count(),
            "auto_approved_count": approvals.filter(auto_approved=True).count(),
        }

        # Calculate average approval time
        completed = approvals.filter(approved_at__isnull=False)
        if completed.exists():
            total_hours = sum(
                [
                    (a.approved_at - a.assigned_at).total_seconds() / 3600
                    for a in completed
                ]
            )
            metrics["avg_approval_time_hours"] = total_hours / completed.count()

        # Calculate SLA compliance
        total_with_sla = approvals.filter(sla_deadline__isnull=False).count()
        if total_with_sla > 0:
            met_sla = approvals.filter(
                sla_deadline__isnull=False, approved_at__lte=models.F("sla_deadline")
            ).count()
            metrics["sla_compliance_percentage"] = (met_sla / total_with_sla) * 100

        # Find bottleneck approver
        bottleneck = (
            approvals.filter(status="pending")
            .values("approver")
            .annotate(pending_count=Count("id"))
            .order_by("-pending_count")
            .first()
        )

        if bottleneck:
            metrics["bottleneck_approver_id"] = bottleneck["approver"]
            metrics["bottleneck_requests"] = bottleneck["pending_count"]

        # Save/update metrics
        ApprovalMetrics.objects.update_or_create(
            company=company, approval_period=period_date, defaults=metrics
        )

        return metrics

    @staticmethod
    def get_team_approval_stats(approver):
        """
        Get approval statistics for a specific approver.
        """
        approvals = ApprovalRequest.objects.filter(approver=approver)

        return {
            "total_assigned": approvals.count(),
            "approved": approvals.filter(status="approved").count(),
            "rejected": approvals.filter(status="rejected").count(),
            "pending": approvals.filter(status="pending").count(),
            "overdue": approvals.filter(
                status="pending", sla_deadline__lt=timezone.now()
            ).count(),
            "average_time": sum(
                [
                    (a.approved_at - a.assigned_at).total_seconds() / 3600
                    for a in approvals.filter(approved_at__isnull=False)
                ]
            )
            / approvals.filter(approved_at__isnull=False).count()
            if approvals.filter(approved_at__isnull=False).count() > 0
            else 0,
        }
