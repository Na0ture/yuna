from datetime import datetime

try:
    import tushare as ts
except ImportError:
    ts = None

from . import logger
from yuna.core import SourceSingleton, Plane, Truck
from yuna.exceptions import SourceError


class TuShareSource(SourceSingleton):
    """
    Tushare Pro 财经库，不支持并发
    需先注册 https://tushare.pro 获取 token，并通过 setup(TUSHARE_TOKEN='xxx') 配置
    """

    _pro = None

    @classmethod
    def call_to_source(cls):
        if ts is None:
            raise SourceError('请先安装 tushare: pip install tushare')
        from yuna.setting import TUSHARE_TOKEN
        if not TUSHARE_TOKEN:
            raise SourceError('请先通过 yuna.setup(TUSHARE_TOKEN="xxx") 设置 tushare token')
        cls._pro = ts.pro_api(TUSHARE_TOKEN)

    @classmethod
    def datetime_to_date(cls, validity_dates):
        return [i.strftime('%Y%m%d') for i in validity_dates]

    async def packing(self, stocks, dates, session):
        logger.debug(stocks)
        from_query_date, to_query_date = self.__class__.datetime_to_date(
            self.__class__.validate_date(dates)
        )
        plane = Plane()
        for stock_name in [stocks]:
            stock_k = self.__class__.tushare_k_to_here(stock_name, from_query_date, to_query_date)
            if stock_k is not None and not stock_k.empty:
                stock_b = self.__class__.tushare_basics_to_here(stock_name, from_query_date, to_query_date)
                plane.append(self.__class__.tushare_to_truck(stock_name, stock_k, stock_b))
        return plane

    @classmethod
    def tushare_to_truck(cls, stock_name, stock_k, stock_b):
        stock_k = stock_k.sort_values('trade_date')
        truck = Truck()
        truck.extend('Code', cls.change_stock(stock_name))
        truck.extend('Times', [datetime.strptime(str(d), '%Y%m%d') for d in stock_k['trade_date']])
        truck.extend('Low', stock_k['low'])
        truck.extend('High', stock_k['high'])
        truck.extend('Close', stock_k['close'])
        truck.extend('Volume', stock_k['vol'])
        if stock_b is not None and not stock_b.empty:
            latest = stock_b.iloc[-1]
            truck.extend('PE', [latest.get('pe', 0) or 0])
            truck.extend('PB', [latest.get('pb', 0) or 0])
        else:
            truck.extend('PE', [0])
            truck.extend('PB', [0])
        truck.extend('PS', [0])
        truck.extend('PCF', [0])
        return truck

    @classmethod
    def tushare_k_to_here(cls, stock_name, from_query_date, to_query_date):
        ts_code = stock_name if '.' in stock_name else stock_name + '.SZ'
        if ts_code[-3] == '6':
            ts_code = stock_name + '.SH'
        try:
            df = cls._pro.daily(ts_code=ts_code, start_date=from_query_date, end_date=to_query_date)
            return df
        except Exception as e:
            logger.warning(f'获取 {ts_code} K线失败: {e}')
            return None

    @classmethod
    def tushare_basics_to_here(cls, stock_name, from_query_date, to_query_date):
        ts_code = stock_name if '.' in stock_name else stock_name + '.SZ'
        if ts_code[-3] == '6':
            ts_code = stock_name + '.SH'
        try:
            df = cls._pro.daily_basic(ts_code=ts_code, start_date=from_query_date, end_date=to_query_date)
            return df
        except Exception:
            return None
