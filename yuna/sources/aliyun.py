import datetime
from urllib.request import *
import ssl
import json

from ..core import SourceSingleton, Plane, Truck
from ..setting import APP_CODE


class AliyunSource(SourceSingleton):

    host = 'https://stock.api51.cn'
    path_kline = '/kline'
    path_cwfx = '/f10'
    method = 'GET'
    query_kline = 'prod_code={}&' \
                  'candle_period=6&' \
                  'candle_mode=1&' \
                  'fields=low_px,high_px,close_px,business_amount&' \
                  'get_type=range&' \
                  'start_date={}&' \
                  'end_date={}'
    query_cwfx = 'info={}_cwfx'
    url_kline = host + path_kline + '?' + query_kline
    url_cwfx = host + path_cwfx + '?' + query_cwfx

    def packing(self, stocks, dates):
        stocks_list = super().change_stock(stocks)
        from_query_date, to_query_date = self.__class__.datetime_to_date(self.__class__.validate_date(dates))
        plane = Plane()
        for stock_name in stocks_list:
            response = self.__class__.request_to_response(stock_name, from_query_date, to_query_date)
            stock_data = self.__class__.json_to_dict(response)
            plane.append(self.__class__.dict_to_truck(stock_name, stock_data))
        return plane

    @classmethod
    def datetime_to_date(cls, validity_dates):
        return [i.strftime('%Y%m%d') for i in validity_dates]

    @classmethod
    def request_to_response(cls, stock_name, *dates):
        request_kline = Request(cls.url_kline.format(stock_name, *dates))
        request_kline.add_header('Authorization', 'APPCODE ' + APP_CODE)
        request_cwfx = Request(cls.url_cwfx.format(stock_name, *dates))
        request_cwfx.add_header('Authorization', 'APPCODE ' + APP_CODE)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return urlopen(request_kline, context=ctx), []

    @classmethod
    def json_to_dict(cls, response):
        content = response.read()
        return json.loads(content)

    @classmethod
    def dict_to_truck(cls, stock_name, stock_data):
        truck = Truck()
        truck.extend("Code", [stock_name])
        candle = stock_data['data']['candle'][stock_name]
        for i in candle:
            truck.append('Times', datetime.datetime.strptime(str(i[0]), '%Y%m%d'))
            truck.append('Low', i[1])
            truck.append('High', i[2])
            truck.append('Close', i[3])
            truck.append('Volume', i[4])
        return truck
