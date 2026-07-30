from django.contrib import admin

from .models import Employee
from .models import EmailOTP


class EmployeeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Employee._meta.fields]
    search_fields = ('employee__username',)


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'purpose',
        'expires_at',
        'attempt_count',
        'sent_at',
        'consumed_at',
        'invalidated_at',
    )
    list_filter = (
        'purpose',
        'consumed_at',
        'invalidated_at',
    )
    search_fields = (
        'user__email',
        'user__username',
    )
    ordering = ('-created_at',)
    readonly_fields = (
        'user',
        'purpose',
        'expires_at',
        'attempt_count',
        'sent_at',
        'created_at',
        'consumed_at',
        'invalidated_at',
    )
    exclude = ('code_hash',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Employee, EmployeeAdmin)
