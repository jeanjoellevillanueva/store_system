import json
from datetime import date
from datetime import datetime
from typing import Any
from typing import Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db.models import DecimalField
from django.db.models import ExpressionWrapper
from django.db.models import F
from django.views.generic import TemplateView

from inventory.models import Product
from pos.models import Sale

from .charts import get_financial_bar_chart


class DashboardTemplateView(LoginRequiredMixin, TemplateView):
    """
    TODO
    """
    template_name = 'dashboards/dashboard.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        current_date = date.today()# - timedelta(days=1)
        context['start_date'] = current_date
        context['end_date'] = current_date
        sale = (
            Sale.objects
                .filter(created_date__date__range=(current_date, current_date))
                .aggregate(
                    total_profit=Sum('profit'),
                    total_sale=Sum('price')
                )
        )
        total_value = Product.objects.annotate(
            product_value=ExpressionWrapper(F('quantity') * F('capital'), output_field=DecimalField())
        ).aggregate(total_value=Sum('product_value'))

        total_cash_in_stock = total_value['total_value']
        deduct = float(sale['total_sale']) * 0.15
        bar_data = get_financial_bar_chart(current_date, current_date)
        context['bar_data'] = json.dumps(bar_data)
        context['total_cash_in_stock'] = total_cash_in_stock
        context['total_profit'] = float(sale['total_profit']) - deduct
        context['total_sale'] = sale['total_sale']
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = datetime.strptime(self.request.POST['start_date'], '%m/%d/%Y')
        end_date = datetime.strptime(self.request.POST['end_date'], '%m/%d/%Y')
        sale = (
            Sale.objects
                .filter(created_date__date__range=(start_date, end_date))
                .aggregate(
                    total_profit=Sum('profit'),
                    total_sale=Sum('price')
                )
        )
        total_value = Product.objects.annotate(
            product_value=ExpressionWrapper(F('quantity') * F('capital'), output_field=DecimalField())
        ).aggregate(total_value=Sum('product_value'))

        total_cash_in_stock = total_value['total_value']
        deduct = float(sale['total_sale']) * 0.15
        bar_data = get_financial_bar_chart(start_date, end_date)
        try:
            context['bar_data'] = json.dumps(bar_data)
        except:
            import pdb; pdb.set_trace()
        context['total_cash_in_stock'] = total_cash_in_stock
        context['total_profit'] = float(sale['total_profit']) - deduct
        context['total_sale'] = sale['total_sale']
        return self.render_to_response(context)
