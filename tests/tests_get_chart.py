from datetime import datetime
from pprint import pprint
from typing import List

from creon.core import Creon
from creon.types import Candle


class TestGetChart:
    def setup(self):
        self.creon = Creon()
        self.code = 'A005930'  # 삼성전자

    def test_1mim(self):
        # 4월 1일 15시 14~16 분
        start = datetime(2020, 4, 1, 15, 14)
        end = datetime(2020, 4, 1, 15, 16)
        period_unit = 1  # 1분봉
        results = self.creon.fetch_chart_data(self.code, start, end, period_unit)
        assert len(results) == 2

    def test_60min(self):
        # 4월 1일 9시 ~ 16시
        start = datetime(2020, 4, 1, 9, 0)
        end = datetime(2020, 4, 1, 16, 0)
        period_unit = 60  # 60분봉
        results = self.creon.fetch_chart_data(self.code, start, end, period_unit)
        assert len(results) == 2
        for idx, row in enumerate(results):
            try:
                next_row = results[idx + 1]
            except IndexError:
                break
            assert row["end_time"] == next_row["start_time"]

    def test_1day(self):
        start: datetime = datetime(2020, 4, 1)
        end: datetime = datetime(2020, 4, 4)
        period_unit: int = 12
        results = self.creon.fetch_chart_data(self.code, start, end, period_unit)
        pprint(results)
        assert len(results) == 2
