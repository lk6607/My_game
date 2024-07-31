# -*- coding: utf-8 -*-
# 需要安装的第三方库:
# pip3 install xlrd==1.2.0
# pip3 install tenjin
# 修改

import sys
import os
import traceback
import xlrd

from tenjin.helpers import *
from tenjin.escaped import *
from xml.dom import minidom
from common import *
import time
import importlib
import codecs

sys.path.append('.')
# import helper
helper = importlib.import_module("helper")


ExportTypeDict = {
    's':'server',
    'c':'client',
}


def excel_cell_value_format(value):
    if isinstance(value, float):
        if int(value) == value:
            return int(value)
        else:
            return round(value, 4)
    elif isinstance(value, str):
        try:
            # 这里有一个坑，int('30_1') = 301，下划线被忽略了
            temp = int(value)
            if str(temp) == value:
                return int(value)
            else:
                return value
        except Exception:
            try:
                return round(value, 4)
            except Exception:
                return as_escaped(value)
    else:
        try:
            return int(value)
        except Exception:
            return as_escaped(value)


class ExportItem(object):
    """
        一个excel文件的导出数据：
            {
                'sheet1':{'server':'data_xxx.erl', 'client':'data_xxx.lua'},
                'sheet2':{'server':'data_xxx.erl', 'client':'data_xxx.lua'}
            }
    """
    def __init__(self, excel_filename):
        super(ExportItem, self).__init__()
        self.excel_filename = excel_filename
        self.sheets = {}

    def add_sheet(self, sheet, export_type, tpl):
        if sheet not in self.sheets:
            self.sheets[sheet] = {'server':'', 'client':''}
        self.sheets[sheet][export_type] = tpl[:-4]

    def get_sheet_size(self):
        return len(self.sheets)
    
    def get_sheets(self):
        return self.sheets

    def excle_filename(self):
        return self.excel_filename

    def is_matched(self, query_str):
        if query_str in self.excel_filename:
            return True
        for sheet in self.sheets:
            if query_str in sheet or query_str in self.sheets[sheet]['server'] or query_str in self.sheets[sheet]['client']:
                return True
        return False


