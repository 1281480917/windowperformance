import xlrd
import os
import logging


class conversions():
    def __init__(self):
        self.config = {}

    def conversions_to_dict(self):
        path = 'input'
        for info in os.listdir(path):
            logging.info('打开文件:%s' % info)
            tables = self.__open_excel(path, info)
            for table in tables:
                try:
                    self.__creat_test_suit(table)
                except IndexError as e:
                    logging.info('当前工作表无数据', e)
                    break

        return self.config

    def __open_excel(self, path, info):
        domain = os.path.abspath(path)
        info = os.path.join(domain, info)
        data = xlrd.open_workbook(info)
        tables = data.sheets()
        return tables

    def __creat_test_suit(self, table):
        for ncols_index in range(0, table.ncols, 2):
            for row_index in range(1, table.nrows):
                url_name = table.col_values(ncols_index)[row_index]
                url = table.col_values(ncols_index + 1)[row_index]
                self.config[url_name] = url


if __name__ == '__main__':
    print(conversions().conversions_to_dict())
