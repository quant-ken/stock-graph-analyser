import time
import numpy as np
import pandas as pd
from stock_summary import StockSummary


class StockSummaryParser:

    __base_excel_path = './resource/stock_list.xlsx'
    __custom_excel_path = './resource/custom_stock_list.xlsx'

    @classmethod
    def __get_stock_code_path(cls, custom_stock_mode):
        if custom_stock_mode == True:
            return cls.__custom_excel_path
        else:
            return cls.__base_excel_path

    @classmethod
    def initialize(cls, custom_stock_mode):
        start = time.time()

        path = cls.__get_stock_code_path(custom_stock_mode)
        data_frame = pd.read_excel(path)

        for row in data_frame.itertuples(index=True):
            cls.__process_line(row)
        
        print('StockSummaryParser.initialize() :', round(time.time() - start, 4))

    @classmethod
    def __process_line(cls, row):

        # TODO : Validate custom mode
        # enable = getattr(row, '활성화')

        summary = StockSummary \
        (
            getattr(row, '회사명'),
            getattr(row, '종목코드'),
            getattr(row, '업종'),
            getattr(row, '주요제품'),
            getattr(row, '상장일'),
            getattr(row, '결산월'),
            getattr(row, '대표자명'),
            getattr(row, '홈페이지'),
            getattr(row, '지역'),
        )

        StockSummary.add_summary(summary)
