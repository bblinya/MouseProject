import os
import sys
from . import web, index, utils

import json
from lxml import html
import logging

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
    f = open(name_path, 'wb')
    return f

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
                html_df.write(data[i]['info'])

    # check path of index
    index_for_read = os.path.join(save_path, 'index.txt')
    if(os.path.isfile(index_for_read)):
        index_df = open(index_for_read, 'r')
    else:
        index_df = open(index_for_read, 'w')
    
    for index_str in index_list:
        index_df.write(index_str)
        index_df.write('\n')
    
    
        
# hit_edu_cn_data(json_path='/Users/linya/Desktop/MouseProject/sources/index/hit_edu_cn.json',
#            save_path='/Users/linya/Desktop/MouseProject/python')