from datetime import timedelta
from decimal import Decimal
from collections import defaultdict

from django.db.models import Sum

from pos.models import Sale


def get_financial_bar_chart(start_date, end_date):
    """
    Retrieves and formats daily sales, expenses, and profit data for a
    Chart.js bar chart.
    """
    # Initialize dictionaries to store daily data
    daily_sales = defaultdict(float)
    daily_expenses = defaultdict(float)
    daily_profit = defaultdict(float)

    # Query the database for relevant sales data within the date range
    sales = (
        Sale.objects
            .filter(created_date__date__range=(start_date, end_date))
            .values('created_date')
            .annotate(
                total_sales=Sum('total'),
                total_expenses=Sum('capital'),
                total_profit=Sum('profit')
        )
    )

    for sale in sales:
        date = sale['created_date'].strftime('%Y-%m-%d')
        daily_sales[date] = float(sale['total_sales'])
        daily_expenses[date] =  float(sale['total_expenses'])
        daily_profit[date] =  float(sale['total_profit'])

    # Generate data for Chart.js
    date_range = [str(start_date + timedelta(days=i)) for i in range((end_date - start_date).days + 1)]
    sales_data = [daily_sales[date] for date in date_range]
    expenses_data = [daily_expenses[date] for date in date_range]
    profit_data = [daily_profit[date] for date in date_range]

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
                'label': 'Expenses',
                'backgroundColor': 'rgba(255, 99, 132, 0.5)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1,
                'data': expenses_data,
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
