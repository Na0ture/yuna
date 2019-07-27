"""
测试Tushare财经库，使用数据为股票康得新16年5月31至16年6月3日的k线数据，以检验数据是否前复权
"""

import unittest
import datetime
from unittest import skipIf
from unittest.mock import Mock, patch, DEFAULT

import pandas as pd

from yuna.sources.tushare import TuShareSource

SKIP_REAL = 0
STOCK_CODE = "600897"
DATES = ["2019-06-27", "2019-06-28"]
CLOSE = [25.62, 24.11]
HIGH = [25.87, 24.32]
LOW = [25.50, 24.05]
VOLUME = [26314.0, 20100.0]

DICT = {'pe': {STOCK_CODE: 14.75}, 'pb': {STOCK_CODE: 1.88}}
DATA_FRAME = {'close': CLOSE, 'high': HIGH, 'low': LOW, 'volume': VOLUME, 'date': DATES}

TRUCK = """'Close': [25.62, 24.11]
'Code': ['600897.SH']
'High': [25.87, 24.32]
'Low': [25.5, 24.05]
'Times': [datetime.datetime(2019, 6, 27, 0, 0), datetime.datetime(2019, 6, 28, 0, 0)]
'Volume': [26314.0, 20100.0]
'PE': [14.75]
'PB': [1.88]
'PS': [0]
'PCF': [0]"""
SKIP_NOTE = "跳过与真实服务器进行数据核对"


class TestTuShare(unittest.TestCase):

    @skipIf(SKIP_REAL, SKIP_NOTE)
    def test_tushare_k_to_here(self):
        expected_response = TuShareSource.tushare_k_to_here(STOCK_CODE, *DATES)
        self.assertEqual(list(expected_response.close), CLOSE)
        self.assertEqual(list(expected_response.high), HIGH)
        self.assertEqual(list(expected_response.low), LOW)
        self.assertEqual(list(expected_response.volume), VOLUME)

    def test_change_date(self):
        dates = [datetime.datetime(2019, 6, 27), datetime.datetime(2019, 6, 28)]
        expected_dates = TuShareSource.datetime_to_date(dates)
        self.assertEqual(expected_dates, DATES)

    @skipIf(SKIP_REAL, SKIP_NOTE)
    def test_tushare_basics_to_here(self):
        expected_response = TuShareSource.tushare_basics_to_here()
        self.assertIsNotNone(expected_response.loc[:, 'pe'][STOCK_CODE])

    @patch.multiple(TuShareSource, tushare_k_to_here=DEFAULT, tushare_basics_to_here=DEFAULT)
    def test_tushare_to_truck(self, tushare_k_to_here, tushare_basics_to_here):
        tushare_k_to_here.return_value = \
            Mock(mock_dataframe=pd.DataFrame(data=DATA_FRAME))
        tushare_basics_to_here.return_value = Mock(mock_dict=DICT)
        expected_truck = \
            TuShareSource.tushare_to_truck(STOCK_CODE, tushare_k_to_here.return_value.mock_dataframe,
                                           tushare_basics_to_here.return_value.mock_dict)
        self.assertEqual(str(expected_truck), TRUCK)
