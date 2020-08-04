import requests
from bs4 import BeautifulSoup
from stock_list_parser import StockListParser



if __name__ == "__main__":

    StockListParser.initialize()
    print(StockListParser.get_codes())
    print(StockListParser.get_names())
    url = ""
