import code
import os
from datetime import date
import re
import glob
from stock_summary import StockSummary
from stock_data_frame_generater import StockDataFrameGenerater

class StockAnalyser:

    __export_path = './export/score/{filename}'

    __trend_count = 140         # 
    __seaarch_count = 72        # Page
    __cross_offset = 4.25       # percent 
    __score_offset = 0

    @classmethod
    def initialize(cls):
        cls.__score_offset = 100 / cls.__seaarch_count / 2.0

    @classmethod
    def analyze(cls, summary, data_frame):
        data_trend = data_frame.tail(cls.__seaarch_count)

        
        sma_names = StockDataFrameGenerater.get_sma_column_names()
        sma_short_middle_percents = list()
        sma_short_long_percents = list()

        price = 0
        price_7 = 0
        price_30 = 0
        price_60 = 0

        # Search - SMA
        for row in data_trend.itertuples():
            
            day_offset = getattr(row, 'Index')
            sma_short = getattr(row, sma_names[0])
            sma_middle = getattr(row, sma_names[1])
            sma_long = getattr(row, sma_names[2])

            if day_offset <= cls.__trend_count:
                # short - middle
                sma_short_middle_percents.append((sma_short - sma_middle) / sma_middle)

                # short - long
                sma_short_long_percents.append((sma_short - sma_long) / sma_long)

            close_price = getattr(row, 'close')

            if day_offset <= 1 and price == 0:
                price = close_price
            elif day_offset <= 7 and price_7 == 0:
                price_7 = close_price
            elif day_offset <= 30 and price_30 == 0:
                price_30 = close_price
            elif day_offset <= 60 and price_60 == 0:
                price_60 = close_price

            continue


        score = cls.__get_score(sma_short_middle_percents)
        score += cls.__get_score(sma_short_long_percents)

        summary.update_trend_score(score)
        summary.price = price
        summary.price_7 = price_7
        summary.price_30 = price_30
        summary.price_60 = price_60

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
        format = '{score}_{filename}_{code}_{price}_{price_7}_{price_30}_{price_60}.txt'
        file_name = format.format(score=score, 
                                  filename=summary.name, 
                                  code=summary.code,
                                  price=summary.price,
                                  price_7=summary.price_7,
                                  price_30=summary.price_30,
                                  price_60=summary.price_60)
        return cls.__export_path.format(filename=file_name)

    @classmethod
    def __natural_sort(cls, list): 
        convert = lambda text: int(text) if text.isdigit() else text.lower() 
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        return sorted(list, key = alphanum_key, reverse=True)

    @classmethod
    def save_score_list(cls):

        result_name = './export/score-result.md'
        file = open(result_name, 'w')        

        file_paths = cls.__natural_sort(glob.glob('./export/score/*.txt'))
        
        # format = '{score}점 \t-\t[{name}]({url})-{code}-{price}원\t7D({price_7}) \t30D({price_30}) \t60D({price_60})'


        for file_path in file_paths:
            file_name = os.path.basename(file_path).replace('.txt', '') 
            
            if file_name == 'Temp':
                continue

            elems = file_name.split('_')
            score = elems[0]
            name = elems[1]
            code = elems[2]
            price = int(elems[3])
            price_7 = int(elems[4])
            price_30 = int(elems[5])
            price_60 = int(elems[6])

            price_7 = (price - price_7) / price_7 * 100
            if price_7 >= 0:
                price_7 = f'<span style="color: red">{format(price_7, ".2f")}</span>'
            else:
                price_7 = f'<span style="color: #0000FF">{format(price_7, ".2f")}</span>'


            price_30 = (price - price_30) / price_30 * 100
            if price_30 >= 0:
                price_30 = f'<span style="color: red">{format(price_30, ".2f")}</span>'
            else:
                price_30 = f'<span style="color: #0000FF">{format(price_30, ".2f")}</span>'


            price_60 = (price - price_60) / price_60 * 100
            if price_60 >= 0:
                price_60 = f'<span style="color: red">{format(price_60, ".2f")}</span>'
            else:
                price_60 = f'<span style="color: #0000FF">{format(price_60, ".2f")}</span>'

            url = 'https://finance.naver.com/item/fchart.naver?code=' + code

            line = f'{score}점 - [{name}]({url})({code}) {price}원 --- 7D({price_7}%) / 30D({price_30}%) / 60D({price_60}%)'


            # line = format.format(score=score, 
            #                      name=name, 
            #                      url=url, 
            #                      code=code, 
            #                      price=format(price, ','), 
            #                      price_7=format((price - price_7) / price_7 * 100, '.2f'), 
            #                      price_30=format((price - price_30) / price_30 * 100, '.2f'), 
            #                      price_60=format((price - price_60) / price_60 * 100, '.2f'))

            file.write(line + '  \n')

        file.write('\nEOF \n')

        file.close()
        


