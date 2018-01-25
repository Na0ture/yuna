from ..core import TechnicalIndicator
from .myema import MyEma


class MyMacd(TechnicalIndicator):
    def __init__(self, data, short=12, long=26, m=9):
        TechnicalIndicator.__init__(self, data)
        self.short = short
        self.long = long
        self.m = m
        if len(self.data) < (self.long + self.m - 2):
            raise ValueError("数据长度不应小于天数")
        self._handle()

    def _handle(self):
        diff = MyEma(self.data, self.short) - MyEma(self.data, self.long)
        self.ans.append(diff.ans)
        dea = MyEma(diff.ans, self.m)
        self.ans.append(dea.ans)
        macd = (diff - dea) * 2
        self.ans.append(macd.ans)