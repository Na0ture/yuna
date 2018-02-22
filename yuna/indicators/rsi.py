from ..core import TechnicalIndicator
from .sma import Sma


class Rsi(TechnicalIndicator):
    """
    相对强弱指标（Relative strength index）
    算法来源：https://en.wikipedia.org/wiki/Relative_strength_index
    """

    def __init__(self, data, n1=6, n2=12, n3=24, handle='off'):
        self.N1 = n1
        self.N2 = n2
        self.N3 = n3
        super().__init__(data, handle)

    def _max(self, opt_list):
        return list(map(lambda x: max(x, 0), opt_list))

    def _abs(self, opt_list):
        return list(map(lambda x: abs(x), opt_list))

    def _handle(self):
        opt_list, opt_list_length = [], len(self.close) - 1
        for one in range(opt_list_length):
            opt_list.append(self.close[one + 1] - self.close[one])
        rsi1 = \
            Sma(self._max(opt_list), self.N1, handle='on') / Sma(self._abs(opt_list), self.N1, handle='on') * 100
        self.ans.append(rsi1.ans)
        rsi2 = \
            Sma(self._max(opt_list), self.N2, handle='on') / Sma(self._abs(opt_list), self.N2, handle='on') * 100
        self.ans.append(rsi2.ans)
        rsi3 = \
            Sma(self._max(opt_list), self.N3, handle='on') / Sma(self._abs(opt_list), self.N3, handle='on') * 100
        self.ans.append(rsi3.ans)
