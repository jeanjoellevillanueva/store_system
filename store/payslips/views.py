from datetime import date
from io import BytesIO
from typing import Any
import ast
import json

from braces.views import JSONResponseMixin
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from django.conf import settings
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
from .utils import parse_deduction


class PayslipCustomCreateView(LoginRequiredMixin, View):
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
                    'employee': str(form.cleaned_data['employee']),
                    'start_date': str(form.cleaned_data['start_date']),
                    'end_date': str(form.cleaned_data['end_date']),
                    'base_pay': str(form.cleaned_data['base_pay']),
                    'rate': str(form.cleaned_data['rate']),
                    'days': str(attendance_data),
                    'ot_hours': str(overtime_hours),
                    'deductions': str(deductions),
                    'total_deduction': str(total_deductions),
                    'created_by': str(request.user),
                }

                json_data = {
                    'status': 'success',
                    'message': 'Payslip successfully created.',
                    'payslip_data': payslip_data,
                    }
                return self.generate_payslip(payslip_data)

        json_data = {'status': 'error', 'errors': form.errors}
        return self.render_json_response(json_data, status=400)
    
    
    def set_pdf_font(self, canvas, font_style='Helvetica', font_size=24):
        """
        setting the font
        """
        canvas.setFont(font_style, font_size)


    def generate_payslip(self, payslip_data, file_name='payslip.pdf'):
        """
        Downloading Payslip into PDF
        """
        buffer = BytesIO()

        payslip_statement = canvas.Canvas(
            buffer,
            pagesize=letter
        )

        FILE_NAME = 'Payslip'
        COMPANY_NAME = 'Galinduh Co.'
        COMPANY_ADDRESS = 'Tikay, Malolos, Bulacan'
        CREATED_BY = 'Created by:'
        
        base_pay = float(payslip_data['base_pay']) if payslip_data['base_pay'] else 0.0
        days_worked = float(payslip_data['days']) if payslip_data['days'] else 0.0
        overtime_hours = float(payslip_data['ot_hours']) if payslip_data['ot_hours'] else 0.0
        rate_pay = float(payslip_data['rate']) if payslip_data['rate'] else 0.0
        total_deduction = float(payslip_data['total_deduction']) if payslip_data['total_deduction'] else 0.0

        basic_pay = base_pay * days_worked
        overtime_pay = overtime_hours * rate_pay
        total_earnings = basic_pay + overtime_pay
        net_pay = (basic_pay + overtime_pay) - total_deduction

        # Payslip PDF settings
        WIDTH, HEIGHT = letter
        MARGIN_LEFT = 50
        MARGIN_RIGHT = 50
        MARGIN_TOP = 50
        MARGIN_BOTTOM = 50
        payslip_statement.setStrokeColorRGB(0.0, 0.0, 0.0)
        payslip_statement.setLineWidth(1)
        payslip_statement.rect(MARGIN_LEFT, MARGIN_BOTTOM, WIDTH - MARGIN_LEFT - MARGIN_RIGHT, HEIGHT - MARGIN_TOP - MARGIN_BOTTOM)
        payslip_statement.setTitle(FILE_NAME)

        # Payslip values TOP TO BOTTOM
        self.set_pdf_font(payslip_statement, 'Helvetica', 24)
        payslip_statement.drawString(235,700, COMPANY_NAME)
        payslip_statement.drawString(180,670, COMPANY_ADDRESS)
        payslip_statement.drawString(265,640, FILE_NAME)

        self.set_pdf_font(payslip_statement, 'Helvetica', 13)
        payslip_statement.drawString(70, 610, f"Name: {payslip_data['employee']}")
        payslip_statement.drawString(70, 595, f"Date: {payslip_data['start_date']} - {payslip_data['end_date']}")
        payslip_statement.drawString(70, 580, f"Base: {payslip_data['base_pay']}")
        payslip_statement.drawString(70, 565, f"Rate/Hr: {payslip_data['rate']}")
        payslip_statement.drawString(70, 550, f"No. Days: {payslip_data['days']}")
        payslip_statement.drawString(70, 535, f"No. OT: {payslip_data['ot_hours']}")
        payslip_statement.drawString(70, 520, f"Created by: {payslip_data['created_by']}")

        # Table Settings
        payslip_statement.line(70, 500, 540, 500) #TOP
        payslip_statement.line(540, 500, 540, 270) #RIGHT
        payslip_statement.line(70, 500, 70, 270) #LEFT
        payslip_statement.line(70, 270, 540, 270) #BOTTOM
        payslip_statement.line(70, 450, 540, 450)
        payslip_statement.line(70, 470, 540, 470)
        payslip_statement.line(300, 500, 300, 270)
        payslip_statement.line(185, 470, 185, 270)
        payslip_statement.line(430, 470, 430, 270)
        payslip_statement.line(70, 290, 540, 290)
        payslip_statement.line(70, 250, 540, 250)
        payslip_statement.line(70, 250, 70, 290)
        payslip_statement.line(540, 250, 540, 290)
        payslip_statement.drawString(150, 480, 'EARNINGS')
        payslip_statement.drawString(375, 480, 'DEDUCTIONS')

        # EARNINGS
        payslip_statement.drawString(100, 430, f"Basic:                       {basic_pay}")
        payslip_statement.drawString(100, 410, f"Overtime:                 {overtime_pay}")
        payslip_statement.drawString(83, 275, f"Total Earnings:              {total_earnings}")
        
        # DEDUCTIONS
        deduction_dict = ast.literal_eval(payslip_data['deductions'])
        DEDUCTION_TEXT_Y_POSITION = 430
        for deduction in deduction_dict:
            deduction_text = f"{deduction['deduction_type']}:"
            payslip_statement.drawString(310, DEDUCTION_TEXT_Y_POSITION, deduction_text)
            DEDUCTION_TEXT_Y_POSITION -= 20

        DEDUCTION_AMOUNT_Y_POSITION = 430
        for deduction in deduction_dict:
            deduction_amount = f"{deduction['amount']}"
            payslip_statement.drawString(470, DEDUCTION_AMOUNT_Y_POSITION, deduction_amount)
            DEDUCTION_AMOUNT_Y_POSITION -= 20

        payslip_statement.drawString(313, 275, f"Total Deductions:               {payslip_data['total_deduction']}")

        # NET EARNING
        payslip_statement.drawString(335,255, f"NET PAY:                 {net_pay}")

        payslip_statement.save()

        buffer.seek(0)
        response = FileResponse(
            buffer, content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        
        return response
