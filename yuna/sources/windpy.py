import datetime

try:
    import WindPy
except ImportError:
    pass

from ..core import SourceSingleton, Plane, Truck, SourceError


class WindpySource(SourceSingleton):

    def call_to_source(self):
        WindPy.w.start()

    def packing(self, stocks, dates):
        stocks_list = self._change_stock(stocks)
        fquery_date, bquery_date = self.change_date(dates)
        plane = Plane()
        for stock_name in stocks_list:
            a = WindPy.w.wsd(stock_name, "close", fquery_date, bquery_date, "Fill=Previous;PriceAdj=F")
            truck = Truck()
            truck.extend("Code", a.Codes)
            truck.extend("Times", a.Times)
            truck.extend("Close", a.Data[0])
            plane.append(truck)
        return plane

    def change_date(self, dates):
        temp = list()
        for date in dates:
            if datetime.date(int(date[:4]), int(date[4:6]), int(date[6:])).toordinal() \
                    <= datetime.date.today().toordinal():
                temp.append('{}-{}-{}'.format(date[:4], date[4:6], date[6:]))
            else:
                raise SourceError("日期不能大于当前日期，请修改")
        return temp