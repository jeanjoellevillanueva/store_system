from decimal import Decimal

from .models import Product


def parse_variation(orig_dict):
    """
    Parse the variation and quantity in the dict.
    """

    variations = []
    for key, value in orig_dict.items():
        if key.startswith('variation_'):
            _, number = key.split('_')
            price_key = f'price_{number}'
            capital_key = f'capital_{number}'
            variations.append({
                'orig_key': key,
                'variation': value,
                'price': orig_dict.get(price_key, 0),
                'capital': orig_dict.get(capital_key, 0),
            })
    return variations


def get_checkout_detail(product_data):
    """
    Returns a list of products with checkout details.
    """
    checkout_data = []
    product_ids = []
    sale_info = {}
    for product in product_data:
        for product_id, value in product.items():
            product_ids.append(product_id)
            sale_info[product_id] = value
    
    products = Product.objects.filter(id__in=product_ids)
    for product in products:
        product_id = str(product.id)
        quantity = sale_info[product_id]['quantity']
        ordering = sale_info[product_id]['ordering']
        total_capital = (quantity * product.capital)
        total_sales = (quantity * product.price)
        profit = total_sales - total_capital
        checkout_info = {
            'ordering': ordering,
            'name': f'{product.name} ({product.variation})',
            'id': product_id,
            'quantity': quantity,
            'total': total_sales,
            'in_stock': product.quantity,
            'price': product.price,
            'capital': product.capital,
            'profit': profit,
        }
        checkout_data.append(checkout_info)
    return sorted(checkout_data, key=lambda x: x['ordering'])


def compute_total(product_list):
    """
    Computes the total of the entire product list.
    """

    total = Decimal('0.00')
    for product in product_list:
        total += product['total']
    return total
