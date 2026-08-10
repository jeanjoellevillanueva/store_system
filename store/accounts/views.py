import datetime
from pytz import timezone
from typing import Any
from typing import Dict

import pandas as pd
from braces.views import JSONResponseMixin

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic import FormView

from .forms import LoginForm
from .forms import EmployeeForm
from .forms import UserForm
from .forms import EmailEnrollmentForm
from .forms import OTPVerificationForm

from .models import Employee
from .models import EmailOTP

from .services import(
    OTPAttemptsExceeded,
    OTPEmailAlreadyInUse,
    OTPEmailInvalid,
    OTPEmailRequired,
    OTPExpired,
    OTPInvalidCode,
    OTPNotAvailable,
    OTPResendTooSoon,
    issue_email_enrollment_otp,
    issue_login_otp,
    verify_email_enrollment_otp,
    verify_login_otp,
)

PENDING_OTP_USER_ID_SESSION_KEY = 'pending_otp_user_id'
PENDING_OTP_PURPOSE_SESSION_KEY = 'pending_otp_purpose'


def clear_pending_otp(request):
    """Remove the temporary pre-authentication state from the session"""
    request.session.pop(PENDING_OTP_USER_ID_SESSION_KEY, None)
    request.session.pop(PENDING_OTP_PURPOSE_SESSION_KEY, None)

def get_pending_otp_user(request):
    """Return the active user stored during password verification, if any."""
    user_id = request.session.get(PENDING_OTP_USER_ID_SESSION_KEY)

    if not user_id:
        return None

    return User.objects.filter(pk=user_id, is_active=True).first()


class LoginView(FormView):
    """
    Verify the password, then start OTP Verification.

    This view never calls login(); Django creates the authenticated session
    only after OTP is verified.
    """

    template_name = 'login.html'
    form_class = LoginForm 

    def form_valid(self, form):
        user = form.get_user()

        # Replace any anonymous session identifier before storing pre-auth state.
        self.request.session.cycle_key()
        self.request.session[PENDING_OTP_USER_ID_SESSION_KEY] = user.pk

        if user.email:
            self.request.session[
                PENDING_OTP_PURPOSE_SESSION_KEY
            ] = EmailOTP.Purpose.LOGIN
            issue_login_otp(user)
            return redirect('accounts:otp_verify')

        self.request.session[
            PENDING_OTP_PURPOSE_SESSION_KEY
        ] = EmailOTP.Purpose.EMAIL_ENROLLMENT
        return redirect('accounts:email_enrollment')

def logout_view(request):
    """Log out the current user."""
    logout(request)
    return redirect(reverse_lazy('accounts:login'))

class EmailEnrollmentView(FormView):
    """Collect and verify an email address for a legacy username user."""

    template_name = 'accounts/email_enrollment.html'
    form_class = EmailEnrollmentForm

    def dispatch(self, request, *args, **kwargs):
        self.pending_user = get_pending_otp_user(request)
        purpose = request.session.get(PENDING_OTP_PURPOSE_SESSION_KEY)

        if (
            self.pending_user is None
            or purpose != EmailOTP.Purpose.EMAIL_ENROLLMENT
            or self.pending_user.email
        ):
            clear_pending_otp(request)
            return redirect('accounts:login')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            issue_email_enrollment_otp(
                self.pending_user,
                form.cleaned_data['email'],
            )
        except (
            OTPEmailRequired,
            OTPEmailInvalid,
            OTPEmailAlreadyInUse,
            OTPResendTooSoon,
        ) as error:
            form.add_error('email', str(error))
            return self.form_invalid(form)

        return redirect('accounts:otp_verify')


class OTPVerificationView(FormView):
    """Verify an OTP and create the Django session only on success."""

    template_name = 'accounts/otp_verify.html'
    form_class = OTPVerificationForm

    def dispatch(self, request, *args, **kwargs):
        self.pending_user = get_pending_otp_user(request)
        self.purpose = request.session.get(PENDING_OTP_PURPOSE_SESSION_KEY)

        if (
            self.pending_user is None
            or self.purpose not in (
                EmailOTP.Purpose.LOGIN,
                EmailOTP.Purpose.EMAIL_ENROLLMENT,
            )
        ):
            clear_pending_otp(request)
            return redirect('accounts:login')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            if self.purpose == EmailOTP.Purpose.LOGIN:
                verify_login_otp(self.pending_user, form.cleaned_data['code'])
            else:
                verify_email_enrollment_otp(
                    self.pending_user,
                    form.cleaned_data['code'],
                )
        except (
            OTPNotAvailable,
            OTPExpired,
            OTPInvalidCode,
            OTPAttemptsExceeded,
            OTPEmailAlreadyInUse,
        ) as error:
            form.add_error('code', str(error))
            return self.form_invalid(form)

        self.pending_user.refresh_from_db()
        login(self.request, self.pending_user)
        clear_pending_otp(self.request)

        if self.pending_user.is_staff:
            return redirect('dashboards:home')

        return redirect('calendars:home')

