"""
Migration: Module 9 — Document Tracking & Audit Trail
- Adds doc_no to MedicalLetter and VisaLetter
- Creates OfferLetterStatusLog, MedicalLetterStatusLog, VisaLetterStatusLog
"""
import uuid
import recruitment.models
from django.db import migrations, models
import django.db.models.deletion


def _assign_medical_doc_nos(apps, schema_editor):
    MedicalLetter = apps.get_model("recruitment", "MedicalLetter")
    for obj in MedicalLetter.objects.filter(doc_no=""):
        obj.doc_no = f"ML-{uuid.uuid4().hex[:8].upper()}"
        obj.save(update_fields=["doc_no"])


def _assign_visa_doc_nos(apps, schema_editor):
    VisaLetter = apps.get_model("recruitment", "VisaLetter")
    for obj in VisaLetter.objects.filter(doc_no=""):
        obj.doc_no = f"VL-{uuid.uuid4().hex[:8].upper()}"
        obj.save(update_fields=["doc_no"])


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0012_seed_medical_visa_templates"),
    ]

    operations = [
        # ── doc_no on MedicalLetter — add nullable first, populate, then constrain ──
        migrations.AddField(
            model_name="medicalletter",
            name="doc_no",
            field=models.CharField(
                max_length=20,
                blank=True,
                default="",
                verbose_name="Document No",
            ),
        ),
        migrations.RunPython(_assign_medical_doc_nos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="medicalletter",
            name="doc_no",
            field=models.CharField(
                default=recruitment.models._medical_letter_no,
                max_length=20,
                unique=True,
                verbose_name="Document No",
            ),
        ),
        # ── doc_no on VisaLetter — same pattern ──────────────────────────────
        migrations.AddField(
            model_name="visaletter",
            name="doc_no",
            field=models.CharField(
                max_length=20,
                blank=True,
                default="",
                verbose_name="Document No",
            ),
        ),
        migrations.RunPython(_assign_visa_doc_nos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="visaletter",
            name="doc_no",
            field=models.CharField(
                default=recruitment.models._visa_letter_no,
                max_length=20,
                unique=True,
                verbose_name="Document No",
            ),
        ),
        # ── OfferLetterStatusLog ─────────────────────────────────────────────
        migrations.CreateModel(
            name="OfferLetterStatusLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("from_status", models.CharField(blank=True, max_length=30, verbose_name="From")),
                ("to_status", models.CharField(max_length=30, verbose_name="To")),
                ("note", models.TextField(blank=True, verbose_name="Note")),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="offer_status_logs",
                        to="employee.employee",
                        verbose_name="Actor",
                    ),
                ),
                (
                    "offer_letter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_logs",
                        to="recruitment.offerletter",
                        verbose_name="Offer Letter",
                    ),
                ),
            ],
            options={
                "verbose_name": "Offer Letter Status Log",
                "verbose_name_plural": "Offer Letter Status Logs",
                "ordering": ["timestamp"],
            },
        ),
        # ── MedicalLetterStatusLog ───────────────────────────────────────────
        migrations.CreateModel(
            name="MedicalLetterStatusLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("from_status", models.CharField(blank=True, max_length=30, verbose_name="From")),
                ("to_status", models.CharField(max_length=30, verbose_name="To")),
                ("note", models.TextField(blank=True, verbose_name="Note")),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="medical_status_logs",
                        to="employee.employee",
                        verbose_name="Actor",
                    ),
                ),
                (
                    "medical_letter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_logs",
                        to="recruitment.medicalletter",
                        verbose_name="Medical Letter",
                    ),
                ),
            ],
            options={
                "verbose_name": "Medical Letter Status Log",
                "verbose_name_plural": "Medical Letter Status Logs",
                "ordering": ["timestamp"],
            },
        ),
        # ── VisaLetterStatusLog ──────────────────────────────────────────────
        migrations.CreateModel(
            name="VisaLetterStatusLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("from_status", models.CharField(blank=True, max_length=30, verbose_name="From")),
                ("to_status", models.CharField(max_length=30, verbose_name="To")),
                ("note", models.TextField(blank=True, verbose_name="Note")),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="visa_status_logs",
                        to="employee.employee",
                        verbose_name="Actor",
                    ),
                ),
                (
                    "visa_letter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_logs",
                        to="recruitment.visaletter",
                        verbose_name="Visa Letter",
                    ),
                ),
            ],
            options={
                "verbose_name": "Visa Letter Status Log",
                "verbose_name_plural": "Visa Letter Status Logs",
                "ordering": ["timestamp"],
            },
        ),
    ]
