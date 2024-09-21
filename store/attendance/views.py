import json
from typing import Any
from datetime import datetime, date

from braces.views import JSONResponseMixin

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from .models import Attendance


class AttendanceTemplateView(LoginRequiredMixin, TemplateView):
    """
    Dashboard for Attendance
    """

    template_name = 'attendance/home.html'

    # def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
    #     context = super().get_context_data(**kwargs)
    #     context['task_choices'] = Attendance.TASK_CHOICES
    #     try:
    #         context['attendance'] = Attendance.objects.get(
    #             employee=self.request.user,
    #             time_in__date=date.today(),
    #             # time_out__isnull=True
    #         )
    #     except ObjectDoesNotExist:
    #         context['attendance'] = None

    #     return context


class AttendanceCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when creating attendance.
    """
    def post(self, request, *args, **kwargs):
        body = self.request.body
        data = json.loads(body)
        attendance = Attendance.objects.get_or_create(
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
    