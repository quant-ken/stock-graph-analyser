import numpy
import pandas as pd

from stock_summary import StockSummary



# set directory with yours
excel_dir = './resource/stock_list.xlsx'



# read a excel file and make it as a DataFrame

df_from_excel = pd.read_excel(excel_dir, # write your directory here


                              dtype = {'region': str, 
                                       'sales_representative': numpy.int64, 
                                       'sales_amount': float}, # dictionary type

                              index_col = 'id', 

                              na_values = 'NaN', 

                              thousands = ',', 

                              nrows = 10, 

                              comment = '#')





class StockSummaryParser:

    __stock_code_path = './resource/stock_list.xlsx'

    @classmethod
    def initialize(cls):
        file = open(cls.__stock_code_path, 'r', encoding='utf8');
        
        while True:
            line = file.readline()

            if not line: 
                break

            cls.__process_line(line)

        file.close()
        return

    @classmethod
    def __process_line(cls, line):
        elems = line.split('=')
        name = elems[0]
        code = elems[1]

        # StockSummary.__code_summary_map[code] = new StockSummary()


    @classmethod
    def get_info(cls):
        return cls.__name_code_map.keys()