import pytest

from yuna.core import SourceSingleton
from yuna.exceptions import SourceError

actual_date = '[datetime.datetime(2018, 1, 1, 0, 0), datetime.datetime(2018, 3, 1, 0, 0)]'


class TestCore:

    def test_change_stock(self):
        stocks = ['000001', '600000', '300001']
        expected_change_stock = SourceSingleton.change_stock(stocks)
        assert expected_change_stock == ['000001.SZ', '600000.SH', '300001.SZ']

    def test_validate_date(self):
        date = ['20180101', '20180301']
        expected_date = SourceSingleton.validate_date(date)
        assert str(expected_date) == actual_date

        date = ['20180301', '20180101', '20180501']
        with pytest.raises(SourceError, match='日期分起始到期末，数量应为2'):
            SourceSingleton.validate_date(date)

        date = ['201801012', '20180301']
        with pytest.raises(SourceError, match="日期的格式不正确，请遵循%Y%m%d，例如'20180101'"):
            SourceSingleton.validate_date(date)

        date = ['20180301', '20180101']
        with pytest.raises(SourceError, match='期末日期要大于起初日期'):
            SourceSingleton.validate_date(date)
