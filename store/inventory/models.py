import uuid

from mixins.models import ModelMixin

from django.db import models
from django.db.models import Sum
from django.db.models import DecimalField
from django.db.models import ExpressionWrapper
from django.db.models import F


class Product(ModelMixin):
    """
    Represents an item in the inventory.
    """

    class Meta:
        db_table = 'products'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    capital = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    variation = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
    @classmethod    
    def update_stock(cls, product_id, quantity_of_sale):
        """
        Class method to update the new stock of a product.
        """

        product = cls.objects.get(id=product_id)
        new_quantity = product.quantity - quantity_of_sale
        product.quantity = new_quantity
        product.save()
    
    @classmethod
    def stock_value(cls):
        """
        Returns the total value of stocks in terms of capital spent.
        """
        total_value = (
                cls.objects
                    .annotate(product_value=ExpressionWrapper(F('quantity') * F('capital'), output_field=DecimalField()))
                    .aggregate(total_value=Sum('product_value'))
            )
        return total_value['total_value']

class Delivery(ModelMixin):
    """
    Represents the movement of the stock of products.
    """
    
    class Meta:
        db_table = 'deliveries'

    DELIVER = 'deliver'
    RETURNED = 'returned'
    PULL_OUT = 'pull_out'
    VOID = 'void'
    DEFAULT_CHOICES = [
        (DELIVER, 'Deliver'),
    ]
    IN_CHOICES = [
        (DELIVER, 'Deliver'),
        (RETURNED, 'Returned Item'),
    ]
    OUT_CHOICES = [
        (PULL_OUT, 'Pull-out'),
        (VOID, 'Void'),
    ]
    DELIVER_CHOICES = IN_CHOICES + OUT_CHOICES

    product_id = models.CharField(max_length=255)
    product_item_code = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    reason = models.CharField(max_length=50, choices=DELIVER_CHOICES, default=DELIVER)