class ResendOTPView(View):
    """Resend the active OTP while preserving the service cooldown rule."""

    def post(self, request, *args, **kwargs):
        pending_user = get_pending_otp_user(request)
        purpose = request.session.get(PENDING_OTP_PURPOSE_SESSION_KEY)

        if pending_user is None or purpose is None:
            clear_pending_otp(request)
            return redirect('accounts:login')

        try:
            if purpose == EmailOTP.Purpose.LOGIN:
                issue_login_otp(pending_user)
            elif purpose == EmailOTP.Purpose.EMAIL_ENROLLMENT:
                active_otp = (
                    EmailOTP.objects.filter(
                        user=pending_user,
                        purpose=purpose,
                        consumed_at__isnull=True,
                        invalidated_at__isnull=True,
                    )
                    .order_by('-created_at')
                    .first()
                )

                if active_otp is None:
                    messages.error(
                        request,
                        'Enter your email address to request a new code.',
                    )
                    return redirect('accounts:email_enrollment')

                issue_email_enrollment_otp(pending_user, active_otp.email)
            else:
                clear_pending_otp(request)
                return redirect('accounts:login')
        except OTPResendTooSoon as error:
            messages.error(request, str(error))
        else:
            messages.success(request, 'A new verification code has been sent')

        return redirect('accounts:otp_verify')
        

class AccountComponentTemplateView(LoginRequiredMixin, JSONResponseMixin, TemplateView):
    """
    Creating User Account, Employee, Admin for Galinduh Web App
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['employee_form'] = EmployeeForm(initial={'base_pay': 0})
        context['user_form'] = UserForm
        context['update_employee_form'] = EmployeeForm(auto_id='id_%s_update')
        context['update_user_form'] = UserForm(auto_id='id_%s_update')
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_form'] = EmployeeForm(initial={'base_pay': 0})
        context['user_form'] = UserForm
        context['update_employee_form'] = EmployeeForm(auto_id='id_%s_update')
        context['update_user_form'] = UserForm(auto_id='id_%s_update')
        return self.render_to_response(context)


class AccountListDatatableTemplateView(LoginRequiredMixin, TemplateView):
    """
    List of all account user.
    """
    template_name = 'accounts/datatables/accounts.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        users = list(User.objects.values().order_by('is_superuser', 'first_name'))
        employees = list(Employee.objects.values('user_id', 'base_pay', 'designation', 'department'))
        for user in users:
            for employee in employees:
                if user['id'] == employee['user_id']:
                    user.update(employee)
        context['users'] = users
        return context


class AccountCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    Creating User Account, Employee, Admin for Galinduh Web App.
    """
    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST)
        employee_form = EmployeeForm(request.POST)
        if user_form.is_valid() and employee_form.is_valid():
            with transaction.atomic():
                accounts = User.objects.values('username')
                user = user_form.cleaned_data
                employee = employee_form.cleaned_data
                if not accounts.filter(username=user['username']).exists():
                    user.update({'date_joined': datetime.datetime.now(timezone('Asia/Manila'))})
                    User.objects.create_user(**user)
                    employee.update({
                        'user_id': User.objects.filter(username=user['username'])
                        .values_list('id',flat=True)
                        .get()
                    })
                    Employee.objects.create(**employee)
                    json_data = {
                        'status': 'success',
                        'message': 'Account successfully created.'
                    }
                    return self.render_json_response(json_data, status=201)
        if employee_form.errors:
            user_form.errors.update(employee_form.errors)
        json_data = {
            'status': 'error',
            'errors': user_form.errors
        }
        return self.render_json_response(json_data, status=400)


class AccountCustomDeleteView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    Deleting User Account, Employee, Admin.
    """
    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=self.kwargs['id'])
        except Exception as e:
             # Object not found
             return self.render_json_response({'message': str(e)}, status=404)
        user.delete()
        json_data = {
            'message': 'Account Successfully deleted'
        }
        return self.render_json_response(json_data, status=204)


class AccountCustomUpdateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    Updating User Account, Employee, Admin.
    """
    def post(self, request, *args, **kwargs):
        account = User.objects.get(id=self.kwargs['id'])
        update_user_form = UserForm(request.POST, instance=account)
        update_employee_form = EmployeeForm(request.POST)
        if update_user_form.is_valid() and update_employee_form.is_valid():
            with transaction.atomic():
                account_data = update_user_form.cleaned_data
                employee_data = update_employee_form.cleaned_data
                # User update
                account.username = account_data['username']
                account.set_password(account_data['password'])
                account.email = account_data['email']
                account.first_name = account_data['first_name']
                account.last_name = account_data['last_name']
                account.is_staff = account_data['is_staff']
                account.is_superuser = account_data['is_superuser']
                account.save()
                # Employee update
                if Employee.objects.filter(user__id=self.kwargs['id']).exists():
                    employee = Employee.objects.get(user__id=self.kwargs['id'])
                    employee.base_pay = employee_data['base_pay']
                    employee.designation = employee_data['designation']
                    employee.department = employee_data['department']
                    employee.save()
                else:
                    employee_data.update({
                        'user_id': self.kwargs['id']
                    })
                    Employee.objects.create(**employee_data)
                json_data = {
                    'status': 'success',
                    'message': 'Updated successfully.'
                }
                return self.render_json_response(json_data, status=200)
        if update_employee_form.errors:
            update_user_form.errors.update(update_employee_form.errors)
        json_data = {
            'status': 'error',
            'errors': update_user_form.errors
        }
        return self.render_json_response(json_data, status=400)