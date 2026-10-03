"""
recruitment/forms_candidate_upload.py

Forms for the Candidate Dashboard CV upload flow (single + bulk).
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from recruitment.models import Recruitment, Stage


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_clean(d, initial) for d in data]
        return single_clean(data, initial)


class SingleCVUploadForm(forms.Form):
    name = forms.CharField(max_length=100, label=_("Candidate Name"))
    email = forms.EmailField(label=_("Email"))
    mobile = forms.CharField(max_length=15, required=False, label=_("Mobile"))
    resume = forms.FileField(label=_("Resume (PDF)"))
    recruitment_id = forms.ModelChoiceField(
        queryset=Recruitment.objects.filter(closed=False),
        required=False,
        label=_("Recruitment"),
    )
    stage_id = forms.ModelChoiceField(
        queryset=Stage.objects.all(),
        required=False,
        label=_("Stage"),
    )


class BulkCVUploadForm(forms.Form):
    files = MultipleFileField(label=_("CV Files"))
    recruitment_id = forms.ModelChoiceField(
        queryset=Recruitment.objects.filter(closed=False),
        required=False,
        label=_("Recruitment"),
    )
    stage_id = forms.ModelChoiceField(
        queryset=Stage.objects.all(),
        required=False,
        label=_("Default Stage"),
    )
