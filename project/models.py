from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        app_label = "project"

    def __str__(self):
        return self.title
