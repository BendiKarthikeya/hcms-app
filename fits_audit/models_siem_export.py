"""
fits_audit/models_siem_export.py

SIEM (Security Information and Event Management) Export
Exports audit logs in standard SIEM formats for security monitoring
Supports CEF, JSON, and Syslog formats
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from base.models import Company, Employee
import json
import csv
import io
from datetime import datetime


class SIEMConfig(models.Model):
    """
    SIEM integration configuration
    """

    SIEM_TYPE_CHOICES = [
        ("splunk", _("Splunk")),
        ("elastic", _("Elastic Stack")),
        ("sumo", _("Sumo Logic")),
        ("datadog", _("Datadog")),
        ("arista", _("Arista")),
        ("generic", _("Generic Syslog")),
    ]

    FORMAT_CHOICES = [
        ("cef", _("Common Event Format (CEF)")),
        ("json", _("JSON")),
        ("syslog", _("Syslog")),
        ("csv", _("CSV")),
    ]

    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name="siem_config"
    )

    # SIEM Configuration
    siem_type = models.CharField(max_length=50, choices=SIEM_TYPE_CHOICES)
    siem_name = models.CharField(max_length=255)

    # Export settings
    export_format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    export_endpoint = models.URLField(null=True, blank=True)

    # Authentication
    api_token = models.CharField(max_length=255, null=True, blank=True)
    api_key = models.CharField(max_length=255, null=True, blank=True)

    # Syslog settings (if applicable)
    syslog_host = models.CharField(max_length=255, null=True, blank=True)
    syslog_port = models.IntegerField(default=514, null=True, blank=True)
    syslog_protocol = models.CharField(
        max_length=10, choices=[("tcp", "TCP"), ("udp", "UDP")], default="tcp"
    )

    # Export configuration
    is_enabled = models.BooleanField(default=True)
    auto_export = models.BooleanField(
        default=True, help_text=_("Automatically export logs on creation")
    )
    export_interval_minutes = models.IntegerField(
        default=60, help_text=_("Batch export interval")
    )

    # Event types to export
    export_user_login_logout = models.BooleanField(default=True)
    export_data_access = models.BooleanField(default=True)
    export_data_modification = models.BooleanField(default=True)
    export_permission_changes = models.BooleanField(default=True)
    export_admin_actions = models.BooleanField(default=True)
    export_security_events = models.BooleanField(default=True)

    # Metadata
    configured_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )
    configured_at = models.DateTimeField(auto_now_add=True)
    last_test = models.DateTimeField(null=True, blank=True)
    last_export = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "audit_siem_config"
        verbose_name = _("SIEM Configuration")

    def __str__(self):
        return f"{self.siem_type} - {self.company}"

    def test_connection(self):
        """Test SIEM connectivity"""
        try:
            if self.siem_type == "generic":
                # Test syslog connection
                import socket

                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b"TEST", (self.syslog_host, self.syslog_port))
                sock.close()
            else:
                # Test API endpoint
                import requests

                headers = {}
                if self.api_token:
                    headers["Authorization"] = f"Bearer {self.api_token}"
                elif self.api_key:
                    headers["X-API-Key"] = self.api_key

                response = requests.get(
                    self.export_endpoint, headers=headers, timeout=10
                )
                return response.status_code < 400

            self.last_test = timezone.now()
            self.save()
            return True
        except Exception as e:
            print(f"SIEM connection test failed: {str(e)}")
            return False


class AuditLogSIEMExport(models.Model):
    """
    Export records for SIEM compliance
    Tracks which logs have been exported
    """

    EXPORT_STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("exported", _("Exported")),
        ("failed", _("Failed")),
        ("retrying", _("Retrying")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="siem_exports"
    )

    # Batch information
    batch_number = models.CharField(max_length=50, unique=True)
    export_format = models.CharField(max_length=20)
    log_count = models.IntegerField()

    # Log range
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()

    # Export content
    export_file = models.FileField(upload_to="siem_exports/", null=True, blank=True)
    export_content = models.TextField(blank=True)

    # Status
    status = models.CharField(
        max_length=20, choices=EXPORT_STATUS_CHOICES, default="pending"
    )

    # SIEM response
    siem_response_code = models.IntegerField(null=True, blank=True)
    siem_reference_id = models.CharField(max_length=100, blank=True)
    siem_response_message = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    exported_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    last_retry = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        db_table = "audit_log_siem_export"
        verbose_name = _("Audit Log SIEM Export")
        verbose_name_plural = _("Audit Log SIEM Exports")
        ordering = ["-created_at"]

    def __str__(self):
        return f"SIEM Export {self.batch_number}"

    def generate_cef_format(self, audit_logs):
        """
        Generate Common Event Format (CEF)
        CEF:0|DevName|AppName|AppVersion|EventID|EventName|Severity|Field1=Value1
        """
        cef_records = []

        for log in audit_logs:
            cef_string = (
                f"CEF:0|HCMS|HR Management System|1.0|"
                f"{log.get('event_type', 'AUDIT')}|"
                f"{log.get('description', 'Audit Event')}|"
                f"{log.get('severity', 5)}|"
                f"src={log.get('user_id', 'N/A')} "
                f"suser={log.get('username', 'N/A')} "
                f"act={log.get('action', 'N/A')} "
                f"cs1Label=Module cs1={log.get('module', 'N/A')} "
                f"cs2Label=ObjectType cs2={log.get('object_type', 'N/A')} "
                f"cs3Label=ObjectID cs3={log.get('object_id', 'N/A')} "
                f"rt={log.get('timestamp', timezone.now().isoformat())} "
                f"msg={log.get('details', '')}"
            )
            cef_records.append(cef_string)

        return "\n".join(cef_records)

    def generate_json_format(self, audit_logs):
        """Generate JSON format SIEM export"""
        json_records = []

        for log in audit_logs:
            record = {
                "timestamp": str(log.get("timestamp", timezone.now())),
                "event_type": log.get("event_type", "AUDIT"),
                "severity": log.get("severity", 5),
                "user": {
                    "id": log.get("user_id"),
                    "username": log.get("username"),
                    "email": log.get("user_email"),
                },
                "action": log.get("action"),
                "module": log.get("module"),
                "object_type": log.get("object_type"),
                "object_id": log.get("object_id"),
                "status": log.get("status"),
                "details": log.get("details"),
                "ip_address": log.get("ip_address"),
                "company": log.get("company_name"),
            }
            json_records.append(record)

        return json.dumps(json_records, indent=2)

    def generate_syslog_format(self, audit_logs):
        """
        Generate Syslog format
        <PRI>TIMESTAMP HOSTNAME TAG[PID]: MESSAGE
        """
        syslog_records = []

        for log in audit_logs:
            pri = 14 * 8 + log.get("severity", 5)  # Local use 14
            timestamp = datetime.fromisoformat(
                log.get("timestamp", timezone.now().isoformat())
            ).strftime("%b %d %H:%M:%S")
            hostname = "hcms-hr"
            tag = "HCMS-AUDIT"
            message = (
                f"{log.get('username', 'unknown')} "
                f"[{log.get('module', 'N/A')}] "
                f"{log.get('action', 'ACTION')} "
                f"{log.get('object_type', 'N/A')} "
                f"ID:{log.get('object_id', 'N/A')} "
                f"Details: {log.get('details', '')}"
            )

            syslog_record = f"<{pri}>{timestamp} {hostname} {tag}: {message}"
            syslog_records.append(syslog_record)

        return "\n".join(syslog_records)

    def generate_csv_format(self, audit_logs):
        """Generate CSV format SIEM export"""
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "timestamp",
                "user_id",
                "username",
                "action",
                "module",
                "object_type",
                "object_id",
                "status",
                "details",
                "ip_address",
                "company",
            ],
        )

        writer.writeheader()

        for log in audit_logs:
            writer.writerow(
                {
                    "timestamp": log.get("timestamp"),
                    "user_id": log.get("user_id"),
                    "username": log.get("username"),
                    "action": log.get("action"),
                    "module": log.get("module"),
                    "object_type": log.get("object_type"),
                    "object_id": log.get("object_id"),
                    "status": log.get("status"),
                    "details": log.get("details"),
                    "ip_address": log.get("ip_address"),
                    "company": log.get("company_name"),
                }
            )

        return output.getvalue()

    def export_to_siem(self, audit_logs):
        """
        Export logs to SIEM system
        """
        config = SIEMConfig.objects.filter(company=self.company).first()
        if not config:
            self.status = "failed"
            self.siem_response_message = "No SIEM configuration found"
            self.save()
            return False

        # Generate appropriate format
        if config.export_format == "cef":
            content = self.generate_cef_format(audit_logs)
        elif config.export_format == "json":
            content = self.generate_json_format(audit_logs)
        elif config.export_format == "syslog":
            content = self.generate_syslog_format(audit_logs)
        else:  # csv
            content = self.generate_csv_format(audit_logs)

        self.export_content = content

        try:
            if config.siem_type == "generic":
                # Send via syslog
                import socket

                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(content.encode(), (config.syslog_host, config.syslog_port))
                sock.close()
                self.status = "exported"
                self.siem_response_code = 200
            else:
                # Send to API endpoint
                import requests

                headers = {}
                if config.api_token:
                    headers["Authorization"] = f"Bearer {config.api_token}"
                elif config.api_key:
                    headers["X-API-Key"] = config.api_key

                response = requests.post(
                    config.export_endpoint, data=content, headers=headers, timeout=30
                )

                self.siem_response_code = response.status_code
                if response.status_code < 400:
                    self.status = "exported"
                    self.siem_response_message = "Success"
                else:
                    self.status = "failed"
                    self.siem_response_message = response.text[:500]

            self.exported_at = timezone.now()
            self.save()
            return self.status == "exported"

        except Exception as e:
            self.status = "failed"
            self.siem_response_message = str(e)[:500]
            self.last_retry = timezone.now()
            self.retry_count += 1
            self.save()
            return False


class SIEMExportSchedule(models.Model):
    """
    Schedule for automatic SIEM exports
    """

    FREQUENCY_CHOICES = [
        ("hourly", _("Hourly")),
        ("daily", _("Daily")),
        ("weekly", _("Weekly")),
        ("monthly", _("Monthly")),
    ]

    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name="siem_export_schedule"
    )

    is_enabled = models.BooleanField(default=True)
    frequency = models.CharField(
        max_length=50, choices=FREQUENCY_CHOICES, default="daily"
    )

    # Schedule timing
    run_time = models.TimeField(default="02:00", help_text=_("Time to run export"))
    day_of_week = models.IntegerField(
        default=0, help_text=_("For weekly: 0=Monday, 6=Sunday")
    )
    day_of_month = models.IntegerField(default=1, help_text=_("For monthly: 1-28"))

    # Last execution
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    last_run_status = models.CharField(
        max_length=20,
        choices=[("success", "Success"), ("failed", "Failed")],
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "audit_siem_export_schedule"
        verbose_name = _("SIEM Export Schedule")

    def __str__(self):
        return f"SIEM Schedule - {self.company}"
