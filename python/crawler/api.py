import os
import json
import string
import logging
from os import path
from hashlib import sha1
from functools import wraps

from . import index, utils, web

def _sicau_single(url: str):
    if "szdw/yjsds.htm" in url:
        return index.xpath_select(
                url_or_path=url,
                root_pat="//tr/td/p/a",
                pat_dict={
                    "link": "./@href",
                    "name": "./text()",
                    })
    return index.xpath_select(
            url_or_path=url,
            root_pat="//div[@class='ming']/a",
            pat_dict={
                "link": "./@href",
                "name": "./text()",
                })

@utils.cache_json_file
def sicau_edu_cn():
    """ crawler for si chuan university"""
    l = logging.getLogger("sicau.edu.cn")

    seed = path.join(utils.ROOT, "sources/index/sicau.txt")
    data = utils.read_seed(seed)

    faculty = None
    outs, fails = [], []
    for d in data:
        if "学院" in d:
            faculty, link = d.split("：")
            l.info("process faculty: {}".format(faculty))
            if len(link) == 0:
                continue

        tag, link = d.split("：")
        l.info("tag {} {}".format(tag, link))
        _f = utils.cache_json_file(
            _sicau_single, utils.temp_file(d))
        out = _f(link)
        assert out
        out = [{"base": link, **v} for v in out]
        outs.extend(out)

    for i, _ in enumerate(data):
        os.remove(utils.temp_file(d))
    return outs


def pku_edu_cn():
    """ crawler for pku(peking university), nouse """
    pass

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

@utils.cache_json_file
def hit_edu_cn():
    """ crawler for hit school """
    pat = "http://homepage.hit.edu.cn/search-teacher-by-phoneticize?letter={}"

    l = logging.getLogger("hit.edu.cn")
    data = []
    for c in string.ascii_uppercase:
        base_url = pat.format(c)
        tmp_path = "hit.{}.json".format(c)
        l.info("process {} into {}".format(
            base_url, tmp_path))
        _f = utils.cache_json_file(
                _hit_edu_cn_single,
                utils.temp_file("hit" + c))
        out = _f(base_url)
        out = [{"base": base_url, **v} for v in out]
        data.extend(out)

    for c in string.ascii_uppercase:
        os.remove(utils.temp_file("hit" + c))
    return data

