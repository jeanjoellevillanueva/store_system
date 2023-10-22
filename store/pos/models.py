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
    is_void = models.BooleanField(default=False)

    # Computed fields.
    profit = models.DecimalField(max_digits=10, decimal_places=2)

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

    @classmethod
    def get_sales_by_date_range(cls, start_date, end_date):
        """
        Returns sales object by date range.

        Params:
        start_date - datetime object
        end_date - datetime object
        """
        sales = (
            cls.objects
                .filter(created_date__date__range=(start_date, end_date))
                .values('created_date', 'price', 'profit', 'quantity', 'product_name')
        )
        return sales
