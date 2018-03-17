import datetime
import math

try:
    import WindPy
except ImportError:
    pass

from ..core import SourceSingleton, Plane, Truck, SourceError


class WindpySource(SourceSingleton):

    @classmethod
    def call_to_source(cls):
        WindPy.w.start()

    def packing(self, stocks, dates):
        stocks_list = super().change_stock(stocks)
        from_query_date, to_query_date = self.__class__.datetime_to_date(self.__class__.validate_date(dates))
        plane = Plane()
        for stock_name in stocks_list:
            stock_data = self.__class__.wind_to_here(stock_name, from_query_date, to_query_date)
            plane.append(self.__class__.list_to_truck(stock_name, stock_data))
        return plane

    @classmethod
    def datetime_to_date(cls, validity_dates):
        return [i.strftime('%Y-%m-%d') for i in validity_dates]

    @classmethod
    def wind_to_here(cls, stock_name, from_query_date, to_query_date):
        return WindPy.w.wsd(stock_name, "low,high,close,volume,val_pe_deducted_ttm,pb_lf,ps_ttm,pcf_ncf_ttm",
                            from_query_date, to_query_date, "Fill=Previous;PriceAdj=F")

    @classmethod
    def list_to_truck(cls, stock_name, stock_data):
        """
        :param stock_name: 股票名字，例如'002450.SZ'
        :param stock_data: 股票k线以及财务list数据
        :return: 装车，准备送往数据库

        因wind资讯无法处理某种情况：比方说某新股在2018年1月1日上市，使用者从2017年某日检索到至今，
        会使2017年到上市日期为止这段数据为NaN或者None，故增加相应的代码处理这些情况
        """
        truck, j = Truck(), 0
        for i in range(len(stock_data.Data[0])):
            if stock_data.Data[0][i] is None or math.isnan(stock_data.Data[0][i]):
                j += 1
        truck.extend('Code', [stock_name])
        truck.extend('Times', stock_data.Times[j:])
        truck.extend('Low', stock_data.Data[0][j:])
        truck.extend('High', stock_data.Data[1][j:])
        truck.extend('Close', stock_data.Data[2][j:])
        truck.extend('Volume', stock_data.Data[3][j:])
        if stock_data.Data[4][-1] is not None and not math.isnan(stock_data.Data[4][-1]):
            truck.extend('PE', [stock_data.Data[4][-1]])
        if stock_data.Data[5][-1] is not None and not math.isnan(stock_data.Data[5][-1]):
            truck.extend('PB', [stock_data.Data[5][-1]])
        if stock_data.Data[6][-1] is not None and not math.isnan(stock_data.Data[6][-1]):
            truck.extend('PS', [stock_data.Data[6][-1]])
        if stock_data.Data[7][-1] is not None and not math.isnan(stock_data.Data[7][-1]):
            truck.extend('PCF', [stock_data.Data[7][-1]])
        return truck
