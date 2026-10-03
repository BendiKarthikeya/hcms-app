from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0026_candidate_portal"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobapplication",
            name="skills",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="rejection_justification",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="rejection_email_sent",
            field=models.BooleanField(default=False),
        ),
    ]
