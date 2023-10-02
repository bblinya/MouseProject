import json
import time
import string
import logging
from os import path
from functools import wraps

from . import index, utils, web

@utils.cache_json_file
def pku_edu_cn_faculties():
    seed = "https://www.pku.edu.cn/department.html"
    attrs = {
        "url_or_path": seed,
        "root_pat": "//div[@class='p links']//a",
        "pat_dict": {
            "link": "./@href",
            "faculty": "./text()",
            }
        }
    return index.xpath_select(**attrs)

def _pku_faculty(url):
    opts = [
        '教师', '教职员工',
        '师资', '学术团队', '科研人员',
        '导师名单', '研究队伍',
        '人员队伍']
    root_pat = "//*[{}]".format(" or ".join([
        "contains(text(), '{}')".format(d) for d in opts
        ]))
    attrs = {
        "url_or_path": url,
        "root_pat": root_pat + "/ancestor-or-self::a",
        "pat_dict": { "link": "./@href", "text": ".//text()" },
        }
    data = index.xpath_select(**attrs)
    data = [d for d in data if "void(0)" not in d["text"]]
    data = [d for d in data if len(d["text"]) < 5]
    return data

def pku_edu_cn():
    """ crawler for pku(peking university) """
    data = pku_edu_cn_faculties()
    for i, d in enumerate(data):
        if d["faculty"] == "信息管理系":
            d["teachers"] = [{
                "link": "http://www.im.pku.edu.cn/szll/syry/index.htm",
                "text": "",
                }]
            continue
        elif "医院" in d["faculty"]:
            continue
        elif "医学" in d["faculty"]:
            continue
        elif "北京国际数学研究中心" in d["faculty"]:
            d["link"] = path.join(d["link"], "cn/")
        out = _pku_faculty(d["link"])
        link_title = index.title(d["link"])[0]
        if link_title.isascii(): # pure english
            d["teachers"] = None
            print(d["link"], "is english title, skip")
            continue
        assert len(out) > 0
        d["teachers"] = out

# data/学校/院系/姓名.html
# data/index.txt
# 清华，计算机系，登俊晖

def _hit_edu_cn_single(url: str):
    attrs = {
        "url_or_path": url,
        "root_pat": "//ul[@id='letterNum']/li/div/a",
        "pat_dict": {
            "link": "./@href",
            "name": "./div/h3/text()",
            "image": "./div/img/@src",
            "faculty": "./div/p[@class='p1']/text()",
        },
        "dyn_type": "Chrome",
    }
    return index.xpath_select(**attrs)

def hit_edu_cn():
    """ crawler for hit school """
    pat = "http://homepage.hit.edu.cn/search-teacher-by-phoneticize?letter={}"

    out_path = "sources/index/hit.edu.cn"
    data = utils.read_json(out_path) or []
    base_urls = set([d["base"] for d in data])

    l = logging.getLogger("hit.edu.cn")
    for c in string.ascii_uppercase:
        base_url = pat.format(c)
        if base_url in base_url:
            l.info("skip hit source: %s" % base_url)
            continue
        if base_url not in base_urls:
            l.info("process hit source: %s" % base_url)
            d = _hit_edu_cn_single(base_url)
            d = [{"base": base_url, **v} for v in d]
            data.extend(d)

            with open(out_path, "w") as f:
                json.dump(data, f,
                          indent=2, ensure_ascii=False)

