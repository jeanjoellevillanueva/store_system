from django.contrib.auth.models import User
from django.db import models

from mixins.models import ModelMixin

class Payslip(ModelMixin):
    """
    Represent a payslip that can be generated
    """
    employee = models.ForeignKey(User, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    base_pay = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
