from datetime import timedelta

import pandas as pd

from django.conf import settings


def get_financial_bar_chart(sales, expenses, start_date, end_date):
    """
    Retrieves and formats daily sales, expenses, and profit data for a
    Chart.js bar chart.
    """
    date_range = []
    for i in range((end_date - start_date).days + 1):
        date_str = (start_date + timedelta(days=i)).strftime(settings.DATE_FORMAT)
        date_range.append(date_str)

    daily_sales = {date: 0.00 for date in date_range}
    daily_expenses = {date: 0.00 for date in date_range}
    daily_profit = {date: 0.00 for date in date_range}
    count=1
    for sale in sales:
        date = sale['created_date'].strftime(settings.DATE_FORMAT)
        count += 1
        total_sale = (sale['price'] * sale['quantity'])
        deduct = float(total_sale) * settings.PLATFORM_PERCENTAGE
        daily_sales[date] += float(total_sale)
        daily_profit[date] +=  float(sale['profit']) - deduct
    
    for expense in expenses:
        date = expense['expense_date'].strftime(settings.DATE_FORMAT)
        daily_expenses[date] += float(expense['amount'])
        daily_profit[date] -= float(expense['amount'])

    # Generate data for Chart.js
    sales_data = [round(daily_sales[date], 2) for date in date_range]
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


def get_top_sold_products(sales, number_of_items=5):
    """
    Returns a list of top sold items.
    """
    top_products = []
    df = pd.DataFrame(sales)
    if df.empty:
        return top_products
    product_sales = df.groupby('product_name')['quantity'].sum().reset_index()
    top_sold = product_sales.sort_values(by='quantity', ascending=False).head(number_of_items)
    for _, row in top_sold.iterrows():
        product_info = {
            'name': row['product_name'],
            'quantity': row['quantity']
        }
        top_products.append(product_info)
    return top_products
