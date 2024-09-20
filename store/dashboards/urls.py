from django.urls import path

from .views import ChartTemplateView
from .views import DashboardSummaryTemplateView
from .views import DashboardTemplateView


app_name = 'dashboards'


urlpatterns = [
    path(
        '',
        DashboardTemplateView.as_view(),
        name='home'
    ),
    path(
        'summary/',
        DashboardSummaryTemplateView.as_view(),
        name='dashboard_summary'
    ),
    path(
        'chart/',
        ChartTemplateView.as_view(),
        name='chart'
    ),
]
