# -*- coding: utf-8 -*-
'''
.tpl文件需要使用到的一些扩展方法都可以定义到这里
以下是一些使用提示：
    如果遇到引号转义问题，使用as_escaped(some_str)来解决
    python有很多很好用的字符串处理方法，如：
        split      str.split(";") 返回分割字符串的数组格式
        join       ",".join(str_list) 将字符串数组使用','连接起来
        replace    str.replace(',', ';') 将字符串中的逗号替换为分号
'''
import attr_transform


def py_split_items(item_str):
    if item_str.strip() == "":
        return "[]"
    else:
        s = "], [".join([s for s in item_str.split("|") if s != ''])
        if s == '':
          return "[]"
        else:
          return "[[" + s + "]]"
        
def py_split_str(item_str, seq):
    return [s for s in item_str.split(seq) if s != '']


# 分割字符串，字符串格式为"1,a|2,b|3,c"，分割后格式为：{{1,a},{2,b},{3,c}}
def lua_split_items(item_str):
    item_str = str(item_str)
    if item_str.strip() == "":
        return "{}"
    else:
        s = "}, {".join([s for s in item_str.split("|") if s != ''])
        if s == '':
          return "{}"
        else:
          return "{{" + s + "}}"


def lua_split_str_table(_str,seq):
    st = str(_str)
    if st.strip() == "":
        return "{}"
    else:
        s = "','".join([s for s in st.split(seq) if s != ''])
        if s == '':
            return "{}"
        else:
            return "{'"+ s + "'}"

#时间转换 将格式 hh:mm:ss 转成{hour=hh,min=mm,sec=ss}
def lua_split_time(time_str):
    if time_str.strip() == "":
        return "{hour=0,min=0,sec=0}"
    else:
        tmp=list(map(int, time_str.split(':')))
        str="hour={0[0]},min={0[1]},sec={0[2]}"
        return '{'+str.format(tmp)+'}'


#时间转换 将格式 hh:mm:ss 转成秒数
def lua_split_time_sec(time_str):
    if time_str.strip() == "":
        return 0
    else:
        tmp=list(map(int, time_str.split(':')))
        return tmp[0] * 3600 + tmp[1] * 60 + tmp[2]


def is_str_num(s):
   try:
        # 这里有一个坑，int('30_1') = 301，下划线被忽略了
        if '_' in s:
            return False
        elif '+' in s:
        	return False
        elif '.' in s:
            return type(float(s)) == type(0.1)
        return type(int(s)) == type(0)
   except:
        return False

# 形如x,x,x格式得字符串中，如果x为字符串，则加引号，为数字则不加
# 如：1,abc,ddd 则返回：1,"abc","ddd"
# 如：1.1,abc,ddd 则返回：1.1,"abc","ddd"
def add_quote_2_alpha_str(s, force=False):
    temp = s.split(',')
    if force:
        return ",".join([ '"' + t + '"' for t in temp])
    else:
        return ",".join([ '"' + t + '"' if not is_str_num(t) else t for t in temp])


# 分割字符串，字符串格式为"1,a|2,b|3,c"，分割后格式为：{{1,'a'},{2,'b'},{3,'c'}}
def lua_split_str_items(item_str):
    item_str = str(item_str)
    if item_str.strip() == "":
        return "{}"
    else:
        s = "}, {".join([add_quote_2_alpha_str(s) for s in item_str.split("|") if s != ''])
        if s == '':
          return "{}"
        else:
          return "{{" + s + "}}"
          
def py_split_str_items(item_str):
    item_str = str(item_str)
    if item_str.strip() == "":
        return []
    else:
        s = "], [".join([add_quote_2_alpha_str(s) for s in item_str.split("|") if s != ''])
        if s == '':
            return []
        else:
            return eval("[["+s+"]]")


# 分割属性字符串，字符串格式为"1,a|2,b|3,c"，分割后格式为：{[1]=a,[2]=b,[3]=c}
# 这个与lua_split_items的不同在于返回值格式不同
def lua_split_attrs(attr_str):
    if attr_str.strip() == "":
        return "{}"
    else:
        return "{" + ", ".join(['[' + item.replace(',', '] = ') for item in attr_str.split("|")]) + "}"


# 将形如:ss,aa,egefd的字符串变成："ss","aa","egefd"
def add_quote_2_str_items(s):
	if s == "":
		return "{}"

	temp = s.split(',')
	t = map(lambda x: "\"%s\"" % x, temp)
	return "{" + ", ".join(t) + "}"


