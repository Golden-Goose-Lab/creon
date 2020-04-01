from creon.core import Creon

creon = Creon()

account = creon.accounts[0]  # 계좌
account_flag = creon.get_account_flags(account, 3)[0]
# https://money2.creontrade.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=284&seq=154&page=1&searchString=GoodsList&p=8841&v=8643&m=9505

print("account flag: ", account_flag)

res = creon.code_to_name(account, 'A005930')
print(res)

res = creon.buy(account, 'A005930', 10, 100000, account_flag)  # A005930(삼성전자) 10주 100000에 매수
print(res)
res = creon.sell(account, 'A005930', 10, 100000, account_flag)  # A005930(삼성전자) 10주 100000에 매도
print(res)


# from creon.core import Creon
# creon = Creon()
# print(type(creon.utils))
