from datetime import datetime
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404
from django.views import View
from django.views.generic import TemplateView

from braces.views import JSONResponseMixin

from .forms import ExpenseForm
from .models import Expense


class ExpenseTemplateView(LoginRequiredMixin, TemplateView):
    """
    Dashboard for expenses.
    """
    template_name = 'expenses/home.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['expense_form'] = ExpenseForm(initial={'amount': 0})
        context['expense_update_form'] = ExpenseForm(auto_id='id_%s_update')
        return context
    

class ExpenseCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when creating expenses.
    """

    def post(self, request, *args, **kwargs):
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            json_data = {
                'status': 'success',
                'message': 'Expense successfully created.'
            }
            return self.render_json_response(json_data, status=201)
        json_data = {'status': 'error', 'errors': form.errors}
        return self.render_json_response(json_data, status=400)


class ExpenseCustomDeleteView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used for deleting an expsense.
    """

    def post(self, request, *args, **kwargs):
        try:
            expense = Expense.objects.get(id=self.kwargs['id'])
        except Exception as e:
             # Object not found
             return self.render_json_response({'message': str(e)}, status=404)
        expense.delete()
        json_data = {
            'message': 'Successfully deleted'
        }
        return self.render_json_response(json_data, status=204)


class ExpenseCustomUpdateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used for updating expenses.
    """

    def post(self, request, *args, **kwargs):
        form = ExpenseForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                try:
                    expense = Expense.objects.get(id=self.kwargs['id'])
                except Expense.DoesNotExist:
                    raise Http404('Expense does not exist')
                expense.name = form.cleaned_data['name']
                expense.category = form.cleaned_data['category']
                expense.amount = form.cleaned_data['amount']
                expense.expense_date = form.cleaned_data['expense_date']
                expense.updated_date = datetime.today()
                expense.updated_by = request.user
                expense.save()
                json_data = {
                    'status': 'success',
                    'message': 'Product variation successfully Updated.'
                }
                return  self.render_json_response(json_data, status=200)
        json_data = {'status': 'error', 'errors': form.errors}
        return self.render_json_response(json_data, status=400)


class ExpenseListDatatableTemplateView(LoginRequiredMixin, TemplateView):
    """
    Renders the datatable that contains the list of expenses.
    """
    template_name = 'expenses/datatables/expenses.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['expenses'] = Expense.objects.all()
        return context
