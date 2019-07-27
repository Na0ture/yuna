from datetime import datetime
try:
    import tushare as ts
except ImportError:
    pass
from . import logger
from yuna.core import SourceSingleton, Plane, Truck


class TuShareSource(SourceSingleton):
    """
    Tushare财经库，不支持并发
    """

    stocks_basics = None

    @classmethod
    def datetime_to_date(cls, validity_dates):
        """
        查询时需要"2000-01-01"这种格式的时间戳
        """

        return [i.strftime('%Y-%m-%d') for i in validity_dates]

    async def packing(self, stocks, dates, session):
        logger.debug(stocks)
        from_query_date, to_query_date = self.__class__.datetime_to_date(self.__class__.validate_date(dates))
        plane = Plane()
        self.__class__.is_stocks_basics()
        for stock_name in [stocks]:
            stock_k = self.__class__.tushare_k_to_here(stock_name, from_query_date, to_query_date)
            plane.append(self.__class__.tushare_to_truck(stock_name, stock_k, self.__class__.stocks_basics))
        return plane

    @classmethod
    def tushare_to_truck(cls, stock_name, stock_k, stocks_basics):
        """
        查询后股票名字需格式转换，例如'000333'->'000333.SZ'，以符合存储数据的标准化

        :param stock_name: 股票名字，例如'002450'
        :param stock_k: 个体K线数据，具体访问->http://tushare.org/trading.html#id2
        :param stocks_basics: 总体基本面数据，具体访问->http://tushare.org/fundamental.html#id4
        :return: 装车，准备送往数据库
        """

        truck = Truck()
        truck.append('Code', super().alter_stock_code(stock_name))
        truck.extend('Times', list(map(lambda x: datetime.strptime(x, '%Y-%m-%d'), stock_k.date.tolist())))
        truck.extend('Low', stock_k.low)
        truck.extend('High', stock_k.high)
        truck.extend('Close', stock_k.close)
        truck.extend('Volume', stock_k.volume)
        truck.extend('PE', [stocks_basics.get('pe').get(stock_name) or 0])
        truck.extend('PB', [stocks_basics.get('pb').get(stock_name) or 0])
        truck.extend('PS', [0])
        truck.extend('PCF', [0])
        return truck

    @classmethod
    def tushare_basics_to_here(cls):
        """
        :return: 返回从tushare获取的所有股票基本面数据
        """

        return ts.get_stock_basics()

    @classmethod
    def is_stocks_basics(cls):
        if cls.stocks_basics is None:
            cls.stocks_basics = cls.tushare_basics_to_here()

    @classmethod
    def tushare_k_to_here(cls, stock_name, from_query_date, to_query_date):
        """
        :param stock_name: 股票名字，例如'002450'
        :param from_query_date: 起始日期，例如'2016-05-31'
        :param to_query_date: 终止日期，例如'2016-06-03'
        :return: 返回从tushare指定获取的股票K线数据
        """

        return ts.get_k_data(stock_name, start=from_query_date, end=to_query_date)
