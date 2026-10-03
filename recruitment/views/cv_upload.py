"""
recruitment/views/cv_upload.py

CV upload endpoints (single + bulk) for the Candidate Dashboard.

Bulk upload accepts multiple files; one Candidate is created per file.
Filenames are used as a name fallback; placeholder emails are generated when
not supplied so bulk imports don't fail Candidate's required email field.
"""

import os
import re
import uuid

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from fits.decorators import login_required
from recruitment.decorators import manager_can_enter
from recruitment.forms_candidate_upload import BulkCVUploadForm, SingleCVUploadForm
from recruitment.models import Candidate, Recruitment, Stage


def _default_stage(recruitment=None):
    if recruitment is not None:
        stage = Stage.objects.filter(
            recruitment_id=recruitment, stage_type="initial"
        ).first()
        if stage:
            return stage
    return Stage.objects.filter(stage_type="initial").first()


def _name_from_filename(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    cleaned = re.sub(r"[_\-]+", " ", base).strip()
    return cleaned[:100] if cleaned else "Imported Candidate"


def _placeholder_email():
    return f"cv-{uuid.uuid4().hex[:10]}@imported.local"


@login_required
@manager_can_enter(perm="recruitment.add_candidate")
def cv_upload_single(request):
    """Single CV upload form view."""
    if request.method == "POST":
        form = SingleCVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            recruitment = cd.get("recruitment_id")
            stage = cd.get("stage_id") or _default_stage(recruitment)
            Candidate.objects.create(
                name=cd["name"],
                email=cd["email"],
                mobile=cd.get("mobile") or "",
                resume=cd["resume"],
                recruitment_id=recruitment,
                stage_id=stage,
                source="application",
            )
            messages.success(request, f"Candidate '{cd['name']}' created.")
            return redirect(reverse("candidate-dashboard"))
    else:
        form = SingleCVUploadForm()
    return render(
        request,
        "recruitment/candidate_dashboard/single_upload.html",
        {"form": form},
    )


@login_required
@manager_can_enter(perm="recruitment.add_candidate")
def cv_upload_bulk(request):
    """Bulk CV upload — one Candidate per uploaded file."""
    if request.method != "POST":
        return redirect(reverse("candidate-dashboard"))

    files = request.FILES.getlist("files")
    if not files:
        messages.error(request, "No files were uploaded.")
        return redirect(reverse("candidate-dashboard"))

    recruitment_id = request.POST.get("recruitment_id") or None
    stage_id = request.POST.get("stage_id") or None
    recruitment = (
        Recruitment.objects.filter(id=recruitment_id).first() if recruitment_id else None
    )
    stage = (
        Stage.objects.filter(id=stage_id).first() if stage_id else None
    ) or _default_stage(recruitment)

    created = 0
    failed = []
    for f in files:
        try:
            Candidate.objects.create(
                name=_name_from_filename(f.name),
                email=_placeholder_email(),
                resume=f,
                recruitment_id=recruitment,
                stage_id=stage,
                source="application",
            )
            created += 1
        except Exception as exc:  # noqa: BLE001 — surface row-level failure
            failed.append({"file": f.name, "error": str(exc)})

    if created:
        messages.success(
            request, f"{created} candidate(s) created from uploaded CVs."
        )
    if failed:
        messages.warning(
            request,
            f"{len(failed)} file(s) failed: "
            + ", ".join(f"{x['file']} ({x['error']})" for x in failed[:5])
            + ("..." if len(failed) > 5 else ""),
        )
    return redirect(reverse("candidate-dashboard"))
