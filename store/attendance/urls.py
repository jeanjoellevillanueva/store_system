from django.urls import path

from .views import AttendanceTemplateView


app_name = 'attendance'


urlpatterns = [
    path(
        '',
        AttendanceTemplateView.as_view(),
        name='home'
    ),
]