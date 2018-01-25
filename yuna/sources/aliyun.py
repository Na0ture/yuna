import datetime
import urllib
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
             'fields=close_px&' \
             'get_type=range&' \
             'start_date={}&' \
             'end_date={}'
    url = host + path + '?' + query

    def packing(self, stocks, dates):
        stocks_list = self._change_stock(stocks)
        plane = Plane()
        for stock_name in stocks_list:
            request = urllib.request.Request(self.url.format(stock_name, *dates))
            request.add_header('Authorization', 'APPCODE ' + APP_CODE)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            response = urllib.request.urlopen(request, context=ctx)
            content = response.read()
            a = json.loads(content)
            b = a['data']['candle'][stock_name]
            truck = Truck()
            truck.extend("Code", [stock_name])
            truck.extend("Times", [datetime.datetime.strptime(str(item[0]), '%Y%m%d') for item in b])
            truck.extend("Close", [item[1] for item in b])
            plane.append(truck)
        return plane