from django.urls import path

from .views import PayslipCustomCreateView
from .views import PayslipTemplateView

app_name = 'payslip'


urlpatterns = [
    path(
        '',
        PayslipTemplateView.as_view(),
        name='home'
    ),

    path(
        'create/',
        PayslipCustomCreateView.as_view(),
        name='create_payslip'
    ),
]
