from django.contrib.auth.models import User
from django.db import models


class Employee(models.Model):
    """
    Describes the data about employee metadata.
    """

    FULLFILMENT = 'fullfilment'
    LOGISTICS = 'logistics'
    DEV = 'dev'
    SALES = 'sales'
    ADMIN = 'admin'
    ACCOUNTING = 'accounting'

    DEPARTMENT_CHOICES = [
        (FULLFILMENT, 'Fullfilment'),
        (LOGISTICS, 'Logistics'),
        (DEV, 'Developers'),
        (SALES, 'Sales & Marketing'),
        (ADMIN, 'HR & Admin'),
        (ACCOUNTING, 'Accounting'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='employee')
    base_pay = models.DecimalField(max_digits=10, decimal_places=2)
    designation = models.CharField(max_length=100, default='')
    department = models.CharField(
        max_length=100, choices=DEPARTMENT_CHOICES, default=FULLFILMENT)
