from enum import (
    Enum,
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
