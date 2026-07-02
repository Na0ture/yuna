"""
测试Tushare财经库，使用数据为股票康得新16年5月31至16年6月3日的k线数据，以检验数据是否前复权
"""

import datetime

import pandas as pd
import pytest
from yuna.sources.tushare import TuShareSource

SKIP_REAL = True
ACTUAL_DATES = ['20160531', '20160603']

# Mock daily kline DataFrame (columns aligned with tushare pro API)
ACTUAL_KLINE_DF = pd.DataFrame({
    'trade_date': ['20160531', '20160601', '20160602', '20160603'],
    'close':      [16.413, 16.552, 16.791, 17.08],
    'high':       [16.462, 16.721, 17.001, 17.489],
    'low':        [15.825, 16.418, 16.352, 16.871],
    'vol':        [247602.0, 228630.0, 500197.0, 606299.0],
})

# Mock daily_basic DataFrame
ACTUAL_BASIC_DF = pd.DataFrame({
    'trade_date': ['20160603'],
    'pe': [21.0],
    'pb': [14.0],
})

ACTUAL_TRUCK = """'Close': [16.413, 16.552, 16.791, 17.08]
'Code': ['002450.SZ']
'High': [16.462, 16.721, 17.001, 17.489]
'Low': [15.825, 16.418, 16.352, 16.871]
'Times': [datetime.datetime(2016, 5, 31, 0, 0), datetime.datetime(2016, 6, 1, 0, 0), datetime.datetime(2016, 6, 2, 0, 0), datetime.datetime(2016, 6, 3, 0, 0)]
'Volume': [247602.0, 228630.0, 500197.0, 606299.0]
'PE': [np.float64(21.0)]
'PB': [np.float64(14.0)]
'PS': [0]
'PCF': [0]"""


class TestTuShare:

    @pytest.mark.skipif(SKIP_REAL, reason='跳过与真实服务器进行数据核对')
    def test_tushare_k_to_here(self):
        expected_response = TuShareSource.tushare_k_to_here('002450', '2016-05-31', '2016-06-03')
        assert list(expected_response.close) == ACTUAL_CLOSE
        assert list(expected_response.high) == ACTUAL_HIGH
        assert list(expected_response.low) == ACTUAL_LOW
        assert list(expected_response.volume) == ACTUAL_VOLUME

    def test_change_date(self):
        dates = [datetime.datetime(2016, 5, 31), datetime.datetime(2016, 6, 3)]
        expected_dates = TuShareSource.datetime_to_date(dates)
        assert expected_dates == ACTUAL_DATES

    @pytest.mark.skipif(SKIP_REAL, reason='跳过与真实服务器进行数据核对')
    def test_tushare_basics_to_here(self):
        expected_response = TuShareSource.tushare_basics_to_here('002450', '20160531', '20160603')
        assert expected_response is not None

    def test_tushare_to_truck(self):
        expected_truck = TuShareSource.tushare_to_truck('002450', ACTUAL_KLINE_DF, ACTUAL_BASIC_DF)
        assert str(expected_truck) == ACTUAL_TRUCK
