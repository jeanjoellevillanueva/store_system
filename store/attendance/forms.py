from django import forms

from .models import Attendance
from .models import Overtime


class OvertimeForm(forms.ModelForm):
    """
    Form used when creating an overtime.
    """
    tasks = forms.MultipleChoiceField(
        choices=Attendance.TASK_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
        required=True
    )
    class Meta:
        model = Overtime
        fields = [
            'date',
            'hours',
            'tasks',
        ]

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        hours = cleaned_data.get('hours')
        if hours is not None and hours <= 0:
            self.add_error('hours', 'Hours must be a positive number.')
        if date:
            if Overtime.objects.filter(date=date).exists():
                self.add_error('date', 'An overtime entry for this date already exists.')
        return cleaned_data


class OvertimeUpdateForm(forms.ModelForm):
    """
    Form used when updating an overtime.
    """
    tasks = forms.MultipleChoiceField(
        choices=Attendance.TASK_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
        required=True
    )
    class Meta:
        model = Overtime
        fields = [
            'date',
            'hours',
            'tasks',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        hours = cleaned_data.get('hours')
        if hours is not None and hours <= 0:
            self.add_error('hours', 'Hours must be a positive number.')
        return cleaned_data