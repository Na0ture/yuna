from . import ema, macd, myema, mymacd, rsi, sma, ema_numpy, macd_numpy

_all_indicators = {
    'macd': macd.Macd,
    'ema': ema.Ema,
    #'myema': myema.MyEma,
    #'mymacd': mymacd.MyMacd,
    'rsi': rsi.Rsi,
    'sma': sma.Sma,
    #'ema_numpy': ema_numpy.Ema_Numpy,
    #'macd_numpy': macd_numpy.Macd_Numpy,
}
