import pandas as pd


class StockGraphParser:

    __base_url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'

    @classmethod
    def initialize(cls):
        return

    @classmethod
    def __make_url(cls, code):
        return cls.__base_url.format(code=code)

    @classmethod
    def get_data_frame(cls, code):
        data_frame = pd.DataFrame()
        url = cls.__make_url(code)

        for page in range(1, 21):
            page_url = 'url&page={page}'.format(url = url, page = page)
            data_frame = data_frame.append(pd.read_html(page_url, header = 0)[0], ignore_index = True)

        data_frame.dronpa()

        return data_frame
