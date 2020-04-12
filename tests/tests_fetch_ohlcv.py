from datetime import datetime, timedelta
from pprint import pprint

from creon.constants import TimeFrameUnit
from creon.core import Creon


class TestFetchOHLCV:
    def setup(self):
        self.creon = Creon()
        self.code = 'A005930'  # 삼성전자

    def test_1day(self):
        # 4월 1일 일봉
        timeframe = (1, TimeFrameUnit.DAY)
        since = datetime(2020, 4, 1)
        limit = 1
        results = self.creon.fetch_ohlcv(self.code, timeframe, since, limit)
        assert len(results) == limit
        r = results[0]
        assert r["open_price"] == 47450
        assert r["high_price"] == 47900
        assert r["low_price"] == 45800
        assert r["close_price"] == 45800
        assert r["volume"] == 27259532
        assert r["start_time"] == since

    def test_15min(self):
        # 4월 1일 15:00 ~ 15:30 15분봉
        since = datetime(2020, 4, 1, 15, 0)
        timeframe = (15, TimeFrameUnit.MINUTE)
        limit = 2
        results = self.creon.fetch_ohlcv(self.code, timeframe, since, limit)
        pprint(results)
        assert len(results) == limit
        assert results[0]["end_time"] == since + timedelta(minutes=15)
        assert results[0]["volume"] == 2242284
        assert results[1]["end_time"] == since + timedelta(minutes=30)
        assert results[1]["volume"] == 3444195

    def test_30min(self):
        pass

    def test_60min(self):
        # 4월 1일, 장마감 시간 포함되는 경우.
        since = datetime(2020, 4, 1, 14, 0)
        timeframe = (60, TimeFrameUnit.MINUTE)
        limit = 2
        results = self.creon.fetch_ohlcv(self.code, timeframe, since, limit)
        pprint(results)
        assert len(results) == limit
        assert results[0]["end_time"] == datetime(2020, 4, 1, 15, 00)
        assert results[0]["volume"] == 5411988
        assert results[1]["start_time"] == datetime(2020, 4, 1, 15, 00)
        assert results[1]["end_time"] == datetime(2020, 4, 1, 15, 30)
        assert results[1]["volume"] == 5686479

    def test_1day_weekend(self):
        # TODO: 주말 처리
        timeframe = (1, TimeFrameUnit.DAY)
        since = datetime(2020, 4, 3)  # Friday
        limit = 2
        results = self.creon.fetch_ohlcv(self.code, timeframe, since, limit)
        pprint(results)
        assert len(results) == limit
        assert results[0]["start_time"] == since
