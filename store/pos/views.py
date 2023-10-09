import json
from typing import Any

from braces.views import JSONResponseMixin

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views import View
from django.views.generic import TemplateView

from inventory.models import Product
from inventory.utils import get_checkout_detail


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
        print(products)
        return self.render_to_response(context)


class SaleCustomCreateView(LoginRequiredMixin, JSONResponseMixin, View):
    """
    View used when creating a new sale.
    """

    def post(self, request, *args, **kwargs):
        import pdb; pdb.set_trace()
        return self.render_to_response()
