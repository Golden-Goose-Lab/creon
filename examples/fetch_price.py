from datetime import datetime, timedelta
from pprint import pprint

from creon.constants import TimeFrameUnit
from creon.core import Creon

"""
특정 종목의 1년, 한달, 일주일, 어제의 시가, 고가, 저가, 종가, 거래량 확인
(Open, Highest, Lowest, Closing, Volume), OHLCV
"""


def main():
    creon = Creon()
    name = '삼성전자'
    code = creon.name_to_code(name)
    # name = creon.code_to_name(code)

    timeframe = (1, TimeFrameUnit.DAY)

    today = datetime(2020, 4, 1)
    times = (
        today,
        today - timedelta(days=1),
        today - timedelta(weeks=1),
        today - timedelta(days=30),  # month
        today - timedelta(days=365),  # year
    )
    timeframe = (1, TimeFrameUnit.DAY)
    limit = 1
    for since in times:
        results = creon.fetch_ohlcv(code, timeframe, since, limit)
        print(f"{name}: {since.month}월 {since.day}일")
        pprint(results)
        print("-" * 40)


if __name__ == '__main__':
    main()
