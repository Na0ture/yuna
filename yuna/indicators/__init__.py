from . import macd, rsi, kdj, boll, ma

_all_indicators = {
    'macd': macd.Macd,
    'rsi': rsi.Rsi,
    'kdj': kdj.Kdj,
    'boll': boll.Boll,
    'ma': ma.Ma,
}
