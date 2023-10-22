from datetime import timedelta

import pandas as pd

from django.conf import settings


def get_financial_bar_chart(sales, start_date, end_date):
    """
    Retrieves and formats daily sales, expenses, and profit data for a
    Chart.js bar chart.
    """
    date_range = [
        (start_date + timedelta(days=i)).strftime(settings.DATE_FORMAT)
        for i in range((end_date - start_date).days + 1)
    ]
    daily_sales = {date: 0.00 for date in date_range}
    daily_profit = {date: 0.00 for date in date_range}

    for sale in sales:
        date = sale['created_date'].strftime(settings.DATE_FORMAT)
        total_sale = sale['price']
        deduct = float(total_sale) * settings.PLATFORM_PERCENTAGE
        daily_sales[date] += float(total_sale)
        daily_profit[date] +=  float(sale['profit']) - deduct

    # Generate data for Chart.js
    sales_data = [round(daily_sales[date], 2) for date in date_range]
    profit_data = [round(daily_profit[date], 2) for date in date_range]
    chart_data = {
        'labels': date_range,
        'datasets': [
            {
                'label': 'Sales',
                'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1,
                'data': sales_data,
            },
            {
                'label': 'Profit',
                'backgroundColor': 'rgba(75, 192, 192, 0.5)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 1,
                'data': profit_data,
            },
        ]
    }

    return chart_data


def get_top_sold_products(sales, number_of_items=5):
    """
    Returns a list of top sold items.
    """
    df = pd.DataFrame(sales)
    product_sales = df.groupby('product_name')['quantity'].sum().reset_index()
    top_sold = product_sales.sort_values(by='quantity', ascending=False).head(number_of_items)
    top_products = []
    for _, row in top_sold.iterrows():
        product_info = {
            'name': row['product_name'],
            'quantity': row['quantity']
        }
        top_products.append(product_info)
    return top_products
