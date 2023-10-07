from datetime import datetime
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
from .forms import ProductUpdateForm
from .forms import VariationUpdateForm
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
        context['product_update_form'] = ProductUpdateForm(auto_id='id_%s_update')
        return context
    

class ProductListDatatableTemplateView(LoginRequiredMixin, TemplateView):
    """
    Render the datatable for the products.
    """

    template_name = 'inventory/datatables/products.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        context['products'] = Product.objects.values(
            'item_code',
            'name',
            'description'
        ).distinct()
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


class ProductCustomUpdateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when updating products.
    """

    def post(self, request, *args, **kwargs):
        form = ProductUpdateForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                try:
                    products = Product.objects.filter(item_code=request.POST['old_item_code'])
                except Product.DoesNotExist:
                    raise Http404('Product does not exist')
                for product in products:
                    product.item_code = form.cleaned_data['item_code']
                    product.name = form.cleaned_data['name']
                    product.description = form.cleaned_data['description']
                    product.updated_date = datetime.today()
                    product.updated_by = request.user
                    product.save()
                json_data = {
                    'status': 'success',
                    'message': 'Product successfully Updated.'
                }
                return  self.render_json_response(json_data, status=200)
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
        context['variation_update_form'] = VariationUpdateForm(auto_id='id_%s_update')
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


class VariationCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when creating product variation.
    """

    def post(self, request, *args, **kwargs):
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
            
            try:
                sample_product = Product.objects.filter(item_code=self.kwargs['item_code'])
            except Product.DoesNotExist:
                raise Http404('Product Does Not Exist')
            
            sample_product = sample_product[0]
            # If items are valid then continue to save to the database.
            for product_variation in variations:
                product = Product(
                    item_code=sample_product.item_code,
                    name=sample_product.name,
                    description=sample_product.description,
                )
                product.pk = None  # Reset the primary key to create a new instance.
                product.variation = product_variation['variation']
                product.quantity = product_variation['quantity']
                product.price = product_variation['price']
                product.capital = product_variation['capital']
                product.created_by = request.user
                product.save()
            json_data = {
                'status': 'success',
                'message': 'Product Variation successfully created.'
            }
            return  self.render_json_response(json_data, status=201)


class VariationCustomUpdateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when updating product variation.
    """

    def post(self, request, *args, **kwargs):
        form = VariationUpdateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                try:
                    product = Product.objects.get(id=self.kwargs['id'])
                except Product.DoesNotExist:
                    raise Http404('Product does not exist')
                product.variation = form.cleaned_data['variation']
                product.price = form.cleaned_data['price']
                product.capital = form.cleaned_data['capital']
                product.quantity = form.cleaned_data['quantity']
                product.updated_date = datetime.today()
                product.updated_by = request.user
                product.save()
                json_data = {
                    'status': 'success',
                    'message': 'Product variation successfully Updated.'
                }
                return  self.render_json_response(json_data, status=200)
        json_data = {'status': 'error', 'errors': form.errors}
        return self.render_json_response(json_data, status=400)


class VariationCustomDeleteView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used for deleting a product.
    """

    def post(self, request, *args, **kwargs):
        try:
            product = Product.objects.get(id=self.kwargs['id'])
        except Exception as e:
             # Object not found
             return self.render_json_response({'message': str(e)}, status=404)
        product.delete()
        json_data = {
            'message': 'Successfully deleted.'
        }
        return self.render_json_response(json_data, status=204)
