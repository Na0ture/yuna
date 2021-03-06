import collections
from datetime import datetime
import pickle

from asgiref.sync import sync_to_async, async_to_sync
import asyncio
import aiohttp

from .setting import *
from .exceptions import SourceError, DestinationRefuseError, CreateError

__title__ = 'yuna'
__version__ = '0.3.0'
__author__ = 'lvzhi'
__copyright__ = 'Copyright 2017 lvzhi'


class SourceSingleton:

    def __new__(cls, *args, **kwargs):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.__call_to_source()
        return it

    def __call_to_source(self):
        try:
            self.__class__.call_to_source()
        except Exception:
            raise SourceError("连接数据源出错")

    @classmethod
    def change_stock(cls, stocks):
        try:
            if isinstance(stocks, str):
                stocks_list = [stocks + '.SH' if stocks[0] == '6' else stocks + '.SZ']
            else:
                stocks_list = [stock + '.SH' if stock[0] == '6' else stock + '.SZ' for stock in stocks]
            return stocks_list
        except Exception:
            raise SourceError("转换股票名字时出错")

    @classmethod
    def validate_date(cls, date):
        """
        此函数是检验date是否合法

        参数date：含有两个字符串的元组
        返回值：含有两个合法的datetime对象的列表
        """

        if len(date) != 2:
            raise SourceError("日期分起始到期末，数量应为2")
        try:
            date = [datetime.strptime(k, '%Y%m%d') for k in date]
        except ValueError:
            raise SourceError("日期的格式不正确，请遵循%Y%m%d，例如'20180101'")
        if date[0].toordinal() - date[1].toordinal() >= 0:
            raise SourceError("期末日期要大于起初日期")
        return date

    @classmethod
    def call_to_source(cls):
        pass

    def packing(self, stocks, dates, session):
        pass


class DestinationSingleton:

    def __new__(cls, *args, **kwargs):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.__call_to_destination()
        return it

    def __call_to_destination(self):
        try:
            self.call_to_destination()
        except Exception:
            raise DestinationRefuseError

    def call_to_destination(self):
        pass

    def unpacking(self, plane):
        pass

    def sold_out(self):
        pass

    def find_out(self, stocks, from_query_date, to_query_date):
        raise NotImplemented


class Plane:

    def __init__(self):
        self.__elem = list()

    def __getitem__(self, item):
        return self.__elem[item]

    def append(self, truck):
        self.__elem.append(truck)


class Truck:

    def __init__(self):
        self.__elem = collections.defaultdict(list)

    def __getitem__(self, item):
        return self.__elem[item]

    def __setitem__(self, key, value):
        self.__elem[key] = value

    def __repr__(self):
        return "'Close': {}\n" \
               "'Code': {}\n" \
               "'High': {}\n" \
               "'Low': {}\n" \
               "'Times': {}\n" \
               "'Volume': {}\n" \
               "'PE': {}\n" \
               "'PB': {}\n" \
               "'PS': {}\n" \
               "'PCF': {}".format(self.__elem['Close'],
                                  self.__elem['Code'],
                                  self.__elem['High'],
                                  self.__elem['Low'],
                                  self.__elem['Times'],
                                  self.__elem['Volume'],
                                  self.__elem['PE'],
                                  self.__elem['PB'],
                                  self.__elem['PS'],
                                  self.__elem['PCF'],)

    def append(self, name, data):
        self.__elem[name].append(data)

    def extend(self, name, data):
        self.__elem[name].extend(data)

    def get(self, name, default):
        """当truck实例中没有名为name的key时，不报错，而是返回default"""
        return self.__elem.get(name, default)

    def keys(self):
        return self.__elem.keys()

from .destinations.hdf5 import Hdf5Destination
from .destinations.mysql import MysqlDestination
from .sources.aliyun import AliyunSource
from .sources.windpy import WindpySource
from .sources.tushare import TuShareSource

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/all.pkl'), 'rb') as i:
    all_stocks_list = pickle.load(i)


class TechnicalIndicator:
    """
    参数data：原数据字典 or 处理过程中的中间列表

    参数handle：仅当参数data为中间列表的时候有效，开启是否把列表的数据过一边_handle方法

    该类的对象分三种情况初始化：
    （1）传入Truck类，处理，结果在ans
    （2）传入list类，开启handle，处理，结果在ans
    （3）传入list类，默认handle，不处理，结果在ans
    """

    def __init__(self, data, handle):
        if isinstance(data, Truck):
            self.times = data['Times']
            self.low = data['Low']
            self.high = data['High']
            self.close = data['Close']
            self.data = data
            self.ans = []
            self._handle()
        elif isinstance(data, list) and handle == 'off':
            self.ans = data
        elif isinstance(data, list) and handle == 'on':
            self.close = data
            self.ans = []
            self._handle()
        else:
            raise TypeError("传入给算法类的初参不符合要求")

    def __call__(self, *args, **kwargs):
        self.data[self.__class__.__name__] = self.ans
        return self.data

    def _handle(self):
        pass


class VisualIndicator:

    def __init__(self, data):
        self.data = data
        self._handle()

    def _handle(self):
        pass

import visual
_visual_indicators = visual._visual_indicators
import indicators
_all_indicators = indicators._all_indicators


def run():
    try:
        exec(f"sourceSingleton = globals().get(SOURCE, None)()", globals())
    except Exception:
        raise CreateError("无法连接数据源（使用setup方法进行相关参数设定，重启shell并引用yuna包，以完成设置）")
    try:
        exec(f"destinationSingleton = globals().get(DESTINATION, None)()", globals())
    except Exception:
        raise CreateError("无法连接数据库（使用setup方法进行相关参数设定，重启shell并引用yuna包，以完成设置）")


async def _update(stock, sema, date):
    async with sema, aiohttp.ClientSession() as session:
        plane = await sourceSingleton.packing(stock, date, session)
    await sync_to_async(destinationSingleton.unpacking)(plane)


def update(stocks, *date):
    run()
    stocks = all_stocks_list if stocks == 'all' else stocks
    stocks_con = []
    loop = asyncio.get_event_loop()
    sema = asyncio.Semaphore(50)
    for i in stocks:
        stocks_con.append(_update(i, sema, date))
    loop.run_until_complete(asyncio.gather(*stocks_con))


def delete():
    run()
    destinationSingleton.sold_out()


def _get_indicator(indicator_name):
    if indicator_name in _all_indicators:
        return _all_indicators[indicator_name]


def query(stocks, string, from_query_date=None, to_query_date=None):
    run()
    methods = string.split(',')
    methods.reverse()
    data = all_stocks_list if stocks == 'all' else stocks
    while True:
        try:
            method = methods.pop()
            data = _query(data, method, from_query_date, to_query_date)
        except IndexError:
            return data


def _query(stocks, indicator_name, from_query_date, to_query_date):
    if indicator_name in _all_indicators:
        indicator = _get_indicator(indicator_name)
        if not isinstance(stocks[0], Truck):
            plane = destinationSingleton.find_out(stocks, from_query_date, to_query_date)
        else:
            plane = stocks
        return [indicator(truck)() for truck in plane]
    elif indicator_name in _visual_indicators:
        indicator = _visual_indicators[indicator_name]
        indicator(stocks)


def all_index():
    return list(_all_indicators.keys())
