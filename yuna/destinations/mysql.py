from ..packages import pymysql
from ..core import DestinationSingleton, Truck, Plane
from ..setting import HOST, PORT, USER, PASS_WD, DB


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

    def find_out(self, stocks):
        plane = Plane()
        cur = self.connector.cursor()
        for stock in stocks:
            truck = Truck()
            cur.execute("select * from `{}` order by Times".format(stock))
            var = cur.fetchall()
            truck.append("Code", stock)
            for i in range(len(var)):
                truck.append("Times", var[i][0])
                truck.append("Close", var[i][1])
            plane.append(truck)
        return plane
