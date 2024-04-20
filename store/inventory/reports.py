import pandas as pd


def extract_orders_from_xlsx(filename='shopee.xlsx'):
    """
    Extract Shopee order file and returns a dict of product: num of order.
    """
    if filename.casefold() == 'shopee.xlsx':
        SKU_COL = 'SKU Reference No.'
    elif filename.casefold() == 'tiktok.xlsx':
        SKU_COL = 'Seller SKU'
    else:
        raise ValueError('File not supported.')
    QUANTITY_COL = 'Quantity'
    ORDER_STATUS_COL = 'Order Status'
    file_path = f'files/{filename}'
    df = pd.read_excel(file_path)
    col_list = [ORDER_STATUS_COL, SKU_COL, QUANTITY_COL]
    df = df[col_list]
    df = df[df[ORDER_STATUS_COL].str.lower() == 'to ship']
    df = df.drop(ORDER_STATUS_COL, axis=1)
    df = df.groupby(SKU_COL, as_index=False).agg({QUANTITY_COL: 'sum'})
    products = df.to_dict(orient='records')
    order_info = {}
    for product in products:
        dict_key = product[SKU_COL]
        dict_value = product[QUANTITY_COL]
        order_info[dict_key] = dict_value
    return order_info


def combine_to_ship_orders(filenames:list):
    SKU = 'SKU'
    QUANTITY = 'Quantity'
    params = {0: SKU, 1: QUANTITY}
    order_array = []
    for to_ship_file in filenames:
        order_dict = extract_orders_from_xlsx(to_ship_file)
        order_df = pd.DataFrame(order_dict.items()).rename(columns=params)
        order_array.append(order_df)

    merged_df = (
        pd.concat(order_array)
        .groupby(SKU, as_index=False)[QUANTITY]
        .sum()
        .sort_values('SKU')
    )
    products = merged_df.to_dict(orient='records')
    merged_order_info = {}
    for product in products:
        product_id = product[SKU]
        product_quantity = product[QUANTITY]
        merged_order_info[product_id] = product_quantity
    return merged_order_info
