from enum import (
    Enum,
    IntEnum,
    IntFlag,
)


class TimeFrameUnit(Enum):
    TICK = 'T'
    MINUTE = 'm'
    DAY = 'D'
    WEEK = 'W'
    MONTH = 'M'


class AccountFilter(IntFlag):
    # https://money2.creontrade.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=284&seq=154&page=1&searchString=GoodsList&p=8841&v=8643&m=9505
    ALL = -1
    STOCK = 1
    NATIONAL_FUTURE = 2
    EUREX = 16
    INTERNATIONAL_FUTURE = 64


class AccountFlag(Enum):
    # https://money2.daishin.com/E5/WTS/Customer/AccountOpen/DW_JijumOpen.aspx 상품 계좌 섹션 참고
    COMPREHENSIVE = '01'  # 종합투자상품
    CONSIGNOR = '10'  # 위탁자 상품
    FUTURE = '50'  # 선물/옵션
