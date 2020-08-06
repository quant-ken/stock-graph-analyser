from stock_summary import StockSummary
from stock_summary_parser import StockSummaryParser
from stock_data_frame_generater import StockDataFrameGenerater
from stock_graph_generater import StockGraphGenerater


if __name__ == "__main__":

    StockSummaryParser.initialize()
    StockDataFrameGenerater.initialize()

    for code in StockSummary.get_codes():

        summary = StockSummary.get_summary(code)
        data_frame = StockDataFrameGenerater.generate_data_frame(code)

        StockGraphGenerater.generate_graph(summary, data_frame)
