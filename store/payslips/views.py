import json
from typing import Any

from braces.views import JSONResponseMixin

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.generic import View

from .forms import PayslipForm
from .models import Payslip

class PayslipTemplateView(LoginRequiredMixin, TemplateView):
    """
    Dashboard for Payslip
    """
    template_name = 'payslip/home.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        deduction_choices = ['Loan', 'Advance Payment', 'Wrong Shipment', 'Misc']
        context['deduction_choices'] = deduction_choices
        return context


class PayslipCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    Saving payslip into tables
    """
    def post(self, request, *args, **kwargs):
        form = PayslipForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                payslips = Payslip(
                    employee=form.cleaned_data['employee'],
                    start_date=form.cleaned_data['start_date'],
                    end_date=form.cleaned_data['end_date'],
                    base_pay=form.cleaned_data['base_pay'],
                    rate=form.cleaned_data['rate'],
                )
                payslips.save()
                import pdb; pdb.set_trace()
        json_data = {'status': 'error', 'errors': form.errors}
        return self.render_json_response(json_data, status=400)