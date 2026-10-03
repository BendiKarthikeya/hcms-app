from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0002_candidate_perf_indexes"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MailboxIntegration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(choices=[("gmail", "Gmail"), ("outlook", "Outlook")], max_length=20)),
                ("email_address", models.EmailField(blank=True, max_length=254)),
                ("display_name", models.CharField(blank=True, max_length=255)),
                ("access_token", models.TextField(blank=True)),
                ("refresh_token", models.TextField(blank=True)),
                ("token_expires_at", models.DateTimeField(blank=True, null=True)),
                ("scope", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("last_error", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mailbox_integrations", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Mailbox Integration",
                "verbose_name_plural": "Mailbox Integrations",
                "unique_together": {("user", "provider")},
            },
        ),
    ]
