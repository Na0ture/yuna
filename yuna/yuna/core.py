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


def _update(conn, stock, date=1):
    """周六日无法更新"""
    if datetime.date.today().weekday() in (5, 6):
        return 'None'
    stock_name = stock + '.sh' if stock[0] == '6' else stock + '.sz'
    WindPy.w.start()
    cur = conn.cursor()
    a = WindPy.w.wsd(stock_name, 'close')
    b = a.Times[0].timetuple()
    c = a.Data[0][0]
    d = a.Codes[0]
    try:
        cur.execute('create table `{}` (time date not null, price float not null)'.format(d[:-3]))
    except pymysql.err.InternalError:
        pass
    if not cur.execute('select * from `{}` where time = {}{}{}'.format(d[:-3], b[0], b[1], _date_update(b[2]))):
        cur.execute('insert into `{}` values ({}{}{}, {})'.format(d[:-3], b[0], b[1], _date_update(b[2]), c))
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
