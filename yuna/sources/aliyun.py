import datetime
from urllib.request import *
import ssl
import json

from ..core import SourceSingleton, Plane, Truck
from ..setting import APP_CODE


class AliyunSource(SourceSingleton):

    host = 'https://stock.api51.cn'
    path = '/kline'
    method = 'GET'
    query = 'prod_code={}&' \
             'candle_period=6&' \
             'candle_mode=1&' \
             'fields=low_px,high_px,close_px&' \
             'get_type=range&' \
             'start_date={}&' \
             'end_date={}'
    url = host + path + '?' + query

    def packing(self, stocks, dates):
        stocks_list = super().change_stock(stocks)
        plane = Plane()
        for stock_name in stocks_list:
            response = self.__class__.request_to_response(stock_name, dates)
            a = self.__class__.json_to_dict(response)
            b = a['data']['candle'][stock_name]
            truck = Truck()
            truck.extend("Code", [stock_name])
            truck.extend("Times", [datetime.datetime.strptime(str(item[0]), '%Y%m%d') for item in b])
            truck.extend("Low", [item[1] for item in b])
            truck.extend("High", [item[2] for item in b])
            truck.extend("Close", [item[3] for item in b])
            plane.append(truck)
        return plane

    @classmethod
    def request_to_response(cls, stock_name, dates):
        request = Request(cls.url.format(stock_name, *dates))
        request.add_header('Authorization', 'APPCODE ' + APP_CODE)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return urlopen(request, context=ctx)

    @classmethod
    def json_to_dict(cls, response):
        content = response.read()
        return json.loads(content)
