import time
import concurrent
from concurrent.futures import ThreadPoolExecutor
from stock_summary import StockSummary
from stock_summary_parser import StockSummaryParser
from stock_data_frame_generater import StockDataFrameGenerater
from stock_graph_generater import StockGraphGenerater
from stock_analyser import StockAnalyser


test_mode = False
restrict_stock_count = 1000
thread_count = 64


def initialize():
    StockSummaryParser.initialize(restrict_stock_count)
    StockDataFrameGenerater.initialize()
    StockAnalyser.initialize()


def process(stock_code):
    summary = StockSummary.get_summary(stock_code)
    data_frame = StockDataFrameGenerater.generate_data_frame(summary)
    StockAnalyser.analyze(summary, data_frame)
    StockGraphGenerater.generate_graph(summary, data_frame)


def run():
    if test_mode == True:
        run_test()
    else:
        run_production()


def run_test():
    process('005930')   # 삼성전자


def run_production():

    thread_list = []

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        for code in StockSummary.get_codes():
            thread_list.append(executor.submit(process, code))
        for execution in concurrent.futures.as_completed(thread_list):
            execution.result()


if __name__ == "__main__":
    start = time.time()

    initialize()
    run()

    StockAnalyser.save_score_list()
    print('main.py :', round(time.time() - start, 4))
