from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0015_add_signature_image_to_offerapproval'),
    ]

    operations = [
        migrations.AddField(
            model_name='offerletter',
            name='role_type',
            field=models.CharField(
                choices=[('full_time', 'Full Time'), ('contract', 'Contract')],
                default='full_time',
                max_length=20,
                verbose_name='Role Type',
            ),
        ),
    ]
