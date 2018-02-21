from ..core import TechnicalIndicator
from .sma import Sma


class Kdj(TechnicalIndicator):
    """随机指标"""

    def __init__(self, data, n=9, m1=3, m2=3, handle='off'):
        self.N = n
        self.M1 = m1
        self.M2 = m2
        super().__init__(data, handle)

    def _handle(self):
        llw = self.__class__.llw(self.low, self.N)
        hhv = self.__class__.hhv(self.high, self.N)
        ans_length, rsv = len(self.close), []
        for one in range(ans_length):
            rsv.append((self.close[one] - llw[one]) / (hhv[one] - llw[one]) * 100)
        k = Sma(rsv, self.M1, 1, handle='on')
        self.ans.append(k.ans)
        d = Sma(k.ans, self.M2, 1, handle='on')
        self.ans.append(d.ans)
        j = k * 3 - d * 2
        self.ans.append(j.ans)

    @staticmethod
    def llw(low, n):
        """
        :param low: 原数据里的最低价列表
        :param n: 周期
        :return: 一定周期内最低价的中间列表
        """
        length = len(low)
        return [min(low[0:i + 1]) if i < n else min(low[i + 1 - n:i + 1]) for i in range(length)]

    @staticmethod
    def hhv(high, n):
        """
        :param high: 原数据里的最高价列表
        :param n: 周期
        :return: 一定周期内最高价的中间列表
        """
        length = len(high)
        return [max(high[0:i + 1]) if i < n else max(high[i + 1 - n:i + 1]) for i in range(length)]

