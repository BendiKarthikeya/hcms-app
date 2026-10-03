import uuid

import django.db.models.deletion
from django.db import migrations, models


def _backfill_tokens(apps, schema_editor):
    OfferLetter = apps.get_model("recruitment", "OfferLetter")
    for offer in OfferLetter.objects.all():
        offer.candidate_signature_token = uuid.uuid4()
        offer.portal_token = uuid.uuid4()
        offer.save(update_fields=["candidate_signature_token", "portal_token"])


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0025_employment_proposal"),
    ]

    operations = [
        # ── Add token fields without unique constraint first ──────────────────
        migrations.AddField(
            model_name="offerletter",
            name="candidate_signature_token",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                verbose_name="Candidate Signature Token",
            ),
        ),
        migrations.AddField(
            model_name="offerletter",
            name="portal_token",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                verbose_name="Portal Token",
            ),
        ),
        # ── Backfill unique values for existing rows ──────────────────────────
        migrations.RunPython(_backfill_tokens, migrations.RunPython.noop),
        # ── Now add the unique constraints ───────────────────────────────────
        migrations.AlterField(
            model_name="offerletter",
            name="candidate_signature_token",
            field=models.UUIDField(
                default=uuid.uuid4,
                unique=True,
                editable=False,
                verbose_name="Candidate Signature Token",
            ),
        ),
        migrations.AlterField(
            model_name="offerletter",
            name="portal_token",
            field=models.UUIDField(
                default=uuid.uuid4,
                unique=True,
                editable=False,
                verbose_name="Portal Token",
            ),
        ),
        # ── candidate_signed_at ───────────────────────────────────────────────
        migrations.AddField(
            model_name="offerletter",
            name="candidate_signed_at",
            field=models.DateTimeField(
                null=True,
                blank=True,
                verbose_name="Candidate Signed At",
            ),
        ),
        # ── CandidatePortalUpload ─────────────────────────────────────────────
        migrations.CreateModel(
            name="CandidatePortalUpload",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "offer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="portal_uploads",
                        to="recruitment.offerletter",
                        verbose_name="Offer Letter",
                    ),
                ),
                (
                    "document_type",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("medical", "Medical Certificate"),
                            ("marksheet", "Academic Marksheet / Degree"),
                            ("experience", "Experience Certificate"),
                            ("passport", "Passport Copy"),
                            ("id_card", "National ID / Civil ID"),
                            ("other", "Other Document"),
                        ],
                        verbose_name="Document Type",
                    ),
                ),
                ("label", models.CharField(blank=True, max_length=100, verbose_name="Label")),
                ("file", models.FileField(upload_to="recruitment/portal_uploads/", verbose_name="File")),
                ("notes", models.TextField(blank=True, verbose_name="Notes")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Candidate Portal Upload",
                "verbose_name_plural": "Candidate Portal Uploads",
                "ordering": ["uploaded_at"],
            },
        ),
    ]
