from django import forms

from .models import Payslip

class PayslipForm(forms.ModelForm):
    """
    Form used when creating an expense.
    """
    class Meta:
        model = Payslip
        fields = [
            'employee',
            'start_date',
            'end_date',
        ]
