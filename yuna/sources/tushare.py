import pandas as pd
import tushare as ts
from ..core import SourceSingleton, Plane, Truck


class TuShareSource(SourceSingleton):

    @classmethod
    def datetime_to_date(cls, validity_dates):
        """
        查询时需要"2000-01-01"这种格式的时间戳
        """

        return [i.strftime('%Y-%m-%d') for i in validity_dates]

    def packing(self, stocks, dates):
        from_query_date, to_query_date = self.__class__.datetime_to_date(self.__class__.validate_date(dates))
        plane = Plane()
        stocks_basics = self.__class__.tushare_basics_to_here()
        for stock_name in [stocks]:
            plane.append(self.__class__.tushare_to_truck(stock_name, from_query_date, to_query_date, stocks_basics))
        return plane

    @classmethod
    def tushare_to_truck(cls, stock_name, from_query_date, to_query_date, stocks_basics):
        """
        查询后股票名字需格式转换，例如'000333'->'000333.SZ'，以符合存储数据的标准化

        :param stock_name: 股票名字，例如'002450'
        :param from_query_date: 起始日期，例如'2016-05-31'
        :param to_query_date: 终止日期，例如'2016-06-03'
        :param stocks_basics: 基本面数据，具体详情访问http://tushare.org/fundamental.html#id4
        :return: 装车，准备送往数据库
        """

        truck = Truck()
        pandas_data = cls.tushare_k_to_here(stock_name, from_query_date, to_query_date)
        truck.extend('Code', cls.change_stock(stock_name))
        truck.extend('Times', pd.to_datetime(pandas_data.date))
        truck.extend('Low', pandas_data.low)
        truck.extend('High', pandas_data.high)
        truck.extend('Close', pandas_data.close)
        truck.extend('Volume', pandas_data.volume)
        truck.extend('PE', [stocks_basics.get('pe').get(stock_name)])
        truck.extend('PB', [stocks_basics.get('pb').get(stock_name)])
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
    def tushare_k_to_here(cls, stock_name, from_query_date, to_query_date):
        """
        :param stock_name: 股票名字，例如'002450'
        :param from_query_date: 起始日期，例如'2016-05-31'
        :param to_query_date: 终止日期，例如'2016-06-03'
        :return: 返回从tushare指定获取的股票K线数据
        """

        return ts.get_k_data(stock_name, start=from_query_date, end=to_query_date)
