"""Embedded e-sign hand-off for Offers + Proposals via real providers
(DocuSign eSignature, Adobe Acrobat Sign).

Flow:
  esign_start  → resolve the caller's active approval step, build the document
                 PDF, create a provider envelope/agreement with one embedded
                 (captive) signer, then redirect into the provider's hosted
                 signing ceremony.
  esign_return → provider redirects back here; download the signed PDF, store
                 its first page as the step's signature image, mark the step
                 approved, and advance/finalize the chain (mirrors the inline
                 offer/proposal e-sign finalisation already used in ui.views).

Adobe / DocuSign are kept behind one provider-agnostic interface defined in
base/integrations/{docusign,adobesign}.py.
"""

import base64
import importlib
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

PROVIDER_MODULES = {
    "docusign": "base.integrations.docusign",
    "adobesign": "base.integrations.adobesign",
}
ACCOUNT_MODELS = {
    "docusign": "DocusignAccount",
    "adobesign": "AdobeSignAccount",
}
PROVIDER_LABELS = {"docusign": "DocuSign", "adobesign": "Adobe Acrobat Sign"}


def _helper(provider):
    return importlib.import_module(PROVIDER_MODULES[provider])


def _active_account(provider, user=None):
    """The signer's own connection — e-sign accounts are linked per-user."""
    from base import models_integrations as mi
    model = getattr(mi, ACCOUNT_MODELS[provider], None)
    if model is None:
        return None
    qs = model.objects.filter(is_active=True)
    if user is not None:
        qs = qs.filter(user=user)
    return qs.first()


def _detail_redirect(kind, obj_id):
    if kind == "offer":
        return redirect("ui:offer-detail", offer_id=obj_id)
    return redirect("ui:proposal-detail", proposal_id=obj_id)


def _resolve(kind, obj_id):
    if kind == "offer":
        from recruitment.models import OfferLetter
        obj = get_object_or_404(OfferLetter, id=obj_id)
    else:
        from recruitment.models_proposal import EmploymentProposal
        obj = get_object_or_404(EmploymentProposal, id=obj_id)
    approvals = list(obj.approvals.order_by("sequence"))
    pending = [a for a in approvals if a.status == "pending"]
    return obj, approvals, (pending[0] if pending else None)


def _offer_pdf_bytes(request, offer):
    from xhtml2pdf import pisa
    if not offer.generated_letter:
        offer.generate_offer_letter()
        offer.save(update_fields=["generated_letter"])
    html = render_to_string("recruitment/offer/pdf.html", {"offer": offer}, request=request)
    buf = io.BytesIO()
    pisa.CreatePDF(html, dest=buf)
    return buf.getvalue()


def _proposal_pdf_bytes(request, proposal):
    from xhtml2pdf import pisa
    html = render_to_string("ui/_proposal_sign_pdf.html", {"proposal": proposal}, request=request)
    buf = io.BytesIO()
    pisa.CreatePDF(html, dest=buf)
    return buf.getvalue()


def _first_page_png_datauri(pdf_bytes):
    """Render the first page of the signed PDF to a PNG data-URL for the chain."""
    import fitz  # PyMuPDF (already a project dependency)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
    png = pix.tobytes("png")
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


def _crop_png_datauri(pdf_bytes, page_index, rect, zoom=3.0):
    """Crop a region (PDF points, top-left origin) of one page to a PNG data-URL."""
    import fitz
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(page_index)
    clip = fitz.Rect(*rect) & page.rect
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip)
    return "data:image/png;base64," + base64.b64encode(pix.tobytes("png")).decode("ascii")


def _signature_image_datauri(provider, helper, acct, esign_reference, signed_pdf):
    """Pull the signer's actual signature image back from the provider.

    DocuSign exposes the adopted signature directly via the recipients
    signature_image endpoint. Adobe Sign has no such endpoint, so we crop the
    signature block Adobe stamps at the bottom of the last page. Falls back to
    a first-page snapshot of the signed PDF if either route fails.
    """
    try:
        if provider == "docusign":
            img, mime = helper.download_signature_image(acct, esign_reference)
            return f"data:{mime};base64," + base64.b64encode(img).decode("ascii")
        import fitz
        doc = fitz.open(stream=signed_pdf, filetype="pdf")
        rect = doc.load_page(doc.page_count - 1).rect
        return _crop_png_datauri(
            signed_pdf, doc.page_count - 1,
            (36, rect.height - 170, rect.width - 36, rect.height - 20),
        )
    except Exception:
        return _first_page_png_datauri(signed_pdf)


