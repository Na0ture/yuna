import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdate
from yuna.core import VisualIndicator


class Relate(VisualIndicator):

    def __init__(self, data):
        super().__init__(data)

    def _handle(self):
        fmt = '%.0f%%'
        yticks = mtick.FormatStrFormatter(fmt)
        fig, ax1 = plt.subplots(nrows=1, ncols=1, figsize=(10, 7))
        ax1.yaxis.set_major_formatter(yticks)
        ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m-%d'))
        ax1.grid(True)
        for j in range(len(self.data)):
            exec(f"tmp0, y0 = self.data[{j}]['Close'], []")
            for k in range(len(self.data[j]['Close'])):
                exec(f'y0.append((tmp0[{k}] / tmp0[0] - 1) * 100)')
            exec(f"ax1.plot(self.data[{j}]['Times'], y0, label='{self.data[j]['Code'][0]}')")
        ax1.legend(loc=(0.65, 0.8))
        plt.show()
