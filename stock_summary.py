class StockSummary:

    __code_summary_map = {}

    @classmethod
    def add_summary(cls, summary):
        cls.__code_summary_map[summary.code] = summary

    @classmethod
    def get_codes(cls):
        return cls.__code_summary_map.keys()

    @classmethod
    def get_summary(cls, code):
        return cls.__code_summary_map[code]

    # 회사명
    # 종목코드
    # 업종
    # 주요제품
    # 상장일
    # 결산월
    # 대표자명
    # 홈페이지
    # 지역
    def __init__(self, name, raw_code):#, sector, product, listing_date, settlement_month, ceo_name, home_page, area):
        self.__name = name
        self.__raw_code = raw_code
        self.__code = raw_code.rjust(6, "0")
        self.__trend_score = 0

    def print_info(self):
        print(self.name, self.code, self.sector, self.product, self.listing_date,
              self.settlement_month, self.ceo_name, self.home_page, self.area)

    @property
    def name(self):
        return self.__name

    @property
    def raw_code(self):
        return self.__raw_code

    @property
    def code(self):
        return self.__code

    # 현재가
    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, value):
       self.__price = value

    # 7일전 가격
    @property
    def price_7(self):
        return self.__price_7

    @price_7.setter
    def price_7(self, value):
       self.__price_7 = value


    # 30일전 가격
    @property
    def price_30(self):
        return self.__price_30

    @price_30.setter
    def price_30(self, value):
       self.__price_30 = value


    # 60일전 가격
    @property
    def price_60(self):
        return self.__price_60

    @price_60.setter
    def price_60(self, value):
       self.__price_60 = value


    @property
    def trend_score(self):
        return self.__trend_score

    def update_trend_score(self, score):
        self.__trend_score = score