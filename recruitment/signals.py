from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from recruitment.models import (
    CandidateDocument,
    CandidateDocumentRequest,
    OfferLetter,
    Recruitment,
    Stage,
)


@receiver(post_save, sender=Recruitment)
def create_initial_stage(sender, instance, created, **kwargs):
    """
    This is post save method, used to create initial stage for the recruitment
    """
    if created:
        applied_stage = Stage()
        applied_stage.sequence = 0
        applied_stage.recruitment_id = instance
        applied_stage.stage = "Applied"
        applied_stage.stage_type = "applied"
        applied_stage.save()

        initial_stage = Stage()
        initial_stage.sequence = 1
        initial_stage.recruitment_id = instance
        initial_stage.stage = "Initial"
        initial_stage.stage_type = "initial"
        initial_stage.save()


@receiver(m2m_changed, sender=CandidateDocumentRequest.candidate_id.through)
def document_request_m2m_changed(sender, instance, action, **kwargs):
    if action == "post_add":
        candidate_document_create(instance)

    elif action == "post_remove":
        candidate_document_create(instance)


def candidate_document_create(instance):
    candidates = instance.candidate_id.all()
    for candidate in candidates:
        document, created = CandidateDocument.objects.get_or_create(
            candidate_id=candidate,
            document_request_id=instance,
            defaults={"title": f"Upload {instance.title}"},
        )
        document.title = f"Upload {instance.title}"
        document.save()


@receiver(post_save, sender=Recruitment)
def send_manager_recruitment_raised_email(sender, instance, created, **kwargs):
    """Send email to managers when a recruitment is raised"""
    if created and instance.raised_from_employee and instance.recruitment_managers.exists():
        from recruitment.views.views import _send_manager_recruitment_notification
        from employee.models import Employee
        
        managers = instance.recruitment_managers.all()
        if managers:
            recruiter_name = "System"
            if hasattr(instance, 'created_by') and instance.created_by:
                recruiter_name = str(instance.created_by)
            
            _send_manager_recruitment_notification(managers, instance, recruiter_name)


@receiver(post_save, sender=OfferLetter)
def auto_convert_candidate_on_joined(sender, instance, **kwargs):
    """When an offer's joining_status is set to 'joined', auto-convert the candidate to an employee."""
    if instance.joining_status == "joined":
        candidate = instance.candidate_id
        if not candidate.converted_employee_id:
            try:
                from recruitment.candidate_utils import convert_candidate_to_employee
                convert_candidate_to_employee(candidate)
            except Exception:
                pass
