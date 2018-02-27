import collections

from .setting import *
from .exceptions import SourceError, DestinationRefuseError

__title__ = 'yuna'
__version__ = '0.2.0'
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
            self.call_to_source()
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

    def call_to_source(self):
        pass

    def packing(self, stocks, dates):
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

    def find_out(self, stocks):
        raise NotImplemented


class Plane:

    def __init__(self):
        self.__elem = list()

    def __getitem__(self, item):
        return self.__elem[item]

    def append(self, truck):
        if isinstance(truck, Truck):
            self.__elem.append(truck)


class Truck:

    def __init__(self):
        self.__elem = collections.defaultdict(list)

    def __getitem__(self, item):
        return self.__elem[item]

    def __call__(self, *args, **kwargs):
        return self.__elem

    def __repr__(self):
        return "'Close': {}\n" \
               "'Code': {}\n" \
               "'High': {}\n" \
               "'Low': {}\n" \
               "'Times': {}".format(self.__elem['Close'],
                                    self.__elem['Code'],
                                    self.__elem['High'],
                                    self.__elem['Low'],
                                    self.__elem['Times'],)

    def append(self, name, data):
        self.__elem[name].append(data)

    def extend(self, name, data):
        self.__elem[name].extend(data)

    def pop(self, name):
        return self.__elem.pop(name)

    def keys(self):
        return self.__elem.keys()


from .destinations.mysql import MysqlDestination
from .sources.aliyun import AliyunSource
from .sources.windpy import WindpySource

sourceSingleton = globals().get(SOURCE, None)()
destinationSingleton = globals().get(DESTINATION, None)()


class TechnicalIndicator:
    """
    参数data：原数据字典 or 处理过程中的中间列表

    参数handle：仅当参数data为中间列表的时候有效，开启是否把列表的数据过一边_handle方法

    该类的对象分三种情况初始化：
    （1）传入collections.defaultdict类，处理，结果在ans
    （2）传入list类，开启handle，处理，结果在ans
    （3）传入list类，默认handle，不处理，结果在ans
    """

    def __init__(self, data, handle):
        if isinstance(data, dict):
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

    def _handle(self):
        pass


def update(stocks, *date):
    plane = sourceSingleton.packing(stocks, date)
    destinationSingleton.unpacking(plane)


def delete():
    destinationSingleton.sold_out()


from .indicators import _all_indicators


def _get_indicator(indicator_name):
    if indicator_name in _all_indicators:
        return _all_indicators[indicator_name]


def query(stocks, indicator_name):
    indicator = _get_indicator(indicator_name)
    plane = destinationSingleton.find_out(stocks)
    data = []
    for truck in plane:
        data.append(indicator(truck()).ans)
    return data


def all_index():
    return list(_all_indicators.keys())
