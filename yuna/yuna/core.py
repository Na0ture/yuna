from packages import pymysql
import WindPy
import re
import datetime
from functools import partial

__title__ = 'yuna'
__version__ = '0.0.2'
__author__ = 'lvzhi'
__copyright__ = 'Copyright 2017 lvzhi'

'''连接数据库相关常量'''
HOST = 'localhost'
PORT = 3306
USER = 'root'
PASS_WD = 'lvzhi'
DB = 'yuna'


def _update(conn, stocks, date=1):
    """周六日无法更新"""
    if datetime.date.today().weekday() in (5, 6):
        return 'None'
    if isinstance(stocks, str):
        stock_list = [stocks + '.sh' if stocks[0] == '6' else stocks + '.sz']
    else:
        stock_list = [stock + '.sh' if stock[0] == '6' else stock + '.sz' for stock in stocks]
    (year, mon, mday, *scrap) = (datetime.date.today() - datetime.timedelta(days=date)).timetuple()
    query_date = '{}-{}-{}'.format(year, mon, mday)
    WindPy.w.start()
    cur = conn.cursor()
    for stock_name in stock_list:
        a = WindPy.w.wsd(stock_name, 'close', query_date)
        time_list, data_list, code_list = a.Times, a.Data, a.Codes
        time_list.append(len(a.Times))
        data_list.append(len(a.Data))
        code_list.append(len(a.Codes))

        """
        #b = a.Times[0].timetuple()
        #c = a.Data[0][0]
        #d = a.Codes[0]
        """

        for code in range(code_list[-1]):
            try:
                cur.execute('create table `{}` (time date not null, price float not null)'.format(code_list[code][:-3]))
            except pymysql.err.InternalError:
                pass
            for time in range(time_list[-1]):
                if not cur.execute('select * from `{}` where time = {}{}{}'.format(
                        code_list[code][:-3], time_list[time].timetuple()[0],
                        _date_update(time_list[time].timetuple()[1]),
                        _date_update(time_list[time].timetuple()[2]))):
                    cur.execute('insert into `{}` values ({}{}{}, {})'.format(
                        code_list[code][:-3], time_list[time].timetuple()[0],
                        _date_update(time_list[time].timetuple()[1]),
                        _date_update(time_list[time].timetuple()[2]),
                        data_list[code][time]))
                else:
                    pass
    conn.commit()
    cur.close()
    return 'OK'


def _delete(conn):
    cur = conn.cursor()
    cur.execute("select concat('drop table `', table_name, '`;') from information_schema.tables where table_schema = "
                "'{}'".format(DB))
    var = cur.fetchall()
    length = len(var)
    for i in range(length):
        cur.execute("{}".format(var[i][0]))
    conn.commit()
    cur.close()


def _date_update(original_date):
    """把类似2这样的单个数字转化为02，而双数字则保持不变"""
    return re.sub(r'(\b[1-9]\b)', r'0\1', str(original_date))


def _macd():
    pass


def _ma():
    pass


if __name__ == '__main__':
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASS_WD, db=DB,
                           charset='utf8')
    update = partial(_update, conn)
    delete = partial(_delete, conn)
    """conn.close()"""
