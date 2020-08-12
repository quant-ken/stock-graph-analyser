from stock_summary import StockSummary
from stock_data_frame_generater import StockDataFrameGenerater

class StockAnalyzer:

    __trend_count = 7
    __cross_offset = 4.25       # percent 
    __score_offset = 0

    @classmethod
    def initialize(cls):
        cls.__score_offset = 100 / cls.__trend_count / 2.0

    @classmethod
    def analyze(cls, summary, data_frame):
        data_trend = data_frame.tail(cls.__trend_count)
        print(data_trend)
        sma_names = StockDataFrameGenerater.get_sma_column_names()
        sma_short_middle_percents = list()
        sma_short_long_percents = list()


        # Search - SMA
        for row in data_trend.itertuples():
            
            sma_short = getattr(row, sma_names[0])
            sma_middle = getattr(row, sma_names[1])
            sma_long = getattr(row, sma_names[2])

            # short - middle
            sma_short_middle_percents.append((sma_short - sma_middle) / sma_middle)

            # short - long
            sma_short_long_percents.append((sma_short - sma_long) / sma_long)

            continue


        score = cls.__get_score(sma_short_middle_percents)
        score += cls.__get_score(sma_short_long_percents)

        summary.update_trend_score(score)

        log = '{name} 점수 : {score}'.format(name=summary.name, score=score)
        print(log)    

        

    @classmethod 
    def __get_score(cls, ma_percents):
        score = 0
        
        for i in ma_percents.count():

            if i is 0:
                if ma_percents[i] < 0:
                    score += cls.__score_offset
                continue

            if ma_percents[i] > ma_percents[i - 1]:
                score += cls.__score_offset

        # Cross Score
        score += cls.__get_cross_score(ma_percents[-1])

        return score


    @classmethod
    def __get_cross_score(cls, last_ma_percent):
        if last_ma_percent >= -cls.__cross_offset and last_ma_percent <= cls.__cross_offset:
            return cls.__score_offset
        else:
            return 0
            


