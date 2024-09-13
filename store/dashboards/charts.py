from decimal import Decimal
from datetime import timedelta

import calendar
import pandas as pd
import pytz

from django.conf import settings

from inventory.models import Product
from pos.models import Sale

def get_financial_bar_chart(sales, expenses, start_date, end_date):
    """
    Retrieves and formats daily sales, expenses, and profit data for a
    Chart.js bar chart.
    """

    date_range = []
    for i in range((end_date - start_date).days + 1):
        date_str = (
            start_date + timedelta(days=i)).strftime(settings.DATE_FORMAT)
        date_range.append(date_str)

    daily_sales = {date: 0.00 for date in date_range}
    daily_orders = {date: 0.00 for date in date_range}
    daily_expenses = {date: 0.00 for date in date_range}
    daily_profit = {date: 0.00 for date in date_range}
    count=1

    sorted_receipts = Sale.objects.order_by('created_date')
    sorted_receipts = Sale.objects.filter(
        created_date__date__range=(
        start_date, end_date)).values(
        'receipt_number', 'created_date').distinct(
        'receipt_number')
    for receipt in sorted_receipts:
        date = (receipt['created_date'].astimezone().strftime(settings.DATE_FORMAT))
        daily_orders[date] += 1

    for sale in sales:
        date = (
            sale['created_date']
            .astimezone()
            .strftime(settings.DATE_FORMAT)
        )
        count += 1
        total_sale = (sale['price'] * sale['quantity'])
        deduct = float(total_sale) * settings.PLATFORM_PERCENTAGE
        daily_sales[date] += float(total_sale)
        daily_profit[date] +=  float(sale['profit']) - deduct
    
    for expense in expenses:
        date = (expense['expense_date'].strftime(settings.DATE_FORMAT))
        daily_expenses[date] += float(expense['amount'])
        daily_profit[date] -= float(expense['amount'])

    # Generate data for Chart.js
    sales_data = [round(daily_sales[date], 2) for date in date_range]
    orders_data = [round(daily_orders[date], 2) for date in date_range]
    expenses_data = [round(daily_expenses[date], 2) for date in date_range]
    profit_data = [round(daily_profit[date], 2) for date in date_range]
    chart_data = {
        'labels': date_range,
        'datasets': [
            {
                'label': 'Sales',
                'backgroundColor': settings.PRIMARY_COLOR,
                'data': sales_data,
            },
            {
                'label': 'Orders',
                'backgroundColor': settings.PRIMARY_COLOR,
                'data': orders_data,
                'fill': False,
                'display': False,
                'hidden': True,
            },
            {
                'label': 'Expenses',
                'backgroundColor': settings.DANGER_COLOR,
                'data': expenses_data,
            },
            {
                'label': 'Profit',
                'backgroundColor': settings.SUCCESS_COLOR,
                'data': profit_data,
            },
        ]
    }
    return chart_data


def get_top_sold_products(sales, number_of_items=10):
    """
    Returns a list of top sold items.
    """
    top_products = []
    df = pd.DataFrame(sales)
    if df.empty:
        return top_products
    agg_params = {
        'quantity': 'sum',
        'computed_profit': 'sum',
    }
    # Compute for the estimated profit deducting the platform fee.
    df['computed_profit'] = df['profit'] - (df['price'] * df['quantity'] * Decimal(str(settings.PLATFORM_PERCENTAGE)))
    # Group by 'product_id' and sum 'quantity', 'computed_profit'.
    product_sales_df = df.groupby('product_id').agg(agg_params).reset_index()

    product_data = Product.objects.values('id', 'item_code')
    product_dict = {str(item['id']): item['item_code'] for item in product_data}
    # Map 'product_id' to 'item_code'
    product_sales_df['item_code'] = product_sales_df['product_id'].map(product_dict)
    
    # Group by 'item_code' and sum 'quantity' and 'computed_profit'
    product_sales_df = product_sales_df.groupby('item_code').agg(agg_params).reset_index()
    top_sold = product_sales_df.sort_values(by='quantity', ascending=False).head(number_of_items)
    top_sold['ave_profit_per_pc'] = top_sold['computed_profit'] / top_sold['quantity']

    for _, row in top_sold.iterrows():
        product_info = {
            'name': row['item_code'],
            'quantity': row['quantity'],
            'computed_profit': round(row['computed_profit'], 2),
            'ave_profit_per_pc': round(row['ave_profit_per_pc'], 2),
        }
        top_products.append(product_info)
    return top_products


def get_month_financial_bar_chart(sales, expenses, start_date, end_date):
    """
    Retrieves and formats monthly sales, expenses, and profit data for a
    Chart.js bar chart.
    """  
    # Helper function to format month-year
    def format_month_year(date):
        return date.strftime('%Y-%m')
    
    date_range = []
    current_date = start_date.replace(day=1)
    
    while current_date <= end_date:
        date_str = format_month_year(current_date)
        date_range.append(date_str)
        next_month = current_date.month % 12 + 1
        next_year = current_date.year if next_month > 1 else current_date.year + 1
        current_date = current_date.replace(year=next_year, month=next_month, day=1)

    monthly_sales = {date: 0.00 for date in date_range}
    monthly_orders= {date: 0.00 for date in date_range}
    monthly_expenses = {date: 0.00 for date in date_range}
    monthly_profit = {date: 0.00 for date in date_range}

    sorted_receipts = Sale.objects.order_by('created_date')
    sorted_receipts = Sale.objects.filter(
        created_date__date__range=(
        start_date, end_date)).values(
        'receipt_number', 'created_date').distinct(
        'receipt_number')
    monthly_receipt = [{
        **receipt, 
        'month': receipt['created_date'].astimezone().strftime('%Y-%m')
    } for receipt in sorted_receipts]

    for receipt in monthly_receipt:
        month = receipt['month']
        monthly_orders[month] += 1

    for sale in sales:
        date = format_month_year(sale['created_date'].astimezone())
        total_sale = sale['price'] * sale['quantity']
        deduct = float(total_sale) * settings.PLATFORM_PERCENTAGE
        monthly_sales[date] += float(total_sale)
        monthly_profit[date] += float(sale['profit']) - deduct
    
    for expense in expenses:
        date = format_month_year(expense['expense_date'])
        monthly_expenses[date] += float(expense['amount'])
        monthly_profit[date] -= float(expense['amount'])
    
    # Generate data for Chart.js
    sales_data = [round(monthly_sales[date], 2) for date in date_range]
    orders_data = [round(monthly_orders[date], 2) for date in date_range]
    expenses_data = [round(monthly_expenses[date], 2) for date in date_range]
    profit_data = [round(monthly_profit[date], 2) for date in date_range]
    chart_month_data = {
        'labels': date_range,
        'datasets': [
            {
                'label': 'Sales',
                'backgroundColor': settings.PRIMARY_COLOR,
                'data': sales_data,
            },
            {
                'label': 'Orders',
                'backgroundColor': settings.PRIMARY_COLOR,
                'data': orders_data,
                'fill': False,
                'display': False,
                'hidden': True,
            },
            {
                'label': 'Expenses',
                'backgroundColor': settings.DANGER_COLOR,
                'data': expenses_data,
            },
            {
                'label': 'Profit',
                'backgroundColor': settings.SUCCESS_COLOR,
                'data': profit_data,
            },

        ]
    }
    return chart_month_data
