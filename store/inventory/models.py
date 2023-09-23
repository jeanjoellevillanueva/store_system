from mixins.models import ModelMixin

from django.db import models


class Color(models.Model):
    """
    Represents a color that can be associated with one or more products.
    """

    class Meta:
        db_table = 'colors'

    name = models.CharField(max_length=255, unique=True)
    hexcode = models.CharField(max_length=7, unique=True, verbose_name="Hex Code")

    def __str__(self):
        return self.name


class Item(ModelMixin, models.Model):
    """
    Represents an item in the inventory.
    """

    class Meta:
        db_table = 'items'

    item_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    colors = models.ManyToManyField(Color, through='Product')

    def __str__(self):
        return self.name


class Product(ModelMixin, models.Model):
    """
    Represents the quantity of a specific color variant in stock for a product.
    """

    class Meta:
        db_table = 'products'

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.item.name} ({self.color.name})"
