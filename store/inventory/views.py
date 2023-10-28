from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict

from braces.views import JSONResponseMixin

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404
from django.views import View
from django.views.generic import TemplateView

from .forms import DeliveryAddForm
from .forms import DeliverySubtractForm
from .forms import ProductForm
from .forms import ProductUpdateForm
from .forms import VariationUpdateForm
from .models import Delivery
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
        ).order_by('name').distinct()
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

                # Check if item code already exists.
                is_exist = (
                    Product.objects
                        .filter(item_code=form.cleaned_data['item_code'])
                        .exclude(item_code=request.POST['old_item_code'])
                )
                if is_exist:
                    form_error = {}
                    form_error['item_code'] = ['Item code already exists.']
                    json_data = {'status': 'error', 'errors': form_error}
                    return self.render_json_response(json_data, status=400)

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
        context['delivery_add_form'] = DeliveryAddForm(auto_id='id_%s_add_deliver')
        context['delivery_subtract_form'] = DeliverySubtractForm(auto_id='id_%s_sub_deliver')
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
            'message': 'Successfully deleted'
        }
        return self.render_json_response(json_data, status=204)


class DeliveryCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when adding stock of a product.
    """

    def post(self, request, *args, **kwargs):
        out_choices = [choice[0] for choice in Delivery.OUT_CHOICES]
        if request.POST.get('reason') in out_choices:
            form = DeliverySubtractForm(request.POST)
        else:
            form = DeliveryAddForm(request.POST)
        if form.is_valid():
            try:
                product = Product.objects.filter(id=self.kwargs['product_id'])[0]
            except Product.DoesNotExist:
                json_data = {'status': 'error', 'errors': {
                    'name': 'Product does not exists.'}}
                return self.render_json_response(json_data, status=404)
            with transaction.atomic():
                current_quantity = product.quantity
                quantity_to_add = int(form.cleaned_data['quantity'])
                reason = form.cleaned_data['reason']
                if reason in out_choices:
                    if quantity_to_add > current_quantity:
                        json_data = {'status': 'error', 'errors': {
                            'quantity': 'Cannot exceed the quantity in stock.'}}
                        return self.render_json_response(json_data, status=403)
                    product.quantity = current_quantity - quantity_to_add
                else:
                    product.quantity = current_quantity + quantity_to_add
                product.save()
                delivery_kwargs = {
                    'product_id': product.id,
                    'product_item_code': product.item_code,
                    'product_name': f'{product.name} ({product.variation})',
                    'quantity': quantity_to_add,
                    'reason': form.cleaned_data['reason'],
                    'created_by': self.request.user,
                }
                Delivery.objects.create(**delivery_kwargs)
                json_data = {
                    'status': 'success',
                    'message': 'Delivery Successful'
                }
                return self.render_json_response(json_data, status=200)
        json_data = {'status': 'error', 'errors': form.errors}
        return self.render_json_response(json_data, status=400)


class DeliveryReportTemplateView(LoginRequiredMixin, TemplateView):
    """
    Report page for the deliveries.
    """
    template_name = 'inventory/delivery.html'


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        current_date = date.today()
        start_date = current_date - timedelta(days=7)
        end_date = current_date
        context['start_date'] = start_date
        context['end_date'] = end_date
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = datetime.strptime(self.request.POST['start_date'], settings.DATE_FORMAT)
        end_date = datetime.strptime(self.request.POST['end_date'], settings.DATE_FORMAT)
        context['start_date'] = start_date
        context['end_date'] = end_date
        return self.render_to_response(context)


class DeliveryListTemplateView(LoginRequiredMixin, TemplateView):
    """
    View used for loading the list of deliveries.
    """
    template_name = 'inventory/datatables/deliveries.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        date_filter = {'created_date__date__range': (datetime.today(), datetime.today())}
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date and end_date:
            start_date = datetime.strptime(self.request.GET['start_date'], settings.DATE_FORMAT)
            end_date = datetime.strptime(self.request.GET['end_date'], settings.DATE_FORMAT)
            date_filter = {
                'created_date__date__range': (start_date, end_date), 
            }
        context['deliveries'] = (
            Delivery.objects
                .filter(**date_filter)
                .order_by('-created_date')
        )
        delivery_inchoices = [choice[0] for choice in Delivery.IN_CHOICES]
        context['deliver_inchoices'] = delivery_inchoices
        return context
