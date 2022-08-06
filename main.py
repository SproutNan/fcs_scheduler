import json
import mycsv
import time

from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import set_env, info as session_info

text_st_mutiple = ['以其最后一次报名情况为准', '取其所有报名情况的并集', '取其所有报名情况的交集']
text_torf = ['有空', '没空']
title_normal = "提示（阅读后即可关闭）"
title_result = "结果（阅读后即可关闭）"

class gw_item:
    index:int
    yk_users:list[str] #有空对象的字符串表
    upper:int #人数上限
    fp_users:list[str] #分配到此岗位的对象字符串表

    def __init__(self) -> None:
        self.index = 0
        self.yk_users = []
        self.upper = 0
        self.fp_users = []

    def __repr__(self) -> str:
        return str([self.index, self.yk_users, self.upper, self.fp_users])

class id_item:
    ident:str #唯一标识名
    yk_gws:list[int] #有空的岗位序号
    upper:int #分配上限
    fp_gws:list[int] #分配给的岗位序号表

    def __init__(self) -> None:
        self.ident = ''
        self.yk_gws = []
        self.upper = 0
        self.fp_gws = []

    def __repr__(self) -> str:
        return str([self.ident, self.yk_gws, self.upper, self.fp_gws])

def get_id_item_by_name(id_list:list[id_item], name:str) -> int:
    for id in id_list:
        if id.ident == name:
            return id_list.index(id)
    return -1

def get_time() -> str:
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    return f'【{timestamp}】'

