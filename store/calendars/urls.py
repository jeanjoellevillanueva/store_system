from django.urls import path

from .views import CalendarComponentTemplateView
from .views import CalendarTemplateView


app_name = 'calendars'


urlpatterns = [
    path(
        '',
        CalendarTemplateView.as_view(),
        name='home'
    ),
    path(
        'calendar/',
        CalendarComponentTemplateView.as_view(),
        name='component'
    ),
]