'''python列表转为lua的table，如:[1,2,3] --> {1,2,3}'''
def list_2_lua_table(item_list):
    return "{" + ", ".join([str(item) for item in item_list]) + "}"


# 将字符串中的单引号加上反斜杠
def modify_backslash_str(s):
    if '\'' in s:
        s = s.replace('\'', '\\\'')
        return s
    else:
        return s


'''
当想根据一个字段获取其相同类型的值的数组，比如
id  type
1    10
2    10
3    12
4    12
想生成如下类型的数据：
local type_2_ids = {
    [10] = {1,2},
    [12] = {3,4},
}
index_field：根据哪个字段名来索引(对应上面的'type')
index_result：获取哪个字段名的值(对应上面的'id')
返回一个字典:{index_field对应的值 = [index_result对应的值]}
'''
def select_one_field(datas, index_field, index_result):
   ret_list = {}
   for data in datas:
       if data[index_field] in ret_list:
           ret_list[data[index_field]].append(data[index_result])
       else:
           ret_list[data[index_field]] = [data[index_result]]
   return ret_list


# 类似于select_one_field，不过值是有多个字段的
# return:{index_field对应的值: [[result_val1, result_val2]]}
def select_one_2_n_field(datas, index_field, index_results):
   ret_list = {}
   for data in datas:
       result = [data[i] for i in index_results]
       if data[index_field] in ret_list:
           ret_list[data[index_field]].append(result)
       else:
           ret_list[data[index_field]] = [result]
   return ret_list



# 将python的tuple_list转为lua中的表，如：[(1,a),(2,b)] ---> {{1,a},{2,b}}
def py_tuple_list_2_lua(tuple_list):
    lua_list = [list_2_lua_table(t) for t in tuple_list]
    return "{" + ", ".join(lua_list) + "}"


# 讲属性字符串转为属性id
def format_attrs(s):
    attr_dict = attr_transform.get_attr_dict()
    l = s.split("|")
    ret = []
    for v in s.split("|"):
        attr_name,attr_val = v.split(',')
        ret.append("%d,%s" % (attr_dict[attr_name], attr_val))
    return lua_split_attrs("|".join(ret))

def format_attr_id(s):
    attr_dict = attr_transform.get_attr_dict()
    return int(attr_dict[s])

    
'''
当想根据一个字段获取其相同类型的值的数组，比如
id  type   ad
1    10    1
2    10    2
3    12    1
4    12    2
想生成如下类型的数据：
local type_2_ids = {
    [10] = {[1] = {1}, [2] = {2}},
    [12] = {[1] = {3}, [2] = {4}},
}
index_field：根据哪个字段名来索引(对应上面的'type')
index_result：获取哪个字段名的值(对应上面的'id')
返回一个字典:{index_field对应的值 = [index_result对应的值]}
'''
def group_by_one_fields(datas, index1):
   ret_list = {}
   for data in datas:
        if not data[index1] in ret_list:
            ret_list[data[index1]] = [data]
        else:
            ret_list[data[index1]].append(data)
   return ret_list

def group_by_tow_fields(datas, index1, index2):
   ret_list = {}
   for data in datas:
        if not data[index1] in ret_list:
            ret_list[data[index1]] = {}
        if data[index2] in ret_list[data[index1]]:
            ret_list[data[index1]][data[index2]].append(data)
        else:
            ret_list[data[index1]][data[index2]]=[data]
   return ret_list

def group_by_three_fields(datas, index1, index2, index3):
   ret_list = {}
   for data in datas:
        if not data[index1] in ret_list:
            ret_list[data[index1]] = {}
        if not data[index2] in ret_list[data[index1]]:
            ret_list[data[index1]][data[index2]] = {}
        if data[index3] in ret_list[data[index1]][data[index2]]:
            ret_list[data[index1]][data[index2]][data[index3]].append(data)
        else:
            ret_list[data[index1]][data[index2]][data[index3]] = [data]
   return ret_list
   
def array_split_items(item_str):
    if item_str.strip() == "":
        return []
    else:
        s = [s for s in item_str.split("|") if s != '']
        ret_list = []
        for t in s:
            if is_str_num(t):
                ret_list.append([int(t)])
            else:
                ret_i = t.split(",")
                if len(ret_i) == 2:
                    ret_list.append([int(ret_i[0]), int(ret_i[1])])
                elif len(ret_i) == 3:
                    ret_list.append([int(ret_i[0]), int(ret_i[1]), int(ret_i[2])])
        return ret_list
     
