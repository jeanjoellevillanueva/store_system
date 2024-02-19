import json
from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict

from braces.views import JSONResponseMixin
import pandas as pd

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.db.models import Sum
from django.views import View
from django.views.generic import TemplateView

from inventory.models import Delivery
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
        context['products'] = (
            Product.objects
                .filter(filter_conditions)
                .order_by('-quantity')
                [:settings.NUMBER_OF_ITEMS]
        )
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


class SaleReportTemplateView(LoginRequiredMixin, TemplateView):
    """
    View used for rendering sales report page.
    """
    template_name = 'pos/sale.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        current_date = date.today()
        start_date = current_date - timedelta(days=7)
        end_date = current_date

        sales_data = Sale.get_sales_by_date_range(start_date, end_date)
        df = pd.DataFrame.from_records(sales_data)
        if not df.empty:
            product_quantities = df.groupby('product_name')['quantity'].sum().reset_index()
            sales = product_quantities.sort_values(by=['quantity'], ascending=False)
        else:
            sales = pd.DataFrame()

        df_receipt = pd.DataFrame.from_records(sales_data)
        if not df_receipt.empty:
            df_receipt.drop_duplicates(
                subset=['receipt_number'], keep='first', inplace=True)
            df_receipt.drop(
                columns=['price', 'profit', 'quantity', 'product_name', 'product_id'], inplace=True)
            sales_per_receipt = df_receipt.sort_values(by=['created_date'], ascending=False)
        else:
            sales_per_receipt = pd.DataFrame()

        context['start_date'] = start_date
        context['end_date'] = end_date
        context['sales_data'] = sales.to_dict('records')
        context['sales_per_receipt'] = sales_per_receipt.to_dict('records')
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = datetime.strptime(self.request.POST['start_date'], settings.DATE_FORMAT)
        end_date = datetime.strptime(self.request.POST['end_date'], settings.DATE_FORMAT)

        sales_data = Sale.get_sales_by_date_range(start_date, end_date)
        df = pd.DataFrame.from_records(sales_data)
        if not df.empty:
            product_quantities = df.groupby('product_name')['quantity'].sum().reset_index()
            sales = product_quantities.sort_values(by=['quantity'], ascending=False)
        else:
            sales = pd.DataFrame()

        df_receipt = pd.DataFrame.from_records(sales_data)
        if not df_receipt.empty:
            df_receipt.drop_duplicates(
                subset=['receipt_number'], keep='first', inplace=True)
            df_receipt.drop(
                columns=['price', 'profit', 'quantity', 'product_name', 'product_id'], inplace=True)
            sales_per_receipt = df_receipt.sort_values(by=['created_date'], ascending=False)
        else:
            sales_per_receipt = pd.DataFrame()

        context['start_date'] = start_date
        context['end_date'] = end_date
        context['sales_data'] = sales.to_dict('records')
        context['sales_per_receipt'] = sales_per_receipt.to_dict('records')
        return self.render_to_response(context)


class ProductSoldTemplateView(LoginRequiredMixin, TemplateView):
    """
    Renders the page for the products sold in specified receipt number.
    """
    template_name = 'pos/product.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['receipt_number'] = self.kwargs['receipt_number']
        return context


class ProductSoldListTemplateView(LoginRequiredMixin, TemplateView):
    """
    Views to render the datatable for the products sold.
    """
    template_name = 'pos/datatables/items_sold.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        items_sold = (
            Sale.objects
                .filter(receipt_number=self.kwargs['receipt_number'])
                .exclude(is_void=True)
        )
        summary = items_sold.aggregate(
            total_profit=Sum('profit'),
            total_amount=Sum('total')
        )
        context['items_sold'] = items_sold
        context['total_amount'] = summary['total_amount']
        context['total_profit'] = summary['total_profit']
        return context


class SaleVoidJSONView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used for voiding a sale.
    """

    def post(self, request, *args, **kwargs):
        try:
            sale = Sale.objects.get(id=self.kwargs['id'])
        except Exception as e:
            # Object not found
            return self.render_json_response({'message': str(e)}, status=404)
        try:
            void_quantity = int(request.POST['void_quantity'])
        except Exception as e:
            return self.render_json_response(
                {'message': 'Quantity must be a whole number.'},
                status=400
            )

        # If void quantity is less than zero or greater than sale quantity,
        # then raise an error.
        if sale.quantity < void_quantity or void_quantity < 1:
            return self.render_json_response(
                {'message': 'Void quantity must be less than the sold quantity or must be greater than 0'}, status=400)
        with transaction.atomic():
            # We will add the quantity back to the product.
            product = Product.objects.get(id=sale.product_id)
            product.quantity = product.quantity + void_quantity
            product.save()

            if sale.quantity == void_quantity:
                sale.is_void = True
            else:
                sale.quantity = sale.quantity - void_quantity
            # Recompute for the profit.
            total_capital = (sale.quantity * sale.capital)
            total_sales = (sale.quantity * sale.price)
            profit = total_sales - total_capital
            sale.total = total_sales
            sale.profit = profit
            sale.save()

            # We will also add the report in the deliveries.
            delivery_kwargs = {
                'product_id': product.id,
                'product_item_code': product.item_code,
                'product_name': f'{product.name} ({product.variation})',
                'quantity': sale.quantity,
                'reason': Delivery.RETURNED,
                'created_by': self.request.user,
            }
            Delivery.objects.create(**delivery_kwargs)

        json_data = {
            'message': 'Void was successful'
        }
        return self.render_json_response(json_data, status=204)


class RecentlySoldTemplateView(LoginRequiredMixin, TemplateView):
    """
    A view to render the recently sold items.
    """

    template_name = 'pos/datatables/recently_sold.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['recent_sales'] = Sale.objects.filter(is_void=False).order_by('-id')[:5]
        return context
