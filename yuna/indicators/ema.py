from ..core import TechnicalIndicator


class Ema(TechnicalIndicator):
    """
    指数移动平均线（Exponential moving average）
    算法来源：https://en.wikipedia.org/wiki/Moving_average
    """

    def __init__(self, data, days=12, handle='off'):
        self.days = days
        self.weight_factor = 2 / (days + 1)
        super().__init__(data, handle)

    def _handle(self):
        ans_length = len(self.close)
        for one in range(ans_length):
            if one == 0:
                self.ans.append(self.close[one])
            else:
                self.ans.append(self.weight_factor * self.close[one] + (1 - self.weight_factor) * self.ans[-1])

    def __sub__(self, other):
        ans, ans_length = [], len(self.ans)
        for one in range(ans_length):
            ans.append(self.ans[one] - other.ans[one])
        return Ema(ans)

    def __mul__(self, other):
        return Ema(list(map(lambda x: x * other, self.ans)))
