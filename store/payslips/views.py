from datetime import date
from io import BytesIO
from typing import Any
import ast
import json

from braces.views import JSONResponseMixin
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle


from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum
from django.http import FileResponse
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.generic import View

from attendance.models import Attendance
from attendance.models import Overtime

from .forms import PayslipForm
from .models import Payslip
from .utils import format_deductions
from .utils import GeneratePayslipView
from .utils import parse_deduction


class PayslipCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    Saving payslip into tables
    """
    def post(self, request, *args, **kwargs):
        form = PayslipForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                deductions = parse_deduction(request.POST)

                # If the value of added deduction is Null or '' = 0.0
                for deduction in deductions:
                    if not deduction['amount']:
                        deduction['amount'] = 0.0

                deduction_list = [(deduction['deduction_type'], deduction['amount']) for deduction in deductions]
                total_deductions = sum(float(deduction['amount']) for deduction in deductions if deduction['amount'])
                payslips = Payslip(
                    employee = form.cleaned_data['employee'],
                    start_date = form.cleaned_data['start_date'],
                    end_date = form.cleaned_data['end_date'],
                    base_pay = form.cleaned_data['base_pay'],
                    rate = form.cleaned_data['rate'],
                    deduction = deduction_list,
                    total_deduction = total_deductions,
                    created_by = request.user,
                    created_date = date.today(),
                )
                payslips.save()
                
                created_by = request.user.get_full_name()
                created_to = form.cleaned_data['employee'].get_full_name()

                deductions = format_deductions(deductions)
                
                attendance_data = Attendance.objects.filter(
                    employee_id=form.cleaned_data['employee'],
                    time_in__date__gte=form.cleaned_data['start_date'],
                    time_in__date__lte=form.cleaned_data['end_date'],
                ).count()
                
                overtime_data = Overtime.objects.filter(
                    employee_id=form.cleaned_data['employee'],
                    date__date__gte=form.cleaned_data['start_date'],
                    date__date__lte=form.cleaned_data['end_date'],
                    #is_approve=True
                ).aggregate(total_hours=Sum('hours'))

                overtime_hours = float(overtime_data['total_hours']) if overtime_data['total_hours'] else 0.0
                
                # Prepare the data you want to return in JSON
                payslip_data = {
                    'created_to': str(created_to),
                    'start_date': str(form.cleaned_data['start_date']),
                    'end_date': str(form.cleaned_data['end_date']),
                    'base_pay': str(form.cleaned_data['base_pay']),
                    'rate': str(form.cleaned_data['rate']),
                    'days': str(attendance_data),
                    'ot_hours': str(overtime_hours),
                    'deductions': str(deductions),
                    'total_deduction': str(total_deductions),
                    'created_by': str(created_by),
                }

                generate_payslip_view = GeneratePayslipView()
                buffer = generate_payslip_view.generate_payslip(payslip_data)
                response = FileResponse(
                    buffer, content_type='application/pdf'
                )
                start_date = form.cleaned_data['start_date'].strftime('%b-%d-%Y')
                end_date = form.cleaned_data['end_date'].strftime('%b-%d-%Y')
                file_name = f"{start_date} - {end_date}"
                response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                json_data = {
                    'status': 'success',
                    'message': 'Payslip successfully created.',
                    }
                return response

        json_data = {'status': 'error', 'errors': form.errors}
        return self.render_json_response(json_data, status=400)
