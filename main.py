from stock_summary_parser import StockSummaryParser
from stock_graph_parser import StockGraphParser

if __name__ == "__main__":

    StockSummaryParser.initialize()
    
    StockGraphParser.get_data_frame('002700')
