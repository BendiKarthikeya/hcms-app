from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0017_interviewround_per_round_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="recruitment",
            name="posting_type",
            field=models.CharField(
                choices=[("internal", "Internal"), ("external", "External")],
                default="external",
                max_length=10,
                verbose_name="Posting Type",
            ),
        ),
        migrations.AddField(
            model_name="recruitment",
            name="budget_available",
            field=models.BooleanField(default=False, verbose_name="Budget Available"),
        ),
        migrations.AddField(
            model_name="recruitment",
            name="budget_document",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="recruitment/budget/",
                verbose_name="Budget Document",
            ),
        ),
    ]
