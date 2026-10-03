"""
recruitment/candidate_utils.py

Shared utility functions for candidate operations.
"""

from django.db import IntegrityError


def convert_candidate_to_employee(candidate_obj):
    """
    Convert a Candidate record into an Employee record.
    Returns the new Employee on success, None if already converted,
    and raises IntegrityError if the email already exists as a user.
    """
    from django.contrib.auth.models import User
    from employee.models import Employee
    from fits_documents.models import Document

    if candidate_obj.converted_employee_id:
        return candidate_obj.converted_employee_id

    if User.objects.filter(username=candidate_obj.email).exists():
        return None

    if Employee.objects.filter(employee_user_id__username=candidate_obj.email).exists():
        return None

    try:
        new_employee = Employee(
            employee_first_name=candidate_obj.name,
            email=candidate_obj.email,
            phone=candidate_obj.mobile or "",
            gender=candidate_obj.gender,
            dob=getattr(candidate_obj, "dob", None),
            is_directly_converted=True,
        )
        new_employee.save()

        work_info = new_employee.employee_work_info
        if candidate_obj.job_position_id:
            work_info.job_position_id = candidate_obj.job_position_id
            if candidate_obj.job_position_id.department_id:
                work_info.department_id = candidate_obj.job_position_id.department_id
        if candidate_obj.recruitment_id and candidate_obj.recruitment_id.company_id:
            work_info.company_id = candidate_obj.recruitment_id.company_id

        # Carry over offer salary and joining date if available
        offer = getattr(candidate_obj, "offer_letter", None)
        if offer:
            work_info.basic_salary = offer.basic_salary
            work_info.date_joining = offer.joining_date

        work_info.save()

        # Transfer candidate documents to employee
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
            ],
            ignore_conflicts=True,
        )

        candidate_obj.converted_employee_id = new_employee
        candidate_obj.save(update_fields=["converted_employee_id"])

        return new_employee

    except IntegrityError:
        return None
