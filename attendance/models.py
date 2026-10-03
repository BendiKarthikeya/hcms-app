from django.db import models


class GraceTime(models.Model):
    allowed_time = models.DurationField(default=0)

    class Meta:
        app_label = "attendance"


class AttendanceLateComeEarlyOut(models.Model):
    class Meta:
        app_label = "attendance"


class AttendanceGeneralSetting(models.Model):
    time_runner = models.BooleanField(default=True)

    class Meta:
        app_label = "attendance"
