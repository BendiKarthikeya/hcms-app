from datetime import date, timedelta

from django.conf import settings


def get_trial_start_date():
    configured_start = getattr(settings, "TRIAL_START_DATE", "")
    if not configured_start:
        return None
    return date.fromisoformat(configured_start)


def get_trial_duration_days():
    return int(getattr(settings, "TRIAL_DURATION_DAYS", 30))


def get_trial_end_date():
    start_date = get_trial_start_date()
    if start_date is None:
        return None
    return start_date + timedelta(days=get_trial_duration_days())


def is_trial_mode_enabled():
    return bool(getattr(settings, "TRIAL_MODE", False))


def is_trial_expired(today=None):
    if not is_trial_mode_enabled():
        return False

    trial_end_date = get_trial_end_date()
    if trial_end_date is None:
        return False

    if today is None:
        today = date.today()

    return today > trial_end_date
