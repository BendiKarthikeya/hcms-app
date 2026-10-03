import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0001_candidate_perf_indexes'),
        ('recruitment', '0016_add_role_type_to_offerletter'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewround',
            name='interviewer',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='interview_rounds_as_interviewer',
                to='employee.employee',
                verbose_name='Interviewer',
            ),
        ),
        migrations.AddField(
            model_name='interviewround',
            name='round_date',
            field=models.DateField(blank=True, null=True, verbose_name='Round Date'),
        ),
        migrations.AddField(
            model_name='interviewround',
            name='round_time',
            field=models.TimeField(blank=True, null=True, verbose_name='Round Time'),
        ),
    ]