def _finalize_step(request, kind, obj, approvals, step, signature_datauri, label):
    """Store the signature on the step, approve it, and advance the chain."""
    step.signature_image = signature_datauri
    step.status = "approved"
    step.acted_at = timezone.now()
    step.save()

    remaining = [a for a in approvals if a.status == "pending" and a.id != step.id]
    if not remaining:
        if kind == "offer":
            obj.status = "pending_approval" if obj.status == "draft" else "approved"
        else:
            obj.status = "approved"
        obj.save(update_fields=["status"])

    messages.success(request, f"Signed via {label} successfully.")
    return _detail_redirect(kind, obj.id)


@login_required(login_url="/ui/login/")
def esign_start(request, provider, kind, obj_id):
    if provider not in PROVIDER_MODULES or kind not in ("offer", "proposal"):
        messages.error(request, "Unknown e-sign request.")
        return redirect("/ui/dashboard/")

    label = PROVIDER_LABELS[provider]
    helper = _helper(provider)
    if not helper.is_configured():
        # Provider not set up — fall back silently to the inline signature pad
        # instead of cluttering the page with a status message.
        return _detail_redirect(kind, obj_id)
    acct = _active_account(provider, user=request.user)
    if not acct:
        # No connected provider account — send the user to Integrations
        # without a noisy status banner on the offer/proposal page.
        return redirect("/ui/integrations/")

    obj, approvals, first_pending = _resolve(kind, obj_id)
    try:
        my_emp = request.user.employee_get
    except Exception:
        my_emp = None
    if not first_pending or not my_emp or first_pending.approver_id != my_emp.id:
        messages.error(request, "You are not the active approver for this document.")
        return _detail_redirect(kind, obj_id)

    signer_email = getattr(my_emp, "email", "") or getattr(request.user, "email", "") or ""
    signer_name = str(my_emp)
    if not signer_email:
        messages.error(request, "Your account has no email address for signing.")
        return _detail_redirect(kind, obj_id)

    try:
        pdf = _offer_pdf_bytes(request, obj) if kind == "offer" else _proposal_pdf_bytes(request, obj)
    except Exception as exc:
        messages.error(request, f"Could not prepare the document PDF: {exc}")
        return _detail_redirect(kind, obj_id)

    return_url = request.build_absolute_uri(
        reverse("ui:esign-return", kwargs={
            "provider": provider, "kind": kind, "obj_id": obj_id, "approval_id": first_pending.id,
        })
    )
    client_user_id = str(first_pending.id)

    try:
        if provider == "adobesign":
            ext_id = helper.create_envelope(acct, pdf, signer_email, signer_name, client_user_id, return_url=return_url)
            sign_url = helper.embedded_sign_url(acct, ext_id)
        else:
            ext_id = helper.create_envelope(acct, pdf, signer_email, signer_name, client_user_id)
            sign_url = helper.embedded_sign_url(acct, ext_id, signer_email, signer_name, client_user_id, return_url)
    except Exception as exc:
        messages.error(request, f"{label} signing could not start: {exc}")
        return _detail_redirect(kind, obj_id)

    first_pending.esign_provider = provider
    first_pending.esign_reference = ext_id
    first_pending.save(update_fields=["esign_provider", "esign_reference"])
    return redirect(sign_url)


