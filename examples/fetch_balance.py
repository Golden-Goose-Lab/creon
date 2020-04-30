from pprint import pprint
from creon.core import Creon
from creon.constants import AccountFilter


def main():
    creon = Creon()
    account_num = creon.accounts[0]  # 계좌
    print(f"계좌번호: {account_num}")
    account_flag = creon.get_account_flags(account_num, AccountFilter.STOCK)
    results = creon.get_holding_stocks(account_num, account_flag[0])
    pprint(results)


if __name__ == '__main__':
    main()
