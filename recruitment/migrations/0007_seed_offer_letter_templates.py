"""
0007_seed_offer_letter_templates.py

Seeds 5 default offer letter templates into recruitment_offerlettertemplate.
Placeholders: {{candidate_name}}, {{position}}, {{department}}, {{joining_date}},
              {{basic_salary}}, {{company_name}}
"""

from django.db import migrations

TEMPLATES = [
    {
        "name": "Standard Employment Offer",
        "body_html": """Dear {{candidate_name}},

We are delighted to offer you the position of <strong>{{position}}</strong>{% if department %} in the <strong>{{department}}</strong> department{% endif %} at <strong>{{company_name}}</strong>.

<strong>Key Terms of Employment:</strong>

• <strong>Position:</strong> {{position}}
• <strong>Department:</strong> {{department}}
• <strong>Joining Date:</strong> {{joining_date}}
• <strong>Basic Salary:</strong> OMR {{basic_salary}} per month

Your employment will be subject to the standard terms and conditions of employment as set out in the Employment Contract, which will be provided to you prior to your joining date.

Please confirm your acceptance of this offer by signing and returning a copy of this letter. If you have any questions, please do not hesitate to contact our HR department.

We look forward to welcoming you to our team.

Yours sincerely,
Human Resources Department
{{company_name}}""",
    },
    {
        "name": "Senior Management Offer",
        "body_html": """Dear {{candidate_name}},

On behalf of the Leadership Team at <strong>{{company_name}}</strong>, we are pleased to extend this offer of employment for the senior role of <strong>{{position}}</strong>.

<strong>Position Details:</strong>

• <strong>Title:</strong> {{position}}
• <strong>Division / Department:</strong> {{department}}
• <strong>Commencement Date:</strong> {{joining_date}}
• <strong>Basic Monthly Remuneration:</strong> OMR {{basic_salary}}

In addition to your basic salary, you will be entitled to a comprehensive benefits package including health insurance, annual leave entitlement per Omani Labour Law, and performance-based incentives as outlined in the attached schedule.

This offer is contingent upon satisfactory reference checks and receipt of original academic and professional credentials.

We are confident that your expertise and leadership will make a significant contribution to our organisation. We look forward to your positive response.

Warmest regards,
Chief Executive Officer
{{company_name}}""",
    },
    {
        "name": "Probationary Offer",
        "body_html": """Dear {{candidate_name}},

We are pleased to offer you the position of <strong>{{position}}</strong>{% if department %} within the <strong>{{department}}</strong> department{% endif %} at <strong>{{company_name}}</strong>, subject to a probationary period.

<strong>Employment Details:</strong>

• <strong>Position:</strong> {{position}}
• <strong>Department:</strong> {{department}}
• <strong>Start Date:</strong> {{joining_date}}
• <strong>Basic Salary:</strong> OMR {{basic_salary}} per month
• <strong>Probationary Period:</strong> Three (3) months from the date of joining

During the probationary period, your performance will be evaluated against set objectives. Upon successful completion, your employment will be confirmed and you will be entitled to the full benefits package as per company policy.

Either party may terminate employment during the probation period with one (1) week's written notice.

Please sign and return this letter to confirm acceptance no later than 5 working days from the date of issue.

Kind regards,
Human Resources Department
{{company_name}}""",
    },
    {
        "name": "Contract Employment Offer",
        "body_html": """Dear {{candidate_name}},

We are pleased to offer you a fixed-term contract position of <strong>{{position}}</strong>{% if department %} in the <strong>{{department}}</strong> department{% endif %} at <strong>{{company_name}}</strong>.

<strong>Contract Details:</strong>

• <strong>Position:</strong> {{position}}
• <strong>Department:</strong> {{department}}
• <strong>Contract Start Date:</strong> {{joining_date}}
• <strong>Contract Duration:</strong> One (1) year, renewable subject to performance and business needs
• <strong>Basic Monthly Salary:</strong> OMR {{basic_salary}}

This is a fixed-term engagement and does not imply any promise of permanent employment beyond the stated term. The contract may be renewed by mutual written agreement prior to expiry.

All other employment conditions shall be governed by the Omani Labour Law and the company's internal policies applicable to contract employees.

Kindly confirm your acceptance of these terms within three (3) working days.

Regards,
Human Resources Department
{{company_name}}""",
    },
    {
        "name": "Executive Offer Letter",
        "body_html": """Dear {{candidate_name}},

The Board of Directors and Executive Leadership of <strong>{{company_name}}</strong> are honoured to extend this offer of employment to you for the executive position of <strong>{{position}}</strong>.

<strong>Executive Appointment Details:</strong>

• <strong>Title:</strong> {{position}}
• <strong>Reporting Division:</strong> {{department}}
• <strong>Effective Date:</strong> {{joining_date}}
• <strong>Basic Monthly Salary:</strong> OMR {{basic_salary}}

<strong>Executive Benefits Include:</strong>
• Comprehensive private medical insurance (employee + dependants)
• Annual performance bonus (as per the Executive Incentive Plan)
• Company vehicle or vehicle allowance
• Annual leave as per Omani Labour Law plus additional executive entitlement
• Business travel and accommodation per company policy

This appointment is subject to board ratification, satisfactory completion of background screening, and execution of the Executive Service Agreement which will be provided separately.

We are excited about the strategic value you will bring to <strong>{{company_name}}</strong> and look forward to your formal acceptance.

With regards,
Chairman, Board of Directors
{{company_name}}""",
    },
]


def seed_templates(apps, schema_editor):
    OfferLetterTemplate = apps.get_model("recruitment", "OfferLetterTemplate")
    for tmpl in TEMPLATES:
        OfferLetterTemplate.objects.get_or_create(
            name=tmpl["name"],
            defaults={"body_html": tmpl["body_html"], "is_active": True},
        )


def remove_templates(apps, schema_editor):
    OfferLetterTemplate = apps.get_model("recruitment", "OfferLetterTemplate")
    OfferLetterTemplate.objects.filter(name__in=[t["name"] for t in TEMPLATES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0006_interview_time_nullable"),
    ]

    operations = [
        migrations.RunPython(seed_templates, remove_templates),
    ]
