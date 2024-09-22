import json
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
                .values_list('employee__username', 'task', 'time_in')
        )
        calendar_data = [
            {
                'title': f'{dict(Attendance.TASK_CHOICES)[task]} - {employee}',
                'start': time_in.strftime('%Y-%m-%d')
            }
            for employee, task, time_in in attendances
        ]
        context['calendar_data'] = json.dumps(calendar_data)
        return context
