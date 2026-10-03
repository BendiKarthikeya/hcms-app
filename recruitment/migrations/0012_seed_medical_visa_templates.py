from django.db import migrations


MEDICAL_TEMPLATES = [
    {
        "name": "Standard Medical Clearance Letter",
        "body_html": (
            "To Whom It May Concern,\n\n"
            "This is to certify that {{candidate_name}} has been assessed and found medically fit "
            "to undertake the role of {{position}} at {{company_name}}.\n\n"
            "The candidate has completed all required pre-employment medical checks and has been "
            "declared medically fit for employment.\n\n"
            "This clearance is valid for a period of three (3) months from the date of issuance.\n\n"
            "Should you require any further information, please do not hesitate to contact us.\n\n"
            "Yours sincerely,\n"
            "Human Resources Department\n"
            "{{company_name}}"
        ),
    },
    {
        "name": "Medical Clearance — Overseas Placement",
        "body_html": (
            "RE: Medical Clearance for Overseas Employment\n\n"
            "Dear Sir/Madam,\n\n"
            "We are pleased to confirm that {{candidate_name}}, who has been selected for the "
            "position of {{position}} at {{company_name}}, has successfully completed all mandatory "
            "pre-employment medical examinations required for overseas deployment.\n\n"
            "The results confirm that the candidate is in good health and is medically cleared for "
            "international travel and employment.\n\n"
            "This letter is issued for official purposes only.\n\n"
            "Yours faithfully,\n"
            "Human Resources\n"
            "{{company_name}}"
        ),
    },
]

VISA_TEMPLATES = [
    {
        "name": "Standard Visa Support Letter",
        "body_html": (
            "To the Consular Officer,\n\n"
            "RE: Visa Support Letter for {{candidate_name}}\n\n"
            "We, {{company_name}}, hereby confirm that {{candidate_name}} has been offered and "
            "accepted the position of {{position}} with our organisation.\n\n"
            "We respectfully request that a work visa / entry permit be granted to the above-named "
            "individual to allow them to commence their employment duties.\n\n"
            "{{company_name}} accepts full responsibility for the candidate's conduct and compliance "
            "with all applicable immigration laws during their stay.\n\n"
            "Please feel free to contact our HR department for any further documentation or "
            "clarification required.\n\n"
            "Yours sincerely,\n"
            "Human Resources Department\n"
            "{{company_name}}"
        ),
    },
    {
        "name": "Visa Support Letter — Skilled Worker",
        "body_html": (
            "To Whom It May Concern,\n\n"
            "This letter serves as official confirmation that {{company_name}} has extended a formal "
            "offer of employment to {{candidate_name}} for the role of {{position}}.\n\n"
            "The candidate possesses the requisite skills, qualifications and experience for this "
            "specialised role, and their employment is essential to our operations.\n\n"
            "We kindly request the relevant authorities to process the work permit / visa application "
            "for {{candidate_name}} at the earliest convenience.\n\n"
            "All supporting documentation will be provided upon request.\n\n"
            "Warm regards,\n"
            "Human Resources\n"
            "{{company_name}}"
        ),
    },
]


def seed_templates(apps, schema_editor):
    MedicalLetterTemplate = apps.get_model("recruitment", "MedicalLetterTemplate")
    VisaLetterTemplate = apps.get_model("recruitment", "VisaLetterTemplate")

    for t in MEDICAL_TEMPLATES:
        MedicalLetterTemplate.objects.get_or_create(name=t["name"], defaults={"body_html": t["body_html"]})

    for t in VISA_TEMPLATES:
        VisaLetterTemplate.objects.get_or_create(name=t["name"], defaults={"body_html": t["body_html"]})


def remove_templates(apps, schema_editor):
    MedicalLetterTemplate = apps.get_model("recruitment", "MedicalLetterTemplate")
    VisaLetterTemplate = apps.get_model("recruitment", "VisaLetterTemplate")
    MedicalLetterTemplate.objects.filter(name__in=[t["name"] for t in MEDICAL_TEMPLATES]).delete()
    VisaLetterTemplate.objects.filter(name__in=[t["name"] for t in VISA_TEMPLATES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0011_add_medical_visa_letters"),
    ]

    operations = [
        migrations.RunPython(seed_templates, remove_templates),
    ]
