headerd:dict = {}
headerl:list = []
process:list[list[str]] = []

def dict_reader(content:bytes):
    global headerd
    global headerl
    global process
    headerd.clear()
    headerl.clear()
    process.clear()
    # 初始化
    # 将字节序列转为字符串
    str_content:str = content.decode('UTF-8')
    # 去除回车符
    str_content = str_content.replace('\r', '')
    if str_content[len(str_content)-1] == '\n':
        str_content = str_content[:len(str_content)-1]
    # 按顺序获得headers
    rows = str_content.split('\n')
    _header = rows[0].split(',')
    for _ in _header:
        headerl.append(_)
    _cnt = 0
    for _ in _header:
        headerd[_] = _cnt
        _cnt += 1
    for row in rows[1:]:
        process.append(row.split(','))

def wash_data(semantic:dict, strategy:str, id_index:int, lb:int, lu:int, ub:int, uu:int):
    """
    strategy = {'bing', 'jiao', 'last'}
    """
    global process
    #将唯一标识那一列小写转大写
    for line in process:
        line[id_index] = line[id_index].upper()

    tmp_id_dict:dict = {}
    new_process:list = []
    semantic_process:list = []
    finally_process:list = []

    new_id_index = id_index - lb
    id_end = lu-lb+1
    gw_end = uu-ub+1

    for line in process:
        new_process.append([line[lb:lu+1], line[ub:uu+1]])

    for case in new_process:
        semantic_process.append([case[0], [semantic[i] for i in case[1]]])
    #print(semantic_process)
    new_process.clear()


    # 开始去重
    for case in semantic_process:
        if case[0][new_id_index] not in tmp_id_dict:
            finally_process.append(case)
            tmp_id_dict[case[0][new_id_index]] = len(finally_process)-1
            #print(tmp_id_dict)
        else:
            info = finally_process[tmp_id_dict[case[0][new_id_index]]]
            #print(info)
            for i in range(id_end):
                if i != new_id_index:
                    # print(i)
                    if case[0][i] != info[0][i] and info[0][i].count('【?】') == 0:
                        info[0][i] = '【?】'+case[0][i]
            
            if strategy == 'last':
                info[1] = case[1]
            elif strategy == 'bing':
                info[1] = [info[1][i] or case[1][i] for i in range(id_end)]
            elif strategy == 'jiao':
                info[1] = [info[1][i] and case[1][i] for i in range(id_end)]
            
            finally_process[tmp_id_dict[case[0][new_id_index]]] = info
        
    semantic_process.clear()
    process = finally_process
    # for line in process:
    #     print(line)

    

                    






