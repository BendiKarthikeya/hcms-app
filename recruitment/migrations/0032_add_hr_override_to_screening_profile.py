from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0031_add_oneic_scoring_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidatescreeningprofile',
            name='hr_override',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='candidatescreeningprofile',
            name='hr_override_justification',
            field=models.TextField(blank=True, null=True),
        ),
    ]
