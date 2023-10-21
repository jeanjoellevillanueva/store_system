from datetime import timedelta
from decimal import Decimal
from collections import defaultdict

from django.conf import settings
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
                total_profit=Sum('profit')
        )
    )

    for sale in sales:
        date = sale['created_date'].strftime(settings.DATE_FORMAT)
        total_sales = sale['total_sales']
        deduct = float(total_sales) * settings.PLATFORM_PERCENTAGE
        daily_sales[date] += float(sale['total_sales'])
        daily_profit[date] +=  float(sale['total_profit']) - deduct

    # Generate data for Chart.js
    date_range = [(start_date + timedelta(days=i)).strftime(settings.DATE_FORMAT) for i in range((end_date - start_date).days + 1)]
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
            # {
            #     'label': 'Expenses',
            #     'backgroundColor': 'rgba(255, 99, 132, 0.5)',
            #     'borderColor': 'rgba(255, 99, 132, 1)',
            #     'borderWidth': 1,
            #     'data': expenses_data,
            # },
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
