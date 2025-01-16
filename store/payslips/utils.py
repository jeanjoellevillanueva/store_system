import ast
import os
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from django.conf import settings
from django.templatetags.static import static
from django.utils import timezone


from .models import Payslip
from .numbers import convert_number_to_words
from attendance.models import Overtime

def parse_items(orig_dict, key_base):
    """
    Parse the deduction type and amount in the dict.
    """
    items = []
    designation_name = str(f'{key_base}_type')
    for key, value in orig_dict.items():
        if key.startswith(f'{key_base}_type_'):
            _, _, number = key.split('_')
            item_type_key = f'{key_base}_type_{number}'
            amount_key = f'{key_base}_amount_{number}'
            items.append({
                designation_name: orig_dict[item_type_key],
                'amount': orig_dict[amount_key],
            })    
    return items


def format_items(items, key_base):
    """
    Converts deduction choice into human-readable
    """
    choices = f'{key_base}_CHOICES'.upper()
    items_dict = dict(getattr(Payslip, choices))
    for item in items:
        item[f'{key_base}_type'] = items_dict.get(item[f'{key_base}_type'])
    return items


class GeneratePayslipView:
    """
    Class responsible for generating a payslip on PDF.
    """

    file_name = 'Payslip'
    company_name = 'Galinduh Co. Online Shop'
    company_street = 'Iris Street, St. Agatha Homes'
    company_address = 'Tikay, Malolos, Bulacan'
    owner_name = 'Glenda Ann S. Ranoco'
    font_style = 'Helvetica'
    payslip_statement = None
    
    def __init__(self, employee):
        self.employee = employee

    def compute_payslip(self, payslip_data):
        """
        Computes the payslip details.
        """
        base_pay = float(payslip_data['base_pay']) if payslip_data['base_pay'] else 0.0
        days_worked = float(payslip_data['days']) if payslip_data['days'] else 0.0
        overtime_hours = float(payslip_data['ot_hours']) if payslip_data['ot_hours'] else 0.0
        rate_pay = float(payslip_data['rate']) if payslip_data['rate'] else 0.0
        total_allowance = float(payslip_data['total_allowance']) if payslip_data['total_allowance'] else 0.0
        total_deduction = float(payslip_data['total_deduction']) if payslip_data['total_deduction'] else 0.0
        basic_pay = round(base_pay * days_worked, 2)

        ot_start_date = datetime.strptime(settings.STANDARD_OVERTIME_START_DATE,  '%Y-%m-%d').replace(tzinfo=timezone.utc)
        ot_end_date = datetime.strptime(settings.STANDARD_OVERTIME_END_DATE,  '%Y-%m-%d').replace(tzinfo=timezone.utc)
        ot_rate_pay = settings.OT_RATE
        start_date = datetime.strptime(payslip_data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(payslip_data['end_date'], '%Y-%m-%d')
        ot_hours = Overtime.objects.filter(
            employee_id=self.employee.id,
            date__range=(start_date, end_date)
        ).values('date', 'hours')
        overtime_list = []

        for overtime in ot_hours:
            if overtime['date'] >= ot_start_date and overtime['date'] <= ot_end_date:
                overtime_pay = round(float(overtime['hours']) * ot_rate_pay, 2)
            else:
                overtime_pay = round(float(overtime['hours']) * rate_pay, 2)
            overtime_list.append({'ot_pay': overtime_pay})
        
        overtime_pay = round(sum(overtime['ot_pay'] for overtime in overtime_list), 2)
        total_earnings = round(basic_pay + overtime_pay + total_allowance, 2)
        net_pay = round((basic_pay + overtime_pay) + total_allowance - total_deduction, 2)
        return base_pay, days_worked, overtime_hours, rate_pay, total_allowance, total_deduction, basic_pay, overtime_pay, total_earnings, net_pay

    def set_pdf_font(self, canvas, font_style='Helvetica', font_size=24):
        """
        Method for setting the font.
        """
        canvas.setFont(font_style, font_size)

    def center_text(self, position_x1, position_x2, text, font_name='Helvetica', font_size=13):
        """
        Returns the starting point of the text for centering between position_x1 and position_x2,
        while ensuring it fits in the available space.
        """
        text_width = pdfmetrics.stringWidth(text, font_name, font_size)
        available_space = position_x2 - position_x1
        if text_width > available_space:
            start_x = position_x1
        else:
            center_x = (position_x1 + position_x2) / 2
            start_x = center_x - (text_width / 2)
        return start_x
    
    def create_coordinates(self, show=True):
        if show:
            self.payslip_statement.drawString(40,0, 'x40')
            self.payslip_statement.drawString(80,0, 'x80')
            self.payslip_statement.drawString(100,0, 'x100')
            self.payslip_statement.drawString(200,0, 'x200')
            self.payslip_statement.drawString(300,0, 'x300')
            self.payslip_statement.drawString(400,0, 'x400')
            self.payslip_statement.drawString(500,0, 'x500')
            self.payslip_statement.drawString(540,0, 'x540')
            self.payslip_statement.drawString(580,0, 'x580')
            self.payslip_statement.drawString(0,40, 'y40')
            self.payslip_statement.drawString(0,80, 'y80')
            self.payslip_statement.drawString(0,100, 'y100')
            self.payslip_statement.drawString(0,200, 'y200')
            self.payslip_statement.drawString(0,300, 'y300')
            self.payslip_statement.drawString(0,400, 'y400')
            self.payslip_statement.drawString(0,500, 'y500')
            self.payslip_statement.drawString(0,600, 'y600')
            self.payslip_statement.drawString(0,700, 'y700')
            self.payslip_statement.drawString(0,740, 'y740')
            self.payslip_statement.drawString(0,780, 'y780')

    def create_header(self, font: str, font_size: int):
        """
        Creates the header of the payslip.
        """
        self.set_pdf_font(self.payslip_statement, font, font_size)
        self.payslip_statement.drawString(self.center_text(0, 612, self.file_name), 740, self.file_name)
        self.payslip_statement.drawString(self.center_text(0, 612, self.company_name), 720, self.company_name)
        self.payslip_statement.drawString(self.center_text(0, 612, self.company_street), 700, self.company_street)
        self.payslip_statement.drawString(self.center_text(0, 612, self.company_address), 680, self.company_address)

    def create_employee_section(self, payslip_data, font: str, font_size: int):
        """
        Creates the employee information section.
        """
        self.set_pdf_font(self.payslip_statement, font, font_size)
        start_date = datetime.strptime(payslip_data['start_date'], '%Y-%m-%d').strftime('%b %d, %Y')
        end_date = datetime.strptime(payslip_data['end_date'], '%Y-%m-%d').strftime('%b %d, %Y')
        self.payslip_statement.drawString(30, 620, 'Date of Joining')
        self.payslip_statement.drawString(120, 620, f': {self.employee.date_joined.strftime("%Y-%m-%d")}')
        self.payslip_statement.drawString(30, 590, 'Pay Period')
        self.payslip_statement.drawString(120, 590, f': {start_date} - {end_date}')
        self.payslip_statement.drawString(30, 560, 'Worked Days')
        self.payslip_statement.drawString(120, 560, f': {payslip_data["days"]}')
        self.payslip_statement.drawString(306, 620, 'Employee Name')
        self.payslip_statement.drawString(426, 620, f': {self.employee.get_full_name()}')
        self.payslip_statement.drawString(306, 590, 'Designation')
        self.payslip_statement.drawString(426, 590, f': {self.employee.employee.designation}')
        self.payslip_statement.drawString(306, 560, 'Department')
        self.payslip_statement.drawString(426, 560, f': {self.employee.employee.get_department_display()}')

    def create_table_border(self):
        """
        Draws the table border.
        """
        self.payslip_statement.line(30, 500, 582, 500) # TOP
        self.payslip_statement.line(30, 480, 582, 480) # LOWER TOP
        self.payslip_statement.line(30, 500, 30, 250) # LEFT
        self.payslip_statement.line(582, 500, 582, 250) # RIGHT
        self.payslip_statement.line(30, 250, 582, 250) # BOTTOM
        self.payslip_statement.line(306, 500, 306, 250) # MIDDLE
        self.payslip_statement.line(195.6, 500, 195.6, 250) # MIDDLE LEFT
        self.payslip_statement.line(471.6, 500, 471.6, 250) # MIDDLE RIGHT
    
    def create_table(self, payslip_data, font: str, font_size: int):
        """
        Creates the table section.
        """
        self.create_table_border()
        self.set_pdf_font(self.payslip_statement, font, font_size)
        (
            base_pay,
            days_worked,
            overtime_hours,
            rate_pay,
            total_allowance, 
            total_deduction,
            basic_pay,
            overtime_pay,
            total_earnings,
            net_pay
        ) = self.compute_payslip(payslip_data)

        self.payslip_statement.drawString(88.5, 485, 'Earnings')
        self.payslip_statement.drawString(230, 485, 'Amount')
        self.payslip_statement.drawString(360, 485, 'Deductions')
        self.payslip_statement.drawString(505, 485, 'Amount')

        # Earnings
        self.payslip_statement.drawString(38, 460, 'Basic')
        self.payslip_statement.drawString(self.center_text(195.6, 306, str(basic_pay)), 460, str(basic_pay))
        self.payslip_statement.drawString(38, 435, 'Overtime')
        self.payslip_statement.drawString(self.center_text(195.6, 306, str(overtime_pay)), 435, str(overtime_pay))
        self.payslip_statement.drawString(105, 275, 'Total Earnings')
        self.payslip_statement.drawString(self.center_text(195.6, 306, str(total_earnings)), 275, str(total_earnings))

        # Allowance Earnings
        allowance_dict = ast.literal_eval(payslip_data['allowances'])
        ALLOWANCES_TEXT_Y_POSITION = 410
        for allowance in allowance_dict:
            allowance_text = f"{allowance['allowance_type']}"
            self.payslip_statement.drawString(38, ALLOWANCES_TEXT_Y_POSITION, allowance_text)
            ALLOWANCES_TEXT_Y_POSITION -= 25

        ALLOWANCES_TEXT_Y_POSITION = 410
        for allowance in allowance_dict:
            allowance_amount = f"{allowance['amount']}"
            self.payslip_statement.drawString(self.center_text(195.6, 306, str(allowance_amount)), ALLOWANCES_TEXT_Y_POSITION, allowance_amount)
            ALLOWANCES_TEXT_Y_POSITION -= 25

        # Deductions
        deduction_dict = ast.literal_eval(payslip_data['deductions'])
        DEDUCTION_TEXT_Y_POSITION = 460
        for deduction in deduction_dict:
            deduction_text = f"{deduction['deduction_type']}"
            self.payslip_statement.drawString(314, DEDUCTION_TEXT_Y_POSITION, deduction_text)
            DEDUCTION_TEXT_Y_POSITION -= 25

        DEDUCTION_AMOUNT_Y_POSITION = 460
        for deduction in deduction_dict:
            deduction_amount = f"{deduction['amount']}"
            self.payslip_statement.drawString(self.center_text(471.6, 582, str(deduction_amount)), DEDUCTION_AMOUNT_Y_POSITION, deduction_amount)
            DEDUCTION_AMOUNT_Y_POSITION -= 25

        self.payslip_statement.drawString(367, 275, 'Total Deductions')
        self.payslip_statement.drawString(self.center_text(471.6, 582, str(total_deduction)),275, str(total_deduction))

        # Net Earning
        self.payslip_statement.drawString(420, 255, 'Net pay')
        self.payslip_statement.drawString(self.center_text(471.6, 582, str(net_pay)),255, str(net_pay))

    def create_footer(self, payslip_data, font: str, font_size: int):
        """
        Creates the footer of the payslip.
        """
        self.set_pdf_font(self.payslip_statement, font, font_size)
        generated_payslip = 'This is a system generated payslip'
        employer_sign_label = 'Employer Signature'
        employee_sign_label = 'Employee Signature'
        (
            base_pay,
            days_worked,
            overtime_hours,
            rate_pay,
            total_allowance,
            total_deduction,
            basic_pay,
            overtime_pay,
            total_earnings,
            net_pay
        ) = self.compute_payslip(payslip_data)

        net_pay_in_words = convert_number_to_words(str(net_pay))
        self.payslip_statement.drawString(self.center_text(0, 612, str(net_pay)), 220, str(net_pay))
        self.payslip_statement.drawString(self.center_text(0, 612, net_pay_in_words), 205, net_pay_in_words)
        self.payslip_statement.drawString(self.center_text(30, 195.6, employer_sign_label), 160, employer_sign_label)
        self.payslip_statement.line(30, 110, 195.6, 110) # Created by
        self.payslip_statement.drawString(self.center_text(30, 195.6, self.owner_name), 113, self.owner_name)
        self.payslip_statement.drawString(self.center_text(416.4, 582, employee_sign_label), 160, employee_sign_label)
        self.payslip_statement.line(416.4, 110, 582, 110) # Created to
        self.payslip_statement.drawString(self.center_text(416.4, 582, self.employee.get_full_name()), 113, self.employee.get_full_name())
        self.payslip_statement.drawString(self.center_text(0, 612, generated_payslip), 35, generated_payslip)

        signature_path = static('img/signature.JPG')
        signature_full_path = os.path.join(os.getcwd(), signature_path.lstrip('/'))
        self.payslip_statement.drawImage(
            signature_full_path, 
            x=65,
            y=120,
            width=100,
            height=40,
            preserveAspectRatio=True,
            mask='auto'
        )
        
    def generate_payslip(self, payslip_data, file_name='payslip.pdf'):
        """
        Downloading Payslip into PDF.
        """
        buffer = BytesIO()

        self.payslip_statement = canvas.Canvas(
            buffer,
            pagesize=letter
        )
        self.payslip_statement.setTitle(file_name)
    
        bg_color = colors.Color(0.8, 0.8, 0.8)
        self.payslip_statement.setFillColor(bg_color)
        self.payslip_statement.rect(30, 480, 552, 20, fill=1)
        self.payslip_statement.setFillColor(colors.black)
        self.create_coordinates(show=False) # Change to false to hide the coordinates.
        self.create_header(self.font_style, 14)
        self.create_employee_section(payslip_data, self.font_style, 13)
        self.create_table(payslip_data, self.font_style, 13)
        self.create_footer(payslip_data, self.font_style, 13)
        self.payslip_statement.save()
        buffer.seek(0)
        return buffer