@login_required(login_url="/ui/login/")
def esign_return(request, provider, kind, obj_id, approval_id):
    if provider not in PROVIDER_MODULES or kind not in ("offer", "proposal"):
        return redirect("/ui/dashboard/")

    label = PROVIDER_LABELS[provider]
    helper = _helper(provider)
    acct = _active_account(provider, user=request.user)
    obj, approvals, _first = _resolve(kind, obj_id)
    step = next((a for a in approvals if a.id == int(approval_id)), None)

    # DocuSign appends ?event=...; only signing_complete means signed.
    event = request.GET.get("event", "")
    if provider == "docusign" and event and event != "signing_complete":
        messages.warning(request, f"Signing was not completed ({event}).")
        return _detail_redirect(kind, obj_id)

    if not step or step.status != "pending":
        return _detail_redirect(kind, obj_id)
    if not acct or not step.esign_reference:
        messages.error(request, f"{label} session expired — please try signing again.")
        return _detail_redirect(kind, obj_id)

    try:
        signed_pdf = helper.download_signed_pdf(acct, step.esign_reference)
        signature_datauri = _signature_image_datauri(provider, helper, acct, step.esign_reference, signed_pdf)
    except Exception as exc:
        messages.error(request, f"Could not retrieve the signed document from {label}: {exc}")
        return _detail_redirect(kind, obj_id)

    return _finalize_step(request, kind, obj, approvals, step, signature_datauri, label)


@login_required(login_url="/ui/login/")
def esign_pick(request, provider, kind, obj_id):
    """Pick one of the signer's saved signatures from their connected account
    and apply it to their approval step.

    DocuSign exposes saved profile signatures via API, so we show a picker.
    Adobe Sign has no such endpoint — for Adobe we fall through to the hosted
    signing ceremony (where the user's saved Adobe signature is offered) and
    extract the signature from the signed document on return.
    """
    from django.shortcuts import render

    if provider not in PROVIDER_MODULES or kind not in ("offer", "proposal"):
        messages.error(request, "Unknown e-sign request.")
        return redirect("/ui/dashboard/")

    label = PROVIDER_LABELS[provider]
    helper = _helper(provider)
    if not helper.is_configured():
        # Provider not set up — fall back silently to the inline signature pad
        # instead of cluttering the page with a status message.
        return _detail_redirect(kind, obj_id)
    acct = _active_account(provider, user=request.user)
    if not acct:
        # No connected provider account — send the user to Integrations
        # without a noisy status banner on the offer/proposal page.
        return redirect("/ui/integrations/")

    obj, approvals, first_pending = _resolve(kind, obj_id)
    try:
        my_emp = request.user.employee_get
    except Exception:
        my_emp = None
    if not first_pending or not my_emp or first_pending.approver_id != my_emp.id:
        messages.error(request, "You are not the active approver for this document.")
        return _detail_redirect(kind, obj_id)

    if provider != "docusign":
        # Adobe Sign: no saved-signature API — use the hosted signing ceremony.
        return redirect("ui:esign-start", provider=provider, kind=kind, obj_id=obj_id)

    if request.method == "POST":
        sig_id = request.POST.get("signature_id", "")
        try:
            img, mime = helper.user_signature_image(acct, sig_id)
        except Exception as exc:
            messages.error(request, f"Could not fetch that signature from {label}: {exc}")
            return _detail_redirect(kind, obj_id)
        first_pending.esign_provider = provider
        first_pending.save(update_fields=["esign_provider"])
        datauri = f"data:{mime};base64," + base64.b64encode(img).decode("ascii")
        return _finalize_step(request, kind, obj, approvals, first_pending, datauri, label)

    try:
        signatures = helper.list_signatures(acct)
    except Exception as exc:
        messages.error(request, f"Could not load your signatures from {label}: {exc}")
        return _detail_redirect(kind, obj_id)

    cards = []
    for s in signatures:
        sig_id = s.get("signatureId", "")
        if not sig_id:
            continue
        try:
            img, mime = helper.user_signature_image(acct, sig_id)
            image = f"data:{mime};base64," + base64.b64encode(img).decode("ascii")
        except Exception:
            image = ""
        cards.append({
            "id": sig_id,
            "name": s.get("signatureName") or s.get("signatureInitials") or "Signature",
            "image": image,
        })

    if not cards:
        # No saved signatures in the connected account — fall through to the
        # hosted signing ceremony silently rather than warning on the page.
        return redirect("ui:esign-start", provider=provider, kind=kind, obj_id=obj_id)

    cancel_url = (
        reverse("ui:offer-detail", kwargs={"offer_id": obj.id}) if kind == "offer"
        else reverse("ui:proposal-detail", kwargs={"proposal_id": obj.id})
    )
    return render(request, "ui/esign_pick.html", {
        "label": label, "provider": provider, "kind": kind, "obj": obj,
        "account": acct, "cards": cards, "cancel_url": cancel_url,
    })
