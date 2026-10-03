from django import template

try:
    from leave.models import LeaveGeneralSetting
except ImportError:
    LeaveGeneralSetting = None

register = template.Library()


@register.filter(name="is_compensatory")
def is_compensatory(user):
    try:
        if LeaveGeneralSetting and LeaveGeneralSetting.objects.exists():
            return LeaveGeneralSetting.objects.first().compensatory_leave
    except Exception:
        pass
    return False
