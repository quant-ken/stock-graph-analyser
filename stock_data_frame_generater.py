import time
import datetime
import pandas as pd

from stock_summary import StockSummary


class StockDataFrameGenerater:

    __base_url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'

    __sma_list = [10, 60, 120]
    __ema_list = [10, 60, 120]

    __ma_column_names = list()

    __page_count = 30

    @classmethod
    def initialize(cls):

        for sma in cls.__sma_list:
            cls.__ma_column_names.append('SMA-{sma}'.format(sma=sma))

        for ema in cls.__ema_list:
            cls.__ma_column_names.append('EMA-{ema}'.format(ema))

    @classmethod
    def get_ma_column_names(cls):
        return cls.__ma_column_names

    @classmethod
    def __make_url(cls, code):
        return cls.__base_url.format(code=code)

    @classmethod
    def generate_data_frame(cls, code):

        url = cls.__make_url(code)
        data_frame = pd.DataFrame()

        for page in range(1, cls.__page_count):
            page_url = '{url}&page={page}'.format(url=url, page=page)
            data_frame = data_frame.append(pd.read_html(
                page_url, header=0)[0], ignore_index=True)
            print(page)

        data_frame = data_frame.dropna()

        # Rename columns
        data_frame = data_frame.rename(
            columns={
                '날짜': 'date',
                '종가': 'close',
                '전일비': 'diff',
                '시가': 'open',
                '고가': 'high',
                '저가': 'low',
                '거래량': 'volume'})

        # Convert data type
        data_frame[['close', 'diff', 'open', 'high', 'low', 'volume']] = data_frame[[
            'close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)
        data_frame['date'] = pd.to_datetime(data_frame['date'])

        # Sort by date
        data_frame = data_frame.sort_values(by=['date'], ascending=True)

        # Generate SMA, EMA
        for sma_value in cls.__sma_list:
            column = 'SMA-{value}'.format(value=sma_value)
            data_frame[column] = data_frame['close'].rolling(sma_value).mean()

        for ema_value in cls.__ema_list:
            column = 'EMA-{value}'.format(value=ema_value)
            data_frame[column] = data_frame['close'].ewm(ema_value).mean()

        return data_frame
