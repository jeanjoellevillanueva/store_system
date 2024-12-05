from typing import Any
from typing import Dict

import pandas as pd
from braces.views import JSONResponseMixin

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic import FormView

from .forms import LoginForm
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
    import pdb; pdb.set_trace()
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['employee_form'] = Employee
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        self.render_to_response(context)


class AccountListDatatableTemplateView(LoginRequiredMixin, TemplateView):
    """
    List of all account user
    """

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        users = User.objects.values('username', 'first_name', 'last_name', 'is_active', 'is_superuser', 'is_staff').order_by('is_superuser', 'name')
        for user in users:
            user['full_name'] = f"{user['first_name'] or ''} {user['last_name'] or ''}".strip()
        context['users'] = users
        return context


class AccountCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    Creating User Account, Employee, Admin for Galinduh Web App
    """



class AccountCustomDeleteView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    Updating User Account, Employee, Admin
    """



class AccountCustomUpdateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    Deleting User Account, Employee, Admin
    """
    
