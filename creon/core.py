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
    __markets__ = None
    __wallets__ = None
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
    def markets(self) -> client.CDispatch:
        if self.__markets__ is None:
            self.__markets__ = client.Dispatch('DsCbo1.StockMst')
        return self.__markets__

    @property
    def wallets(self) -> client.CDispatch:
        if self.__wallets__ is None:
            self.__wallets__ = client.Dispatch('CpTrade.CpTd6033')
        return self.__wallets__

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

    def get_price_data(self, code: str) -> dict:
        self.markets.SetInputValue(0, code)
        self.markets.BlockRequest()

        if self.markets.GetDibStatus() != 0:
            self.__logger__.warning(self.markets.GetDibMsg1())
            return {}

        return {
            'code': self.markets.GetHeaderValue(0),
            'name': self.markets.GetHeaderValue(1),
            'time': self.markets.GetHeaderValue(4),
            'diff': self.markets.GetHeaderValue(12),
            'price': self.markets.GetHeaderValue(13),
            'close_price': self.markets.GetHeaderValue(11),
            'high_price': self.markets.GetHeaderValue(14),
            'low_price': self.markets.GetHeaderValue(15),
            'offer': self.markets.GetHeaderValue(16),
            'bid': self.markets.GetHeaderValue(17),
            'volume': self.markets.GetHeaderValue(18),
            'volume_price': self.markets.GetHeaderValue(19),
            'expect_flag': self.markets.GetHeaderValue(58),
            'expect_price': self.markets.GetHeaderValue(55),
            'expect_diff': self.markets.GetHeaderValue(56),
            'expect_volume': self.markets.GetHeaderValue(57)
        }

    def get_holding_stocks(self, account: str, flag: str, count: int = 50):
        self.wallets.SetInputValue(0, account)
        self.wallets.SetInputValue(1, flag)
        self.wallets.SetInputValue(2, count)

        self.wallets.BlockRequest()
        if self.wallets.GetDibStatus() != 0:
            self.__logger__.warning(self.wallets.GetDibMsg1())
            return []

        stocks = []
        for index in range(self.wallets.GetHeaderValue(7)):
            stocks.append({
                'code': self.wallets.GetDataValue(12, index),
                'name': self.wallets.GetDataValue(0, index),
                'quantity': self.wallets.GetDataValue(7, index),
                'bought_price': self.wallets.GetDataValue(17, index),
                'expect_price': self.wallets.GetDataValue(9, index),
                'expect_profit': self.wallets.GetDataValue(11, index)
            })
        return stocks

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
            self.__logger__.warning(self.trades.GetDibMsg1())
            return False
        return True

    def buy(self, account: str, code: str, quantity: int, price: int, flag: str) -> bool:
        return self._order(account, code, quantity, price, flag, 'buy')

    def sell(self, account: str, code: str, quantity: int, price: int, flag: str) -> bool:
        return self._order(account, code, quantity, price, flag, 'sell')
