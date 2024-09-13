import json
from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict

import pandas as pd

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views.generic import TemplateView

from expenses.models import Expense
from inventory.models import Product
from pos.models import Sale

from .charts import get_financial_bar_chart
from .charts import get_month_financial_bar_chart
from .charts import get_top_sold_products


class DashboardTemplateView(LoginRequiredMixin, TemplateView):
    """
    Renders the dashboard for the entire Point of Sale (POS) system, providing an
    analysis and overview of key business metrics and performance.
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
        bar_month_data = get_month_financial_bar_chart(sales, expenses, start_date, end_date)

        total_sale = 0
        total_expense = 0
        total_profit = 0
        for sale in sales:
            total_sale += (sale['price'] * sale['quantity'])
            total_profit += sale['profit']
        if expenses:
            total_expense = float(expenses.aggregate(total_amount=Sum('amount'))['total_amount'])

        df_receipt = pd.DataFrame.from_records(sales)
        if not df_receipt.empty:
            df_receipt.drop_duplicates(
                subset=['receipt_number'], keep='first', inplace=True)
            df_receipt = df_receipt[['receipt_number']]
            number_of_items = len(df_receipt)
        else:
            number_of_items = 0

        # Deduct platform fee
        deduction = float(total_sale) * settings.PLATFORM_PERCENTAGE
        total_net_profit = float(total_profit)
        total_gross_profit = float(total_profit) - deduction - total_expense

        # Context
        context['start_date'] = start_date
        context['end_date'] = end_date

        context['date_start'] = start_date.isoformat()
        context['date_end'] = end_date.isoformat()
        # Summary
        context['stock_value'] = Product.stock_value()
        context['total_net_profit'] = round(total_net_profit, 2)
        context['total_gross_profit'] = round(total_gross_profit, 2)
        context['total_sale'] = total_sale
        context['total_expense'] = round(total_expense, 2)
        context['total_platform_fee'] = round(deduction, 2)
        context['number_of_items'] = number_of_items
        context['item_sold'] = len(sales)
        total_stock = Product.objects.aggregate(total=Sum('quantity'))
        total_stock = total_stock['total']
        context['total_stock'] = total_stock

        # Chart
        context['bar_data'] = json.dumps(bar_data)
        context['bar_month_data'] = json.dumps(bar_month_data)
        context['top_sold_products'] = get_top_sold_products(sales)
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = datetime.strptime(self.request.POST['start_date'], settings.DATE_FORMAT)
        end_date = datetime.strptime(self.request.POST['end_date'], settings.DATE_FORMAT)
        sales = Sale.get_sales_by_date_range(start_date, end_date)
        expenses = Expense.get_expenses_by_date_range(start_date, end_date)
        bar_data = get_financial_bar_chart(sales, expenses, start_date, end_date)
        bar_month_data = get_month_financial_bar_chart(sales, expenses, start_date, end_date)
        total_sale = 0
        total_expense = 0
        total_profit = 0
        for sale in sales:
            total_sale += (sale['price'] * sale['quantity'])
            total_profit += sale['profit']
        if expenses:
            total_expense = float(expenses.aggregate(total_amount=Sum('amount'))['total_amount'])

        df_receipt = pd.DataFrame.from_records(sales)
        if not df_receipt.empty:
            df_receipt.drop_duplicates(
                subset=['receipt_number'], keep='first', inplace=True)
            df_receipt = df_receipt[['receipt_number']]
            number_of_items = len(df_receipt)
        else:
            number_of_items = 0

        # Deduct platform fee
        deduction = float(total_sale) * settings.PLATFORM_PERCENTAGE
        total_net_profit = float(total_profit)
        total_gross_profit = float(total_profit) - deduction - total_expense

        # Context
        context['start_date'] = start_date
        context['end_date'] = end_date

        context['date_start'] = start_date.isoformat()
        context['date_end'] = end_date.isoformat()

        # Summary
        context['stock_value'] = Product.stock_value()
        context['total_net_profit'] = round(total_net_profit, 2)
        context['total_gross_profit'] = round(total_gross_profit, 2)
        context['total_sale'] = total_sale
        context['total_expense'] = round(total_expense, 2)
        context['total_platform_fee'] = round(deduction, 2)
        context['number_of_items'] = number_of_items
        context['item_sold'] = len(sales)
        total_stock = Product.objects.aggregate(total=Sum('quantity'))
        total_stock = total_stock['total']
        context['total_stock'] = total_stock

        # Chart
        context['bar_data'] = json.dumps(bar_data)
        context['bar_month_data'] = json.dumps(bar_month_data)
        context['top_sold_products'] = get_top_sold_products(sales)
        return self.render_to_response(context)   
