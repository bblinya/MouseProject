import os, re
import json
import string
import logging
import urllib.parse
from os import path
from hashlib import sha1
from functools import wraps

from . import index, utils, web

def _bjut_single(faculty, tag, url):
    data = []
    div_classes = [
            'listR floatR w680',
            'ny_right_con',
            'zhy']
    div_classes = " or ".join([
        "@class='%s'" % s for s in div_classes])
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[{}]//ul/li/a".format(div_classes),
        pat_dict={ "link": "./@href", "name": "./text()" })
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@class='teacher-name']/a",
        pat_dict={ "link": "./@href", "name": "./text()" })
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@class='teacher_pic']/ul/a",
        pat_dict={
            "link": "./@href",
            "name": "./li/span/text()" })
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@id='vsb_content']/p/a",
        pat_dict={ "link": "./@href", "name": "./text()" })
    return data

@utils.index_cache
def bjut_edu_cn():
    return index.run_faculties("bjut", _bjut_single)

def _sicau_single(faculty, tag, url):
    data = index.xpath_select(
        url_or_path=url,
        root_pat="//div[@class='ming']/a",
        pat_dict={ "link": "./@href", "name": ".//text()"
        })
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@class='decoration']",
        allow_empty=True,
        pat_dict={
            "link": "./div[last()]/a/@href",
            "name": "./div[1]/span//text()",
            })
    root_pat = "//div[@id='vsb_content']//*[ancestor-or-self::a and {} > 0]"
    whitelist = [
            "spxy.sicau.edu.cn/szdw/js.htm",
            "rwy.sicau.edu.cn/index/xygk/szdw/qngg.htm",
            ]
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat=root_pat.format(index.xpath_str_len),
        allow_multi= any([w in url for w in whitelist]),
        pat_dict={
            "link": "./ancestor-or-self::a/@href",
            "name": "./ancestor-or-self::a//text()" })
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
        root_pat="//div[@class='teacher']/a",
        allow_empty=True,
        pat_dict={
          "link": "./@href",
          "name": "./div[@class='teacher-name']/span/text()"
        })
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@class='teacher_list']//ul/li/a",
        pat_dict={ "link": "./@href", "name": "./h1/text()" }
        )
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@id='fitslist']/dl/dt/a",
        pat_dict={ "link": "./@href", "name": "./text()" }
        ) # 9
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@class='ldtz']/ul/li/a",
        pat_dict={
            "link": "./@href",
            "name": "./div[@class='ldtz-info']/h3/text()" }
        ) # 10
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//li[contains(@id, 'line_u4')]/a",
        pat_dict={
            "link": "./@href",
            "name": "./div[@class='b_span']/text()" }
        )
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//li[contains(@id, 'line_u7')]/a",
        pat_dict={ "link": "./@href", "name": "./@title" }
        )
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[@class='main_conRCa']/ul/div/a",
        pat_dict={ "link": "./@href", "name": "./h3/text()" }
        )
    data = [d for d in data if d["name"]]
    outs = []
    blacklist = [
        '导师', 'http', '四川', '专家' ]
    for d in data:
        name = d["name"]
        if any([k in name for k in blacklist]):
            continue
        name = name.removeprefix("人文学院教师风采——")
        name = name.removesuffix("副教授")
        name = name.removesuffix("教授")
        name = name.removesuffix("讲师")
        d["name"] = name
        if len(name) == 0:
            continue
        assert len(name) > 0 and len(name) < 6, d
        d["link"] = urllib.parse.urljoin(url, d["link"])
        outs.append(d)
    data = outs
    assert data
    return data

@utils.index_cache
def sicau_edu_cn():
    """ crawler for si chuan university"""
    return index.run_faculties("sicau", _sicau_single)

def _pku_single(faculty, tag, url):
    data = []
    if url == "https://chinese.pku.edu.cn/szdw/zzjs/index.htm":
        data = index.api_json(
            url, "/common/shizi.json", "data", {
                "title": "name",
                "url": "link",
                "viceTitle": "viceTitle"})
    elif url == "https://chinese.pku.edu.cn/szdw/ltxjs/index.htm":
        data = index.api_json(
            url, "/common/ltxshizi.json", "data", {
                "title": "name",
                "url": "link",
                "viceTitle": "viceTitle"})
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//ul[@class='list_con01']/li//a",
        pat_dict={ "link": "./@href", "name": "./text()" })
    div_classes = [ 'newsList', 'minglu', ]
    div_classes = " or ".join([
        "@class='%s'" % s for s in div_classes])
    data = data or index.xpath_select(
        url_or_path=url,
        root_pat="//div[{}]//ul/li/a".format(div_classes),
        pat_dict={ "link": "./@href", "name": "./text()" })

    outs = []
    for d in data:
        name = d["name"]
        if name == "行政教辅人员":
            continue
        name = name.removeprefix("主任：")
        name = name.removeprefix("副主任：")
        name = re.sub("（.*?）$", "", name)
        d["name"] = name
        outs.append(d)
    return outs

@utils.index_cache
def pku_edu_cn():
    """ crawler for pku(peking university), nouse """
    return index.run_faculties("pku", _pku_single)

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

