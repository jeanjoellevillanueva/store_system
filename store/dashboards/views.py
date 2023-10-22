import json
from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views.generic import TemplateView

from expenses.models import Expense
from inventory.models import Product
from pos.models import Sale

from .charts import get_financial_bar_chart
from .charts import get_top_sold_products


class DashboardTemplateView(LoginRequiredMixin, TemplateView):
    """
    TODO
    """
    template_name = 'dashboards/dashboard.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        current_date = date.today()
        start_date = current_date - timedelta(days=7)
        end_date = current_date
        sales = Sale.get_sales_by_date_range(start_date, end_date)
        expenses = Expense.get_expenses_by_date_range(start_date, end_date)
        bar_data = get_financial_bar_chart(sales, expenses, start_date, end_date)

        total_sale = 0
        total_profit = 0
        for sale in sales:
            total_sale += sale['price']
            total_profit += sale['profit']
        total_expense = float(expenses.aggregate(total_amount=Sum('amount'))['total_amount'])

        # Deduct platform fee
        deduction = float(total_sale) * settings.PLATFORM_PERCENTAGE
        total_profit = float(total_profit) - deduction - total_expense

        # Context
        context['start_date'] = start_date
        context['end_date'] = end_date

        # Summary
        context['stock_value'] = Product.stock_value()
        context['total_profit'] = round(total_profit, 2)
        context['total_sale'] = total_sale
        context['total_expense'] = round(total_expense, 2)

        # Chart
        context['bar_data'] = json.dumps(bar_data)
        context['top_sold_products'] = get_top_sold_products(sales)
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = datetime.strptime(self.request.POST['start_date'], settings.DATE_FORMAT)
        end_date = datetime.strptime(self.request.POST['end_date'], settings.DATE_FORMAT)
        sales = Sale.get_sales_by_date_range(start_date, end_date)
        expenses = Expense.get_expenses_by_date_range(start_date, end_date)
        bar_data = get_financial_bar_chart(sales, expenses, start_date, end_date)

        total_sale = 0
        total_profit = 0
        for sale in sales:
            total_sale += sale['price']
            total_profit += sale['profit']
        total_expense = float(expenses.aggregate(total_amount=Sum('amount'))['total_amount'])

        # Deduct platform fee
        deduction = float(total_sale) * settings.PLATFORM_PERCENTAGE
        total_profit = float(total_profit) - deduction - total_expense

        # Context
        context['start_date'] = start_date
        context['end_date'] = end_date

        # Summary
        context['stock_value'] = Product.stock_value()
        context['total_profit'] = round(total_profit, 2)
        context['total_sale'] = total_sale
        context['total_expense'] = round(total_expense, 2)

        # Chart
        context['bar_data'] = json.dumps(bar_data)
        context['top_sold_products'] = get_top_sold_products(sales)
        return self.render_to_response(context)
