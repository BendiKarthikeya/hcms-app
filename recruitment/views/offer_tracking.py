"""
recruitment/views/offer_tracking.py — Phase 6: post-offer clearance tracking.
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from fits.decorators import login_required
from recruitment.models import OfferLetter


@login_required
def offer_tracking(request):
    offers = OfferLetter.objects.filter(status="accepted").select_related("candidate_id")
    columns = ["Candidate", "Position", "Joining Date", "Medical", "Visa", "Labour", "Documents %", "Joining Status", "Actions"]
    return render(request, "recruitment/offer/tracking.html", {"offers": offers, "columns": columns})


@login_required
def offer_update(request, offer_id):
    offer = get_object_or_404(OfferLetter, id=offer_id)
    CLEARANCE = offer.CLEARANCE_STATUS
    JOINING = offer.JOINING_STATUS
    fields = [
        ("medical_status", "Medical"),
        ("visa_status", "Visa"),
        ("labour_clearance_status", "Labour Clearance"),
    ]

    if request.method == "POST":
        now = timezone.now()
        for fname, _ in fields:
            old = getattr(offer, fname)
            new = request.POST.get(fname)
            setattr(offer, fname, new)
            if old != "cleared" and new == "cleared":
                setattr(offer, fname.replace("_status", "_cleared_at"), now)
        offer.documents_completion_pct = int(request.POST.get("documents_completion_pct") or 0)
        offer.joining_status = request.POST.get("joining_status", offer.joining_status)
        offer.save()

        # Auto-close ManpowerRequest if all positions joined
        if offer.joining_status == "joined":
            try:
                rec = offer.candidate_id.recruitment_id
                if rec and rec.manpower_request:
                    mr = rec.manpower_request
                    mr.closed_positions += 1
                    mr.save()
                    if mr.is_fully_filled:
                        mr.status = "closed"
                        mr.save()
            except Exception:
                pass

        messages.success(request, "Clearance status updated.")
        return redirect("offer-tracking")

    return render(request, "recruitment/offer/update.html", {
        "offer": offer,
        "fields": fields,
        "choices": CLEARANCE,
        "joining_choices": JOINING,
        "current": {
            "medical_status": offer.medical_status,
            "visa_status": offer.visa_status,
            "labour_clearance_status": offer.labour_clearance_status,
        },
    })
