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

        data_frame = data_frame.dropna()

        # Convert data type
        data_frame['date'] = pd.to_datetime(data_frame['date'])
        data_frame[['close', 'open', 'high', 'low', 'volume']] \
            = data_frame[['close', 'open', 'high', 'low', 'volume']].astype(int)

        # Sort by date
        data_frame = data_frame.sort_values(by=['date'], ascending=True)

        # Reset index
        data_frame = data_frame.reset_index(drop=True)

        # Generate SMA, EMA
        for sma_value in cls.__sma_list:
            column = cls.__sma_column_format.format(value=sma_value)
            data_frame[column] = data_frame['close'].rolling(sma_value).mean()

        for ema_value in cls.__ema_list:
            column = cls.__ema_column_format.format(value=ema_value)
            data_frame[column] = data_frame['close'].ewm(ema_value, adjust=False).mean()

        # RSI (14일)
        delta = data_frame['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        data_frame['RSI14'] = 100 - (100 / (1 + rs))

        # MACD, MACDS
        ema12 = data_frame['close'].ewm(span=12, adjust=False).mean()
        ema26 = data_frame['close'].ewm(span=26, adjust=False).mean()
        data_frame['MACD'] = ema12 - ema26
        data_frame['MACDS'] = data_frame['MACD'].ewm(span=9, adjust=False).mean()

        log = 'StockDataFrameGenerater.generate_data_frame({name})'.format(name = summary.name)
        print(log, round(time.time() - start, 4))

        return data_frame
