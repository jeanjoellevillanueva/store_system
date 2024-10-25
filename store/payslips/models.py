from django.contrib.auth.models import User
from django.db import models

from mixins.models import ModelMixin

class Payslip(ModelMixin):
    """
    Represent a payslip that can be generated
    """

    DEDUCTION_LOAN = 'loan'
    DEDUCTION_ADVANCE = 'advance_payment'
    DEDUCTION_WRONG_SHIPMENT = 'wrong_shipment'
    DEDUCTION_MISC = 'misc'
    DEDUCTION_CHOICES = (
        (DEDUCTION_LOAN, 'Loan'),
        (DEDUCTION_ADVANCE, 'Advance Payment'),
        (DEDUCTION_WRONG_SHIPMENT, 'Wrong Shipment'),
        (DEDUCTION_MISC, 'Misc'),
    )
    employee = models.ForeignKey(User, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    base_pay = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    deduction = models.TextField(blank=True, null=True)
    total_deduction = models.DecimalField(max_digits=10, decimal_places=2)