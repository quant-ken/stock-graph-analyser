import time
from stock_summary import StockSummary
from stock_summary_parser import StockSummaryParser
from stock_data_frame_generater import StockDataFrameGenerater
from stock_graph_generater import StockGraphGenerater


test_mode = False


def initialize():
    StockSummaryParser.initialize()
    StockDataFrameGenerater.initialize()


def run():
    if test_mode is True:
        run_test()
    else:
        run_production()


def run_test():
    summary = StockSummary.get_summary('005930')
    data_frame = StockDataFrameGenerater.generate_data_frame(summary)
    StockGraphGenerater.generate_graph(summary, data_frame)
    pass


def run_production():
    for code in StockSummary.get_codes():
        summary = StockSummary.get_summary(code)
        data_frame = StockDataFrameGenerater.generate_data_frame(summary)
        StockGraphGenerater.generate_graph(summary, data_frame)


if __name__ == "__main__":
    start = time.time()

    initialize()
    run()

    print('main.py :', round(time.time() - start, 4))
