# -*- coding: utf-8 -*-

import xlrd

attr_list = {}

def init():
    global attr_list
    xml_data = xlrd.open_workbook("../W_玩家属性表_date_player_attr.xlsx")
    table = xml_data.sheet_by_name('enum_player_attr')
    begin_row = 2
    for i in range(begin_row, table.nrows):
        attr_list[table.cell(i, 0).value] = table.cell(i, 1).value


def get_attr_dict():
    global attr_list
    return attr_list


init()
