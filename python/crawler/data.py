import os
import sys
from . import web, index, utils

import json
from lxml import html
import logging
import numpy as np
import time

logger = logging.getLogger('data')

def html_target(v):
  return html.tostring(v, encoding='utf-8')


def create_path(data_path:str):
    if(os.path.exists(data_path)):
        pass
    else:
        os.makedirs(data_path)

def create_html(data_path:str, name:str):
    name_path = os.path.join(data_path, name+'.html')
    if(os.path.isfile(name_path)):
        os.remove(name_path)
    f = open(name_path, 'wb')
    return f

# check same name in same school
def check_name_in_school(dict_data: dict):
    school_name = {}
    for sin_dict in dict_data:
        keys_dict = list(school_name.keys())
        faculty = sin_dict['faculty']
        name = sin_dict['name']
        if(len(keys_dict) == 0):
            school_name[faculty] = [name]
        elif(faculty in keys_dict):
            school_name[faculty].append(name)
        else:
            school_name[faculty] = [name]

    modify_dict = {}
    repeat_exist = False
    for key, value in school_name.items():
        unique_value = list(set(value))
        if(len(unique_value) == len(value)):
            repeat_exist = True
        else:
            modify_dict[key] = []
            array_value = np.array(value)
            for name in unique_value:
                indexes = np.where(array_value == name)[0]
                if(indexes.shape[0]>1):
                    modify_dict[key].append(name)
                    modify_dict[key].append(indexes.shape[0])
                    # count
                    modify_dict[key].append(1)
    
    for idx, sin_dict in enumerate(dict_data):
        modify_keys = list(modify_dict.keys())
        faculty = sin_dict['faculty']
        name = sin_dict['name']
        if(faculty in modify_keys and (name in modify_dict[faculty])):
            # print('facult ', faculty, ', name ', name)
            count = modify_dict[faculty][2]
            sin_dict['name'] = name+str(count)
            modify_dict[faculty][2] = modify_dict[faculty][2] + 1
            dict_data[idx] = sin_dict
            # print(sin_dict)
    return dict_data, repeat_exist

# 哈尔滨工业大学
def hit_edu_cn(save_path:str):
    logger.info('hit_edu_cn_data')
    json_path = '/Users/linya/Desktop/MouseProject/sources/index/hit_edu_cn.json'
    f = open(json_path)
    dict_data = json.load(f)
    f.close()
    
    # print(dict_data)
    
    '''attr dict settings for hit'''
    root_path = ["//div[@id='teacher_info']", 
            "//li[@class='con_parts']",
            "//div[@class='col-r']",]
    info = ['.', 
            '.',
        './div[@class="cont"]']
    
    base_url = ''
    index_list = []
    for idx, idx_dict in enumerate(dict_data):
        base_url = idx_dict['base'].rsplit('/', 1)[0]
        base_url = os.path.join(base_url, idx_dict['link'])
        print('idx ', idx, ', name ', idx_dict['name'])
        
        name = idx_dict['name']
        faculty = idx_dict['faculty']
        
        index_str = '哈尔滨工业大学,'+faculty+','+name
        index_list.append(index_str)
        
        encode_dict = json.dumps(idx_dict, ensure_ascii=False).encode('utf-8')
        data_path = os.path.join(save_path, '哈尔滨工业大学', faculty)
        create_path(data_path=data_path)
        html_df = create_html(data_path=data_path, name=name)
        html_df.write(encode_dict)

        for root_pat, pat_info in zip(root_path, info):
            attrs = {
            "url_or_path":base_url,
            "root_pat":root_pat,
            "pat_dict":{
            "info":pat_info,
            },
            "target_process":html_target,
            "dyn_type": "Chrome",
            }
            data = index.xpath_select(**attrs)
            # print('len data ', len(data))
            len_data = len(data)
            for i in range(len_data):
                html_df.write(data[i]['info'] or b"")

    # check path of index
    index_for_read = os.path.join(save_path, 'index.txt')
    if(os.path.isfile(index_for_read)):
        index_df = open(index_for_read, 'r')
    else:
        index_df = open(index_for_read, 'w')
    
    for index_str in index_list:
        index_df.write(index_str)
        index_df.write('\n')
    

