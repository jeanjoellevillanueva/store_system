from django.shortcuts import render

# Create your views here.

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class AttendanceTemplateView(LoginRequiredMixin, TemplateView):
    """
    Dashboard for Attendance
    """
    
    template_name = 'attendance/home.html'
