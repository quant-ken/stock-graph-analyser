import os
import re
import glob
from stock_summary import StockSummary
from stock_data_frame_generater import StockDataFrameGenerater

class StockAnalyzer:

    __export_path = './export/score/{filename}'
    __file_name_format = '{score}_{filename}.txt'

    __trend_count = 7
    __cross_offset = 4.25       # percent 
    __score_offset = 0

    @classmethod
    def initialize(cls):
        cls.__score_offset = 100 / cls.__trend_count / 2.0

    @classmethod
    def analyze(cls, summary, data_frame):
        data_trend = data_frame.tail(cls.__trend_count)

        
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

        cls.__save_result(summary, score)

        

    @classmethod 
    def __get_score(cls, ma_percents):
        score = 0
        
        for i in range(len(ma_percents)):

            if i is 0:
                if ma_percents[i] < 0:
                    score += cls.__score_offset
                continue

            if ma_percents[i] > ma_percents[i - 1]:
                score += cls.__score_offset

        # Cross Score
        score += cls.__get_cross_score(ma_percents[-1])

        return int(score)


    @classmethod
    def __get_cross_score(cls, last_ma_percent):
        if last_ma_percent >= -cls.__cross_offset and last_ma_percent <= cls.__cross_offset:
            return cls.__score_offset
        else:
            return 0
            

    @classmethod
    def __save_result(cls, summary, score):

        cls.__pre_process_result(summary)

        file_name = cls.__get_file_name(summary, score)

        f = open(file_name, 'w')
        f.close()

        
    @classmethod
    def __pre_process_result(cls, summary):
        search_form = cls.__get_file_name(summary, '*')
        search_results = glob.glob(search_form)

        for result in search_results:
            os.remove(result)

    @classmethod 
    def __get_file_name(cls, summary, score):
        file_name = cls.__file_name_format.format(score=score, filename=summary.name)
        return cls.__export_path.format(filename=file_name)

    @classmethod
    def __natural_sort(cls, list): 
        convert = lambda text: int(text) if text.isdigit() else text.lower() 
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        return sorted(list, key = alphanum_key, reverse=True)

    @classmethod
    def save_score_list(cls):

        result_name = 'score-result.txt'
        file = open(result_name, 'w')        

        file_names = cls.__natural_sort(glob.glob('./export/score/*.txt'))
        
        for line in file_names:
            file.write(line.split('/')[-1] + '\n')

        file.write('\nEOF \n')

        file.close()
        


