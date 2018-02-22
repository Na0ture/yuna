from ..core import TechnicalIndicator


class Ma(TechnicalIndicator):
    """
    简单移动平均线（moving average）
    算法来源：https://en.wikipedia.org/wiki/Moving_average
    """

    def __init__(self, data, n=20, handle='off'):
        self.N = n
        super().__init__(data, handle)

    def _handle(self):
        ans_length = len(self.close)
        for i in range(ans_length):
            if i < self.N:
                self.ans.append(sum(self.close[0:i + 1]) / self.N)
            else:
                self.ans.append(sum(self.close[i + 1 - self.N:i + 1]) / self.N)

    def __add__(self, other):
        ans, ans_length = [], len(self.ans)
        for one in range(ans_length):
            ans.append(self.ans[one] + other.ans[one])
        return Ma(ans)

    def __sub__(self, other):
        ans, ans_length = [], len(self.ans)
        for one in range(ans_length):
            ans.append(self.ans[one] - other.ans[one])
        return Ma(ans)

    def __mul__(self, other):
        return Ma(list(map(lambda x: x * other, self.ans)))
