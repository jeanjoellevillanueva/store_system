from django.contrib import admin
from .models import Attendance


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'task', 'time_in', 'time_out')
    list_filter = ('task', 'time_in', 'time_out')
    search_fields = ('employee__username',)

admin.site.register(Attendance, AttendanceAdmin)
