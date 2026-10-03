"""
recruitment/views/email_templates.py

Self-service CRUD for JobEmailTemplate — selection and rejection email subjects/bodies
that HR can edit without touching code.
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from fits.decorators import login_required
from recruitment.models import JobEmailTemplate


@login_required
def email_template_list(request):
    """List all candidate email templates; also handles create via POST."""
    templates = JobEmailTemplate.objects.all().order_by("id")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        sel_subject = request.POST.get("selection_subject", "").strip()
        sel_body = request.POST.get("selection_body", "").strip()
        rej_subject = request.POST.get("rejection_subject", "").strip()
        rej_body = request.POST.get("rejection_body", "").strip()
        is_default = request.POST.get("is_default") == "on"

        if not all([name, sel_subject, sel_body, rej_subject, rej_body]):
            messages.error(request, _("All fields are required."))
        else:
            JobEmailTemplate.objects.create(
                name=name,
                selection_subject=sel_subject,
                selection_body=sel_body,
                rejection_subject=rej_subject,
                rejection_body=rej_body,
                is_default=is_default,
            )
            messages.success(request, _(f"Template '{name}' created."))
        return redirect(reverse("email-template-list"))

    return render(request, "recruitment/email_templates/list.html", {"templates": templates})


@login_required
def email_template_edit(request, tpl_id):
    """Edit an existing email template."""
    tpl = get_object_or_404(JobEmailTemplate, pk=tpl_id)

    if request.method == "POST":
        tpl.name = request.POST.get("name", "").strip()
        tpl.selection_subject = request.POST.get("selection_subject", "").strip()
        tpl.selection_body = request.POST.get("selection_body", "").strip()
        tpl.rejection_subject = request.POST.get("rejection_subject", "").strip()
        tpl.rejection_body = request.POST.get("rejection_body", "").strip()
        tpl.is_default = request.POST.get("is_default") == "on"

        if not all([tpl.name, tpl.selection_subject, tpl.selection_body, tpl.rejection_subject, tpl.rejection_body]):
            messages.error(request, _("All fields are required."))
        else:
            tpl.save()
            messages.success(request, _(f"Template '{tpl.name}' updated."))
            return redirect(reverse("email-template-list"))

    return render(request, "recruitment/email_templates/edit.html", {"tpl": tpl})


@login_required
def email_template_delete(request, tpl_id):
    tpl = get_object_or_404(JobEmailTemplate, pk=tpl_id)
    name = tpl.name
    tpl.delete()
    messages.success(request, _(f"Template '{name}' deleted."))
    return redirect(reverse("email-template-list"))


@login_required
def email_template_set_default(request, tpl_id):
    tpl = get_object_or_404(JobEmailTemplate, pk=tpl_id)
    tpl.is_default = True
    tpl.save()
    messages.success(request, _(f"'{tpl.name}' is now the default template."))
    return redirect(reverse("email-template-list"))
