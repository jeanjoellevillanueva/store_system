import json
from typing import Any

from braces.views import JSONResponseMixin

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.views import View
from django.views.generic import TemplateView

from inventory.models import Product
from inventory.utils import compute_total
from inventory.utils import get_checkout_detail

from .models import Sale


class POSTemplateView(LoginRequiredMixin, TemplateView):
    """
    View used for rendering cash register page.
    """
    template_name = 'pos/home.html'


class POSProductListTemplateView(LoginRequiredMixin, TemplateView):
    """
    View used for rendering product list on cash register.
    """
    template_name = 'pos/component/cash-register-products.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        searched_term = self.request.GET.get('searched_term')
        if not searched_term:
            searched_term = ''
        filter_conditions = (
            Q(name__icontains=searched_term) |
            Q(item_code__icontains=searched_term) |
            Q(variation__icontains=searched_term)
        )
        context['products'] = Product.objects.filter(filter_conditions)[:12]
        return context
    

class POSCheckOutTemplateView(LoginRequiredMixin, TemplateView):
    """
    View used for rendering checkout component.
    """
    template_name = 'pos/component/checkout.html'

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        data = json.loads(request.body.decode('utf-8'))
        product_data = data['products_in_json']
        products = get_checkout_detail(product_data)
        context['products'] = products
        context['products'] = products
        context['total'] = compute_total(products)
        return self.render_to_response(context)


class SaleCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when creating a new sale.
    """

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        product_data = data['products_in_json']
        products = get_checkout_detail(product_data)
        sale_instances = []
        status = 500
        with transaction.atomic():
            # For each sale, we will only generate one receipt even if the
            # sale consisted of multiple products.
            receipt_number = Sale.generate_receipt_number()
            for product in products:
                product_id = product['id']
                product_name = product['name']
                capital = product['capital']
                price = product['price']
                quantity = product['quantity']
                discount = 0 # Default to zero because this is not yet implemented.
                total = product['total']
                profit = product['profit']
                in_stock = product['in_stock']

                # We cannot have negative stock so we will raise
                # a vaildation error if this happen.
                if in_stock < quantity:
                    data = {
                        'status': 'failed',
                        'message': 'Insufficient inventory stock available'
                    }
                    return self.render_json_response(data, status=400)
                
                # Update the stock.
                Product.update_stock(product_id, quantity)

                # Create a Sale instance and append it to the list
                sale_instance = Sale(
                    receipt_number=receipt_number,
                    product_id=product_id,
                    product_name=product_name,
                    capital=capital,
                    price=price,
                    quantity=quantity,
                    discount=discount,
                    total=total,
                    profit=profit,
                )
                sale_instances.append(sale_instance)
            # Save the created objects.
            Sale.objects.bulk_create(sale_instances)
            status = 201
        data = {
            'status': 'success',
            'message': 'Transaction was successful'
        }
        return self.render_json_response(data, status)
