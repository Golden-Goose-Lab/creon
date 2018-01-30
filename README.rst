creon
=====

대신증권 크레온의 파이썬 클라이언트 입니다.

빠른 시작
---------
.. code-block:: python

   from creon.core import Creon
   creon = Creon()

   account = creon.accounts[0]                              # 계좌
   account_flag = creon.get_account_flags(account, 3)

   creon.buy(account, 'A005930', 10, 100000, account_flag)  # A005930(삼성전자) 10주 100000에 매수
   creon.sell(account, 'A005930', 10, 100000, account_flag)  # A005930(삼성전자) 10주 100000에 매도
