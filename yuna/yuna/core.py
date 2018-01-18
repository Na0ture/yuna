import collections
import datetime
import WindPy
from setting import *
from packages import pymysql

__title__ = 'yuna'
__version__ = '0.1.0'
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

    def call_to_source(self):
        pass

    def packing(self, stock, date):
        pass


class WindpySource(SourceSingleton):

    def call_to_source(self):
        WindPy.w.start()

    def packing(self, stocks, dates):
        stocks_list = self.__change_stock(stocks)
        fquery_date, bquery_date = self.__change_date(dates)
        plane = Plane()
        for stock_name in stocks_list:
            a = WindPy.w.wsd(stock_name, "close", fquery_date, bquery_date, "Fill=Previous;PriceAdj=F")
            truck = Truck()
            truck.append("Code", a.Codes)
            truck.append("Times", a.Times)
            truck.append("Close", a.Data[0])
            plane.append(truck)
        return plane

    def __change_date(self, dates):
        temp = list()
        for date in dates:
            if datetime.date(int(date[:4]), int(date[4:6]), int(date[6:])).toordinal() \
                    <= datetime.date.today().toordinal():
                temp.append('{}-{}-{}'.format(date[:4], date[4:6], date[6:]))
            else:
                raise SourceError("日期不能大于当前日期，请修改")
        return temp

    def __change_stock(self, stocks):
        try:
            if isinstance(stocks, str):
                stocks_list = [stocks + '.sh' if stocks[0] == '6' else stocks + '.sz']
            else:
                stocks_list = [stock + '.sh' if stock[0] == '6' else stock + '.sz' for stock in stocks]
            return stocks_list
        except Exception:
            raise SourceError("转换股票名字时出错")


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

    def find_out(self, stock):
        return Truck()


class MysqlDestination(DestinationSingleton):

    def call_to_destination(self):
        self.connector = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASS_WD, db=DB,
                                         charset='utf8')

    def unpacking(self, plane):
        cur = self.connector.cursor()
        for truck in plane:
            code, time, close = truck.pop("Code")[0], truck.pop("Times"), truck.pop("Close")
            try:
                cur.execute('create table `{}` (Times date not null, Close float not null)'.format(code[:-3]))
            except pymysql.err.InternalError:
                pass
            data_length = len(time)
            for i in range(data_length):
                if not cur.execute('select * from `{}` where Times = {}'.format(code[:-3], time[i].strftime("%Y%m%d"))):
                    cur.execute('insert into `{}` values ({}, {})'.format(
                        code[:-3], time[i].strftime("%Y%m%d"), close[i]))
                else:
                    pass
        self.connector.commit()
        cur.close()
        return 'OK'

    def sold_out(self):
        cur = self.connector.cursor()
        cur.execute(
            "select concat('drop table `', table_name, '`;') from information_schema.tables where table_schema = "
            "'{}'".format(DB))
        var = cur.fetchall()
        length = len(var)
        for i in range(length):
            cur.execute("{}".format(var[i][0]))
        self.connector.commit()
        cur.close()

    def find_out(self, stock):
        truck = Truck()
        cur = self.connector.cursor()
        cur.execute("select * from `{}` order by Times".format(stock))
        var = cur.fetchall()
        for i in range(len(var)):
            truck.append("Times", var[i][0])
            truck.append("Close", var[i][1])
        return truck

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

    def append(self, name, data):
        self.__elem[name].extend(data)

    def pop(self, name):
        return self.__elem.pop(name)

    def keys(self):
        return self.__elem.keys()


sourceSingleton = globals().get(source, None)()
destinationSingleton = globals().get(destination, None)()


class TechnicalIndicator:

    def __init__(self, data):       # data = [price1, price2...priceN]
        self.data = data
        self.ans = []

    def _handle(self):
        pass


class MyEma(TechnicalIndicator):
    def __init__(self, data, days, weight_factor=0.7):
        TechnicalIndicator.__init__(self, data)
        self.days = days
        self.weight_factor = 2 / (days + 1)
        if len(self.data) < self.days:
            raise ValueError("数据长度不应小于天数")
        self._handle()

    def _handle(self):
        """
            data = [3, 4, 5]
            len(data) #3
            Ema(data, 1) => len(.ans) #3 => 3-1+1=3
        """
        ans_length = len(self.data) - self.days + 1
        for one in range(ans_length):
            var = 0
            for day in range(self.days):
                if day == 0:
                    var = self.data[day + one]
                else:
                    var = self.weight_factor * self.data[day + one] + (1 - self.weight_factor) * var
            self.ans.append(var)

    def __sub__(self, other):
        ans = []
        if len(other.ans) > len(self.ans):
            other.ans = other.ans[-(len(self.ans)):]
            ans_length = len(self.ans)
        else:
            self.ans = self.ans[-(len(other.ans)):]
            ans_length = len(other.ans)
        for one in range(ans_length):
            ans.append(self.ans[one] - other.ans[one])
        obj = Ema(ans, 1)
        return obj

    def __mul__(self, other):
        obj = Ema(list(map(lambda x: x * other, self.ans)), 1)
        return obj


