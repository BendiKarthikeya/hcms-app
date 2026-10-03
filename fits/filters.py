"""
filters.py
"""

import hashlib
import uuid

import django_filters
from django import forms
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_filters.filterset import FILTER_FOR_DBFIELD_DEFAULTS

from base.methods import reload_queryset
from fits.fits_middlewares import _thread_locals
from fits_views.templatetags.generic_template_filters import getattribute

FILTER_FOR_DBFIELD_DEFAULTS[models.ForeignKey]["filter_class"] = (
    django_filters.ModelMultipleChoiceFilter
)


def filter_by_name(queryset, name, value):
    """
    Filter queryset by first name or last name.
    """
    # Split the search value into first name and last name
    parts = value.split()
    first_name = parts[0]
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    # Filter the queryset by first name and last name
    if first_name and last_name:
        queryset = queryset.filter(
            employee_id__employee_first_name__icontains=first_name,
            employee_id__employee_last_name__icontains=last_name,
        )
    elif first_name:
        queryset = queryset.filter(
            employee_id__employee_first_name__icontains=first_name
        )
    elif last_name:
        queryset = queryset.filter(employee_id__employee_last_name__icontains=last_name)

    return queryset


class FilterSet(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ensure queryset-backed fields are refreshed based on context
        # (company selection, active flags, etc.). This mutates
        # `field.queryset` for ModelChoiceFields.
        reload_queryset(self.form.fields)

        # Cache the evaluated choices for queryset-backed fields.
        # This prevents N repeated DB round-trips (one per FK field) on every
        # filter-panel render. The cache key uses the queryset SQL so different
        # filters get separate cache entries. TTL = 120s matches other caches.
        for fname, fld in self.form.fields.items():
            if not hasattr(fld, "queryset"):
                continue
            try:
                qs_hash = hashlib.md5(
                    str(fld.queryset.query).encode(), usedforsecurity=False
                ).hexdigest()
                cache_key = f"flt_ch_{qs_hash}"
                cached = cache.get(cache_key)
                if cached is not None:
                    fld.choices = cached
                else:
                    evaluated = list(fld.choices)
                    cache.set(cache_key, evaluated, 120)
                    fld.choices = evaluated
            except Exception:
                pass

        default_input_class = "oh-input w-100"
        select_class = "oh-select oh-select-2"
        checkbox_class = "oh-switch__checkbox"

        for field_name, field in self.form.fields.items():
            widget = field.widget
            label = _(field.label) if field.label else ""

            # Date field
            if isinstance(widget, forms.DateInput):
                widget.input_type = "date"
                widget.format = "%Y-%m-%d"
                field.input_formats = ["%Y-%m-%d"]

                existing_class = widget.attrs.get("class", default_input_class)
                widget.attrs.update(
                    {
                        "class": f"{existing_class} form-control",
                        "placeholder": label,
                    }
                )

            # Time field
            elif isinstance(widget, forms.TimeInput):
                widget.input_type = "time"
                widget.format = "%H:%M"
                field.input_formats = ["%H:%M"]

                existing_class = widget.attrs.get("class", default_input_class)
                widget.attrs.update(
                    {
                        "class": f"{existing_class} form-control",
                        "placeholder": label,
                    }
                )

            # Number, Email, Text, File, URL fields
            elif isinstance(
                widget,
                (
                    forms.NumberInput,
                    forms.EmailInput,
                    forms.TextInput,
                    forms.FileInput,
                    forms.URLInput,
                ),
            ):
                existing_class = widget.attrs.get("class", default_input_class)
                widget.attrs.update(
                    {
                        "class": f"{existing_class} form-control",
                        "placeholder": _(field.label.title()) if field.label else "",
                    }
                )

            # Select fields
            elif isinstance(widget, forms.Select):
                if not isinstance(field, forms.ModelMultipleChoiceField):
                    field.empty_label = _("---Choose {label}---").format(label=label)
                existing_class = widget.attrs.get("class", select_class)
                widget.attrs.update(
                    {
                        "class": existing_class,
                        "id": str(uuid.uuid4()),
                    }
                )

            # Textarea
            elif isinstance(widget, forms.Textarea):
                existing_class = widget.attrs.get("class", default_input_class)
                widget.attrs.update(
                    {
                        "class": f"{existing_class} form-control",
                        "placeholder": label,
                        "rows": 2,
                        "cols": 40,
                    }
                )

            # Checkbox types
            elif isinstance(
                widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)
            ):
                existing_class = widget.attrs.get("class", checkbox_class)
                widget.attrs.update({"class": existing_class})


class FitsPaginator(Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_count = 0
        self.end_count = 0

    def get_page(self, number):
        self.page = super().get_page(number)
        self.page.start_count = (
            1
            if number == 1 or number is None
            else max((int(number) - 1) * self.per_page + 1, 1)
        )
        self.page.end_count = (
            min(int(number) * self.per_page, self.count)
            if number and int(number) > 1
            else self.per_page
        )
        return self.page


class FitsFilterSet(FilterSet):
    """
    FitsFilterSet
    """

    verbose_name: dict = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.verbose_name.items():
            self.form.fields[key].label = value

        request = getattr(_thread_locals, "request", None)
        if request:
            setattr(request, "is_filtering", True)

    def search_in(self, queryset, name, value):
        """
        Search in generic method for filter field
        """
        search = self.data.get("search", "")
        search_field = self.data.get("search_field")
        if not search_field:
            search_field = self.filters[name].field_name

        def _icontains(instance):
            result = str(getattribute(instance, search_field)).lower()
            return instance.pk if search in result else None

        ids = list(filter(None, map(_icontains, queryset)))
        return queryset.filter(id__in=ids)
