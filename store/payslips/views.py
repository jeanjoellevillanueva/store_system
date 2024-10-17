from datetime import date
from io import BytesIO
from typing import Any
import json

from braces.views import JSONResponseMixin

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.generic import View

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

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
                payslips = Payslip()
                # If form is valid then continue to save to the database.
                payslips.employee = form.cleaned_data['employee']
                payslips.start_date = form.cleaned_data['start_date']
                payslips.end_date = form.cleaned_data['end_date']
                payslips.base_pay = form.cleaned_data['base_pay']
                payslips.rate = form.cleaned_data['rate']
                payslips.created_by = request.user
                payslips.created_date = date.today()
                payslips.save()

                # Prepare the data you want to return in JSON
                payslip_data = {
                'employee': form.cleaned_data['employee'],
                'start_date': str(form.cleaned_data['start_date']),
                'end_date': str(form.cleaned_data['end_date']),
                'base_pay': str(form.cleaned_data['base_pay']),
                'rate': str(form.cleaned_data['rate']),
                }

                json_data = {
                    'status': 'success',
                    'message': 'Payslip successfully created.',
                    'payslip_data': payslip_data,
                    }
                return self.generate_payslip(payslip_data)

        json_data = {'status': 'error', 'errors': form.errors}
        return self.render_json_response(json_data, status=400)
    

    """
    Downloading Payslip into PDF
    """
    def generate_payslip(self, payslip_data, file_name='payslip.pdf'):
        # Generate the PDF logic (same as before)
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        # Table data
        data = [
            ['Employee:', payslip_data['employee']],
            ['Start Date:', payslip_data['start_date']],
            ['End Date:', payslip_data['end_date']],
            ['Base Pay:', payslip_data['base_pay']],
            ['Rate:', payslip_data['rate']],
        ]

        # Create and style the table
        table = Table(data, colWidths=[2.5 * inch, 3.0 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)


        doc.build(elements)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        
        return response
