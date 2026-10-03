# Generated for the onboarding document e-sign workflow.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0001_candidate_perf_indexes'),
        ('recruitment', '0035_offerletter_add_location'),
    ]

    operations = [
        migrations.CreateModel(
            name='OnboardingDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_key', models.CharField(max_length=40, verbose_name='Document Key')),
                ('title', models.CharField(max_length=150, verbose_name='Title')),
                ('body_html', models.TextField(blank=True, verbose_name='Body')),
                ('batch', models.PositiveIntegerField(default=1, verbose_name='Batch')),
                ('sequence', models.PositiveIntegerField(default=1, verbose_name='Sequence')),
                ('released', models.BooleanField(default=False, verbose_name='Released to Candidate')),
                ('candidate_signature', models.TextField(blank=True, verbose_name='Candidate Signature')),
                ('candidate_signed_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('awaiting_signature', 'Awaiting Signature'), ('signed', 'Signed — Awaiting HR Approval'), ('approved', 'Approved')], default='awaiting_signature', max_length=20, verbose_name='Status')),
                ('hr_note', models.TextField(blank=True, verbose_name='HR Note')),
                ('hr_acted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('hr_acted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='employee.employee')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sign_documents', to='recruitment.offerletter', verbose_name='Offer Letter')),
            ],
            options={
                'verbose_name': 'Onboarding Document',
                'verbose_name_plural': 'Onboarding Documents',
                'ordering': ['batch', 'sequence'],
            },
        ),
    ]
