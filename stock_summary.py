

class StockSummary:

    __code_summary_map = {}

    @staticmethod
    def get_summary(cls, code):
        return cls.__code_summary_map[code]

    # test code 
    def __init__(self):
        self.__name = "Name"                                 # 회사명
        self.__code = "Code"                                 # 종목코드
        self.__sector = "Sector"                             # 업종
        self.__product = "Product"                           # 주요제품
        self.__listing_date = "Listing Date"                 # 상장일
        self.__settlement_month = "Settlement Month"         # 결산월
        self.__ceo_name = "CEO Name"                         # 대표자명
        self.__home_page = "Homepage"                        # 홈페이지
        self.__area = "Area"                                 # 지역


    # def __init__(self, name, code, sector, product, listing_date, settlement_month, ceo_name, home_page, area):
    #     self.__name = name
    #     self.__code = code
    #     self.__sector = sector
    #     self.__product = product
    #     self.__listing_date = listing_date
    #     self.__settlement_month = settlement_month
    #     self.__ceo_name = ceo_name
    #     self.__home_page = home_page
    #     self.__area = area

    
    @property
    def name(self): 
        return self.__name

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



# Test
if __name__ == "__main__":

    summary = StockSummary()
    print(summary.name)