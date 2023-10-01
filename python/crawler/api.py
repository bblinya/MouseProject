import json
import string
import logging
from os import path
from functools import wraps

from . import index, utils, web

@utils.cache_json_file("sources/index/ahu.faculties.json")
def _ahu_edu_cn_faculties():
    seed = "sources/index/ahu.edu.cn.html"
    attrs = {
        "url_or_path": path.join(utils.ROOT, seed),
        "root_pat": "//div[@class='policy_department1_box']/dl/dt",
        "pat_dict": {
            "link": "./a/@href",
            "faculty": "./a/text()",
            },
        }
    return index.apply_pattern(**attrs)

def ahu_edu_cn():
    """ crawler for ahu(anhui university) """
    data = _ahu_edu_cn_faculties()
    print(data)
    for d in data:
        if d["link"] is None:
            continue


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
    return index.apply_pattern(**attrs)

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

