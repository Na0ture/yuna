"""
测试网极API，使用数据为股票康得新16年5月31至16年6月3日的k线数据，以检验数据是否前复权
"""

import unittest
import datetime
import asyncio
from unittest import skipIf
import aiohttp
from yuna.sources.aliyun import AliyunSource

SKIP_REAL = True
ACTUAL_DATES = (5, '20160603')
ACTUAL_JSON_KLINE = """{"errorInfo":"","errorNo":0,"count":1,"results":[{"name":"康得新","code":"002450","market":"SZ","count":4,"array":[[20160531,15.8643,16.3997,16.4498,15.8093,15.8043,247602.9219,808446464.0000,16.1836,16.2952,16.5281,16.5465,16.3524],[20160601,16.4598,16.5398,16.7099,16.4047,16.3997,228630.1250,761680192.0000,16.2246,16.3337,16.4710,16.5185,16.3805],[20160602,16.5130,16.7830,16.9930,16.3430,33.2030,500197.6250,840809024.0000,16.3513,16.3840,16.4434,16.5332,16.4100],[20160603,16.8630,17.0730,17.4830,16.8630,16.7830,606299.1875,1045912384.0000,16.5200,16.4453,16.4716,16.5634,16.4553]]}]}"""
ACTUAL_DICT_CWFX = {'errorInfo': '',
                     'errorNo': 0,
                     'results': [
                         ['002450', '康得新', 2, 'SZ', 20180723, 239,
                          0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                          0.0, 0.0, 0.0, 17.08, 0.0, 0.0, 0.0, 17.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                          21.138, 'KDX']]}

ACTUAL_DICT_KLINE = {'errorInfo': '',
                    'errorNo': 0,
                    'count': 1,
                    'results': [{
                        'name': '康得新',
                        'code': '002450',
                        'market': 'SZ',
                        'count': 4,
                        'array':
                            [[20160531, 15.8643, 16.3997, 16.4498, 15.8093, 15.8043,
                              247602.9219, 808446464.0, 16.1836, 16.2952, 16.5281, 16.5465, 16.3524],
                             [20160601, 16.4598, 16.5398, 16.7099, 16.4047, 16.3997,
                              228630.125, 761680192.0, 16.2246, 16.3337, 16.471, 16.5185, 16.3805],
                             [20160602, 16.513, 16.783, 16.993, 16.343, 33.203,
                              500197.625, 840809024.0, 16.3513, 16.384, 16.4434, 16.5332, 16.41],
                             [20160603, 16.863, 17.073, 17.483, 16.863, 16.783,
                              606299.1875, 1045912384.0, 16.52, 16.4453, 16.4716, 16.5634, 16.4553]]}]}

ACTUAL_TRUCK = """'Close': [16.3997, 16.5398, 16.783, 17.073]
'Code': ['002450.SZ']
'High': [16.4498, 16.7099, 16.993, 17.483]
'Low': [15.8093, 16.4047, 16.343, 16.863]
'Times': [datetime.datetime(2016, 5, 31, 0, 0), datetime.datetime(2016, 6, 1, 0, 0), datetime.datetime(2016, 6, 2, 0, 0), datetime.datetime(2016, 6, 3, 0, 0)]
'Volume': [247602.9219, 228630.125, 500197.625, 606299.1875]
'PE': [21.138]
'PB': [0]
'PS': [0]
'PCF': [0]"""


class TestAliyun(unittest.TestCase):

    @skipIf(SKIP_REAL, '跳过与真实服务器进行数据核对')
    def test_integration_contract(self):
        """
        测试真实服务器的数据跟本地缓存数据是否一致，仅当常量SKIP_REAL为False时生效
        """

        async def _request_to_response():
            async with aiohttp.ClientSession() as session:
                return await AliyunSource.request_to_response('002450.SZ', session, 4, "20160603")
        loop = asyncio.get_event_loop()
        expected_response = loop.run_until_complete(_request_to_response())
        expected_json = expected_response[0]
        self.assertEqual(str(expected_json), ACTUAL_JSON_KLINE)
        self.assertTrue(expected_response[1])

    def test_change_stock(self):
        stocks = ['000001', '600000', '300001']
        expected_change_stock = AliyunSource.change_stock(stocks)
        self.assertEqual(expected_change_stock, ['000001.SZ', '600000.SH', '300001.SZ'])

    def test_datetime_to_date(self):
        dates = [5, datetime.datetime(2016, 6, 3)]
        expected_dates = AliyunSource.datetime_to_date(dates)
        self.assertEqual(expected_dates, ACTUAL_DATES)

    def test_dict_to_truck(self):
        expected_truck = AliyunSource.dict_to_truck('002450.SZ', ACTUAL_DICT_KLINE, ACTUAL_DICT_CWFX)
        self.assertEqual(str(expected_truck), ACTUAL_TRUCK)


if __name__ == '__main__':
    unittest.main()
