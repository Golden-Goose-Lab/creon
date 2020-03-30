from creon.core import Creon


def main():
    creon = Creon()
    stock_code = 'A005930'
    name = creon.code_to_name(stock_code)
    print(name)

    # TODO: 가격 가져오는 동작 구현


if __name__ == '__main__':
    main()
