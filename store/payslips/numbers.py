import inflect


def convert_number_to_words(number):
    """
    Converts numbers to words.
    """
    p = inflect.engine()
    
    # Split the number into integer and decimal parts
    integer_part, decimal_part = str(number).split('.')
    integer_words = p.number_to_words(int(integer_part))
    # Convert decimal part (cents) manually
    cents = int(decimal_part.ljust(2, '0'))  # Pad to ensure two digits for cents
    if cents == 0:
        cents_words = 'zero cents'
    else:
        cents_words = f'{p.number_to_words(cents)} cents'
    return f'{integer_words} and {cents_words}'
