from logging import Logger
from os import environ

from psutil import process_iter
from win32com import client

from creon.utils import run_creon_plus


class Creon:

    __codes__ = None
    __utils__ = None
    __trades__ = None
    __trade_actions__ = {'sell': '1', 'buy': '2'}
    __logger__ = Logger(__name__)

    def __init__(self):
        if 'CpStart.exe' not in [p.name() for p in process_iter()]:
            run_creon_plus(
                environ.get('CREON_USERNAME', ''),
                environ.get('CREON_PASSWORD', ''),
                environ.get('CREON_CERTIFICATION_PASSWORD', ''),
                environ.get('CREON_PATH', '')
            )

    @property
    def codes(self) -> client.CDispatch:
        if self.__codes__ is None:
            self.__codes__ = client.Dispatch("CpUtil.CpCodeMgr")
        return self.__codes__

    @property
    def utils(self) -> client.CDispatch:
        if self.__utils__ is None:
            self.__utils__ = client.Dispatch('CpTrade.CpTdUtil')
            self.__utils__.TradeInit()
        return self.__utils__

    @property
    def trades(self) -> client.CDispatch:
        if self.__trades__ is None:
            self.__trades__ = client.Dispatch('CpTrade.CpTd0311')
        return self.__trades__

    @property
    def accounts(self) -> tuple:
        return self.utils.AccountNumber

    def get_account_flags(self, account: str, account_filter: int) -> tuple:
        return self.utils.GoodsList(account, account_filter)

    def get_all_codes(self, category: str, with_name: bool = False) -> tuple:
        category = category.lower()
        if category == 'kospi':
            section = 1
        elif category == 'kosdaq':
            section = 2
        else:
            raise ValueError

        codes = self.codes.GetStockListByMarket(section)

        if with_name:
            results = []
            for code in codes:
                results.append((code, self.codes.CodeToName(code)))
            return tuple(results)
        return codes

    def _order(self, account: str, code: str, quantity: int, price: int, flag: str, action: str) -> bool:
        self.trades.SetInputValue(0, self.__trade_actions__[action.lower()])
        self.trades.SetInputValue(1, account)
        self.trades.SetInputValue(2, flag)
        self.trades.SetInputValue(3, code)
        self.trades.SetInputValue(4, quantity)
        self.trades.SetInputValue(5, price)
        self.trades.SetInputValue(7, "0")
        self.trades.SetInputValue(8, "01")

        self.trades.BlockRequest()

        if self.trades.GetDibStatus() != 0:
            self.__loger__.warning(self.trades.GetDibMsg1())
            return False
        return True

    def buy(self, account: str, code: str, quantity: int, price: int, flag: str) -> bool:
        return self._order(account, code, quantity, price, flag, 'buy')

    def sell(self, account: str, code: str, quantity: int, price: int, flag: str) -> bool:
        return self._order(account, code, quantity, price, flag, 'sell')
