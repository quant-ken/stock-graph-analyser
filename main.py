import time
from stock_summary import StockSummary
from stock_summary_parser import StockSummaryParser
from stock_data_frame_generater import StockDataFrameGenerater
from stock_graph_generater import StockGraphGenerater
from stock_analyzer import StockAnalyzer


test_mode = False
use_custom_stock_list = False


def initialize():
    StockSummaryParser.initialize(use_custom_stock_list)
    StockDataFrameGenerater.initialize()
    StockAnalyzer.initialize()


def process(stock_code):
    summary = StockSummary.get_summary(stock_code)
    data_frame = StockDataFrameGenerater.generate_data_frame(summary)
    StockAnalyzer.analyze(summary, data_frame)
    StockGraphGenerater.generate_graph(summary, data_frame)


def run():
    if test_mode is True:
        run_test()
    else:
        run_production()


def run_test():
    process('005930')   # 삼성전자


def run_production():
    for code in StockSummary.get_codes():
        process(code)
        pass



if __name__ == "__main__":
    start = time.time()

    initialize()
    run()

    print('main.py :', round(time.time() - start, 4))
