from django.urls import path

from .views import LoginView
from .views import logout_view

from .views import AccountComponentTemplateView
from .views import AccountCustomCreateView
from .views import AccountCustomDeleteView
from .views import AccountCustomUpdateView
from .views import AccountListDatatableTemplateView
from .views import EmailEnrollmentView
from .views import OTPVerificationView
from .views import ResendOTPView
from .views import RegistrationView

app_name = 'accounts'

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(),
        name='login'
    ),
    path(
        'email-enrollment/',
        EmailEnrollmentView.as_view(),
        name='email_enrollment',
        ),
    path(
        'otp/',
        OTPVerificationView.as_view(),
        name='otp_verify',
    ),
    path(
        'otp/resend/',
        ResendOTPView.as_view(),
        name='otp_resend',
    ),
    path(
        'logout/',
        logout_view,
        name='logout'
    ),
    path(
        '',
        AccountComponentTemplateView.as_view(),
        name='home'
    ),
    path(
        'accounts/list/',
        AccountListDatatableTemplateView.as_view(),
        name='list_account'
    ),
    path(
        'create/',
        AccountCustomCreateView.as_view(),
        name='create_account'
    ),
    path(
        'delete/<int:id>/',
        AccountCustomDeleteView.as_view(),
        name='delete_account'
    ),
    path(
        'update/<int:id>/',
        AccountCustomUpdateView.as_view(),
        name='update_account'
    ),
    path(
        'register/',
        RegistrationView.as_view(),
        name='register'
    )
]
