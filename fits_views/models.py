from django.contrib.auth.models import User
from django.db import models

from fits.fits_middlewares import _thread_locals
from fits.models import FitsModel

# Create your models here.


class ToggleColumn(FitsModel):
    """
    ToggleColumn
    """

    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_excluded_column",
        editable=False,
    )
    path = models.CharField(max_length=256)
    excluded_columns = models.JSONField(default=list)

    def save(self, *args, **kwargs):
        request = getattr(_thread_locals, "request", {})
        user = request.user
        self.user_id = user
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.user_id.employee_get)


class ActiveTab(FitsModel):
    """
    ActiveTab
    """

    path = models.CharField(max_length=256)
    tab_target = models.CharField(max_length=256)


class ActiveGroup(FitsModel):
    """
    ActiveGroup
    """

    path = models.CharField(max_length=256)
    group_target = models.CharField(max_length=256)
    group_by_field = models.CharField(max_length=256)


class SavedFilter(FitsModel):
    """
    SavedFilter
    """

    title = models.CharField(max_length=20, null=True)
    color = models.CharField(max_length=10, default="")
    is_default = models.BooleanField(default=False)
    filter = models.TextField()
    urlencode = models.TextField(default="")
    path = models.CharField(max_length=256)
    referrer = models.CharField(max_length=256, default="")

    xss_exempt_fields = [
        "urlencode",
    ]

    def save(self, *args, **kwargs):
        SavedFilter.objects.filter(
            is_default=True, path=self.path, created_by=self.created_by
        ).exclude(id=self.pk).update(is_default=False)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.title)


class ActiveView(FitsModel):
    """
    This model to store the active view type for HNV
    """

    path = models.CharField(max_length=256)
    type = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
