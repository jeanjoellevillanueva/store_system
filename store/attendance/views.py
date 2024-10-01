import json
from decimal import Decimal

import pytz
from typing import Any

from braces.views import JSONResponseMixin

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from generics.models.utils import get_or_none

from .forms import OvertimeForm
from .forms import OvertimeUpdateForm
from .models import Attendance
from .models import Overtime


class AttendanceComponentTemplateView(LoginRequiredMixin, TemplateView):
    """
    Renders the attendance component.
    """
    template_name = 'attendance/component/attendance.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        manila_tz = pytz.timezone('Asia/Manila')
        manila_now = timezone.now().astimezone(manila_tz)
        attendance = get_or_none(
            Attendance,
            employee=self.request.user,
            time_in__date=manila_now.date()
        )
        if attendance:
            task_selected = attendance.task
        else:
            task_selected = ''
        context['attendance'] = attendance
        context['task_selected'] = task_selected.split(',')
        context['task_choices'] = Attendance.TASK_CHOICES
        context['date_today'] = manila_now.date()
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
            time_in__date=timezone.now().astimezone(
                pytz.timezone('Asia/Manila')
            ).date()
        )
        if not data['task']:
            raise ValidationError('Please select a task.')
        if is_attendance:
            raise ValidationError('Attendance for today has already been created.')

        tasks = ','.join(data['task'])
        # Otherwise, let's create an attendance for the user.
        attendance = Attendance.objects.create(
            employee=request.user,
            task=tasks,
            time_in=timezone.now()
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
        attendance = Attendance.objects.get(
            employee=self.request.user,
            time_in__date=timezone.now().astimezone(
                pytz.timezone('Asia/Manila')
            ).date(),
            time_out__isnull=True
        )
        if not data['task']:
            raise ValidationError('Please select a task.')
        tasks = ','.join(data['task'])
        attendance.task = tasks
        attendance.save()
        json_data = {
            'status': 'success',
            'message': 'Updated successfully.'
        }
        return self.render_json_response(json_data, status=200)


class AttendanceTimeoutView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when timing out of attendance.
    """

    def post(self, request, *args, **kwargs):
        body = self.request.body
        attendance = Attendance.objects.get(
            employee=self.request.user,
            time_in__date=timezone.now().astimezone(
                pytz.timezone('Asia/Manila')
            ).date(),
            time_out__isnull=True
        )
        attendance.time_out=timezone.now()
        attendance.save()
        json_data = {
            'status': 'success',
            'message': 'Time-Out successfully.'
        }
        return self.render_json_response(json_data, status=200)


class OvertimeCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    Responsible in creating overtime objects.
    """

    def post(self, request, *args, **kwargs):
        
        user_form_data = {
            'user' : request.user,
            'date' : request.POST['date'],
            'tasks' : request.POST.getlist('tasks'),
            'hours' : request.POST['hours'],
        }
        form = OvertimeForm(user_form_data)
        if form.is_valid():
            overtime_data = {
                'employee': self.request.user,
                'date': form.cleaned_data['date'],
                'hours': form.cleaned_data['hours'],
                'task': ','.join(form.cleaned_data['tasks'])
            }
            Overtime.objects.create(**overtime_data)
            json_data = {
                'status': 'success',
                'message': 'Overtime created successfully.',
            }
            return self.render_json_response(json_data, status=201)
        else:
            json_data = {
                'status': 'error',
                'message': 'Validation failed.',
                'errors': form.errors
            }
            return self.render_json_response(json_data, status=400)


class OvertimeCustomUpdateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    Updating overtime objects
    """

    def post(self, request, *args, **kwargs):
        form = OvertimeUpdateForm(request.POST)
        if form.is_valid():
            primary_key = self.request.POST['primary_key']
            overtime = Overtime.objects.get(id=int(primary_key))
            hours = form.cleaned_data['hours'],
            task = ','.join(form.cleaned_data['tasks'])
            overtime.hours = hours[0]
            overtime.task = task
            overtime.save()
            json_data = {
                'status': 'success',
                'message': 'Overtime updated successfully.',
            }
            return self.render_json_response(json_data, status=201)
        else:
            json_data = {
                'status': 'error',
                'message': 'Validation failed.',
                'errors': form.errors
            }
            return self.render_json_response(json_data, status=400)


class OvertimeCustomDeleteView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    Delete overtime objects
    """

    def post(self, request, *args, **kwargs):
            primary_key = self.request.POST['primary_key']
            overtime = Overtime.objects.get(id=int(primary_key))
            overtime.delete()
            json_data = {
                'status': 'success',
                'message': 'Overtime deleted successfully.',
            }
            return self.render_json_response(json_data, status=204)
