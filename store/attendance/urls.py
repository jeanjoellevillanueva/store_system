from django.urls import path

from .views import AttendanceComponentTemplateView
from .views import AttendanceCustomCreateView
from .views import AttendanceCustomUpdateView


app_name = 'attendance'


urlpatterns = [
    path(
        '',
        AttendanceComponentTemplateView.as_view(),
        name='component',
    ),
    path(
        'create/',
        AttendanceCustomCreateView.as_view(),
        name='create_attendance'
    ),
    path(
        'update/',
        AttendanceCustomUpdateView.as_view(), 
        name='update_attendance'
    ),
]
