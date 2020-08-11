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
    def __init__(self, name, raw_code, sector, product, listing_date, settlement_month, ceo_name, home_page, area):
        self.__name = name
        self.__raw_code = raw_code
        self.__code = format(raw_code, '06')
        self.__sector = sector
        self.__product = product
        self.__listing_date = listing_date
        self.__settlement_month = settlement_month
        self.__ceo_name = ceo_name
        self.__home_page = home_page
        self.__area = area
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

    @property
    def sector(self):
        return self.__sector

    @property
    def product(self):
        return self.__product

    @property
    def listing_date(self):
        return self.__listing_date

    @property
    def settlement_month(self):
        return self.__settlement_month

    @property
    def ceo_name(self):
        return self.__ceo_name

    @property
    def home_page(self):
        return self.__home_page

    @property
    def area(self):
        return self.__area

    @property
    def trend_score(self):
        return self.__trend_score

    def update_trend_score(self, score):
        self.__trend_score = score