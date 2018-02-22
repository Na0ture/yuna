from ..core import TechnicalIndicator
from .ema import Ema


class Macd(TechnicalIndicator):
    """
    指数平滑移动平均线(Moving average convergence/divergence)
    算法来源：https://en.wikipedia.org/wiki/MACD
    """
    def __init__(self, data, short=12, long=26, m=9, handle='off'):
        self.short = short
        self.long = long
        self.m = m
        super().__init__(data, handle)

    def _handle(self):
        """self.ans = [[diff], [dea], [macd]]"""
        diff = Ema(self.data, self.short) - Ema(self.data, self.long)
        self.ans.append(diff.ans)
        dea = Ema(diff.ans, self.m, handle='on')
        self.ans.append(dea.ans)
        macd = (diff - dea) * 2
        self.ans.append(macd.ans)
