from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0029_add_personal_fields_to_screening_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="recruitmentapproval",
            name="signature_image",
            field=models.TextField(blank=True, verbose_name="Signature (base64)"),
        ),
    ]
