from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0021_seed_hr_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recruitment",
            name="approval_status",
            field=models.CharField(
                choices=[
                    ("pending", _("Pending Approval")),
                    ("approved", _("Approved")),
                    ("rejected", _("Rejected")),
                    ("queried", _("Returned with Query")),
                ],
                default="pending",
                max_length=20,
                verbose_name=_("Approval Status"),
            ),
        ),
        migrations.AlterField(
            model_name="recruitmentapproval",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", _("Pending")),
                    ("approved", _("Approved")),
                    ("rejected", _("Rejected")),
                    ("queried", _("Returned with Query")),
                ],
                default="pending",
                max_length=20,
                verbose_name=_("Approval Status"),
            ),
        ),
    ]
