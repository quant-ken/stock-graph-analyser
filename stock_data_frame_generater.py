import time
import datetime
import pandas as pd
import requests
from stock_summary import StockSummary

class StockDataFrameGenerater:

    __base_url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'

    __sma_column_format = 'SMA{value}'
    __ema_column_format = 'EMA{value}'

    __sma_list = [10, 20, 60, 120]
    __ema_list = [10, 20, 60, 120]

    __ma_column_names = list()
    __sma_column_names = list()
    __ema_column_names = list()

    # 12 = 4달 전 까지
    # 30 = 15달 전 까지
    __page_count = 12



    @classmethod
    def initialize(cls):
        start = time.time()

        for sma in cls.__sma_list:
            name = cls.__sma_column_format.format(value=sma)
            cls.__sma_column_names.append(name)
            cls.__ma_column_names.append(name)

        for ema in cls.__ema_list:
            name = cls.__ema_column_format.format(value=ema)
            cls.__ema_column_names.append(name)
            cls.__ma_column_names.append(name)

        print('StockDataFrameGenerater.initialize() :', round(time.time() - start, 4))

    @classmethod
    def get_sma_column_names(cls):
        return cls.__sma_column_names

    @classmethod
    def get_ema_column_names(cls):
        return cls.__ema_column_names

    @classmethod
    def get_ma_column_names(cls):
        return cls.__ma_column_names

    @classmethod
    def __make_url(cls, code):
        return cls.__base_url.format(code=code)

    @classmethod
    def generate_data_frame(cls, summary):
        start = time.time()

        code = summary.code
        url = cls.__make_url(code)
        data_frame = pd.DataFrame()

        for page in range(1, cls.__page_count):
            page_url = '{url}&page={page}'.format(url=url, page=page)
            #page_html = pd.read_html(page_url, encoding="euc-kr", headers={'User-agent': 'Mozilla/5.0'}).text)
            
            page_html = pd.read_html(requests.get(page_url, headers={'User-agent': 'Mozilla/5.0'}).text)

            #pd.read_html(requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text) 
            data_frame = data_frame.append(page_html[0], ignore_index=True)

        data_frame = data_frame.dropna()

        # Rename columns
        data_frame = data_frame.rename  \
        (
            columns =
            {
                '날짜': 'date',
                '종가': 'close',
                # '전일비': 'diff',
                '시가': 'open',
                '고가': 'high',
                '저가': 'low',
                '거래량': 'volume'
            }
        )

        # Convert data type
        data_frame['date'] = pd.to_datetime(data_frame['date'])
        data_frame[['close', 'open', 'high', 'low', 'volume']] \
            = data_frame[['close', 'open', 'high', 'low', 'volume']].astype(int)

        # Sort by date
        data_frame = data_frame.sort_values(by=['date'], ascending=True)

        # Generate SMA, EMA
        for sma_value in cls.__sma_list:
            column = cls.__sma_column_format.format(value=sma_value)
            data_frame[column] = data_frame['close'].rolling(sma_value).mean()

        for ema_value in cls.__ema_list:
            column = cls.__ema_column_format.format(value=ema_value)
            data_frame[column] = data_frame['close'].ewm(ema_value).mean()

        log = 'StockDataFrameGenerater.generate_data_frame({name})'.format(name = summary.name)
        print(log, round(time.time() - start, 4))

        return data_frame
