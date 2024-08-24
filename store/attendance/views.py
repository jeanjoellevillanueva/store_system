from braces.views import JSONResponseMixin

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView

from .models import Attendance


class AttendanceTemplateView(LoginRequiredMixin, TemplateView):
    """
    Dashboard for Attendance
    """

    template_name = 'attendance/home.html'


class AttendanceCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when creating attendance.
    """

    def post(self, request, *args, **kwargs):
        attendance = Attendance.objects.create(employee=request.user, task='Task Description')
        json_data = {
            'status': 'success',
            'message': 'Expense successfully created.'
        }
        return self.render_json_response(json_data, status=201)


