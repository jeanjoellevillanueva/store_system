from django import forms

from .models import Expense


class ExpenseForm(forms.ModelForm):
    """
    Form used when creating an expense.
    """
    class Meta:
        model = Expense
        fields = [
            'expense_date',
            'name',
            'address',
            'tin_number',
            'or_number',
            'category',
            'amount',
        ]
