from django.urls import path

from .views import PayslipCustomCreateView

app_name = 'payslip'


urlpatterns = [
    path(
        'create/',
        PayslipCustomCreateView.as_view(),
        name='create_payslip'
    ),
]
