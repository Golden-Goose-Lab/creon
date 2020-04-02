from datetime import datetime
from pprint import pprint
from typing import List

from creon.core import Creon
from creon.types import Candle


class TestGetChart:
    def setup(self):
        self.creon = Creon()

    def test_1(self):
        code = 'A005930'  # 삼성전자
        # 4월 1일 15시 14~16 분
        start = datetime(2020, 4, 1, 15, 14)
        end = datetime(2020, 4, 1, 15, 16)
        period_unit = 1  # 1분봉
        results = self.creon.get_chart_data(code, start, end, period_unit)
        assert 2 == len(results)

    def test_60(self):
        code: str = 'A005930'  # 삼성전자
        # 4월 1일 9시 ~ 16시
        start: datetime = datetime(2020, 4, 1, 9, 0)
        end: datetime = datetime(2020, 4, 1, 16, 0)
        period_unit: int = 60  # 60분봉
        results = self.creon.get_chart_data(code, start, end, period_unit)
        assert 7 == len(results)
        for idx, row in enumerate(results):
            try:
                next_row = results[idx + 1]
            except IndexError:
                break
            assert row["end_time"] == next_row["start_time"]
