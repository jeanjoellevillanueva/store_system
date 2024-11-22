from datetime import datetime
from io import BytesIO
import ast

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from .models import Payslip


def parse_deduction(orig_dict):
    """
    Parse the deduction type and amount in the dict.
    """

    deductions = []
    for key, value in orig_dict.items():
        if key.startswith('deduction_type_'):
            _, _, number = key.split('_')
            deduction_type_key = f'deduction_type_{number}'
            amount_key = f'deduction_amount_{number}'
            deductions.append({
                'deduction_type': orig_dict[deduction_type_key],
                'amount': orig_dict[amount_key],
            })
    return deductions


def format_deductions(deductions):
    """
    Converts deduction choice into human-readable
    """
    deductions_dict = dict(Payslip.DEDUCTION_CHOICES)
    for deduction in deductions:
        deduction['deduction_type'] = deductions_dict.get(deduction['deduction_type'])
    return deductions


class GeneratePayslipView:
    """
    Class responsible for generating a payslip on PDF.
    """

    file_name = 'Payslip'
    company_name = 'Galinduh Co. Online Shop'
    company_street = 'Iris Street, St. Agatha Homes'
    company_address = 'Tikay, Malolos, Bulacan'
    font_style = 'Helvetica'
    payslip_statement = None

    def set_pdf_font(self, canvas, font_style='Helvetica', font_size=24):
        """
        setting the font
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
        hired_date = payslip_data['date_joined'].strftime('%Y-%m-%d')
        pay_date = f": {start_date} - {end_date}"
        work_days = f": {payslip_data['days']}"
        employee_name = f": {payslip_data['created_to']}"
        employee_designation = f": {payslip_data['created_to']}"
        employee_fulfillment = f": {payslip_data['created_to']}"
        self.payslip_statement.drawString(30, 620, 'Date of Joining')
        self.payslip_statement.drawString(120, 620, f'{hired_date}')
        self.payslip_statement.drawString(30, 590, 'Pay Period')
        self.payslip_statement.drawString(120, 590, f'{pay_date}')
        self.payslip_statement.drawString(30, 560, 'Worked Days')
        self.payslip_statement.drawString(120, 560, f'{work_days}')
        self.payslip_statement.drawString(306, 620, 'Employee Name')
        self.payslip_statement.drawString(426, 620, f'{employee_name}')
        self.payslip_statement.drawString(306, 590, 'Designation')
        self.payslip_statement.drawString(426, 590, f'{employee_designation}')
        self.payslip_statement.drawString(306, 560, 'Fulfillment')
        self.payslip_statement.drawString(426, 560, f'{employee_fulfillment}')
    
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
        base_pay = float(payslip_data['base_pay']) if payslip_data['base_pay'] else 0.0
        days_worked = float(payslip_data['days']) if payslip_data['days'] else 0.0
        overtime_hours = float(payslip_data['ot_hours']) if payslip_data['ot_hours'] else 0.0
        rate_pay = float(payslip_data['rate']) if payslip_data['rate'] else 0.0
        total_deduction = float(payslip_data['total_deduction']) if payslip_data['total_deduction'] else 0.0

        basic_pay = round(base_pay * days_worked, 2)
        overtime_pay = round(overtime_hours * rate_pay, 2)
        total_earnings = round(basic_pay + overtime_pay, 2)
        net_pay = round((basic_pay + overtime_pay) - total_deduction, 2)

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
        generated_payslip = 'This is system generated payslip'
        self.payslip_statement.line(30, 150, 195.6, 150) # Created by
        self.payslip_statement.drawString(self.center_text(30, 195.6, payslip_data['created_by']), 153, payslip_data['created_by'])
        self.payslip_statement.line(416.4, 150, 582, 150) # Created to
        self.payslip_statement.drawString(self.center_text(416.4, 582, payslip_data['created_to']), 153, payslip_data['created_to'])
        self.payslip_statement.drawString(self.center_text(0, 612, generated_payslip), 35, generated_payslip)
        
    def generate_payslip(self, payslip_data, file_name='payslip.pdf'):
        """
        Downloading Payslip into PDF.
        """
        buffer = BytesIO()

        self.payslip_statement = canvas.Canvas(
            buffer,
            pagesize=letter
        )
        page_width, page_height = letter
        #text_width = payslip_statement.stringWidth(company_name, "Helvetica", 24)
        # Payslip PDF settings
        WIDTH, HEIGHT = letter
        self.payslip_statement.setTitle(file_name)
        self.set_pdf_font(self.payslip_statement, 'Helvetica', 13)
        bg_color = colors.Color(0.8, 0.8, 0.8)
        self.payslip_statement.setFillColor(bg_color)
        self.payslip_statement.rect(30, 480, 552, 20, fill=1)
        self.payslip_statement.setFillColor(colors.black)
        self.create_header(self.font_style, 14)
        self.create_employee_section(payslip_data, self.font_style, 14)
        self.create_table(payslip_data, self.font_style, 14)
        self.create_footer(payslip_data, self.font_style, 14)
        self.payslip_statement.save()
        buffer.seek(0)
        return buffer
