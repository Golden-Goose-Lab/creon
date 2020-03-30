from ctypes import windll
from logging import Logger
from os import environ

from psutil import process_iter
from win32com import client

from creon.utils import run_creon_plus, snake_to_camel


class COMWrapper:

    def __init__(self, com):
        self.com = client.Dispatch(com)

    def __getattr__(self, item):
        try:
            return super(COMWrapper, self).__getattr__(item)
        except AttributeError:
            return self.com.__getattr__(snake_to_camel(item))

    def block_request(self):
        self.com.BlockRequest()

    def get_dib_msg1(self):
        return self.com.get_dib_msg1()

    def get_dib_status(self):
        return self.com.GetDibStatus()

    def get_data_value(self, key, value):
        return self.com.GetDataValue(key, value)

    def get_header_value(self, key):
        return self.com.GetHeaderValue(key)

    def set_input_value(self, key, value):
        self.com.SetInputValue(key, value)


class Creon:

    __codes__ = None
    __utils__ = None
    __trades__ = None
    __trade_actions__ = {'sell': '1', 'buy': '2'}
    __markets__ = None
    __wallets__ = None
    __stock_code__ = None
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
    def codes(self) -> COMWrapper:
        if self.__codes__ is None:
            self.__codes__ = COMWrapper("CpUtil.CpCodeMgr")
        return self.__codes__

    @property
    def utils(self) -> COMWrapper:
        if self.__utils__ is None:
            self.__utils__ = COMWrapper('CpTrade.CpTdUtil')
            try:
                self.__utils__.TradeInit()
            except BaseException as e:  # to catch pywintypes.error
                if not windll.shell32.IsUserAnAdmin():
                    raise PermissionError("관리자 권한으로 실행시켜야 됨") from None
                    # TODO: 에러메세지 형식 통일
                else:
                    raise e

        return self.__utils__

    @property
    def trades(self) -> COMWrapper:
        if self.__trades__ is None:
            self.__trades__ = COMWrapper('CpTrade.CpTd0311')
        return self.__trades__

    @property
    def markets(self) -> COMWrapper:
        if self.__markets__ is None:
            self.__markets__ = COMWrapper('DsCbo1.StockMst')
        return self.__markets__

    @property
    def wallets(self) -> COMWrapper:
        if self.__wallets__ is None:
            self.__wallets__ = COMWrapper('CpTrade.CpTd6033')
        return self.__wallets__

    @property
    def stock_code(self):
        if self.__stock_code__ is None:
            self.__stock_code__ = COMWrapper("CpUtil.CpStockCode")
        return self.__stock_code__

    @property
    def accounts(self) -> tuple:
        return self.utils.account_number

    def get_account_flags(self, account: str, account_filter: int) -> tuple:
        return self.utils.goods_list(account, account_filter)

    def get_all_codes(self, category: str, with_name: bool = False) -> tuple:
        category = category.lower()
        if category == 'kospi':
            section = 1
        elif category == 'kosdaq':
            section = 2
        else:
            raise ValueError

        codes = self.codes.get_stock_list_by_market(section)

        if with_name:
            results = []
            for code in codes:
                results.append((code, self.codes.code_to_name(code)))
            return tuple(results)
        return codes

    def get_price_data(self, code: str) -> dict:
        self.markets.set_input_value(0, code)
        self.markets.block_request()

        if self.markets.get_dib_status() != 0:
            self.__logger__.warning(self.markets.get_dib_msg1())
            return {}

        return {
            'code': self.markets.get_header_value(0),
            'name': self.markets.get_header_value(1),
            'time': self.markets.get_header_value(4),
            'diff': self.markets.get_header_value(12),
            'price': self.markets.get_header_value(13),
            'close_price': self.markets.get_header_value(11),
            'high_price': self.markets.get_header_value(14),
            'low_price': self.markets.get_header_value(15),
            'offer': self.markets.get_header_value(16),
            'bid': self.markets.get_header_value(17),
            'volume': self.markets.get_header_value(18),
            'volume_price': self.markets.get_header_value(19),
            'expect_flag': self.markets.get_header_value(58),
            'expect_price': self.markets.get_header_value(55),
            'expect_diff': self.markets.get_header_value(56),
            'expect_volume': self.markets.get_header_value(57)
        }

    def get_holding_stocks(self, account: str, flag: str, count: int = 50) -> list:
        self.wallets.set_input_value(0, account)
        self.wallets.set_input_value(1, flag)
        self.wallets.set_input_value(2, count)

        self.wallets.block_request()
        if self.wallets.get_dib_status() != 0:
            self.__logger__.warning(self.wallets.get_dib_msg1())
            return []

        stocks = []
        for index in range(self.wallets.get_header_value(7)):
            stocks.append({
                'code': self.wallets.get_data_value(12, index),
                'name': self.wallets.get_data_value(0, index),
                'quantity': self.wallets.get_data_value(7, index),
                'bought_price': self.wallets.get_data_value(17, index),
                'expect_price': self.wallets.get_data_value(9, index),
                'expect_profit': self.wallets.get_data_value(11, index)
            })
        return stocks

    def _order(self, account: str, code: str, quantity: int, price: int, flag: str, action: str) -> bool:
        self.trades.set_input_value(0, self.__trade_actions__[action.lower()])
        self.trades.set_input_value(1, account)
        self.trades.set_input_value(2, flag)
        self.trades.set_input_value(3, code)
        self.trades.set_input_value(4, quantity)
        self.trades.set_input_value(5, price)
        self.trades.set_input_value(7, "0")
        self.trades.set_input_value(8, "01")

        self.trades.block_request()

        if self.trades.get_dib_status() != 0:
            self.__logger__.warning(self.trades.get_dib_msg1())
            return False
        return True

    def buy(self, account: str, code: str, quantity: int, price: int, flag: str) -> bool:
        return self._order(account, code, quantity, price, flag, 'buy')

    def sell(self, account: str, code: str, quantity: int, price: int, flag: str) -> bool:
        return self._order(account, code, quantity, price, flag, 'sell')

    def code_to_name(self, code: str):
        return self.stock_code.code_to_name(code)