class ExportTool(object):
    def __init__(self, excel_dir, export_type = 'server'):
        self.excel_dir = excel_dir
        self.export_type = export_type
        self.load_export_conf()

    def load_export_conf(self):
        """
        tpl_dict:{
            'export_type':'client' or 'server'
            'tpl':'data_xxx.lua.tpl',
            'excle_file':对应的excel文件名称
            'datas':[{'data_key':data_key, 'sheet':sheet, 'begin_row':begin_row, 'sort_col':sort_col, 'season_sheet': season_sheet}]
        }
        """
        doc = minidom.parse(os.path.join('config', 'cfg_module.xml'))
        root = doc.documentElement
        seasons = get_attrvalue(root, 'seasons')
        if seasons:
            seasons = int(seasons)
        else:
            seasons = 1

        setattr(self, "total_season", seasons)
        
        self.export_files = {}  # {'data_xxx.lua.tpl':tpl_dict}
        self.export_items = []  # [ExportItem]
        for key in ExportTypeDict.values():
            setattr(self, 'export_files_' + key, {})

        for node in get_xmlnode(root, 'file'):
            excle_file    = get_attrvalue(node, 'excle_file')
            export_item   = ExportItem(excle_file)
            for node2 in get_xmlnode(node, 'export'):
                export_type = ExportTypeDict[get_attrvalue(node2, 'type')]
                tpl_dict = {}
                tpl_dict['tpl'] = get_attrvalue(node2, 'tpl')
                tpl_dict['export_type'] = export_type
                tpl_dict['excle_file'] = excle_file
                datas = []
                for node3 in get_xmlnode(node2, 'dict'):
                    d = {}
                    d['data_key'] = get_attrvalue(node3, 'data_key')
                    d['sheet'] = get_attrvalue(node3, 'sheet')
                    d['begin_row'] = int(get_attrvalue(node3, 'begin_row'))
                    d['sort_col'] = get_attrvalue(node3, 'sort_col')
                    d['season_sheet'] = True if get_attrvalue(node3, 'season_sheet') == 'true' else False
                    datas.append(d)
                    export_item.add_sheet(d['sheet'], export_type, tpl_dict['tpl'])
                tpl_dict['datas'] = datas
                self.export_files[tpl_dict['tpl']] = tpl_dict

                tmp = getattr(self, 'export_files_' + export_type)
                tmp[tpl_dict['tpl']] = tpl_dict
            self.export_items.append(export_item)

    def on_export_all_server(self, save_dir):
        try:
            begin = time.time()
            export_files = []

            export_files_server = getattr(self, 'export_files_' + self.export_type)
            for key in export_files_server:
                tpl_dict = export_files_server[key]
                if tpl_dict['export_type'] == self.export_type:
                    ret = self.export_one_file_help(save_dir, tpl_dict)
                    export_files.extend(ret)
            end = time.time()
            msg = '\n'.join(export_files) + u"\n消耗时间：{0}秒".format(int(end - begin))
            print(msg)
        except Exception:
            msg = traceback.format_exc()
            print("导出发生错误:", msg)

    def export_one_file_help(self, save_dir, tpl_dict, translate_cols = None, translate_words = None):
        excle_file = tpl_dict['excle_file']
        tpl = tpl_dict['tpl']
        cfg, _ = os.path.splitext(tpl)

        file_list = []
        file_list.append((excle_file, cfg))

        ret = []
        for e_file, t_file in file_list:
            dict = {}
            for data in tpl_dict['datas']:
                excle_filename = os.path.join(self.excel_dir, e_file)
                xml_data = xlrd.open_workbook(excle_filename)
                sheet_name = data['sheet']
                if data['season_sheet']:
                    sheet_name = sheet_name + '_' + str(self.cur_season)
                table = xml_data.sheet_by_name(sheet_name)
                key = data['data_key']
                col_start = 1
                col_end = table.ncols
                begin_row = data['begin_row']
                dict[key] = []

                for i in range(begin_row, table.nrows):
                    data_dict = {}
                    # 如果第i行的第一列所在的单元格没有数据，则认为是空的，跳过该行
                    if str(table.cell(i, 0).value).strip() == '':
                        continue
                    for j in range(col_start - 1, col_end):
                        if table.cell(0, j).ctype == xlrd.XL_CELL_TEXT:
                            tran_key = e_file + "." + sheet_name + "." + table.cell(0, j).value
                            val = excel_cell_value_format(table.cell(i, j).value)
                            if translate_cols != None and tran_key in translate_cols:
                                if val in translate_words:
                                    data_dict[table.cell(0, j).value.strip()] = translate_words[val]
                                else:
                                    data_dict[table.cell(0, j).value.strip()] = val
                            else:
                                data_dict[table.cell(0, j).value.strip()] = val
                    dict[key].append(data_dict)

                if 'sort_col' in data and len(data['sort_col']) > 0:
                    dict[key].sort(key=lambda x: x[data['sort_col']], reverse=True)
            # render template with dict data
            print("tpl:", tpl)
            print("pwd:", os.getcwd())
            dict['__season'] = self.cur_season
            content = engine.render(os.path.join(os.getcwd(), "config", tpl), dict)
            cfg_file = os.path.join(save_dir, t_file)
            dest = codecs.open(cfg_file, "w", 'utf-8')
            # 写入common代码
            _, ext = os.path.splitext(t_file)
            if tpl_dict['export_type'] == 'server':
                common_code_path = "common_server"
            else:
                common_code_path = "common_client"
            common_code_path = os.path.join("config", common_code_path + ext)
            if os.path.exists(common_code_path):
                common_code = open(common_code_path, "r").read()
                if "%s" in common_code:
                    dest.write(common_code % t_file)
                else:
                    dest.write(common_code)

            content = content.replace(u"\r\n", u"\n")
            dest.write(content)
            dest.close()
            ret.append(cfg_file)
        return ret


    def do_export_all(self, save_dir):
        for i in range(self.total_season):
            setattr(self, 'cur_season', i + 1)
            path = os.path.join(save_dir, str(i + 1))
            if not os.path.exists(path) :
                os.mkdir(path)
            self.on_export_all_server(path)
    


if __name__ == "__main__":
    excel_dir = sys.argv[1]  # Excel表路径
    save_dir  = sys.argv[2]  # 保存到哪个目录去
    export_type = sys.argv[3]
    # excel_dir = u'F:/work/xgame/xgame-design/5_配置表'
    # save_dir = u'F:/work/slg/slg-server/config/'

    if not os.path.exists(save_dir) :
        print('save dir not found!')
    else :
        mod = ExportTool(excel_dir, export_type)
        mod.do_export_all(save_dir)
