"""
测试Tushare财经库，使用数据为股票康得新16年5月31至16年6月3日的k线数据，以检验数据是否前复权
"""

import unittest
import datetime
from unittest import skipIf
from unittest.mock import Mock, patch, DEFAULT

import pandas as pd

from yuna.sources.tushare import TuShareSource

SKIP_REAL = True
ACTUAL_DATES = ['2016-05-31', '2016-06-03']
ACTUAL_CLOSE = [16.413, 16.552, 16.791, 17.08]
ACTUAL_HIGH = [16.462, 16.721, 17.001, 17.489]
ACTUAL_LOW = [15.825, 16.418, 16.352, 16.871]
ACTUAL_VOLUME = [247602.0, 228630.0, 500197.0, 606299.0]
ACTUAL_DICT = {'pe': {'002450': 21}, 'pb': {'002450': 14}}
ACTUAL_DATAFRAME = {'close': [16.413, 16.552, 16.791, 17.08],
                    'high': [16.462, 16.721, 17.001, 17.489],
                    'low': [15.825, 16.418, 16.352, 16.871],
                    'volume': [247602.0, 228630.0, 500197.0, 606299.0],
                    'date': ["2016-05-31", "2016-01-01", "2016-01-02", "2016-01-03"]}
ACTUAL_TRUCK = """'Close': [16.413, 16.552, 16.791, 17.08]
'Code': ['002450.SZ']
'High': [16.462, 16.721, 17.001, 17.489]
'Low': [15.825, 16.418, 16.352, 16.871]
'Times': [datetime.datetime(2016, 5, 31, 0, 0), datetime.datetime(2016, 1, 1, 0, 0), datetime.datetime(2016, 1, 2, 0, 0), datetime.datetime(2016, 1, 3, 0, 0)]
'Volume': [247602.0, 228630.0, 500197.0, 606299.0]
'PE': [21]
'PB': [14]
'PS': [0]
'PCF': [0]"""


class TestTuShare(unittest.TestCase):

    @skipIf(SKIP_REAL, '跳过与真实服务器进行数据核对')
    def test_tushare_k_to_here(self):
        expected_response = TuShareSource.tushare_k_to_here('002450', '2016-05-31', '2016-06-03')
        self.assertEqual(list(expected_response.close), ACTUAL_CLOSE)
        self.assertEqual(list(expected_response.high), ACTUAL_HIGH)
        self.assertEqual(list(expected_response.low), ACTUAL_LOW)
        self.assertEqual(list(expected_response.volume), ACTUAL_VOLUME)

    def test_change_date(self):
        dates = [datetime.datetime(2016, 5, 31), datetime.datetime(2016, 6, 3)]
        expected_dates = TuShareSource.datetime_to_date(dates)
        self.assertEqual(expected_dates, ACTUAL_DATES)

    @skipIf(SKIP_REAL, '跳过与真实服务器进行数据核对')
    def test_tushare_basics_to_here(self):
        expected_response = TuShareSource.tushare_basics_to_here()
        self.assertTrue(expected_response.get('pe').get('002450'))

    @patch.multiple(TuShareSource, tushare_k_to_here=DEFAULT, tushare_basics_to_here=DEFAULT)
    def test_tushare_to_truck(self, tushare_k_to_here, tushare_basics_to_here):
        tushare_k_to_here.return_value = \
            Mock(mock_dataframe=pd.DataFrame(data=ACTUAL_DATAFRAME))
        tushare_basics_to_here.return_value = Mock(mock_dict=ACTUAL_DICT)
        expected_truck = \
            TuShareSource.tushare_to_truck('002450', tushare_k_to_here.return_value.mock_dataframe,
                                           tushare_basics_to_here.return_value.mock_dict)
        self.assertEqual(str(expected_truck), ACTUAL_TRUCK)
