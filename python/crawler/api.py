import os
import json
import string
import logging
from os import path
from hashlib import sha1
from functools import wraps

from . import index, utils, web

def _sicau_single(url: str):
    data = index.xpath_select(
        url_or_path=url,
        root_pat="//div[@class='ming']/a",
        pat_dict={ "link": "./@href", "name": ".//text()" })
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//tr/td[descendant::a]",
        pat_dict={
            "link": ".//a/@href",
            "name": ".//text()" })
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@class='decoration']",
        allow_empty=True,
        pat_dict={
            "link": "./div[last()]/a/@href",
            "name": "./div[1]/span//text()",
            })
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@id='vsb_content']//p//a//*[string-length(text()) > 0]",
        pat_dict={ "link": "./parent::a/@href", "name": ".//text()" }
        )
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@class='teacher-name']/a",
        pat_dict={ "link": "./@href", "name": "./text()" }
        )
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@class='sz_tit']/a[@href]",
        pat_dict={ "link": "./@href", "name": "./text()" }
        )
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@class='teacher']/a[@href]",
        pat_dict={
          "link": "./@href",
          "name": "./div[@class='teacher-name']//text()" }
        )
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@class='teacher_list']//ul/li/a",
        pat_dict={ "link": "./@href", "name": ".//text()" }
        )
    data = [d for d in data if d["link"]]
    assert data
    return data

@utils.index_cache
def sicau_edu_cn():
    """ crawler for si chuan university"""
    l = logging.getLogger("sicau")

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
        _f = utils.index_cache(
            _sicau_single,
            fname=utils.temp_file(d), cache=False)
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

@utils.index_cache
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
        _f = utils.index_cache(
                _hit_edu_cn_single,
                utils.temp_file("hit" + c))
        out = _f(base_url)
        out = [{"base": base_url, **v} for v in out]
        data.extend(out)

    for c in string.ascii_uppercase:
        os.remove(utils.temp_file("hit" + c))
    return data

