from django.urls import path

from .views import DashboardTemplateView


app_name = 'dashboards'


urlpatterns = [
    path(
        '',
        DashboardTemplateView.as_view(),
        name='home'
    ),
]
