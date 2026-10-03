from django.db import models


class DefaultAccessibility(models.Model):
    feature = models.CharField(max_length=100)
    employees = models.ManyToManyField("employee.Employee", blank=True)

    class Meta:
        app_label = "accessibility"
        managed = False