class MyMacd(TechnicalIndicator):
    def __init__(self, data, short=12, long=26, m=9):
        TechnicalIndicator.__init__(self, data)
        self.short = short
        self.long = long
        self.m = m
        if len(self.data) < (self.long + self.m - 2):
            raise ValueError("数据长度不应小于天数")
        self._handle()

    def _handle(self):
        diff = MyEma(self.data, self.short) - MyEma(self.data, self.long)
        self.ans.append(diff.ans)
        dea = MyEma(diff.ans, self.m)
        self.ans.append(dea.ans)
        macd = (diff - dea) * 2
        self.ans.append(macd.ans)


class Sma(TechnicalIndicator):
    """移动平均线"""

    def __init__(self, data, days, factor):
        TechnicalIndicator.__init__(self, data)
        if days <= factor: raise ValueError("天数必须大于权重参数")
        self.days = days
        self.weight_factor = factor / days
        self._handle()

    def _handle(self):
        """self.ans = [ans]"""
        ans_length = len(self.data)
        for one in range(ans_length):
            if one == 0:
                self.ans.append(self.data[one])
            else:
                self.ans.append(self.weight_factor * self.data[one] + (1 - self.weight_factor) * self.ans[-1])

    def __sub__(self, other):
        ans, ans_length = [], len(self.ans)
        for one in range(ans_length):
            ans.append(self.ans[one] - other.ans[one])
        obj = Ema(ans, 1)
        return obj

    def __mul__(self, other):
        obj = Ema(list(map(lambda x: x * other, self.ans)), 1)
        return obj

    def __truediv__(self, other):
        ans, ans_length = [], len(self.ans)
        for one in range(ans_length):
            if other.ans[one] == 0:
                other.ans[one] = other.ans[one] + 0.000000001
            ans.append(self.ans[one] / other.ans[one])
        obj = Ema(ans, 1)
        return obj


class Ema(TechnicalIndicator):
    """指数移动平均线"""

    def __init__(self, data, days):
        TechnicalIndicator.__init__(self, data)
        self.days = days
        self.weight_factor = 2 / (days + 1)
        self._handle()

    def _handle(self):
        """self.ans = [ans]"""
        ans_length = len(self.data)
        for one in range(ans_length):
            if one == 0:
                self.ans.append(self.data[one])
            else:
                self.ans.append(self.weight_factor * self.data[one] + (1 - self.weight_factor) * self.ans[-1])

    def __sub__(self, other):
        ans, ans_length = [], len(self.ans)
        for one in range(ans_length):
            ans.append(self.ans[one] - other.ans[one])
        obj = Ema(ans, 1)
        return obj

    def __mul__(self, other):
        obj = Ema(list(map(lambda x: x * other, self.ans)), 1)
        return obj


class Macd(TechnicalIndicator):
    """指数平滑移动平均线"""
    def __init__(self, data, short=12, long=26, m=9):
        TechnicalIndicator.__init__(self, data)
        self.short = short
        self.long = long
        self.m = m
        self._handle()

    def _handle(self):
        """self.ans = [[diff], [dea], [macd]]"""
        diff = Ema(self.data, self.short) - Ema(self.data, self.long)
        self.ans.append(diff.ans)
        dea = Ema(diff.ans, self.m)
        self.ans.append(dea.ans)
        macd = (diff - dea) * 2
        self.ans.append(macd.ans)


class Rsi(TechnicalIndicator):
    """相对强弱指标"""
    def __init__(self, data, n1=6, n2=12, n3=24):
        TechnicalIndicator.__init__(self, data)
        self.N1 = n1
        self.N2 = n2
        self.N3 = n3
        self._handle()

    def _max(self, opt_list):
        return list(map(lambda x: max(x, 0), opt_list))

    def _abs(self, opt_list):
        return list(map(lambda x: abs(x), opt_list))

    def _handle(self):
        opt_list, opt_list_length = [], len(self.data) - 1
        for one in range(opt_list_length):
            opt_list.append(self.data[one + 1] - self.data[one])
        rsi1 = Sma(self._max(opt_list), self.N1, 1) / Sma(self._abs(opt_list), self.N1, 1) * 100
        self.ans.append(rsi1.ans)
        rsi2 = Sma(self._max(opt_list), self.N2, 1) / Sma(self._abs(opt_list), self.N2, 1) * 100
        self.ans.append(rsi2.ans)
        rsi3 = Sma(self._max(opt_list), self.N3, 1) / Sma(self._abs(opt_list), self.N3, 1) * 100
        self.ans.append(rsi3.ans)


def update(stocks, *date):
    plane = sourceSingleton.packing(stocks, date)
    destinationSingleton.unpacking(plane)


def delete():
    destinationSingleton.sold_out()


def query(stock, indicator):
    truck = destinationSingleton.find_out(stock)
    indicator(truck)


class YunaException(Exception):
    pass


class SourceError(YunaException):
    pass


class DestinationRefuseError(YunaException):
    pass


class CreateError(YunaException):
    pass


class SetiingError(YunaException):
    pass