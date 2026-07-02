"""
测试 Tushare Pro 数据源
Mock 测试使用 000001.SZ 的 前复权数据
"""

import datetime

import pandas as pd
import pytest
from yuna.sources.tushare import TuShareSource

SKIP_REAL = True

# 日期格式转换测试常量
ACTUAL_DATES = ['20160531', '20160603']

# 000001.SZ 平安银行 2024-01-02 ~ 2024-01-05 前复权 K线数据
ACTUAL_KLINE_DF = pd.DataFrame({
    'trade_date': ['20240102', '20240103', '20240104', '20240105'],
    'close':      [9.21, 9.20, 9.11, 9.27],
    'high':       [9.42, 9.22, 9.19, 9.44],
    'low':        [9.21, 9.15, 9.08, 9.07],
    'vol':        [1158366.45, 733610.31, 864193.99, 1991622.16],
})

# Mock daily_basic DataFrame
ACTUAL_BASIC_DF = pd.DataFrame({
    'trade_date': ['20240105'],
    'pe': [4.5],
    'pb': [0.5],
})

ACTUAL_TRUCK = """'Close': [9.21, 9.2, 9.11, 9.27]
'Code': ['000001.SZ']
'High': [9.42, 9.22, 9.19, 9.44]
'Low': [9.21, 9.15, 9.08, 9.07]
'Times': [datetime.datetime(2024, 1, 2, 0, 0), datetime.datetime(2024, 1, 3, 0, 0), datetime.datetime(2024, 1, 4, 0, 0), datetime.datetime(2024, 1, 5, 0, 0)]
'Volume': [1158366.45, 733610.31, 864193.99, 1991622.16]
'PE': [np.float64(4.5)]
'PB': [np.float64(0.5)]
'PS': [0]
'PCF': [0]"""


class TestTuShare:

    @pytest.mark.skipif(SKIP_REAL, reason='跳过与真实服务器进行数据核对')
    def test_tushare_k_to_here(self):
        df = TuShareSource.tushare_k_to_here('000001', '20240102', '20240105')
        assert df is not None
        assert not df.empty
        assert 'close' in df.columns
        assert 'trade_date' in df.columns
        assert len(df) >= 4

    def test_change_date(self):
        dates = [datetime.datetime(2016, 5, 31), datetime.datetime(2016, 6, 3)]
        expected_dates = TuShareSource.datetime_to_date(dates)
        assert expected_dates == ACTUAL_DATES

    @pytest.mark.skipif(SKIP_REAL, reason='跳过与真实服务器进行数据核对')
    def test_tushare_basics_to_here(self):
        df = TuShareSource.tushare_basics_to_here('000001', '20240102', '20240105')
        # daily_basic may be rate-limited on free tier; accept either success or None
        if df is not None:
            assert not df.empty

    def test_tushare_to_truck(self):
        expected_truck = TuShareSource.tushare_to_truck('000001', ACTUAL_KLINE_DF, ACTUAL_BASIC_DF)
        assert str(expected_truck) == ACTUAL_TRUCK
