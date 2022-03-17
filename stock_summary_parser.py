import time
import numpy as np
import pandas as pd
from stock_summary import StockSummary


class StockSummaryParser:

    # __base_excel_path = './resource/stock_list.xlsx'
    __base_excel_path = './resource/stock_list.xlsm'
    __use_restrict_stock_count = 20000

    @classmethod
    def initialize(cls, restrict_stock_count):
        start = time.time()

        cls.restrict_stock_count = restrict_stock_count
        data_frame = pd.read_excel(cls.__base_excel_path)

        i = 0
        for row in data_frame.itertuples(index=True):
            cls.__process_line(row)

            i = i + 1
            if i > cls.__restrict_stock_count:
                break
        
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
