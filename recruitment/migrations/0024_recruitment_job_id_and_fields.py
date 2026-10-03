from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0023_seed_oneic_form_templates"),
    ]

    operations = [
        migrations.AddField(
            model_name="recruitment",
            name="job_id",
            field=models.CharField(
                blank=True, editable=False, max_length=20, null=True, unique=True, verbose_name="Job ID"
            ),
        ),
        migrations.AddField(
            model_name="recruitment",
            name="grade",
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name="Grade"),
        ),
        migrations.AddField(
            model_name="recruitment",
            name="band",
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name="Band"),
        ),
        migrations.AddField(
            model_name="recruitment",
            name="budget",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="Budget"
            ),
        ),
        migrations.AddField(
            model_name="recruitment",
            name="employment_type",
            field=models.CharField(
                choices=[("full_time", "Full Time"), ("contract", "Contract")],
                default="full_time",
                max_length=20,
                verbose_name="Employment Type",
            ),
        ),
        migrations.AddField(
            model_name="recruitment",
            name="expat_allowed",
            field=models.BooleanField(default=False, verbose_name="Expat Allowed"),
        ),
        migrations.AddField(
            model_name="recruitment",
            name="location",
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name="Location"),
        ),
    ]
