import json
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.generic import TemplateView
from django.views import View


from attendance.forms import OvertimeForm
from attendance.forms import OvertimeUpdateForm
from attendance.models import Attendance
from payslips.forms import PayslipForm
from payslips.models import Payslip

from .calendars import get_calendar_data


class CalendarTemplateView(LoginRequiredMixin, TemplateView):
    """
    Renders the home page for calendar.
    """
    template_name = 'calendars/home.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['overtime_form'] = OvertimeForm(
            initial={
                'date': timezone.now().date().strftime('%B %d, %Y'),
                'hours': 0
            }
        )
        context['overtime_update_form'] = OvertimeUpdateForm(auto_id='id_%s_update')
        context['payslip_form'] = PayslipForm
        context['task_choices'] = Attendance.TASK_CHOICES
        context['users'] = User.objects.values('id', 'username')
        context['deduction_choices'] = Payslip.DEDUCTION_CHOICES
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
        calendar_data = get_calendar_data(filters)
        context['calendar_data'] = json.dumps(calendar_data)
        return context
