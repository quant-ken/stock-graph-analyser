
class StockListParser:

    __stock_code_path = './resource/stock_list.xlsx'
    __code_info_map = {}

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

        cls.__code_name_map[code] = name
        cls.__name_code_map[name] = code


    @classmethod
    def get_info(cls):
        return cls.__name_code_map.keys()