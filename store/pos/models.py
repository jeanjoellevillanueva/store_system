import random
import string
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from mixins.models import ModelMixin


class Sale(ModelMixin):
    """
    The transaction that happened between the buyer and the seller.
    """

    BANK_TRANSFER = 'bank_transfer'
    CASH = 'cash'
    CREDIT = 'credit'

    PAYMENT_METHODS = [
        (BANK_TRANSFER, 'Bank Transfer'),
        (CASH, 'Cash'),
        (CREDIT, 'Credit Card'),
    ]

    receipt_number = models.CharField(max_length=20, editable=False)
    # Product info.
    product_id = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    capital = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Sale info.
    quantity = models.PositiveIntegerField()
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Computed fields.
    profit = models.DecimalField(max_digits=10, decimal_places=2)

    # Transaction info.
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    payment_method = models.CharField(
        max_length=50, default=CASH, choices=PAYMENT_METHODS)

    def __str__(self):
        return f'Sale {self.receipt_number}'

    @classmethod
    def generate_receipt_number(cls):
        """
        Generates a unique receipt number with the format YYYYMMDDXXXXXXXXXXXXXXXX.
        """
        while True:
            # Generate a random 12-character string of letters and digits
            random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            
            # Create the receipt number with the format YYYYMMDDXXXXXXXXXXXXXXXX
            date_part = datetime.now().strftime('%Y%m%d')
            receipt_number = f'{date_part}{random_chars}'
            
            # Check if the receipt number already exists
            if not cls.objects.filter(receipt_number=receipt_number).exists():
                return receipt_number
