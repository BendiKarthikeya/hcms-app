from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0019_jobapplication_hr_override_justification"),
    ]

    operations = [
        migrations.AddField(
            model_name="manpowerrequest",
            name="clarification_document",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="recruitment/manpower/clarifications/",
                verbose_name="Clarification Document",
            ),
        ),
        migrations.AddField(
            model_name="manpowerrequest",
            name="last_query",
            field=models.TextField(blank=True, verbose_name="Last Query"),
        ),
        migrations.AddField(
            model_name="manpowerrequest",
            name="query_count",
            field=models.PositiveIntegerField(default=0, verbose_name="Times Queried"),
        ),
        migrations.AlterField(
            model_name="manpowerrequest",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("submitted", "Submitted"),
                    ("under_approval", "Under Approval"),
                    ("queried", "Returned with Query"),
                    ("approved", "Approved"),
                    ("sourcing", "Sourcing"),
                    ("interviewing", "Interviewing"),
                    ("offer", "Offer Stage"),
                    ("joined", "Joined"),
                    ("closed", "Closed"),
                    ("rejected", "Rejected"),
                ],
                default="draft",
                max_length=20,
                verbose_name="Status",
            ),
        ),
        migrations.AlterField(
            model_name="manpowerapproval",
            name="action",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("delegated", "Delegated"),
                    ("auto_escalated", "Auto Escalated"),
                    ("queried", "Queried — Returned to Requester"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]
