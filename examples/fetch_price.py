from datetime import datetime
from pprint import pprint

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
    timeframe = '1d'
    since = datetime(2020, 4, 1)
    limit = 1
    results = creon.fetch_ohlcv(code, timeframe, since, limit)
    pprint(results)


if __name__ == '__main__':
    main()
