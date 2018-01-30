from win32com import client


class Creon:

    __utils__ = None

    @property
    def utils(self) -> client.CDispatch:
        if self.__utils__ is None:
            self.__utils__ = client.Dispatch('CpTrade.CpTdUtil')
            self.__utils__.TradeInit()
        return self.__utils__

    @property
    def account_numbers(self) -> tuple:
        return self.utils.AccountNumber
