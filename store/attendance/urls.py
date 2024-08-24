from django.urls import path

from .views import AttendanceTemplateView
from .views import AttendanceCustomCreateView

app_name = 'attendance'


urlpatterns = [
    path(
        '',
        AttendanceTemplateView.as_view(),
        name='home'
    ),
   path(
        'create/',
        AttendanceCustomCreateView.as_view(),
        name='create_attendance'
    ),
]