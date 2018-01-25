from ..core import TechnicalIndicator
from .ema import Ema


class MyEma(TechnicalIndicator):
    def __init__(self, data, days, weight_factor=0.7):
        TechnicalIndicator.__init__(self, data)
        self.days = days
        self.weight_factor = 2 / (days + 1)
        if len(self.data) < self.days:
            raise ValueError("数据长度不应小于天数")
        self._handle()

    def _handle(self):
        """
            data = [3, 4, 5]
            len(data) #3
            Ema(data, 1) => len(.ans) #3 => 3-1+1=3
        """
        ans_length = len(self.data) - self.days + 1
        for one in range(ans_length):
            var = 0
            for day in range(self.days):
                if day == 0:
                    var = self.data[day + one]
                else:
                    var = self.weight_factor * self.data[day + one] + (1 - self.weight_factor) * var
            self.ans.append(var)

    def __sub__(self, other):
        ans = []
        if len(other.ans) > len(self.ans):
            other.ans = other.ans[-(len(self.ans)):]
            ans_length = len(self.ans)
        else:
            self.ans = self.ans[-(len(other.ans)):]
            ans_length = len(other.ans)
        for one in range(ans_length):
            ans.append(self.ans[one] - other.ans[one])
        obj = Ema(ans, 1)
        return obj

    def __mul__(self, other):
        obj = Ema(list(map(lambda x: x * other, self.ans)), 1)
        return obj