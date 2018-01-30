import numpy


class Ema_Numpy():
    """指数移动平均线"""

    def __init__(self, data, days=12, switch=False):
        self.data = self._list2numpy(data)
        self.days = days
        self.weight_factor = 2 / (days + 1)
        if not switch:
            self.ans = numpy.zeros(self.data.size)
            self._handle()
        else:
            self.ans = self.data

    def _handle(self):
        ans_length = self.ans.size
        for one in range(ans_length):
            if one == 0:
                self.ans[0] = self.data[one]
            else:
                self.ans[one] = self.weight_factor * self.data[one] + (1 - self.weight_factor) * self.ans[one - 1]

    def __sub__(self, other):
        return Ema_Numpy(self.ans - other.ans, switch=True)

    def __mul__(self, other):
        return Ema_Numpy(self.ans * other, switch=True)

    def _list2numpy(self, data):
        return numpy.array(data)