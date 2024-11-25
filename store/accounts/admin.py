from django.contrib import admin

from .models import Employee


class EmployeeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Employee._meta.fields]
    search_fields = ('employee__username',)

admin.site.register(Employee, EmployeeAdmin)
