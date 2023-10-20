def get_financial_bar_chart(source_name=None):
    """
    Returns the Sales, expenses and profit per month of the current year.
    """
    current_year = timezone.now().year
    sales_data = []
    expenses_data = []
    profit_data = []

    for month in range(1, len(MONTHS) + 1):
        start_date = timezone.datetime(current_year, month, 1)
        end_date = start_date.replace(day=28) + timezone.timedelta(days=4)
        end_date = end_date - timezone.timedelta(days=end_date.day)
        sales = DailySale.total_sales(
            start_date=start_date,
            end_date=end_date,
            source_name=source_name
        )
        expenses = DailyExpense.total_expenses(
            start_date=start_date,
            end_date=end_date,
            source_name=source_name
        )
        profit = sales - expenses

        sales_data.append(sales)
        expenses_data.append(expenses)
        profit_data.append(profit)
    
    sales_data = [decimal_to_float(sale) for sale in sales_data]
    expenses_data = [decimal_to_float(expense) for expense in expenses_data]
    profit_data = [decimal_to_float(profit) for profit in profit_data]
    
    chart_config = {
        'labels': MONTHS,
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
    return chart_config