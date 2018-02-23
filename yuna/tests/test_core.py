import unittest
from unittest.mock import patch

from ..core import SourceSingleton


class TestCore(unittest.TestCase):

    def test_change_stock(self):
        stocks = ['000001', '600000', '300001']
        expected_change_stock = SourceSingleton.change_stock(stocks)
        self.assertEqual(expected_change_stock, ['000001.SZ', '600000.SH', '300001.SZ'])
