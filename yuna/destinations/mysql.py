from datetime import datetime
from peewee import *
from yuna.core import DestinationSingleton, Truck, Plane
from ..setting import HOST, PORT, USER, PASS_WD, DB


class MysqlDestination(DestinationSingleton):

    def call_to_destination(self):
        self.db = MySQLDatabase(DB, user=USER, password=PASS_WD, host=HOST, port=PORT)
        self.db.connect()
        self.db.bind([Basic, Details])

    def unpacking(self, plane):
        """
        当truck不存在任何字段时，从truck获取到的数据内容如下：
        code = "None"，pe = 0, pb = 0, ps = 0, pcf = 0, time = [datetime(2000, 1, 1)],
        low = [0], high = [0], close = [0], volume = [0]

        :param plane: 即将要卸货装载着多个truck的plane实例
        """
        for truck in plane:
            code = truck.get("Code", "None")[0]
            pe = truck.get("PE", [0])[0]
            pb = truck.get("PB", [0])[0]
            ps = truck.get("PS", [0])[0]
            pcf = truck.get("PCF", [0])[0]
            time = truck.get("Times", [datetime(2000, 1, 1)])
            low = truck.get("Low", [0])
            high = truck.get("High", [0])
            close = truck.get("Close", [0])
            volume = truck.get("Volume", [0])

            self.db.create_tables([Basic, Details])

            Basic.create(code=code, PE=pe, PB=pb, PS=ps, PCF=pcf)

            data_length = len(time)
            for i in range(data_length):
                Details.create(basic=Basic.get(Basic.code == code).id, time=time[i], low=low[i],
                               high=high[i], close=close[i], volume=volume[i])

    def sold_out(self):
        self.db.drop_tables([Basic, Details])

    def find_out(self, stocks):
        plane = Plane()
        for stock in stocks:
            truck = Truck()
            basic = Basic.get(fn.Substr(Basic.code, 1, 6) == stock)
            truck.append("Code", basic.code)
            truck.append("PE", basic.PE)
            truck.append("PB", basic.PB)
            truck.append("PS", basic.PS)
            truck.append("PCF", basic.PCF)

            details = Details.select().join(Basic).where(fn.Substr(Basic.code, 1, 6) == stock).order_by(Details.time)
            for i in details:
                truck.append("Times", i.time)
                truck.append("Low", i.low)
                truck.append("High", i.high)
                truck.append("Close", i.close)
                truck.append("Volume", i.volume)
            plane.append(truck)
        return plane


class Basic(Model):

    code = CharField()
    PE = DoubleField()
    PB = DoubleField()
    PS = DoubleField()
    PCF = DoubleField()


class Details(Model):

    basic = ForeignKeyField(Basic)
    time = DateTimeField()
    low = DoubleField()
    high = DoubleField()
    close = DoubleField()
    volume = DoubleField()

