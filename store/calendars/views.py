import json
import pytz
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import TemplateView

from attendance.models import Attendance


class CalendarTemplateView(LoginRequiredMixin, TemplateView):
    """
    Renders the home page for calendar.
    """
    template_name = 'calendars/home.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.values('id', 'username')
        return context


class CalendarComponentTemplateView(LoginRequiredMixin, TemplateView):
    """
    Loads the calendar component.
    """
    template_name = 'calendars/component/calendar.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        employee_number = self.request.GET.get('employee')
        filters = {}
        if not self.request.user.is_superuser:
            filters['employee'] = self.request.user
        if employee_number:
            filters['employee__id'] = int(employee_number)
        attendances = (
            Attendance.objects
                .filter(**filters)
                .order_by('id')
                .values_list('employee__username', 'task', 'time_in', 'time_out')
        )
        manila_tz = pytz.timezone('Asia/Manila')
        calendar_data = [
            {
                'title': f'{employee} - {Attendance.get_task_display(task)} '
                        f'({time_in.astimezone(manila_tz).strftime("%I:%M:%S %p") if time_in else "N/A"} - '
                        f'{time_out.astimezone(manila_tz).strftime("%I:%M:%S %p") if time_out else "N/A"})',
                'start': time_in.astimezone(manila_tz).strftime('%Y-%m-%d') if time_in else 'N/A'
            }
            for employee, task, time_in, time_out in attendances
        ]
        context['calendar_data'] = json.dumps(calendar_data)
        return context
