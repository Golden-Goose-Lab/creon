from datetime import (
    datetime,
    timedelta,
)
from pprint import pprint

from creon.core import Creon


def main():
    creon = Creon()
    code = 'A005930'  # 삼성전자
    # 4월 1일 15시 14~16 분
    start = datetime(2020, 4, 1, 15, 14)
    end = datetime(2020, 4, 1, 15, 16)
    period_unit = 1  # 1분봉
    results = creon.fetch_chart_data(code, start, end, period_unit)
    # pprint(results, width=120)

    start = datetime(2020, 4, 1, 9, 0)
    end = datetime(2020, 4, 1, 16, 0)
    period_unit = 60  # 일봉
    results = creon.fetch_chart_data(code, start, end, period_unit)
    pprint(results)

    # 3년, 1년, 한달, 일주일, 어제


if __name__ == '__main__':
    main()
