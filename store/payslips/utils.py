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
    generate payslip
    """
    def set_pdf_font(self, canvas, font_style='Helvetica', font_size=24):
        """
        setting the font
        """
        canvas.setFont(font_style, font_size)
        
    def center_text(self, position_x1, position_x2, text, font_name="Helvetica", font_size=13):
        """
        Returns the starting point of the text for centering between position_x1 and position_x2,
        while ensuring it fits in the available space.
        
        :param position_x1: The left x-coordinate.
        :param position_x2: The right x-coordinate.
        :param text: The text to center.
        :param font_name: The font to use (default "Helvetica").
        :param font_size: The size of the font (default 12).
        """
        # Calculate the width of the text using ReportLab's stringWidth
        text_width = pdfmetrics.stringWidth(text, font_name, font_size)
        
        # Calculate the available space between position_x1 and position_x2
        available_space = position_x2 - position_x1
        
        # If the text is wider than the available space, adjust the position
        if text_width > available_space:
            # If the text doesn't fit, place it at position_x1 (left aligned)
            start_x = position_x1
        else:
            # Calculate the center position and offset by half the text width
            center_x = (position_x1 + position_x2) / 2
            start_x = center_x - (text_width / 2)
        
        return start_x

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
        COMPANY_NAME = 'Galinduh Co. Online Shop'
        COMPANY_STREET = 'Iris Street, St. Agatha Homes'
        COMPANY_ADDRESS = 'Tikay, Malolos, Bulacan'
        CREATED_BY = 'Created by:'
        start_date = datetime.strptime(payslip_data['start_date'], '%Y-%m-%d').strftime('%b %d, %Y')
        end_date = datetime.strptime(payslip_data['end_date'], '%Y-%m-%d').strftime('%b %d, %Y')
        hired_date = f": {start_date} - {end_date}"
        pay_date = f": {start_date} - {end_date}"
        work_days = f": {payslip_data['days']}"
        employee_name = f": {payslip_data['created_to']}"
        employee_designation = f": {payslip_data['created_to']}"
        employee_fulfillment = f": {payslip_data['created_to']}"


        base_pay = float(payslip_data['base_pay']) if payslip_data['base_pay'] else 0.0
        days_worked = float(payslip_data['days']) if payslip_data['days'] else 0.0
        overtime_hours = float(payslip_data['ot_hours']) if payslip_data['ot_hours'] else 0.0
        rate_pay = float(payslip_data['rate']) if payslip_data['rate'] else 0.0
        total_deduction = float(payslip_data['total_deduction']) if payslip_data['total_deduction'] else 0.0

        basic_pay = round(base_pay * days_worked, 2)
        overtime_pay = round(overtime_hours * rate_pay, 2)
        total_earnings = round(basic_pay + overtime_pay, 2)
        net_pay = round((basic_pay + overtime_pay) - total_deduction, 2)

        page_width, page_height = letter
        text_width = payslip_statement.stringWidth(COMPANY_NAME, "Helvetica", 24)
        x_position = (page_width - text_width) / 2
        # Payslip PDF settings
        WIDTH, HEIGHT = letter
        payslip_statement.setTitle(FILE_NAME)

        # PDF CONTENTS
        self.set_pdf_font(payslip_statement, 'Helvetica', 15)
        payslip_statement.drawString(self.center_text(0, 612, FILE_NAME), 740, FILE_NAME)
        payslip_statement.drawString(self.center_text(0, 612, COMPANY_NAME), 720, COMPANY_NAME)
        payslip_statement.drawString(self.center_text(0, 612, COMPANY_STREET), 700, COMPANY_STREET)
        payslip_statement.drawString(self.center_text(0, 612, COMPANY_ADDRESS), 680, COMPANY_ADDRESS)

        self.set_pdf_font(payslip_statement, 'Helvetica', 13)

        generated_payslip = 'This is system generated payslip'

        bg_color = colors.Color(0.8, 0.8, 0.8)
        payslip_statement.setFillColor(bg_color)
        payslip_statement.rect(30, 480, 552, 20, fill=1)

        payslip_statement.setFillColor(colors.black)
        payslip_statement.drawString(30, 620, 'Date of Joining')
        payslip_statement.drawString(120, 620, f'{hired_date}')
        payslip_statement.drawString(30, 590, 'Pay Period')
        payslip_statement.drawString(120, 590, f'{pay_date}')
        payslip_statement.drawString(30, 560, 'Worked Days')
        payslip_statement.drawString(120, 560, f'{work_days}')




        payslip_statement.drawString(306, 620, 'Employee Name')
        payslip_statement.drawString(426, 620, f'{employee_name}')
        payslip_statement.drawString(306, 590, 'Designation')
        payslip_statement.drawString(426, 590, f'{employee_designation}')
        payslip_statement.drawString(306, 560, 'Fulfillment')
        payslip_statement.drawString(426, 560, f'{employee_fulfillment}')

        # Table Settings
        payslip_statement.line(30, 500, 582, 500) # TOP
        payslip_statement.line(30, 480, 582, 480) # LOWER TOP
        payslip_statement.line(30, 500, 30, 250) # LEFT
        payslip_statement.line(582, 500, 582, 250) # RIGHT
        payslip_statement.line(30, 250, 582, 250) # BOTTOM
        payslip_statement.line(306, 500, 306, 250) # MIDDLE
        payslip_statement.line(195.6, 500, 195.6, 250) # MIDDLE LEFT
        payslip_statement.line(471.6, 500, 471.6, 250) # MIDDLE RIGHT

        

        payslip_statement.drawString(88.5, 485, 'Earnings')
        payslip_statement.drawString(230, 485, 'Amount')
        payslip_statement.drawString(360, 485, 'Deductions')
        payslip_statement.drawString(505, 485, 'Amount')

        # EARNINGS
        payslip_statement.drawString(38, 460, 'Basic')
        payslip_statement.drawString(self.center_text(195.6, 306, str(basic_pay)), 460, str(basic_pay))
        payslip_statement.drawString(38, 435, 'Overtime')
        payslip_statement.drawString(self.center_text(195.6, 306, str(overtime_pay)), 435, str(overtime_pay))
        payslip_statement.drawString(105, 275, 'Total Earnings')
        payslip_statement.drawString(self.center_text(195.6, 306, str(total_earnings)), 275, str(total_earnings))
        # DEDUCTIONS
        deduction_dict = ast.literal_eval(payslip_data['deductions'])
        DEDUCTION_TEXT_Y_POSITION = 460
        for deduction in deduction_dict:
            deduction_text = f"{deduction['deduction_type']}"
            payslip_statement.drawString(314, DEDUCTION_TEXT_Y_POSITION, deduction_text)
            DEDUCTION_TEXT_Y_POSITION -= 25

        DEDUCTION_AMOUNT_Y_POSITION = 460
        for deduction in deduction_dict:
            deduction_amount = f"{deduction['amount']}"
            payslip_statement.drawString(self.center_text(471.6, 582, str(deduction_amount)), DEDUCTION_AMOUNT_Y_POSITION, deduction_amount)
            DEDUCTION_AMOUNT_Y_POSITION -= 25

        payslip_statement.drawString(367, 275, "Total Deductions")
        payslip_statement.drawString(self.center_text(471.6, 582, str(total_deduction)),275, str(total_deduction))

        # NET EARNING
        payslip_statement.drawString(420,255, "Net pay")
        payslip_statement.drawString(self.center_text(471.6, 582, str(net_pay)),255, str(net_pay))


        payslip_statement.drawString(40,0, "x40")
        payslip_statement.drawString(80,0, "x80")
        payslip_statement.drawString(100,0, "x100")
        payslip_statement.drawString(200,0, "x200")
        payslip_statement.drawString(300,0, "x300")
        payslip_statement.drawString(400,0, "x400")
        payslip_statement.drawString(500,0, "x500")
        payslip_statement.drawString(540,0, "x540")
        payslip_statement.drawString(580,0, "x580")

        payslip_statement.drawString(0,40, "y40")
        payslip_statement.drawString(0,80, "y80")
        payslip_statement.drawString(0,100, "y100")
        payslip_statement.drawString(0,200, "y200")
        payslip_statement.drawString(0,300, "y300")
        payslip_statement.drawString(0,400, "y400")
        payslip_statement.drawString(0,500, "y500")
        payslip_statement.drawString(0,600, "y600")
        payslip_statement.drawString(0,700, "y700")
        payslip_statement.drawString(0,740, "y740")
        payslip_statement.drawString(0,780, "y780")

        payslip_statement.line(30, 150, 195.6, 150) # Created by
        payslip_statement.drawString(self.center_text(30, 195.6, payslip_data['created_by']), 153, payslip_data['created_by'])
        payslip_statement.line(416.4, 150, 582, 150) # Created to
        payslip_statement.drawString(self.center_text(416.4, 582, payslip_data['created_to']), 153, payslip_data['created_to'])
        payslip_statement.drawString(self.center_text(0, 612, generated_payslip), 35, generated_payslip)

        payslip_statement.save()
        buffer.seek(0)
        return buffer
