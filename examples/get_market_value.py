from datetime import (
    datetime,
    timedelta,
)
from pprint import pprint

from creon.core import Creon


def main():
    creon = Creon()
    name = '삼성전자'
    code = creon.name_to_code(name)
    # name = creon.code_to_name(code)
    # pprint(creon.get_price_data(code))

    start = datetime(2020, 3, 31)
    end = start + timedelta(days=1)
    period_unit = 60  # 60 분봉
    results = creon.get_chart_data(code, start, end, period_unit)
    print(results)

    # 3년, 1년, 한달, 일주일, 어제

    # TODO: 시간대 별 조회 구현
    # 4월 1일 12시 30분
    start = datetime(2020, 4, 1, 12, 30)
    end = datetime(2020, 4, 1, 12, 31)
    period_unit = 1
    results = creon.get_chart_data(code, start, end, period_unit)
    pprint(results, width=120)


if __name__ == '__main__':
    main()
