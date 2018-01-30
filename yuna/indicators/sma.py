from ..core import TechnicalIndicator
from .ema import Ema


class Sma(TechnicalIndicator):
    """移动平均线"""

    def __init__(self, data, days, factor):
        TechnicalIndicator.__init__(self, data)
        if days <= factor: raise ValueError("天数必须大于权重参数")
        self.days = days
        self.weight_factor = factor / days
        self._handle()

    def _handle(self):
        """self.ans = [ans]"""
        ans_length = len(self.data)
        for one in range(ans_length):
            if one == 0:
                self.ans.append(self.data[one])
            else:
                self.ans.append(self.weight_factor * self.data[one] + (1 - self.weight_factor) * self.ans[-1])

    def __sub__(self, other):
        ans, ans_length = [], len(self.ans)
        for one in range(ans_length):
            ans.append(self.ans[one] - other.ans[one])
        return Ema(ans, switch=True)

    def __mul__(self, other):
        return Ema(list(map(lambda x: x * other, self.ans)), switch=True)

    def __truediv__(self, other):
        ans, ans_length = [], len(self.ans)
        for one in range(ans_length):
            if other.ans[one] == 0:
                other.ans[one] = other.ans[one] + 0.000000001
            ans.append(self.ans[one] / other.ans[one])
        return Ema(ans, switch=True)
