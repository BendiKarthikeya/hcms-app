from django.db import models


class LeaveType(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "leave"

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    class Meta:
        app_label = "leave"
