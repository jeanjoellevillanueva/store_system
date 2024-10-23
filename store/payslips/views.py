from datetime import date
from io import BytesIO
from typing import Any
import json

from braces.views import JSONResponseMixin

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum
from django.http import FileResponse
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.generic import View

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from .forms import PayslipForm
from .models import Payslip
from attendance.models import Attendance
from attendance.models import Overtime

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


class PayslipCustomCreateView(LoginRequiredMixin, View):
    """
    Saving payslip into tables
    """
    def post(self, request, *args, **kwargs):
        form = PayslipForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                payslips = Payslip(
                    employee = form.cleaned_data['employee'],
                    start_date = form.cleaned_data['start_date'],
                    end_date = form.cleaned_data['end_date'],
                    base_pay = form.cleaned_data['base_pay'],
                    rate = form.cleaned_data['rate'],
                    created_by = request.user,
                    created_date = date.today(),
                )
                payslips.save()

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

    
    def pdf_table(self, canvas, x1, y1, x2, y2):
        """
        setting the table
        """
        canvas.line(x1, y1, x2, y2)


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

        # Table data
        data = [
            ['Employee:', payslip_data['employee']],
            ['Start Date:', payslip_data['start_date']],
            ['End Date:', payslip_data['end_date']],
            ['Base Pay:', payslip_data['base_pay']],
            ['Rate:', payslip_data['rate']],
            ['Days:', payslip_data['days']],
            ['OT Hours:', payslip_data['ot_hours']],
        ]

        base_pay = float(payslip_data['base_pay']) if payslip_data['base_pay'] else 0.0
        days_worked = float(payslip_data['days']) if payslip_data['days'] else 0.0
        overtime_hours = float(payslip_data['ot_hours']) if payslip_data['ot_hours'] else 0.0
        rate_pay = float(payslip_data['rate']) if payslip_data['rate'] else 0.0

        basic_pay = base_pay * days_worked
        overtime_pay = overtime_hours * rate_pay
        total_earnings = basic_pay + overtime_pay
        total_deductions = 0
        net_pay = basic_pay + overtime_pay
        

        # Payslip PDF settings
        WIDTH, HEIGHT = letter
        MARGIN_LEFT = 50
        MARGIN_RIGHT = 50
        MARGIN_TOP = 50
        MARGIN_BOTTOM = 50
        payslip_statement.setStrokeColorRGB(0.0, 0.0, 0.0)
        payslip_statement.setLineWidth(1)
        payslip_statement.rect(MARGIN_LEFT, MARGIN_BOTTOM, WIDTH - MARGIN_LEFT - MARGIN_RIGHT, HEIGHT - MARGIN_TOP - MARGIN_BOTTOM)
        # Payslip values TOP TO BOTTOM
        payslip_statement.setTitle(FILE_NAME)
        
        self.set_pdf_font(payslip_statement, 'Helvetica', 24)
        payslip_statement.drawString(235,700, COMPANY_NAME)
        payslip_statement.drawString(180,670, COMPANY_ADDRESS)
        payslip_statement.drawString(265,640, FILE_NAME)

        self.set_pdf_font(payslip_statement, 'Helvetica', 13)
        payslip_statement.drawString(70, 600, f"Name: {payslip_data['employee']}")
        payslip_statement.drawString(70, 585, f"Date: {payslip_data['start_date']} - {payslip_data['end_date']}")
        payslip_statement.drawString(70, 570, f"Base: {payslip_data['base_pay']}")
        payslip_statement.drawString(70, 555, f"Rate/Hr: {payslip_data['rate']}")
        payslip_statement.drawString(70, 540, f"No. Days: {payslip_data['days']}")
        payslip_statement.drawString(70, 525, f"No. OT: {payslip_data['ot_hours']}")

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
        payslip_statement.drawString(100, 430, f"Basic:                     {basic_pay}")
        payslip_statement.drawString(100, 410, f"Overtime:               {overtime_pay}")
        payslip_statement.drawString(80, 275, f"Total Earnings:              {total_earnings}")
        # DEDUCTIONS
        payslip_statement.drawString(310, 275, f"Total Deductions:                  {total_deductions}")

        # NET EARNING
        payslip_statement.drawString(335,255, f"NET PAY:                 {net_pay}")

        payslip_statement.drawString(100,150, CREATED_BY)
        
        # X Cartesian Plane
        payslip_statement.drawString(100,10,'x100')
        payslip_statement.drawString(200,10,'x200')
        payslip_statement.drawString(300,10,'x300')
        payslip_statement.drawString(400,10,'x400')
        payslip_statement.drawString(500,10,'x500')

        # Y Cartesian Plane
        payslip_statement.drawString(10,100,'y100')
        payslip_statement.drawString(10,200,'y200')
        payslip_statement.drawString(10,300,'y300')
        payslip_statement.drawString(10,400,'y400')
        payslip_statement.drawString(10,500,'y500')
        payslip_statement.drawString(10,600,'y600')
        payslip_statement.drawString(10,700,'y700')

        payslip_statement.save()

        buffer.seek(0)
        response = FileResponse(
            buffer, content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        
        return response
