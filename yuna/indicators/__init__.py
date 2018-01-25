from . import ema, macd, myema, mymacd, rsi, sma

_all_indicators = {
    'macd': macd.Macd,
    'ema': ema.Ema,
    'myema': myema.MyEma,
    'mymacd': mymacd.MyMacd,
    'rsi': rsi.Rsi,
    'sma': sma.Sma,
}
