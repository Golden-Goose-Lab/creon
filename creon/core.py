from calendar import Calendar
from ctypes import windll
from datetime import datetime, timedelta
from logging import Logger
from os import environ
from typing import (
    List,
)


from psutil import process_iter
from win32com import client

from creon.constants import (
    TimeFrameUnit,
    AccountFilter,
)
from creon.types import Candle
from creon.utils import run_creon_plus, snake_to_camel, timeframe_to_timedelta


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
        return self.com.GetDibMsg1()

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

    def __init__(self, username: str = '', password: str = '', cert_password: str = '', path: str = ''):
        if not windll.shell32.IsUserAnAdmin():
            raise PermissionError("Run as administrator")

        if 'CpStart.exe' not in [p.name() for p in process_iter()]:
            run_creon_plus(
                username or environ.get('CREON_USERNAME', ''),
                password or environ.get('CREON_PASSWORD', ''),
                cert_password or environ.get('CREON_CERTIFICATION_PASSWORD', ''),
                path or environ.get('CREON_PATH', '')
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
            self.__utils__.TradeInit()
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

    def get_account_flags(self, account: str, account_filter: AccountFilter) -> tuple:
        # https://money2.creontrade.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=284&seq=154&page=1&searchString=GoodsList&p=8841&v=8643&m=9505
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

    def fetch_ohlcv(
            self, code: str, timeframe: tuple, since: datetime, limit: int,
            fill_gap=False, use_adjusted_price=True) -> List[Candle]:
        """
        https://money2.creontrade.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=288&seq=102&page=2&searchString=&p=&v=&m=

        :param code: 종목 코드
        :param timeframe:
        :param since:
        :param limit:
        :param fill_gap: 갭보정 여부
        :param use_adjusted_price: 수정주가 사용여부
        :return:
        """
        if limit > 2856:
            raise ValueError("Too big request, increase period_unit or reduce date range")

        timeframe_timedelta = timeframe_to_timedelta(timeframe)
        if timeframe[1] == TimeFrameUnit.DAY:
            to = since + (timeframe_timedelta * limit) - timedelta(minutes=1)
            # 23시 59분으로 만들기 위해
        else:
            to = since + (timeframe_timedelta * limit)

        if timeframe[1] in [TimeFrameUnit.MINUTE, TimeFrameUnit.TICK]:
            market_end = datetime(since.year, since.month, since.day, 15, 21, 0)
            diff: timedelta = market_end - since
            count = int(diff.total_seconds()) // timeframe_timedelta.seconds
            count += 1
        else:
            count = limit
        count += 1  # 장시작/마감시간 고려하면 하나 더 얻어와야함
        request_items = (
            "date", "time", "open_price", "high_price", "low_price", "close_price", "volume",
        )
        item_pair = {
            "date": 0, "time": 1, "open_price": 2, "high_price": 3, "low_price": 4, "close_price": 5,
            "volume": 8, "volume_price": 9,
        }
        interval, unit = timeframe
        fill_gap = '1' if fill_gap else '0'
        use_adjusted_price = '1' if use_adjusted_price else '0'

        self.chart.set_input_value(0, code)
        self.chart.set_input_value(1, ord('2'))  # 갯수로 받아오는 것. '1'(기간)은 일봉만 지원
        self.chart.set_input_value(2, int(to.strftime("%Y%m%d")))  # 요청종료일 (가장 최근)
        self.chart.set_input_value(3, int(since.strftime("%Y%m%d")))  # 요청시작일
        self.chart.set_input_value(4, count)  # 요청갯수, 최대 2856 건
        self.chart.set_input_value(5, [item_pair.get(key) for key in request_items])
        self.chart.set_input_value(6, ord(unit.value))  # '차트 주기 ('D': 일, 'W': 주, 'M': 월, 'm': 분, 'T': 틱)
        self.chart.set_input_value(7, interval)  # 분/틱차트 주기
        self.chart.set_input_value(8, ord(fill_gap))  # 갭보정여부, 0: 무보정
        self.chart.set_input_value(9, use_adjusted_price)  # 수정주가여부, 1: 수정주가 사용
        self.chart.set_input_value(10, '1')  # 거래량 구분
        # '1': 시간외거래량모두포함, '2': 장종료시간외거래량만포함, '3': 시간외거래량모두제외, '4': 장전시간외거래량만포함

        self.chart.block_request()
        if self.chart.get_dib_status() != 0:
            self.__logger__.warning(self.chart.get_dib_msg1())
            return []

        chart_data = []
        row_cnt = self.chart.get_header_value(3)
        for i in range(row_cnt):
            resp = {
                "date": self.chart.get_data_value(0, i),
                "time": self.chart.get_data_value(1, i),
                "open": self.chart.get_data_value(2, i),
                "high": self.chart.get_data_value(3, i),
                "low": self.chart.get_data_value(4, i),
                "close": self.chart.get_data_value(5, i),
                "volume": self.chart.get_data_value(6, i),
            }
            candle: Candle = Candle(
                start_time=datetime(1970, 1, 1),
                end_time=datetime(1970, 1, 1),
                open_price=resp["open"],
                high_price=resp["high"],
                low_price=resp["low"],
                close_price=resp["close"],
                volume=resp["volume"],
            )
            if unit == TimeFrameUnit.MONTH:
                raise NotImplementedError()  # TODO
            elif unit == TimeFrameUnit.WEEK:
                date = str(resp["date"])
                year = int(date[:4])
                month = int(date[4:6])
                nth_week = int(date[6])
                nth_friday = Calendar(0).monthdatescalendar(year, month)[nth_week][4]
                candle["start_time"] = datetime.strptime(str(nth_friday), "%Y-%m-%d")
                candle["end_time"] = candle["start_time"] + timedelta(weeks=1, hours=23, minutes=59)
            elif unit == TimeFrameUnit.DAY:
                candle["start_time"] = datetime.strptime(str(resp["date"]), "%Y%m%d")
                candle["end_time"] = candle["start_time"] + timedelta(hours=23, minutes=59)
            else:
                candle["end_time"] = datetime.strptime(f'{resp["date"]}-{resp["time"]}', "%Y%m%d-%H%M")
                if candle["end_time"].hour == 15 and candle["end_time"].minute == 30:
                    if len(chart_data) > 0:
                        candle["start_time"] = chart_data[0]["end_time"]
                    else:
                        next_date = self.chart.get_data_value(0, i + 1)
                        next_time = self.chart.get_data_value(1, i + 1)
                        candle["start_time"] = datetime.strptime(f'{next_date}-{next_time}', "%Y%m%d-%H%M")
                else:
                    candle["start_time"] = candle["end_time"] - timeframe_timedelta
            chart_data.insert(0, candle)
        for ohlcv in chart_data:
            if ((ohlcv["start_time"] - timeframe_timedelta) < since) or ohlcv["end_time"] > to:
                chart_data.remove(ohlcv)
        return chart_data

    def get_holding_stocks(self, account_number: str, flag: str, count: int = 50) -> dict:
        # TODO: 평가금액과 잔고까지 리턴하므로 함수명 바꿀 것
        # http://money2.daishin.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=284&seq=176&page=1&searchString=CpTrade.CpTd6033&p=8839&v=8642&m=9508
        self.wallets.set_input_value(0, account_number)
        self.wallets.set_input_value(1, flag)
        self.wallets.set_input_value(2, count)

        self.wallets.block_request()
        status = self.wallets.get_dib_status()
        if status != 0:
            self.__logger__.warning(self.wallets.get_dib_msg1())
            return []
        for i in range(13):
            print(f"{i}: {self.wallets.get_header_value(i)}")
        expect_valuation = self.wallets.get_header_value(3)
        remain_deposit = self.wallets.get_header_value(9)
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
        result = {
            "expect_valuation": expect_valuation,
            "remain_deposit": remain_deposit,
            "stocks": stocks,
        }
        return result

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

    def name_to_code(self, name: str):
        return self.stock_code.name_to_code(name)
