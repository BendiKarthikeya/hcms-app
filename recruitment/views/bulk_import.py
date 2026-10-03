"""
recruitment/views/bulk_import.py — Phase 3: CSV bulk import for candidates and manpower requests.
"""

import csv
import io
import uuid

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from fits.decorators import login_required
from recruitment.decorators import manager_can_enter
from recruitment.models import Candidate, ManpowerRequest, Stage


def _get_company_and_employee(request):
    emp = getattr(request.user, "employee_get", None)
    company = getattr(emp, "company_id", None)
    if not company and request.user.is_superuser:
        from base.models import Company
        company = Company.objects.first()
    return company, emp


@login_required
@manager_can_enter(perm="recruitment.add_candidate")
def bulk_import_candidates(request):
    errors = []
    preview = []
    committed = 0

    if request.method == "POST":
        action = request.POST.get("action")
        csv_file = request.FILES.get("csv_file")

        if not csv_file:
            messages.error(request, "No file uploaded.")
            return redirect("bulk-import-candidates")

        text = csv_file.read().decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)

        if action == "preview":
            for i, row in enumerate(rows, 1):
                name = row.get("name", "").strip()
                email = row.get("email", "").strip()
                err = []
                if not name:
                    err.append("name required")
                if not email:
                    err.append("email required")
                preview.append({"row": i, "name": name, "email": email, "errors": err})
            return render(request, "recruitment/bulk_import/preview.html", {
                "preview": preview, "raw_csv": text
            })

        elif action == "commit":
            raw_csv = request.POST.get("raw_csv", "")
            reader2 = csv.DictReader(io.StringIO(raw_csv))
            company, emp = _get_company_and_employee(request)
            stage = Stage.objects.filter(stage_type="initial").first()

            for row in reader2:
                name = row.get("name", "").strip()
                email = row.get("email", "").strip() or f"import-{uuid.uuid4().hex[:8]}@imported.local"
                if not name:
                    errors.append(f"Row skipped (no name): {dict(row)}")
                    continue
                try:
                    Candidate.objects.create(
                        name=name,
                        email=email,
                        mobile=row.get("mobile", "").strip(),
                        country=row.get("country", "").strip(),
                        experience_years=float(row.get("experience_years") or 0),
                        stage_id=stage,
                        source="other",
                    )
                    committed += 1
                except Exception as e:
                    errors.append(f"{name}: {e}")

            messages.success(request, f"{committed} candidate(s) imported.")
            if errors:
                messages.warning(request, f"{len(errors)} row(s) failed: " + "; ".join(errors[:5]))
            return redirect("candidate-dashboard")

    return render(request, "recruitment/bulk_import/upload.html", {
        "import_type": "candidates",
        "template_url": "/recruitment/bulk-import/candidates/template/",
    })


@login_required
@manager_can_enter(perm="recruitment.add_candidate")
def bulk_import_candidates_template(request):
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="candidates_template.csv"'
    w = csv.writer(resp)
    w.writerow(["name", "email", "mobile", "country", "experience_years"])
    w.writerow(["John Doe", "john@example.com", "9999999999", "OM", "3"])
    return resp


@login_required
@manager_can_enter(perm="recruitment.view_recruitment")
def bulk_import_manpower(request):
    errors = []
    committed = 0

    if request.method == "POST":
        action = request.POST.get("action")
        csv_file = request.FILES.get("csv_file")

        if not csv_file:
            messages.error(request, "No file uploaded.")
            return redirect("bulk-import-manpower")

        text = csv_file.read().decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)

        if action == "preview":
            preview = []
            for i, row in enumerate(rows, 1):
                err = [] if row.get("justification") else ["justification required"]
                preview.append({"row": i, "data": dict(row), "errors": err})
            return render(request, "recruitment/bulk_import/preview.html", {
                "preview": preview, "raw_csv": text, "is_manpower": True
            })

        elif action == "commit":
            raw_csv = request.POST.get("raw_csv", "")
            reader2 = csv.DictReader(io.StringIO(raw_csv))
            company, emp = _get_company_and_employee(request)

            for row in reader2:
                if not row.get("justification"):
                    errors.append(f"Row skipped (no justification): {dict(row)}")
                    continue
                try:
                    from base.models import Department, JobPosition
                    mr = ManpowerRequest(
                        company_id=company,
                        grade=row.get("grade", ""),
                        positions_count=int(row.get("positions_count") or 1),
                        justification=row.get("justification", ""),
                        budget_code=row.get("budget_code", ""),
                        employment_type=row.get("employment_type", "full_time"),
                        nationality_preference=row.get("nationality_preference", "any"),
                        requested_by=emp,
                    )
                    dept_name = row.get("department", "").strip()
                    if dept_name:
                        dept = Department.objects.filter(department__iexact=dept_name).first()
                        if dept:
                            mr.department = dept
                    mr.save()
                    committed += 1
                except Exception as e:
                    errors.append(str(e))

            messages.success(request, f"{committed} manpower request(s) imported.")
            if errors:
                messages.warning(request, f"{len(errors)} failed: " + "; ".join(errors[:5]))
            return redirect("manpower-list")

    return render(request, "recruitment/bulk_import/upload.html", {
        "import_type": "manpower_requests",
        "template_url": "/recruitment/bulk-import/manpower/template/",
    })


@login_required
def bulk_import_manpower_template(request):
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="manpower_template.csv"'
    w = csv.writer(resp)
    w.writerow(["department", "grade", "positions_count", "employment_type", "nationality_preference", "budget_code", "justification"])
    w.writerow(["Engineering", "Grade 4", "2", "full_time", "any", "BUD-001", "Project expansion requires 2 engineers"])
    return resp
