from typing import Any
from typing import Dict

from braces.views import JSONResponseMixin

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404
from django.views import View
from django.views.generic import TemplateView

from .forms import ProductForm
from .models import Product
from .utils import parse_variation


class InventoryTemplateView(LoginRequiredMixin, TemplateView):
    """
    Dashboard for inventories.
    """
    template_name = 'inventory/home.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['product_form'] = ProductForm
        return context
    

class ProductListDatatableTemplateView(LoginRequiredMixin, TemplateView):
    """
    Render the datatable for the products.
    """

    template_name = 'inventory/datatables/products.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        context['products'] = Product.objects.values('item_code', 'name').distinct()
        return context


class ProductCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when creating products.
    """

    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                variations = parse_variation(request.POST)

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
                    product.quantity = product_variation['quantity']
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


class ProductTemplateView(LoginRequiredMixin, TemplateView):
    """
    Renders the page of the specific product using item_code.
    """

    template_name = 'inventory/product.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        try:
            products = Product.objects.filter(item_code=self.kwargs['item_code'])
        except Product.DoesNotExist:
            raise Http404('Product does not exist')
        context['product'] = products[0]
        context['variations'] = products
        return context
    

class VariationListDatatableTemplateView(LoginRequiredMixin, TemplateView):
    """
    Render the datatable for the product variations.
    """

    template_name = 'inventory/datatables/variations.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        context['variations'] = Product.objects.filter(item_code=self.kwargs['item_code'])
        return context
