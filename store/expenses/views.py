import io
import pandas as pd

from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import FileResponse
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

    def get_filters(self, request):
        filters = self.request.session.get('filters', {})
        name_filter = request.POST.get('name_filter')
        category_filter = request.POST.get('category_filter')
        if name_filter:
            filters['name'] = name_filter
        if category_filter:
            filters['category'] = category_filter
        if request.POST.get('start_date') and request.POST.get('end_date'):
            start_date = datetime.strptime(request.POST.get('start_date'), settings.DATE_FORMAT)
            end_date = datetime.strptime(request.POST.get('end_date'), settings.DATE_FORMAT)
        elif filters.get('start_date') and filters.get('end_date'):
            start_date = datetime.strptime(filters.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(filters.get('end_date'), '%Y-%m-%d')
        else:
            start_date, end_date = self.get_initial_dates()
        if start_date:
            filters['start_date'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            filters['end_date'] = end_date.strftime('%Y-%m-%d')
        self.request.session['filters'] = filters
        return filters

    def get_initial_dates(self):
        current_date = date.today()
        start_date = current_date - timedelta(days=7)
        end_date = current_date
        return start_date, end_date

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('clear') == 'True':
            self.request.session['filters'] = {}
        filters = self.get_filters(self.request)
        context['expense_form'] = ExpenseForm(initial={'amount': 0})
        context['expense_update_form'] = ExpenseForm(auto_id='id_%s_update')
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        filters = self.get_filters(request)
        context['expense_form'] = ExpenseForm(initial={'amount': 0})
        context['expense_update_form'] = ExpenseForm(auto_id='id_%s_update')
        context.update({
            'start_date': datetime.strptime(filters['start_date'], '%Y-%m-%d'),
            'end_date': datetime.strptime(filters['end_date'], '%Y-%m-%d'),
            'filters': filters,
        })
        return self.render_to_response(context)


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
                expense.address = form.cleaned_data['address']
                expense.tin_number = form.cleaned_data['tin_number']
                expense.or_number = form.cleaned_data['or_number']
                expense.is_business = form.cleaned_data['is_business']
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
        start_date = datetime.strptime(self.request.session['filters']['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(self.request.session['filters']['end_date'], '%Y-%m-%d')
        filters = {
            'expense_date__range': (start_date, end_date),
        }
        if self.request.session['filters'].get('name'):
            name = self.request.session['filters'].get('name')
            filters.update({'name': name})
        if self.request.session['filters'].get('category'):
            category = self.request.session['filters'].get('category')
            filters.update({'category': category})
        context['expenses'] = (
            Expense.objects
                .filter(**filters)
                .order_by('-expense_date')
        )
        context['categories'] = Expense.CATEGORY_CHOICES
        context['names'] = Expense.objects.values_list('name', flat=True).distinct()
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['filters'] = filters
        return context


class ExpenseListDownloadView(LoginRequiredMixin, View):
    """
    Download the datatable that contains the list of expenses into CSV.
    """
    
    def get(self, request, *args, **kwargs):
        DATE_FORMAT = "%m/%d/%Y"
        STATIC_FILTERS = {
            'tin_number':'',
            'or_number':'',
            }
        combined_filters = {}
        filters = self.request.session['filters']
        filter_list = {
            'expense_date__range': (filters['start_date'], filters['end_date'],), 
        }
        if filters.get('name'):
            name = filters.get('name')
            filter_list.update({'name': name})
        if filters.get('category'):
            category = filters.get('category')
            filter_list.update({'category': category})
        combined_filters = {**filter_list}        
        expenses_list = (
            Expense.objects
                .filter(**combined_filters)
                .exclude(**STATIC_FILTERS)
                .order_by('-expense_date')
                .values()
        )
        for expense in expenses_list:
            expense['created_date'] = (
                expense['created_date'].strftime(DATE_FORMAT) if expense['created_date'] else ""
            )
            expense['expense_date'] = (
                expense['expense_date'].strftime(DATE_FORMAT) if expense['expense_date'] else ""
            )
            expense['updated_date'] = (
                expense['updated_date'].strftime(DATE_FORMAT) if expense['updated_date'] else ""
            )
        expenses_summary = pd.DataFrame.from_records(expenses_list)
        buffer = io.BytesIO()
        expenses_summary.to_excel(buffer)
        buffer.seek(0)
        response = FileResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        start_date_name = datetime.strptime(filters['start_date'], "%Y-%m-%d").strftime("%b-%d, %Y")
        end_date_name = datetime.strptime(filters['end_date'], "%Y-%m-%d").strftime("%b-%d, %Y")
        filename = f'expense summary-{start_date_name} - {end_date_name}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
