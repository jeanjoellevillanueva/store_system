import json
from typing import Any
from datetime import datetime, date

from braces.views import JSONResponseMixin

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.views import View
from django.views.generic import TemplateView

from generics.models.utils import get_or_none

from .models import Attendance


class AttendanceComponentTemplateView(LoginRequiredMixin, TemplateView):
    """
    Renders the attendance component.
    """
    template_name = 'attendance/component/attendance.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        attendance = get_or_none(
            Attendance,
            employee=self.request.user,
            time_in__date=datetime.now().date()
        )
        if attendance:
            task_selected = attendance.task
        else:
            task_selected = ''
        context['attendance'] = attendance
        context['task_selected'] = task_selected
        context['task_choices'] = Attendance.TASK_CHOICES
        context['date_today'] = datetime.now().date()
        return context


class AttendanceCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when creating attendance.
    """
    def post(self, request, *args, **kwargs):
        body = self.request.body
        data = json.loads(body)
        # Check if the attendance is already created. If yes we need to raise an error.
        is_attendance = get_or_none(
            Attendance,
            employee=self.request.user,
            time_in__date=datetime.now().date()
        )
        if not data['task']:
            raise ValidationError('Please select a task.')
        if is_attendance:
            raise ValidationError('Attendance for today has already been created.')

        # Otherwise, let's create an attendance for the user.
        attendance = Attendance.objects.create(
            employee=request.user,
            task=data['task'],
            time_in=datetime.now()
        )
        json_data = {
            'status': 'success',
            'message': 'Time-In successfully created.'
        }
        return self.render_json_response(json_data, status=201)


class AttendanceCustomUpdateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when timing out of attendance.
    """

    def post(self, request, *args, **kwargs):
        body = self.request.body
        data = json.loads(body)
        attendance=Attendance.objects.filter(
            employee=self.request.user,
            time_in__date=date.today(),
            time_out__isnull=True
        ).last()
        attendance.time_out=datetime.now()
        attendance.save()
        json_data = {
            'status': 'success',
            'message': 'Time-Out successfully.'
        }
        return self.render_json_response(json_data, status=201)
