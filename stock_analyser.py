import code
import os
from datetime import date
import re
import glob
from stock_summary import StockSummary
from stock_data_frame_generater import StockDataFrameGenerater

class StockAnalyser:

    export_path = './export/score/'

    __trend_count = 280         # 
    __search_count = 72        # Page
    __cross_offset = 4.25       # percent 
    __score_offset = 0

    @classmethod
    def initialize(cls):
        cls.__score_offset = 100 / cls.__search_count * 1.5     # 1.5배 가중치

    @classmethod
    def analyze(cls, summary, data_frame):
        # +60: price 60
        mininum_count = 60
        data_trend = data_frame.tail(cls.__search_count + mininum_count)
        total_count = len(data_trend)

        sma_names = StockDataFrameGenerater.get_sma_column_names()
        sma_short_middle_percents = []
        sma_short_long_percents = []

        price = price_7 = price_30 = price_60 = 0

        volumes = []
        count = 0
        for row in data_trend.itertuples():
            if count < mininum_count:
                count += 1
                continue

            day_offset = total_count - getattr(row, 'Index')
            sma_short = getattr(row, sma_names[0])
            sma_middle = getattr(row, sma_names[1])
            sma_long = getattr(row, sma_names[2])
            close_price = getattr(row, 'close')

            if day_offset <= cls.__trend_count:
                sma_short_middle_percents.append((sma_short - sma_middle) / sma_middle)
                sma_short_long_percents.append((sma_short - sma_long) / sma_long)

            if day_offset <= 1 and price == 0:
                price = close_price
            elif day_offset <= 7 and price_7 == 0:
                price_7 = close_price
            elif day_offset <= 30 and price_30 == 0:
                price_30 = close_price
            elif day_offset <= 60 and price_60 == 0:
                price_60 = close_price

            volumes.append(getattr(row, 'volume', 0))

        # 점수 계산
        score_offset = 0
        score_short = cls.__get_score(sma_short_middle_percents)
        score_long = cls.__get_score(sma_short_long_percents)

        # 🔴 RSI 점수 반영 (기본: 14일 기준)
        last_rsi = data_frame['RSI14'].iloc[-1] if 'RSI14' in data_frame.columns else None
        if last_rsi:
            if 30 < last_rsi < 70:
                score_offset += 5
            elif last_rsi > 70:  # 과매수 경고
                score_offset -= 5

        # 🟠 MACD > Signal
        if 'MACD' in data_frame.columns and 'MACDS' in data_frame.columns:
            macd = data_frame['MACD'].iloc[-1]
            macds = data_frame['MACDS'].iloc[-1]
            if macd > macds:
                score_offset += 7

        # 🔵 거래량이 최근 평균 이상이면 +1
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        current_volume = data_frame['volume'].iloc[-1] if 'volume' in data_frame.columns else 0
        if current_volume > avg_volume:
            score_offset += 7

        # 결과 저장
        summary.update_trend_score(score_offset)
        summary.price = price
        summary.price_7 = price_7
        summary.price_30 = price_30
        summary.price_60 = price_60

        score_short -= score_offset
        score_long -= score_offset

        # 단기/장기 가중치
        max_score = max(score_short, score_long, 1)  # 0 나누기 방지용

        short_ratio = score_short / max_score  # 0~1 사이
        long_ratio = score_long / max_score    # 0~1 사이

        # 가중치 0.3~1.0 사이로 조절
        short_weight = 0.3 + 0.7 * short_ratio
        long_weight = 0.3 + 0.7 * long_ratio

        total_weight = short_weight + long_weight

        score_overall = round((score_short * short_weight + score_long * long_weight) / total_weight)

        print(f'{summary.name} 점수 : {score_offset}')
        cls.__save_result(summary, score_overall, score_short, score_long)
        

    @classmethod 
    def __get_score(cls, ma_percents):
        score = 0
        
        for i in range(len(ma_percents)):
            if i == 0:
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
    def __save_result(cls, summary, score_overall, score_short, score_long):
        file_name = cls.__get_file_name(summary, score_overall, score_short, score_long)

        f = open(file_name, 'w')
        f.close()

    
    @classmethod 
    def __get_file_name(cls, summary, score_overall, score_short, score_long):
        format = '{score_overall}_{score_short}_{score_long}_{filename}_{code}_{price}_{price_7}_{price_30}_{price_60}.txt'
        file_name = format.format(score_overall=score_overall, 
                                  score_short=score_short, 
                                  score_long=score_long, 
                                  filename=summary.name, 
                                  code=summary.code,
                                  price=summary.price,
                                  price_7=summary.price_7,
                                  price_30=summary.price_30,
                                  price_60=summary.price_60)
        return cls.export_path + file_name

    @classmethod
    def __natural_sort(cls, list): 
        return sorted(
            list,
            key=lambda path: int(os.path.basename(path).split('_')[0]),
            reverse=True
        )

    # 12.3 --> 🔺 12.3%
    @classmethod
    def __format_change(cls, value):
        arrow = '🟥+' if value >= 0 else '🟦-'
        return f'{arrow}{abs(value):.2f}%'

    @classmethod
    def save_score_list(cls):

        result_name = './export/score-result.md'
        file = open(result_name, 'w')        

        file_paths = list(filter(lambda path: not path.endswith('Temp.txt'), glob.glob('./export/score/*.txt')))
        file_paths = cls.__natural_sort(file_paths)
        
        # format = '{score}점 \t-\t[{name}]({url})-{code}-{price}원\t7D({price_7}) \t30D({price_30}) \t60D({price_60})'

        header = '| 종합 점수 | 단기 점수 | 장기 점수 | 종목명 | 코드 | 현재가 | 7일 수익률 | 30일 수익률 | 60일 수익률 |'
        separator = '|-------|-------|-------|----------|---------|----------|------------|------------|------------|'
        file.write(header + '  \n')
        file.write(separator + '  \n')

        for file_path in file_paths:
            file_name = os.path.basename(file_path).replace('.txt', '') 
            
            if file_name == 'Temp':
                continue

            i = 0
            elems = file_name.split('_')
            score_overall = elems[i]; i += 1
            score_short = elems[i]; i += 1
            score_long = elems[i]; i += 1
            name = elems[i]; i += 1
            code = elems[i]; i += 1
            price = int(elems[i]); i += 1
            price_7 = int(elems[i]); i += 1
            price_30 = int(elems[i]); i += 1
            price_60 = int(elems[i])

            # 7일 수익률
            price_7 = 0 if price_7 == 0 else (price - price_7) / price_7 * 100
            price_7 = cls.__format_change(price_7)

            # 30일 수익률
            price_30 = 0 if price_30 == 0 else (price - price_30) / price_30 * 100
            price_30 = cls.__format_change(price_30)

            # 60일 수익률
            price_60 =  0 if price_60 == 0 else (price - price_60) / price_60 * 100
            price_60 = cls.__format_change(price_60)

            url_naver = 'https://finance.naver.com/item/fchart.naver?code=' + code

            line = f'| {score_overall}점 | {score_short}점 | {score_long}점 | {name} ([네이버]({url_naver})) | {code} | {price:,}원 | {price_7} | {price_30} | {price_60} |'
            file.write(line + '  \n')

        file.write('\nEOF \n')
        file.close()
        


