from django.contrib import admin
from .models import GraceTime, AttendanceLateComeEarlyOut, AttendanceGeneralSetting

admin.site.register(GraceTime)
admin.site.register(AttendanceLateComeEarlyOut)
admin.site.register(AttendanceGeneralSetting)

