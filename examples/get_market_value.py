from pprint import pprint

from creon.core import Creon


def main():
    creon = Creon()
    name = '삼성전자'
    code = creon.name_to_code(name)
    # name = creon.code_to_name(code)
    pprint(creon.get_price_data(code))

    # TODO: 시간대 별 조회 구현


if __name__ == '__main__':
    main()
