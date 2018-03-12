import unittest
import datetime
from unittest import skipIf
from unittest.mock import Mock, patch
from yuna.sources.windpy import WindpySource

SKIP_REAL = True
ACTUAL_DATES = ['2016-05-31', '2016-06-03']
ACTUAL_FIELDS = ['LOW', 'HIGH', 'CLOSE', 'VOLUME', 'VAL_PE_DEDUCTED_TTM', 'PB_LF', 'PS_TTM', 'PCF_NCF_TTM']
ACTUAL_DATA = [[15.82459054289774, 16.416768616672844, 16.351716985702836, 16.87018606085927],
               [16.461555193681043, 16.720322083061763, 16.99980332964838, 17.48836072739194],
               [16.4117923303386, 16.551128347697446, 16.79042158775828, 17.079567802749366],
               [24760291.0, 22863013.0, 50019764.0, 60629918.00000001],
               [35.29177883081898, 35.59140581907335, 36.01531856377234, 36.635534857328985],
               [5.525568008422852, 5.572480201721191, 5.7250566482543945, 5.8236470222473145],
               [6.669246277954532, 6.725868138400435, 6.805976837605679, 6.9231819020174585],
               [8.685918807983398, 8.759662628173828, 8.863994598388672, 9.016640663146973]]
ACTUAL_TIMES = [datetime.datetime(2016, 5, 31, 0, 0, 0, 5000),
                datetime.datetime(2016, 6, 1, 0, 0, 0, 5000),
                datetime.datetime(2016, 6, 2, 0, 0, 0, 5000),
                datetime.datetime(2016, 6, 3, 0, 0, 0, 5000)]
ACTUAL_TRUCK = "'Close': [16.4117923303386, 16.551128347697446, 16.79042158775828, 17.079567802749366]\n" \
               "'Code': ['002450.SZ']\n" \
               "'High': [16.461555193681043, 16.720322083061763, 16.99980332964838, 17.48836072739194]\n" \
               "'Low': [15.82459054289774, 16.416768616672844, 16.351716985702836, 16.87018606085927]\n" \
               "'Times': [datetime.datetime(2016, 5, 31, 0, 0, 0, 5000)," \
               " datetime.datetime(2016, 6, 1, 0, 0, 0, 5000)," \
               " datetime.datetime(2016, 6, 2, 0, 0, 0, 5000), datetime.datetime(2016, 6, 3, 0, 0, 0, 5000)]\n" \
               "'Volume': [24760291.0, 22863013.0, 50019764.0, 60629918.00000001]\n" \
               "'PE': [36.635534857328985]\n" \
               "'PB': [5.8236470222473145]\n" \
               "'PS': [6.9231819020174585]\n" \
               "'PCF': [9.016640663146973]"


class TestWindpy(unittest.TestCase):

    @skipIf(SKIP_REAL, '跳过与真实服务器进行数据核对')
    def test_integration_contract(self):
        expected_response = WindpySource.wind_to_here('002450.SZ', "2016-05-31", "2016-06-03")
        self.assertTrue(expected_response)
        self.assertEqual(expected_response.Fields, ACTUAL_FIELDS)
        self.assertEqual(expected_response.Data, ACTUAL_DATA)
        self.assertEqual(expected_response.Times, ACTUAL_TIMES)

    def test_change_date(self):
        dates = [datetime.datetime(2016, 5, 31), datetime.datetime(2016, 6, 3)]
        expected_dates = WindpySource.datetime_to_date(dates)
        self.assertEqual(expected_dates, ACTUAL_DATES)

    @patch.object(WindpySource, 'wind_to_here')
    def test_list_to_truck(self, mock_get):
        mock_get.return_value = Mock(Times=ACTUAL_TIMES, Data=ACTUAL_DATA)
        expected_truck = WindpySource.list_to_truck('002450.SZ', mock_get.return_value)
        self.assertEqual(str(expected_truck), ACTUAL_TRUCK)

