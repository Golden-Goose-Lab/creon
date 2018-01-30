from win32com import client


class Creon:

    __codes__ = None
    __utils__ = None

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
    def account_numbers(self) -> tuple:
        return self.utils.AccountNumber

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
