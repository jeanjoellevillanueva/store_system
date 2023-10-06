def parse_variation(orig_dict):
    """
    Parse the variation and quantity in the dict.
    """

    variations = []
    for key, value in orig_dict.items():
        if key.startswith('variation_'):
            _, number = key.split('_')
            quantity_key = f'quantity_{number}'
            price_key = f'price_{number}'
            capital_key = f'capital_{number}'
            variations.append({
                'orig_key': key,
                'variation': value,
                'quantity': orig_dict.get(quantity_key, 0),
                'price': orig_dict.get(price_key, 0),
                'capital': orig_dict.get(capital_key, 0),
            })
    return variations
