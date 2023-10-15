from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
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
        return context
    

class ExpenseCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when creating products.
    """

    def post(self, request, *args, **kwargs):
        form = ExpenseForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                variations = parse_variation(request.POST)

                # Check if item code already exists.
                is_exist = Product.objects.filter(item_code=form.cleaned_data['item_code'])
                if is_exist:
                    form_error = {}
                    form_error['item_code'] = ['Item code already exists.']
                    json_data = {'status': 'error', 'errors': form_error}
                    return self.render_json_response(json_data, status=400)

                # Check if the variations are empty.
                invalid_variations = []
                for product_variation in variations:
                    if not product_variation['variation']:
                        invalid_variations.append(product_variation['orig_key'])
                if invalid_variations:
                    form_error = {}
                    for var_key in invalid_variations:
                        form_error[var_key] = ['This field is required.']
                    json_data = {'status': 'error', 'errors': form_error}
                    return self.render_json_response(json_data, status=400)
                
                # If items are valid then continue to save to the database.
                for product_variation in variations:
                    product = form.save(commit=False)
                    product.pk = None  # Reset the primary key to create a new instance.
                    product.variation = product_variation['variation']
                    product.price = product_variation['price']
                    product.capital = product_variation['capital']
                    product.created_by = request.user
                    product.save()
                json_data = {
                    'status': 'success',
                    'message': 'Product successfully created.'
                }
                return  self.render_json_response(json_data, status=201)
        json_data = {'status': 'error', 'errors': form.errors}
        return self.render_json_response(json_data, status=400)
