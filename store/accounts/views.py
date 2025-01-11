import datetime
from pytz import timezone
from typing import Any
from typing import Dict

import pandas as pd
from braces.views import JSONResponseMixin

from django.conf import settings
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
from .models import Employee


class LoginView(FormView):
    """
    View used for logging in.
    """

    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        if not self.request.user.is_staff:
            self.success_url = reverse_lazy('calendars:home')
        return super().form_valid(form)


def logout_view(request):
    """
    View used for logging out the user.
    """
    logout(request)
    return redirect(reverse_lazy('accounts:login'))


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
