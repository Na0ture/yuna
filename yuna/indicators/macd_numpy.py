import logging
import numpy

from .ema_numpy import Ema_Numpy


class Macd_Numpy():
    """指数平滑移动平均线"""
    def __init__(self, data, short=12, long=26, m=9):
        self.data = self._list2numpy(data)
        self.ans = []
        self.short = short
        self.long = long
        self.m = m
        self._handle()

    def _handle(self):
        diff = Ema_Numpy(self.data, self.short) - Ema_Numpy(self.data, self.long)
        self.ans.append(diff.ans)
        dea = Ema_Numpy(diff.ans.tolist(), self.m)
        self.ans.append(dea.ans)
        macd = (diff - dea) * 2
        self.ans.append(macd.ans)

    def _list2numpy(self, data):
        return numpy.array(data)