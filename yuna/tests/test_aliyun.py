import unittest
from unittest import skipIf
from unittest.mock import Mock, patch
from ..sources.aliyun import AliyunSource

SKIP_REAL = True
ACTUAL_JSON = b'{' \
              b'"data":{' \
              b'"candle":{' \
              b'"fields":[' \
              b'"min_time","low_px","high_px","close_px"],' \
              b'"002450.SZ":[' \
              b'[20160531,15.81,16.45,16.40],' \
              b'[20160601,16.40,16.71,16.54],' \
              b'[20160602,16.34,16.99,16.78],' \
              b'[20160603,16.86,17.48,17.07]' \
              b']' \
              b'}' \
              b'}' \
              b'}'
ACTUAL_DICT = {''
               'data': {''
                        'candle': {''
                                   '002450.SZ': [
                                    [20160531, 15.81, 16.45, 16.4],
                                    [20160601, 16.4, 16.71, 16.54],
                                    [20160602, 16.34, 16.99, 16.78],
                                    [20160603, 16.86, 17.48, 17.07]],
                                   'fields':
                                   ['min_time', 'low_px', 'high_px', 'close_px']
                                   }
                        }
               }


class TestAliyun(unittest.TestCase):

    @skipIf(SKIP_REAL, '跳过与真实服务器进行数据核对')
    def test_integration_contract(self):
        expected_response = AliyunSource.request_to_response('002450.SZ', ("20160531", "20160603"))
        expected_json = expected_response.read()
        actual_json = ACTUAL_JSON
        self.assertEqual(expected_json, ACTUAL_JSON)

    def test_change_stock(self):
        stocks = ['000001', '600000', '300001']
        expected_change_stock = AliyunSource.change_stock(stocks)
        self.assertEqual(expected_change_stock, ['000001.SZ', '600000.SH', '300001.SZ'])

    @patch.object(AliyunSource, 'request_to_response')
    def test_json_to_dict(self, mock_get):
        mock_get.return_value = Mock()
        mock_get.return_value.read.return_value = ACTUAL_JSON
        expected_response = mock_get.return_value
        expected_dict = AliyunSource.json_to_dict(expected_response)
        self.assertEqual(expected_dict, ACTUAL_DICT)
