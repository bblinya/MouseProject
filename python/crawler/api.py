import json
import string
from os import path
from functools import wraps

from . import index, utils

def _hit_edu_cn_single(url: str):
    attrs = {
        "url": url,
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

    for c in string.ascii_uppercase:
        base_url = pat.format(c)
        print("process hit source: {}".format(base_url))
        if base_url not in base_urls:
            d = _hit_edu_cn_single(base_url)
            d = [{"base": base_url, **v} for v in d]
            print(d)
            data.extend(d)

            with open(out_path, "w") as f:
                json.dump(data, f,
                          indent=2, ensure_ascii=False)


