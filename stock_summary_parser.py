import time
import numpy as np
import pandas as pd
from stock_summary import StockSummary


class StockSummaryParser:

    __stock_code_path = './resource/stock_list.xlsx'

    @classmethod
    def initialize(cls):
        start = time.time()

        data_frame = pd.read_excel(cls.__stock_code_path)

        for row in data_frame.itertuples(index=True):
            cls.__process_line(row)

        print("StockSummaryParser.initialize() :", time.time() - start) 
        
    @classmethod
    def __process_line(cls, row):

        summary = StockSummary(
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
        return

    @classmethod
    def get_info(cls):
        return cls.__name_code_map.keys()
