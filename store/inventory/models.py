import uuid

from mixins.models import ModelMixin

from django.db import models


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
