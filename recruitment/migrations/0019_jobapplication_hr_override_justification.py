from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0018_recruitment_budget_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobapplication",
            name="hr_override_justification",
            field=models.TextField(blank=True, null=True),
        ),
    ]