# 四川农业大学
def sicau_edu_cn(save_path:str):
    logger.info('sicau_edu_cn')
    json_path = '/Users/linya/Desktop/MouseProject/sources/index/sicau_edu_cn.json'
    f = open(json_path)
    dict_data = json.load(f)
    f.close()
    
    # return modified dict
    dict_data, repeat_exist = check_name_in_school(dict_data)
    if(repeat_exist):
        print('same name exists in same school')
    else:
        print('no same name in same school')


    '''attr dict settings for sicau'''
    root_path = ["//div[@class='Section0']",
                 "//div[@class='v_news_content']",
                 "//body"]
    info = ['.', '.', '.']
    
    base_url = ''
    index_list = []
    count = 0
    for idx, idx_dict in enumerate(dict_data):
        count = idx+1
        count_zero = 0
        count_nonzero = 0
        stop_state = False
        try:
            base_url = idx_dict['link']
            print('idx ', idx, ', name ', idx_dict['name'])
        except Exception:
            print('idx ', idx, ', name ', idx_dict['name'])
            continue
        
        name = idx_dict['name']
        faculty = idx_dict['faculty']
        index_str = '四川农业大学,'+faculty+','+name
        index_list.append(index_str)
        encode_dict = json.dumps(idx_dict, ensure_ascii=False).encode('utf-8')
        data_path = os.path.join(save_path, '四川农业大学', faculty)
        create_path(data_path=data_path)
        html_df = create_html(data_path=data_path, name=name)
        html_df.write(encode_dict)


        for root_pat, pat_info in zip(root_path, info):
            attrs = {
            "url_or_path":base_url,
            "root_pat":root_pat,
            "pat_dict":{
            "info":pat_info,
            },
            "target_process":html_target,
            "dyn_type": "Chrome",
            }
            # print('base url ', base_url)
            data = index.xpath_select(**attrs)
            print('len data ', len(data))
            len_data = len(data)
            if(len_data == 0):
                count_zero += 1
            else:
                count_nonzero += 1
                if(count_nonzero == 1):
                    print('root pat ', root_pat)
                    if((root_pat == "//div[@class='v_news_content']") and (len_data>1)):
                        html_df.write(data[0]['info'] or b"")
                    else:
                        for i in range(len_data):
                            html_df.write(data[i]['info'] or b"")
                else:
                    pass
            if(count_zero == len(root_path)):
                stop_state = True
                break
            
        if(stop_state):
            break
        
    # # check path of index
    # index_for_read = os.path.join(save_path, 'index.txt')
    # if(os.path.isfile(index_for_read)):
    #     index_df = open(index_for_read, 'a')
    # else:
    #     index_df = open(index_for_read, 'w')
    
    # for index_str in index_list:
    #     index_df.write(index_str)
    #     index_df.write('\n')
        
    # print('num in sicau ', count)
    
# 北京工业大学
def bjut_edu_cn(save_path:str):
    logger.info('bjut_edu_cn')
    json_path = '/Users/linya/Desktop/MouseProject/sources/index/bjut_edu_cn.json'
    f = open(json_path)
    dict_data = json.load(f)
    f.close()
    
    # return modified dict
    dict_data, repeat_exist = check_name_in_school(dict_data)
    if(repeat_exist):
        print('no same name in same school')
    else:
        print('same name exists in same school')
    
    '''attr dict settings for bjut'''
    root_path = ["//div[@class='kcbj']",
                "//div[@class='ny_right_con']//div[@class='dpzw']",
                "//div[@class='v_news_content']",
                 ]
    info = ['./div[@class="kc_nr"]', '.', '.']
    
    base_url = ''
    index_list = []
    count = 0
    for idx, idx_dict in enumerate(dict_data):
        count = idx+1
        count_zero = 0
        count_nonzero = 0
        stop_state = False
        try:
            base_url = idx_dict['link']
            print('idx ', idx, ', name ', idx_dict['name'])
        except Exception:
            # [":link"] means: wrong link
            print('idx ', idx, ', name ', idx_dict['name'])
            continue
        
        
        name = idx_dict['name']
        faculty = idx_dict['faculty']
        index_str = '北京工业大学,'+faculty+','+name
        index_list.append(index_str)
        encode_dict = json.dumps(idx_dict, ensure_ascii=False).encode('utf-8')
        data_path = os.path.join(save_path, '北京工业大学', faculty)
        create_path(data_path=data_path)
        html_df = create_html(data_path=data_path, name=name)
        html_df.write(encode_dict)
        

        for root_pat, pat_info in zip(root_path, info):
            attrs = {
            "url_or_path":base_url,
            "root_pat":root_pat,
            "pat_dict":{
            "info":pat_info,
            },
            "target_process":html_target,
            # "dyn_type": "Chrome",
            }
            data = index.xpath_select(**attrs)            
            print('len data ', len(data))
            len_data = len(data)
            if(len_data == 0):
                count_zero += 1
            else:
                count_nonzero += 1
                if(count_nonzero == 1):
                    print('root pat ', root_pat == "//div[@class='v_news_content']")
                    if((root_pat == "//div[@class='v_news_content']") and (len_data>1)):
                        html_df.write(data[0]['info'] or b"")
                    else:
                        for i in range(len_data):
                            html_df.write(data[i]['info'] or b"")
                else:
                    pass
            if(count_zero == len(root_path)):
                stop_state = True
                break
            

        if(stop_state):
            break
    
    
    # check path of index
    index_for_read = os.path.join(save_path, '北京工业大学', 'index.txt')
    index_df = open(index_for_read, 'w')
    
    for index_str in index_list:
        index_df.write(index_str)
        index_df.write('\n')
        
    print('num in sicau ', count)

    
    
