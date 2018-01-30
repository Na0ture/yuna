from ..core import TechnicalIndicator


class Ema(TechnicalIndicator):
    """指数移动平均线"""

    def __init__(self, data, days=12, switch=False):
        TechnicalIndicator.__init__(self, data)
        self.days = days
        self.weight_factor = 2 / (days + 1)
        if not switch:
            self._handle()
        else:
            self.ans = self.data

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