def get_value(str):
    if str == "":
        return 0
    else:
        return str

def make_lua_table(tab):
    return LuaMaker.makeLuaTable(tab)

# 20|20|60 这种格式转化成概率 {0.2,0.2,0.6}
def lua_trans_weight(input):
    weight_int = [int(s) for s in input.split("|") if s != '']
    sum_num = sum([x for x in weight_int])
    weight_float = [str(round(x / sum_num, 4)) for x in weight_int]  
    return "{" + ", ".join(weight_float) + "}"

# 20,123|20,456|60,789 这种格式转化成概率 {{0.2, 123},{0.2, 456},{0.6,789}}
# index按python习惯, 设置为0, 1, 2, 3...
def lua_trans_weighta_array_index(input, index):
    weight_1 = [s for s in input.split("|") if s != '']
    weight_2 = [(s.split(",")) for s in weight_1]
    weight_3 = [int(x[index]) for x in weight_2]
    sum_num = sum([x for x in weight_3])
    weight_4 = [str(round(x / sum_num, 4)) for x in weight_3]  
    weight_5 = []
    for i in range(0, len(weight_2)):
        weight_2[i][index] = weight_4[i]
    weight_5 = ["{" + ", ".join(x) + "}" for x in weight_2]
    return "{" + ", ".join(weight_5) + "}"
      
# 前端多语言使用，需要使用as_escaped处理引号转义
# 例：${as_escaped(helper.client_language(data['tips']))}
def client_language(key):
    if key == "":
        return "''"
    else:
        return "LanguageMgr:GetConfigLanguage('"+key+"')"
    
class LuaMaker:
    """
    lua 处理器
    """

    @staticmethod
    def makeLuaTable(table):
        """
        table 转换为 lua table 字符串
        """
        _tableMask = {}
        _keyMask = {}
        def analysisTable(_table, _indent, _parent):
            if isinstance(_table, tuple):
                _table = list(_table)
            if isinstance(_table, list):
                _table = dict(zip(range(1, len(_table) + 1), _table))
            if isinstance(_table, dict):

                """if id(_table) in _tableMask:
                    print("error: LuaMaker.makeLuaTable() 成环: this = "+ _parent + "  oldP = " + _tableMask[id(_table)])
                    return
"""
                _tableMask[id(_table)] = _parent
                cell = []
                thisIndent = _indent + "    "
                for k in _table:
                    if not (isinstance(k, str) or isinstance(k, int) or isinstance(k, float)):
                        print("error: LuaMaker.makeLuaTable() key类型错误: parent = "+ _parent + "  key = " + k)
                        return
                    key = isinstance(k, int) and "[" + str(k) + "]" or "[\"" + str(k) + "\"]"
                    if _parent + key in _keyMask:
                        print("error: LuaMaker.makeLuaTable() 重复key: key = "+ _parent + key)
                        return
                    _keyMask[_parent + key] = True

                    var = None
                    v = _table[k]
                    if isinstance(v, str):
                        var = "\"" + v + "\""
                    elif isinstance(v, bool):
                        var = v and "true" or "false"
                    elif isinstance(v, int) or isinstance(v, float):
                        var = str(v)
                    else:
                        var = analysisTable(v, thisIndent, _parent + key)
                    cell.append(thisIndent + key + " = " + var)
                lineJoin = ",\n"
                return "{\n" + lineJoin.join(cell) + "\n" + _indent +"}"

            else:
                print("error: LuaMaker.makeLuaTable() table类型错误: "+ _parent)

        return analysisTable(table, "", "root")


def transform_build_size(s):
    t = eval(py_split_items(s))
    print(t)
    ret = []
    for d in t:
        if d[0] % 2 == 1:
            ret.append((d[0], d[1] + 1))
        else:
            ret.append((d[0], d[1]))
    return py_tuple_list_2_lua(ret)


def transform_build_size_with_xy(s):
    t = eval(py_split_items(s))
    ret = []
    for d in t:
        if d[0] % 2 == 1:
            ret.append(("x=" + str(d[0]), "y=" + str(d[1] + 1)))
        else:
            ret.append(("x=" + str(d[0]), "y=" + str(d[1])))
    return py_tuple_list_2_lua(ret)        
