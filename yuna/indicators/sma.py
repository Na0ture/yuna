from ..core import TechnicalIndicator


class Sma(TechnicalIndicator):
    """
    指数移动平均线（moving average）
    算法来源：https://en.wikipedia.org/wiki/Moving_average
    """

    def __init__(self, data, days=6, factor=1, handle='off'):
        self.days = days
        self.weight_factor = factor / days
        super().__init__(data, handle)

    def _handle(self):
        """self.ans = [ans]"""
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
        return Sma(ans)

    def __mul__(self, other):
        return Sma(list(map(lambda x: x * other, self.ans)))

    def __truediv__(self, other):
        ans, ans_length = [], len(self.ans)
        for one in range(ans_length):
            if other.ans[one] == 0:
                other.ans[one] = other.ans[one] + 0.000000001
            ans.append(self.ans[one] / other.ans[one])
        return Sma(ans)
