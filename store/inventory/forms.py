from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    """
    Form used when creating/updating Product.
    """
    class Meta:
        model = Product
        exclude = [
            'variation',
            'quantity',
        ]
