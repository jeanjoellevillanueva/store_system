from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    """
    Form used when creating Product.
    """
    class Meta:
        model = Product
        exclude = [
            'capital',
            'price',
            'variation',
            'quantity',
            'created_by',
            'updated_by',
        ]


class ProductUpdateForm(forms.ModelForm):
    """
    Form used when updating a Product.
    """

    class Meta:
        model = Product
        fields = [
            'item_code',
            'name',
            'description', 
        ]
