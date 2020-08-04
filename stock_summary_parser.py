import numpy as np
import pandas as pd
from stock_summary import StockSummary


class StockSummaryParser:

    __stock_code_path = './resource/stock_list.xlsx'

    @classmethod
    def initialize(cls):

        # read a excel file and make it as a DataFrame
        data_frame = pd.read_excel(cls.__stock_code_path)

        for row in data_frame.itertuples(index=True):
            cls.__process_line(row)

    @classmethod
    def __process_line(cls, row):

        # 회사명	종목코드	업종	주요제품	상장일	결산월	대표자명	홈페이지	지역
        summary = StockSummary(
            getattr(row, '회사명'),
            format(getattr(row, '종목코드'), '06'),
            getattr(row, '업종'),
            getattr(row, '주요제품'),
            getattr(row, '상장일'),
            getattr(row, '결산월'),
            getattr(row, '대표자명'),
            getattr(row, '홈페이지'),
            getattr(row, '지역'),
        )

        StockSummary.add_summary(summary)
        summary.print_info()
        return

    @classmethod
    def get_info(cls):
        return cls.__name_code_map.keys()
