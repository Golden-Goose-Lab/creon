from datetime import datetime
from pprint import pprint

from creon.core import Creon
from creon.constants import (
    AccountFilter,
    TimeFrameUnit,
)


def main():
    """
    9시부터 3시 15분까지 기준 가격(상수)을 매개로 2% 하락시 매수 2% 상승시 매도
    """
    creon = Creon()
    name = '삼성전자'
    code = creon.name_to_code(name)

    account_num = creon.accounts[0]  # 계좌
    account_flag = creon.get_account_flags(account_num, AccountFilter.STOCK)[0]
    result = creon.get_price_data(code)
    as_of_price = result["expect_price"]  # 기준가

    while True:
        # TODO: loop 언제 탈출하지... 잔고가 바닥날 때 까지...?
        result = creon.get_price_data(code)
        current_price = result["expect_price"]
        gap = as_of_price - current_price
        if gap > 0 and (gap > as_of_price * 0.02):
            # 2% 이상 하락
            creon.buy(account_num, code, 10, current_price, account_flag)
        elif gap < 0 and (abs(gap) > as_of_price * 0.02):
            # 2% 이상 상승
            creon.sell(account_num, code, 10, current_price, account_flag)


if __name__ == '__main__':
    main()
