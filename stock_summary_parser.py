from stock_summary import StockSummary


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