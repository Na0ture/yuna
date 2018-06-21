import datetime
import time
from urllib.request import *
import ssl
import json

from ..core import SourceSingleton, Plane, Truck
from ..setting import APP_CODE


def retry(f):
    """简易重试机制"""
    def wrap(*args):
        retry_count = 50
        while retry_count > 0:
            try:
                ans = f(*args)
            except Exception as e:
                ans = None
            if ans is not None:
                return ans
            retry_count -= 1
            time.sleep(1)
    return wrap


class AliyunSource(SourceSingleton):
    """
    因aliyun商家提供的api缘故，获取财务数据跟k线数据分别各需要一条请求才能获取
    """

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
            plane.append(self.__class__.temp(stock_name, from_query_date, to_query_date))
        return plane

    @classmethod
    @retry
    def temp(cls, stock_name, from_query_date, to_query_date):
        response = cls.request_to_response(stock_name, from_query_date, to_query_date)
        stock_kline_data = cls.json_kline_to_dict(response[0])
        stock_cwfx_data = cls.json_cwfx_to_dict(response[1])
        return cls.dict_to_truck(stock_name, stock_kline_data, stock_cwfx_data)

    @classmethod
    def datetime_to_date(cls, validity_dates):
        return [i.strftime('%Y%m%d') for i in validity_dates]

    @classmethod
    def request_to_response(cls, stock_name, *dates):
        """
        :param stock_name: 股票名字，例如'002450.SZ'
        :param dates: 从...到...日期，例如"20160531", "20160603"
        :return: 一个是股票k线json数据，一个是股票财务json数据，具体内容见test
        """

        request_kline = Request(cls.url_kline.format(stock_name, *dates))
        request_kline.add_header('Authorization', 'APPCODE ' + APP_CODE)
        request_cwfx = Request(cls.url_cwfx.format(stock_name[:6]))
        request_cwfx.add_header('Authorization', 'APPCODE ' + APP_CODE)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return urlopen(request_kline, context=ctx), urlopen(request_cwfx, context=ctx)

    @classmethod
    def json_kline_to_dict(cls, response):
        """
        :param response: 股票k线json数据
        :return: 返回python类型，具体内容看test部分
        """
        content = response.read()
        return json.loads(content)

    @classmethod
    def json_cwfx_to_dict(cls, response):
        """
        :param response: 股票财务json数据
        :return: 返回python类型，指向'gsgz'，具体内容看test部分

        因财务数据过于庞大，暂不做测试，字段gsgz的内容范例如下：
                "gsgz": [
            {
                "InnerCode": 36647,
                "PB": 4.8866,
                "PCF": -53.3646808,
                "PS": 10.3098917,
                "PE": 87.3309896,
                "TradingDay": 1506700800000
            }
        ],
        """

        content = response.read()
        return json.loads(content)['gsgz']

    @classmethod
    def dict_to_truck(cls, stock_name, stock_kline_data, stock_cwfx_data):
        """
        有时候阿里云会没有某些股票的pe，pb等相应的财务数据，它们存在的时候是一个数字，
        不存在的时候，使用get不会报错，则返回0

        :param stock_name: 股票名字，例如'002450.SZ'
        :param stock_kline_data: 股票k线dict数据
        :param stock_cwfx_data: 股票财务dict数据
        :return: 装车，准备送往数据库
        """

        truck = Truck()
        truck.extend("Code", [stock_name])
        truck.extend("PE", [stock_cwfx_data[0].get('PE', 0)])
        truck.extend("PB", [stock_cwfx_data[0].get('PB', 0)])
        truck.extend("PS", [stock_cwfx_data[0].get('PS', 0)])
        truck.extend("PCF", [stock_cwfx_data[0].get('PCF', 0)])
        candle = stock_kline_data['data']['candle'][stock_name]
        for i in candle:
            truck.append('Times', datetime.datetime.strptime(str(i[0]), '%Y%m%d'))
            truck.append('Low', i[1])
            truck.append('High', i[2])
            truck.append('Close', i[3])
            truck.append('Volume', i[4])
        return truck
