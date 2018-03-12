import unittest
import datetime
from unittest import skipIf
from unittest.mock import Mock, patch

from yuna.sources.aliyun import AliyunSource

SKIP_REAL = True
ACTUAL_DATES = ['20160531', '20160603']
ACTUAL_JSON_KLINE = b'{' \
                    b'"data":{' \
                    b'"candle":{' \
                    b'"fields":[' \
                    b'"min_time","low_px","high_px","close_px","business_amount"],' \
                    b'"002450.SZ":[' \
                    b'[20160531,15.81,16.45,16.40,24760291],' \
                    b'[20160601,16.40,16.71,16.54,22863013],' \
                    b'[20160602,16.34,16.99,16.78,50019764],' \
                    b'[20160603,16.86,17.48,17.07,60629918]]}}}'
ACTUAL_DICT_KLINE = {''
                     'data': {''
                              'candle': {''
                                         '002450.SZ': [
                                          [20160531, 15.81, 16.45, 16.4, 24760291],
                                          [20160601, 16.4, 16.71, 16.54, 22863013],
                                          [20160602, 16.34, 16.99, 16.78, 50019764],
                                          [20160603, 16.86, 17.48, 17.07, 60629918]],
                                         'fields':
                                         ['min_time', 'low_px', 'high_px', 'close_px', 'business_amount']
                                         }
                              }
                     }
ACTUAL_DICT_CWFX = [{'InnerCode': 10736,
                     'PB': 4.0284,
                     'PCF': 23.3197089,
                     'PS': 5.5528455,
                     'PE': 27.9231992,
                     'TradingDay': 1506700800000}]
ACTUAL_TRUCK = "'Close': [16.4, 16.54, 16.78, 17.07]\n" \
               "'Code': ['002450.SZ']\n" \
               "'High': [16.45, 16.71, 16.99, 17.48]\n" \
               "'Low': [15.81, 16.4, 16.34, 16.86]\n" \
               "'Times': [datetime.datetime(2016, 5, 31, 0, 0), datetime.datetime(2016, 6, 1, 0, 0)," \
               " datetime.datetime(2016, 6, 2, 0, 0), datetime.datetime(2016, 6, 3, 0, 0)]\n" \
               "'Volume': [24760291, 22863013, 50019764, 60629918]\n" \
               "'PE': [27.9231992]\n" \
               "'PB': [4.0284]\n" \
               "'PS': [5.5528455]\n" \
               "'PCF': [23.3197089]"


class TestAliyun(unittest.TestCase):

    @skipIf(SKIP_REAL, '跳过与真实服务器进行数据核对')
    def test_integration_contract(self):
        """
        测试真实服务器的数据跟本地缓存数据是否一致，仅当常量SKIP_REAL为False时生效
        """
        expected_response = AliyunSource.request_to_response('002450.SZ', "20160531", "20160603")
        expected_json = expected_response[0].read()
        self.assertEqual(expected_json, ACTUAL_JSON_KLINE)
        self.assertTrue(expected_response[1].read())

    def test_change_stock(self):
        stocks = ['000001', '600000', '300001']
        expected_change_stock = AliyunSource.change_stock(stocks)
        self.assertEqual(expected_change_stock, ['000001.SZ', '600000.SH', '300001.SZ'])

    def test_datetime_to_date(self):
        dates = [datetime.datetime(2016, 5, 31), datetime.datetime(2016, 6, 3)]
        expected_dates = AliyunSource.datetime_to_date(dates)
        self.assertEqual(expected_dates, ACTUAL_DATES)

    @patch.object(AliyunSource, 'request_to_response')
    def test_json_kline_to_dict(self, mock_get):
        mock_get.return_value = Mock()
        mock_get.return_value.read.return_value = ACTUAL_JSON_KLINE
        expected_response = mock_get.return_value
        expected_dict = AliyunSource.json_kline_to_dict(expected_response)
        self.assertEqual(expected_dict, ACTUAL_DICT_KLINE)

    def test_dict_to_truck(self):
        expected_truck = AliyunSource.dict_to_truck('002450.SZ', ACTUAL_DICT_KLINE, ACTUAL_DICT_CWFX)
        self.assertEqual(str(expected_truck), ACTUAL_TRUCK)
