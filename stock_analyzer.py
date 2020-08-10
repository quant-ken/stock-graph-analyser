import pandas as pd
from stock_summary import StockSummary
from stock_data_frame_generater import StockDataFrameGenerater

class StockAnalyzer:

    __trend_count = 7
    __cross_offset = 4.25       # percent 
    
    __sma_short = 


    @classmethod
    def analyze(cls, summary, data_frame):
        data_trend = data_frame.tail(cls.__trend_count)

        sma_short_middle_percents = list()
        sma_short_long_percents = list()

        # Search - SMA
        for row in data_trend.itertuples():
            
            sma_names = StockDataFrameGenerater.get_sma_column_names()
            sma_short = getattr(row, sma_names[0])
            sma_middle = getattr(row, sma_names[1])
            sma_long = getattr(row, sma_names[2])

            # short - middle
            sma_short_middle_percents.append((sma_short - sma_middle) / sma_middle)

            # short - long
            sma_short_long_percents.append((sma_short - sma_long) / sma_long))

            continue


        score = 0
        score_offset = cls.__trend_count * 100 / 4

        # Score : short - middle

        # Score : short - long 

        print(data_trend)    

        pass