def main():
    put_markdown("""
    # 志愿服务活动排班工具 v0.1
    这个工具是用于大型活动同学填报之后负责同学来排班的自动化工具。

    说明：
    
    - 如果使用本工具进行排班操作，请确保个人信息区和岗位填报区是隔离的两段连续区间
    - 个人信息区：可包含姓名、学号、手机号等，对象唯一标识从这个区域产生
    - 可选时间段/可选岗位：值全部是二元的，是/否，如果出现多个值会导致弹窗要求辨明语义
    - 无关数据区：这些数据是与排班无关的，将被丢弃
    - 考虑到同学手误的原因，在清洗数据时，被指定为唯一标识的变量内容将被小写转大写，防止“pb20”和“PB20”混淆
    - 暂时不支持同一时间段多岗位的排班，将在后续更新中推出

    作者：

    - 计算机科学与技术学院 黄瑞轩

    FAQ：

    """)

    put_button('怎么把xlsx转成csv格式，又怎么把csv格式转回xlsx？', onclick=lambda:popup('问题解答', 'baidu.com'))
    put_button('为什么出现乱码？', onclick=lambda:popup('问题解答', '请保证上传的csv文件均是utf-8编码，并且用excel打开时也要用utf-8编码。\n如果是excel中出现乱码，可以尝试先用记事本打开，再另存为，此时在下方编码格式中选择“带BOM的UTF-8”即可。'))
    put_button('怎么把csv文档转成utf-8编码？', onclick=lambda:popup('问题解答', 'baidu.com'))
    put_button('怎么在excel中把文档以utf-8编码形式打开？', onclick=lambda:popup('问题解答', 'baidu.com'))
    put_button('怎么反馈bug或者提出建议？', onclick=lambda:popup('问题解答', '请邮件联系：sprout@mail.ustc.edu.cn'))

    put_markdown("测试数据下载地址：http://sprout.vip/fcs_scheduler/测试数据.csv")

    raw_csv = file_upload("上传收集表格（csv格式）", accept=".csv", help_text='如果您的数据是xlsx格式，可以在Excel中将其保存为csv格式。')
    if raw_csv is None:
        put_markdown(get_time() + "csv文件上传失败，刷新页面重试。")
        return None
    else:
        mycsv.dict_reader(raw_csv['content'])

    scroll_to(scope=None, position='bottom')
    put_markdown(get_time() + f'现在请划定个人信息区的范围。（闭区间，即区间两端的变量都会被认为是个人信息区）')

    # print(mycsv.headerl)
    id_start_index = select('请选择 个人信息区 起始变量', mycsv.headerl[:-1])
    id_start_index = mycsv.headerl.index(id_start_index)

    id_end_index = select('请选择 个人信息区 结束变量', mycsv.headerl[id_start_index:-1])
    id_end_index = mycsv.headerl.index(id_end_index)

    tmp_result = f'{get_time()}个人信息区编号为{id_start_index}~{id_end_index}，具体有：\n'
    for id in range(id_start_index, id_end_index+1):
        tmp_result += f'- `{mycsv.headerl[id]}`\n'
    put_markdown(tmp_result)

    put_markdown(get_time() + f'请选定一个数据名作为对象的唯一标识（如姓名、学号等），唯一标识相同的数据对象将被认为是同一个现实对象。')
    scroll_to(scope=None, position='bottom')

    id_item_index = select('请选择 唯一标识变量', mycsv.headerl[id_start_index:id_end_index+1])
    id_item_index = mycsv.headerl.index(id_item_index)

    put_markdown(f'{get_time()}你选择了{id_item_index}号变量（`{mycsv.headerl[id_item_index]}`）作为唯一标识。')

    # 个人信息区划定结束，下面开始划定可选时间段/可选岗位编号区

    put_markdown(get_time() + f'现在请划定可选时间段/可选岗位的范围。（闭区间，即区间两端的编号都会被认为是可选时间段/可选岗位）')
    scroll_to(scope=None, position='bottom')

    gw_start_index = select('请选择 可选时间段/可选岗位 起始变量', mycsv.headerl[id_end_index+1:-1])
    gw_start_index = mycsv.headerl.index(gw_start_index)

    gw_end_index = select('请选择 可选时间段/可选岗位 结束变量', mycsv.headerl[gw_start_index:])
    gw_end_index = mycsv.headerl.index(gw_end_index)

    tmp_result = f'\n{get_time()}可选时间段/可选岗位区编号为{gw_start_index}~{gw_end_index}，具体有：\n'
    for id in range(gw_start_index, gw_end_index+1):
        tmp_result += f'- `{mycsv.headerl[id]}`\n'
    put_markdown(tmp_result)

    # 可选时间段/可选岗位区域划定结束，下面开始数据清洗
    put_markdown(get_time() + f'现在请你选择一种策略，以处理同一个现实对象进行了多次报名的情况。')
    scroll_to(scope=None, position='bottom')
    strategy_mutiple = select('要如何处理多次报名的情况？', text_st_mutiple, help_text='一般而言以最后一次报名情况为准。')
    strategy_mutiple = text_st_mutiple.index(strategy_mutiple)
    put_markdown(f'\n{get_time()}对于多次报名的情况，你的策略是：`{text_st_mutiple[strategy_mutiple]}`')
    scroll_to(scope=None, position='bottom')

    # 先对有空岗位的语义做判断

    gw_semantic_dict = {}
    for line in mycsv.process:
        for i in range(gw_start_index, gw_end_index+1):
            if line[i] not in gw_semantic_dict:
                ans = select(f'语义未知：{line[i]}的语义未说明', text_torf)
                if ans == '有空':
                    gw_semantic_dict[line[i]] = True
                else:
                    gw_semantic_dict[line[i]] = False

    tmp_result = f'{get_time()}对于岗位的报名情况，【有空】的代名词有：'
    tmp_result2 = f'；【没空】的代名词有：'
    for j in gw_semantic_dict:
        if gw_semantic_dict[j]:
            tmp_result += f'【{j}】'
        else:
            tmp_result2 += f'【{j}】'

    tmp_result += tmp_result2
    put_markdown(tmp_result)
    scroll_to(scope=None, position='bottom')

    # 下面根据策略合并结果
    mycsv.wash_data(gw_semantic_dict, 'last', id_item_index, id_start_index, id_end_index, gw_start_index, gw_end_index)
    # print(mycsv.process)

    
    def check(p):
        if p <= 0:
            return '非法数值'

    def check2(p):
        if p < 0:
            return '非法数值'

    check_if_all_the_same = input('所有岗位的人数都一样吗？如果都一样，请输入这个人数上限；如果不都一样，请输入0，以进入更细的分配。', type=NUMBER, validate=check2)

    upper_max = 0
    upper_number = {}
    if check_if_all_the_same == 0:
        upper_number = input_group("设置各岗位人数上限", [
            input(f'{mycsv.headerl[i]}岗位的人数上限是？', name=f'{i-gw_start_index}', type=NUMBER, validate=check) for i in range(gw_start_index, gw_end_index+1)
        ])
        for y in upper_number:
            if upper_number[y] > upper_max:
                upper_max = upper_number[y]
    else:
        upper_max = check_if_all_the_same
        for i in range(gw_start_index, gw_end_index+1):
            upper_number[str(i-gw_start_index)] = check_if_all_the_same

    upper_fp = int(input('每个用户至多分配多少个岗位？', type=NUMBER, validate=check))
    put_markdown(f'{get_time()}每个用户至多分配{upper_fp}个岗位。')
    # 下面生成岗位表数据结构和对象表数据结构
    id_dict:dict = {}
    gw_list:list[gw_item] = []
    id_list:list[id_item] = []


    for i in range(gw_start_index, gw_end_index+1):
        gw_item_instance = gw_item()
        gw_item_instance.index = i-gw_start_index
        gw_item_instance.yk_users = []
        gw_item_instance.upper = upper_number[str(i-gw_start_index)]
        gw_item_instance.fp_users = []
        gw_list.append(gw_item_instance)

    for case in mycsv.process:
        
        if case[0][id_item_index-id_start_index] not in id_dict:
            id_item_instance = id_item()
            id_item_instance.ident = case[0][id_item_index-id_start_index]
            id_item_instance.upper = upper_fp
            for i in range(len(case[1])):
                if case[1][i]:
                    id_item_instance.yk_gws.append(i)
                    gw_list[i].yk_users.append(case[0][id_item_index-id_start_index])

            id_list.append(id_item_instance)
            id_dict[case[0][id_item_index-id_start_index]] = len(id_list)-1

        else:
            pass

    # 下面可以根据这两个数据结构来排班了
    # 第一步：粗排班，对所有的岗位列表，把所有人填进去，尽可能填满
    for gw in gw_list:
        for yk_person in gw.yk_users:
            if len(gw.fp_users) >= gw.upper:
                break #如果此岗位满了，则退出，进入下一岗位的分配
            id_item_index = get_id_item_by_name(id_list, yk_person)#从人员表中拿到人员信息的序号
            id_item_inst = id_list[id_item_index]#将序号转化为对象
            if len(id_item_inst.fp_gws) < id_item_inst.upper:#如果此人还可以分配，接下来将其添加到gw_fp表
                id_item_inst.fp_gws.append(gw_list.index(gw))
                gw.fp_users.append(id_item_inst.ident)

    # for gw in gw_list:
    #     print(gw.fp_users)

    #上面以后再做优化，下面假装已经弄好了
    put_markdown(f'{get_time()}排班结果如下：\n')
    output_table:list[list[str]] = []
    output_table_headers = ['岗位名称']
    for i in range(upper_max):
        output_table_headers.append(f'人员{i+1}')
    output_table.append(output_table_headers)
    for i in range(gw_start_index, gw_end_index+1):
        line = [mycsv.headerl[i]]
        line += gw_list[i-gw_start_index].fp_users
        output_table += [line]
    
    for line in output_table:
        while len(line) < len(output_table_headers):
            line.append('')
    # print(output_table)
    scroll_to(scope=None, position='bottom')

    # 生成可供下载的csv文件
    output_csv = ''
    for line in output_table:
        for i in range(upper_max):
            output_csv += line[i]
            if i == upper_max-1:
                output_csv += '\n'
            else:
                output_csv += ','

    put_file(f'{get_time()}排班结果.csv', bytes(output_csv, encoding='utf-8'))

    put_table(output_table)


        
    

    





if __name__ == '__main__':
    start_server(main, debug=True, port=7777)