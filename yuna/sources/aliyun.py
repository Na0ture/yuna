from datetime import datetime
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
    因网极api样式缘故，获取基本面数据跟k线数据分别各需要一条请求才能获取
    """

    host = 'https://data.api51.cn/apis'
    path_kline = '/kline/'
    path_cwfx = '/real/'
    method = 'GET'
    query_kline = 'stockcode={}&' \
                  'market={}&' \
                  'fqtype=1&' \
                  'type=day&' \
                  'token={}&' \
                  'count={}&' \
                  'date={}'
    query_cwfx = 'stockcode={}&' \
                 'market={}&' \
                 'token={}'
    url_kline = host + path_kline + '?' + query_kline
    url_cwfx = host + path_cwfx + '?' + query_cwfx
    z = 0

    def packing(self, stocks, dates):
        stocks_list = super().change_stock(stocks)
        time_delta, to_query_date = self.__class__.datetime_to_date(self.__class__.calc_time_delta(self.__class__.validate_date(dates)))
        plane = Plane()
        for stock_name in stocks_list:
            plane.append(self.__class__.request_to_truck(stock_name, time_delta, to_query_date))
        return plane

    @classmethod
    @retry
    def request_to_truck(cls, stock_name, from_query_date, to_query_date):
        response = cls.request_to_response(stock_name, from_query_date, to_query_date)
        stock_kline_data = cls.json_kline_to_dict(response[0])
        stock_cwfx_data = cls.json_cwfx_to_dict(response[1])
        return cls.dict_to_truck(stock_name, stock_kline_data, stock_cwfx_data)

    @classmethod
    def datetime_to_date(cls, time_delta):
        return time_delta[0], time_delta[1].strftime('%Y%m%d')

    @classmethod
    def request_to_response(cls, stock_name, *dates):
        """
        :param stock_name: 股票名字，例如'002450.SZ'
        :param dates: 一个包含截止日期前多少天以及截止日期的二元组，例如(5, datetime.datetime(2016, 6, 3))
        :return: 一个是股票k线json数据，一个是股票财务json数据，具体内容见test
        """

        request_kline = Request(cls.url_kline.format(stock_name[:6], stock_name[7:], APP_CODE, *dates))
        request_cwfx = Request(cls.url_cwfx.format(stock_name[:6], stock_name[7:], APP_CODE))
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return urlopen(request_kline, context=ctx), urlopen(request_cwfx, context=ctx)

    @classmethod
    def json_kline_to_dict(cls, response):
        """
        :param response: 股票k线json数据
        :return: 返回dict类型，具体内容看test部分
        """
        content = response.read()
        return json.loads(content)

    @classmethod
    def json_cwfx_to_dict(cls, response):
        """
        :param response: 股票财务json数据
        :return: 返回dict类型，具体内容看test部分
        """

        content = response.read()
        return json.loads(content)

    @classmethod
    def dict_to_truck(cls, stock_name, stock_kline_data, stock_cwfx_data):
        """

        :param stock_name: 股票名字，例如'002450.SZ'
        :param stock_kline_data: 股票k线dict数据
        :param stock_cwfx_data: 股票财务dict数据
        :return: 装车，准备送往数据库
        """

        truck = Truck()
        truck.extend("Code", [stock_name])
        truck.extend("PE", [stock_cwfx_data['results'][0][-2]])
        truck.extend("PB", [0])
        truck.extend("PS", [0])
        truck.extend("PCF", [0])
        candle = stock_kline_data['results'][0]['array']
        for i in candle:
            truck.append('Times', datetime.strptime(str(i[0]), '%Y%m%d'))
            truck.append('Low', i[4])
            truck.append('High', i[3])
            truck.append('Close', i[2])
            truck.append('Volume', i[6])
        cls.z += 1
        print(cls.z)
        return truck

    @classmethod
    def calc_time_delta(cls, time_list):
        delta = time_list[1] - time_list[0]
        return delta.days, time_list[1]
