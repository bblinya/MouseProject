import os
import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))+'/../'))
from crawler import web, index

import json
from lxml import html


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

def hit_edu_cn(json_path:str, save_path:str):
    f = open(json_path)
    dict_data = json.load(f)
    f.close()
    
    print(dict_data)

    # cache for url (static/dynamic)
    # json_path
    cache = web._temp_path('/Users/linya/Desktop/MouseProject/python/contents')
    if os.path.exists(cache):
        with open(cache, "r") as f:
            f.read()
            
    df = open(cache, "wb")
    
    '''attr dict settings for hit'''
    root_path = ["//div[@id='teacher_info']", 
            "//li[@class='con_parts']",
            "//div[@class='col-r']",]
    info = ['.', 
            '.',
        './div[@class="cont"]']
    
    base_url = ''

    for idx, idx_dict in enumerate(dict_data):
        base_url = idx_dict['base'].rsplit('/', 1)[0]
        base_url = os.path.join(base_url, idx_dict['link'])
        print('idx ', idx, ', name ', idx_dict['name'])
        
        name = idx_dict['name']
        faculty = idx_dict['faculty']
        
        encode_dict = json.dumps(idx_dict, ensure_ascii=False).encode('utf-8')
        data_path = os.path.join(save_path, 'data', '哈尔滨工业大学', faculty)
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
            data = index.apply_pattern(**attrs)
            print('len data ', len(data))
            len_data = len(data)
            for i in range(len_data):
                html_df.write(data[i]['info'])

        
hit_edu_cn(json_path='/Users/linya/Desktop/MouseProject/sources/index/hit.edu.cn',
           save_path='/Users/linya/Desktop/MouseProject/python')