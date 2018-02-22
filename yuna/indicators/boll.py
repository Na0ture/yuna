from math import sqrt
from ..core import TechnicalIndicator
from .ma import Ma


class Boll(TechnicalIndicator):
    """
    布林带指标
    算法来源：https://en.wikipedia.org/wiki/Bollinger_Bands
    """

    def __init__(self, data, n=20, p=2, handle='off'):
        self.N = n
        self.P = p
        super().__init__(data, handle)

    def _handle(self):
        mid = Ma(self.close, self.N, handle='on')
        self.ans.append(mid.ans)
        upper = mid + self.__class__.std(self.close, self.N) * self.P
        self.ans.append(upper.ans)
        lower = mid - self.__class__.std(self.close, self.N) * self.P
        self.ans.append(lower.ans)

    @staticmethod
    def std(close, n):
        """
        :param close: 原数据里的收盘价列表
        :param n: 周期
        :return: 不处理的Ma对象，其字段ans存放收盘价列表的方差列表

        选用的是样本方差
        算法来源：https://en.wikipedia.org/wiki/Standard_deviation
        """
        length, ans, temp = len(close), [], 0
        ma = Ma(close, n, handle='on').ans
        for i in range(length):
            if i < n:
                for j in range(i + 1):
                    temp += (close[j] - ma[i]) ** 2
            else:
                for j in range(i + 1 - n, i + 1):
                    temp += (close[j] - ma[i]) ** 2
            ans.append(sqrt(temp / (n - 1)))
            temp = 0
        return Ma(ans)
