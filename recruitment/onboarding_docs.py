"""
recruitment/onboarding_docs.py

Sequential onboarding document e-sign workflow.

After an offer letter is fully approved through its internal e-sign chain, the
candidate is given a token-gated portal where they e-sign documents in stages:

  Batch 1 : the offer letter itself (released immediately).
  Batch 2 : Terms & Conditions, Code of Conduct, NDA, Data Privacy Consent
            (released only after HR approves the signed offer letter).

Each document is signed by the candidate, then reviewed by HR who either
approves it or sends it back to be re-signed. Once every document is approved,
HR can dispatch the candidate to the visa team.
"""

import threading

from django.utils import timezone

from recruitment.models import OnboardingDocument


# ── Standard batch-2 documents (authored boilerplate) ─────────────────────────

STAGE2_TEMPLATES = [
    {
        "doc_key": "terms_conditions",
        "title": "Terms & Conditions of Employment",
        "body_html": (
            "<h4>Terms &amp; Conditions of Employment</h4>"
            "<p>This document sets out the general terms and conditions governing "
            "your employment, including working hours, leave entitlement, notice "
            "periods, and conduct expectations. By signing below you acknowledge "
            "that you have read, understood, and agree to abide by these terms.</p>"
            "<ul>"
            "<li>Standard working hours apply as per company policy.</li>"
            "<li>Annual leave accrues in line with statutory entitlement.</li>"
            "<li>Either party may terminate employment subject to the agreed notice period.</li>"
            "<li>You agree to comply with all company policies in force from time to time.</li>"
            "</ul>"
        ),
    },
    {
        "doc_key": "code_of_conduct",
        "title": "Code of Conduct",
        "body_html": (
            "<h4>Code of Conduct</h4>"
            "<p>The company is committed to maintaining a professional, respectful "
            "and inclusive workplace. By signing this Code of Conduct you agree to:</p>"
            "<ul>"
            "<li>Act with integrity and honesty in all dealings.</li>"
            "<li>Treat colleagues, clients and partners with respect and fairness.</li>"
            "<li>Avoid conflicts of interest and disclose any that arise.</li>"
            "<li>Comply with all applicable laws and company policies.</li>"
            "</ul>"
        ),
    },
    {
        "doc_key": "nda",
        "title": "Non-Disclosure Agreement (NDA)",
        "body_html": (
            "<h4>Non-Disclosure Agreement</h4>"
            "<p>In the course of your employment you may have access to confidential "
            "and proprietary information. By signing this agreement you undertake to:</p>"
            "<ul>"
            "<li>Keep all confidential information strictly private.</li>"
            "<li>Use such information only for legitimate business purposes.</li>"
            "<li>Not disclose any confidential information to third parties.</li>"
            "<li>Continue to honour these obligations after employment ends.</li>"
            "</ul>"
        ),
    },
    {
        "doc_key": "data_privacy",
        "title": "Data Privacy Consent",
        "body_html": (
            "<h4>Data Privacy Consent</h4>"
            "<p>The company will process your personal data for employment, payroll, "
            "and statutory compliance purposes. By signing you consent to:</p>"
            "<ul>"
            "<li>The collection and processing of your personal data.</li>"
            "<li>Retention of records as required by law and company policy.</li>"
            "<li>Sharing data with authorities and service providers where necessary.</li>"
            "</ul>"
            "<p>You may withdraw consent or request access to your data at any time, "
            "subject to legal limitations.</p>"
        ),
    },
]


def _email_async(target, *args):
    try:
        threading.Thread(target=target, args=args, daemon=True).start()
    except Exception:
        pass


def create_onboarding_documents(offer):
    """Create the batch-1 offer letter sign-doc (released) and the batch-2 docs
    (not yet released), then email the candidate their portal link.

    Idempotent — safe to call more than once.
    """
    if offer.sign_documents.exists():
        return

    body = offer.generated_letter or ""
    if not body:
        try:
            offer.generate_offer_letter()
            offer.save(update_fields=["generated_letter"])
            body = offer.generated_letter or ""
        except Exception:
            body = ""

    OnboardingDocument.objects.create(
        offer=offer,
        doc_key="offer_letter",
        title="Offer Letter",
        body_html=body,
        batch=1,
        sequence=1,
        released=True,
    )

    for idx, tpl in enumerate(STAGE2_TEMPLATES, start=1):
        OnboardingDocument.objects.create(
            offer=offer,
            doc_key=tpl["doc_key"],
            title=tpl["title"],
            body_html=tpl["body_html"],
            batch=2,
            sequence=idx,
            released=False,
        )

    from recruitment.email_utils import email_candidate_documents_ready
    _email_async(email_candidate_documents_ready, offer, 1)


def on_candidate_signed(doc, signature_data):
    """Record the candidate's e-signature on a document."""
    doc.candidate_signature = signature_data
    doc.candidate_signed_at = timezone.now()
    doc.status = OnboardingDocument.STATUS_SIGNED
    doc.hr_note = ""
    doc.save(update_fields=["candidate_signature", "candidate_signed_at", "status", "hr_note"])

    # When the offer letter itself is signed, mirror the legacy acceptance side
    # effects so the rest of the system sees the candidate as accepted/hired.
    if doc.doc_key == "offer_letter":
        offer = doc.offer
        offer.candidate_signed_at = timezone.now()
        if offer.status == "sent":
            offer.status = "accepted"
            offer.accepted_date = timezone.now()
            candidate = offer.candidate_id
            candidate.hired = True
            candidate.joining_date = offer.joining_date
            candidate.save()
        offer.save()


def on_hr_approve(doc, employee):
    """HR approves a candidate-signed document. Releases batch 2 once the offer
    letter (batch 1) is approved."""
    doc.status = OnboardingDocument.STATUS_APPROVED
    doc.hr_acted_by = employee
    doc.hr_acted_at = timezone.now()
    doc.save(update_fields=["status", "hr_acted_by", "hr_acted_at"])

    offer = doc.offer
    if doc.batch == 1:
        batch1_done = not offer.sign_documents.filter(batch=1).exclude(
            status=OnboardingDocument.STATUS_APPROVED
        ).exists()
        if batch1_done:
            batch2 = offer.sign_documents.filter(batch=2, released=False)
            if batch2.exists():
                batch2.update(released=True)
                from recruitment.email_utils import email_candidate_documents_ready
                _email_async(email_candidate_documents_ready, offer, 2)


def on_hr_resign(doc, employee, note=""):
    """HR sends a signed document back to the candidate to e-sign again."""
    doc.candidate_signature = ""
    doc.candidate_signed_at = None
    doc.status = OnboardingDocument.STATUS_AWAITING
    doc.hr_note = note or ""
    doc.hr_acted_by = employee
    doc.hr_acted_at = timezone.now()
    doc.save(update_fields=[
        "candidate_signature", "candidate_signed_at", "status",
        "hr_note", "hr_acted_by", "hr_acted_at",
    ])
    from recruitment.email_utils import email_candidate_resign_request
    _email_async(email_candidate_resign_request, doc)


def all_documents_approved(offer):
    """True when the offer has sign-documents and every one is approved."""
    docs = offer.sign_documents.all()
    if not docs.exists():
        return False
    return not docs.exclude(status=OnboardingDocument.STATUS_APPROVED).exists()
