import json
from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.generic import View

from .forms import PayslipForm


class PayslipCustomCreateView(LoginRequiredMixin, View):
    """
    Saving payslip into tables
    """
    def post(self, request, *args, **kwargs):
        form = PayslipForm(request.POST)
        import pdb; pdb.set_trace()
