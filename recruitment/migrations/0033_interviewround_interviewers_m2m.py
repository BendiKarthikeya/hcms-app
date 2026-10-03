from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0032_add_hr_override_to_screening_profile"),
        ("employee", "0001_candidate_perf_indexes"),
    ]

    operations = [
        migrations.AddField(
            model_name="interviewround",
            name="interviewers",
            field=models.ManyToManyField(
                blank=True,
                related_name="interview_rounds_as_panelist",
                to="employee.employee",
                verbose_name="Panelists",
            ),
        ),
    ]
