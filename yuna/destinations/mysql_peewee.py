from peewee import *
from yuna.core import DestinationSingleton, Truck, Plane
from ..setting import HOST, PORT, USER, PASS_WD, DB


class MysqlDestination(DestinationSingleton):

    def call_to_destination(self):
        self.db = MySQLDatabase(DB, user=USER, password=PASS_WD, host=HOST, port=PORT)
        self.db.connect()
        self.db.bind([Basic, Details])

    def unpacking(self, plane):
        for truck in plane:
            code = truck.pop("Code")[0]
            pe = truck.pop("PE")[0]
            pb = truck.pop("PB")[0]
            ps = truck.pop("PS")[0]
            pcf = truck.pop("PCF")[0]
            time = truck.pop("Times")
            low = truck.pop("Low")
            high = truck.pop("High")
            close = truck.pop("Close")
            volume = truck.pop("Volume")

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
    #name = CharField()  #验证下中文名字是否可行
    PE = DoubleField()  #市盈率
    PB = DoubleField()  #市净率
    PS = DoubleField()  #市销率
    PCF = DoubleField() #市现率


class Details(Model):

    basic = ForeignKeyField(Basic)
    time = DateTimeField()
    low = DoubleField()
    high = DoubleField()
    close = DoubleField()
    volume = IntegerField()

