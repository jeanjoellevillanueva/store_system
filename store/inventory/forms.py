from django import forms

from .models import Delivery
from .models import Product


class ProductForm(forms.ModelForm):
    """
    Form used when creating Product.
    """
    class Meta:
        model = Product
        exclude = [
            'sku',
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


class VariationUpdateForm(forms.ModelForm):
    """
    Form used when updating a variation of a product.
    """

    class Meta:
        model = Product
        fields = [
            'sku',
            'variation',
            'capital',
            'price',        
        ]


class DeliveryAddForm(forms.ModelForm):
    """
    Form used when adding stock of a product.
    """
    reason = forms.ChoiceField(
        choices=Delivery.DEFAULT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Delivery
        fields = [
            'quantity',
            'reason',
            'remarks',
        ]


class DeliverySubtractForm(forms.ModelForm):
    """
    Form used when subtracting stock on a product.
    """
    reason = forms.ChoiceField(
        choices=Delivery.OUT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Delivery
        fields = [
            'quantity',
            'reason',
            'remarks',
        ]
