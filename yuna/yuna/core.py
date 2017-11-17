from packages import pymysql
import WindPy

__title__ = 'yuna'
__version__ = '0.0.2'
__author__ = 'lvzhi'
__copyright__ = 'Copyright 2017 lvzhi'

WindPy.w.start()


def update():
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
    if not cur.execute('select * from `{}` where time = {}{}{}'.format(d[:-3], b[0], b[1], b[2])):
        cur.execute('insert into `{}` values ({}{}{}, {})'.format(d[:-3], b[0], b[1], b[2], c))
    else:
        pass
    conn.commit()
    cur.close()
    conn.close()
