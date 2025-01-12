import re
from typing import List

from django.conf import settings


def is_file_supported(
        filename:str, supported_extensions:List[str], supported_filenames:List[str]) -> bool:
    """
    Check if the file is supported.
    """

    pattern = re.compile('|'.join(map(re.escape, supported_filenames)))
    extension = filename.split('.')[-1]
    if extension not in supported_extensions:
        return False
    return bool(pattern.search(filename))


def is_shopee_file(filename:str) -> bool:
    """
    Returns a boolean if the file is shopee or not.
    """
    
    return is_file_supported(
            filename, [settings.EXTENSION_EXCEL], [settings.FILENAME_SHOPEE])


def is_tiktok_file(filename:str) -> bool:
    """
    Returns a boolean if the file is tiktok or not.
    """
    
    return is_file_supported(
            filename, [settings.EXTENSION_EXCEL], [settings.FILENAME_TIKTOK])
