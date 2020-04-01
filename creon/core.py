from ctypes import windll
from datetime import (
    datetime,
    timedelta,
)
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
    __chart__ = None
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
    def chart(self):
        if self.__chart__ is None:
            self.__chart__ = COMWrapper("CpSysDib.StockChart")
        return self.__chart__

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

    def get_chart_data(self, code: str, start: datetime, end: datetime, period_unit: int):
        """
        # https://money2.creontrade.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=288&seq=102&page=2&searchString=&p=&v=&m=
        :param code: 종목 코드
        :param start:
        :param end:
        :param period_unit: 조회 단위 (분)
        :return:

        creon에서는 최근~과거 꼴로 조회하지만 일반적으로 범위를 생각할 때 오름차순으로 생각하므로(과거~최근) 순서를 바꿈
        """

        now = datetime.now()
        if start > now or end > now:
            raise ValueError("Invalid date range: start or end time is future")
        elif start > end:
            raise ValueError("Invalid date range: start({}) should be earlier than end({})".format(start, end))
        # TODO: Categorize exception

        self.chart.set_input_value(0, code)
        self.chart.set_input_value(1, ord('2'))  # 갯수로 받아오는 것. '1'(기간)은 일봉만 지원
        self.chart.set_input_value(2, int(end.strftime("%Y%m%d")))  # 요청종료일 (가장 최근)
        self.chart.set_input_value(3, int(start.strftime("%Y%m%d")))  # 요청시작일
        diff: timedelta = end - start
        count = diff.total_seconds() / 60 / period_unit
        if count > 2856:
            raise ValueError("Too big request, increase period_unit or reduce date range")
        self.chart.set_input_value(4, count)  # 요청갯수, 최대 2856 건
        request_items = ("date", "time", "open_price", "high_price", "low_price", "close_price")
        item_pair = {
            "date": 0, "time": 1, "open_price": 2, "high_price": 3, "low_price": 4, "close_price": 5,
        }
        self.chart.set_input_value(5, [item_pair.get(key) for key in request_items])
        self.chart.set_input_value(6, ord("m"))  # '차트 주기 - 분/틱
        self.chart.set_input_value(7, 1)  # 분틱차트 주기
        self.chart.set_input_value(8, ord('0'))  # 갭보정여부, 0: 무보정
        self.chart.set_input_value(9, ord('1'))  # 수정주가여부, 1: 수정주가 사용

        self.chart.block_request()
        if self.chart.get_dib_status() != 0:
            self.__logger__.warning(self.chart.get_dib_msg1())
            return []
        for i in range(0, 10):
            res = self.chart.get_header_value(i)
            print(f"{i}: {res}", end=" | ")
        print()
        chart_data = []
        for index in range(self.chart.get_header_value(3)):
            row = {}
            for key in request_items:
                item_const = item_pair[key]
                row[key] = self.chart.get_data_value(item_const, index)
            chart_data.append(row)
        return chart_data

    def _order(self, account: str, code: str, quantity: int, price: int, flag: str, action: str) -> bool:
        self.trades.set_input_value(0, self.__trade_actions__[action.lower()])
        self.trades.set_input_value(1, account)
        self.trades.set_input_value(2, flag)
        self.trades.set_input_value(3, code)
        self.trades.set_input_value(4, quantity)
        self.trades.set_input_value(5, price)
        self.trades.set_input_value(7, "0")  # 주문 조건 구분 코드, 0: 기본 1: IOC 2:FOK
        self.trades.set_input_value(8, "01")

        self.trades.block_request()
        rqStatus = self.trades.GetDibStatus()
        rqRet = self.trades.GetDibMsg1()

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

    def name_to_code(self, name: str):
        return self.stock_code.name_to_code(name)
