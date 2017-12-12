from packages import pymysql
import WindPy
import re
import datetime

__title__ = 'yuna'
__version__ = '0.0.2'
__author__ = 'lvzhi'
__copyright__ = 'Copyright 2017 lvzhi'


def main():
    pass


def update(stock=600068, date=None):
    """周六日无法更新"""
    if datetime.date.today().weekday() in (5, 6):
        return 'None'

    WindPy.w.start()
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='lvzhi', db='yuna',
                           charset='utf8')
    cur = conn.cursor()
    a = WindPy.w.wsd('600068.sh', 'close')
    b = a.Times[0].timetuple()
    c = a.Data[0][0]
    d = a.Codes[0]
    try:
        cur.execute('create table `{}` (time date not null, price float not null)'.format(d[:-3]))
    except pymysql.err.InternalError:
        pass
    if not cur.execute('select * from `{}` where time = {}{}{}'.format(d[:-3], b[0], b[1], __date_update(b[2]))):
        cur.execute('insert into `{}` values ({}{}{}, {})'.format(d[:-3], b[0], b[1],__date_update(b[2]), c))
    else:
        pass
    conn.commit()
    cur.close()
    conn.close()
    return 'OK'


def __date_update(original_date):
    """把类似2这样的单个数字转化为02，而双数字则保持不变"""
    return re.sub(r'(\b[1-9]\b)', r'0\1', str(original_date))


def _macd():
    pass


def _ma():
    pass


if __name__ == '__main__':
    main()