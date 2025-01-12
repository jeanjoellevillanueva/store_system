from django.test import TestCase

from ..validation import is_file_supported
from ..validation import is_shopee_file
from ..validation import is_tiktok_file


class FileSupportedValidationTestCase(TestCase):
    """
    Test to check the `is_file_supported` function.
    """

    def setUp(self):
        self.supported_files = ['tiktok', 'shopee']
        self.supported_extensions = ['xlsx']
        self.supported_filename = 'tiktok1.xlsx'
        self.unsupported_filename = 'unsupported.xlsx'

    def test_supported_filename(self):
        self.assertEqual(
            is_file_supported(
                self.supported_filename, self.supported_extensions, self.supported_files),
            True
        )
    
    def test_unsupported_filename(self):
        self.assertEqual(
            is_file_supported(
                self.unsupported_filename, self.supported_extensions, self.supported_files),
            False
        )


class ShopeeFileValidationTestCase(TestCase):
    """
    Test to check the `is_shopee_file` function.
    """

    def setUp(self):
        self.supported_filename = 'shopee+1.xlsx'
        self.unsupported_filename = 'unsupported.xlsx'

    def test_supported_filename(self):
        self.assertEqual(is_shopee_file(self.supported_filename), True)
    
    def test_unsupported_filename(self):
        self.assertEqual(is_shopee_file(self.unsupported_filename), False)


class TiktokFileValidationTestCase(TestCase):
    """
    Test to check the `is_tiktok_file` function.
    """

    def setUp(self):
        self.supported_filename = 'tiktok~1.xlsx'
        self.unsupported_filename = 'unsupported.xlsx'

    def test_supported_filename(self):
        self.assertEqual(is_tiktok_file(self.supported_filename), True)
    
    def test_unsupported_filename(self):
        self.assertEqual(is_tiktok_file(self.unsupported_filename), False)
