from ..core import TechnicalIndicator
from .ema import Ema


class Macd(TechnicalIndicator):
    """指数平滑移动平均线"""
    def __init__(self, data, short=12, long=26, m=9):
        TechnicalIndicator.__init__(self, data)
        self.short = short
        self.long = long
        self.m = m
        self._handle()

    def _handle(self):
        """self.ans = [[diff], [dea], [macd]]"""
        diff = Ema(self.data, self.short) - Ema(self.data, self.long)
        self.ans.append(diff.ans)
        dea = Ema(diff.ans, self.m)
        self.ans.append(dea.ans)
        macd = (diff - dea) * 2
        self.ans.append(macd.ans)