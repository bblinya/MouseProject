import typing
import logging
from functools import wraps
from urllib.parse import urljoin
from dataclasses import dataclass

import os
import json
from os import path

from lxml import html, etree
import lxml.html.clean

from . import web, utils

logger = logging.getLogger("index")

xpath_str_strip = "translate(text(), ' &#9;&#10;&#13', '')"
xpath_str_len = "string-length({})".format(xpath_str_strip)

target_str = lambda v: "".join(
    [c for c in str(v).replace(" ", "") if c.isprintable()])
target_multi_str = lambda v: "".join(v)

PatAttrsT = typing.Dict[str, str]

def xpath_select(
        url_or_path: str,
        root_pat: str,
        pat_dict: dict,
        target_process = target_str,
        allow_empty: bool = False,
        allow_multi: bool = False,
        multi_process = target_multi_str,
        dyn_type: typing.Optional[str] = None) -> list:
    if path.exists(url_or_path):
        with open(url_or_path, "r") as f:
            data = f.read()
    else:
        data = web.get_url_content(url_or_path, dyn_type)
    data = html.fromstring(data)
    cleaner = lxml.html.clean.Cleaner(style=True)
    data = cleaner.clean_html(data)
    logger.debug("apply root pattern: {}".format(root_pat))
    matches = data.xpath(root_pat)
    #  if not matches:
    #      logger.warning((
    #          "matches is empty for pattern: {}"
    #      ).format(root_pat))

    teacher_infos = []
    for ele in matches:
        info = {k: ele.xpath(v) for k,v in pat_dict.items()}
        out = {}
        ele_str = html.tostring(
                ele, encoding="utf-8", pretty_print=True
            ).decode("utf-8")
        for k, v in info.items():
            msg = "pat_dict match {} failed: {}\n{}".format(
                    ele_str, pat_dict[k], v)
            v = [ target_process(d) for d in v ]
            v = [ d for d in v if d ]
            assert allow_empty or len(v) > 0, msg
            assert allow_multi or len(v) < 2, msg
            out[k] = multi_process(v) or None
        teacher_infos.append(out)
    return teacher_infos

def read_faculties(seed: str):
    _split = lambda v: [c.strip() for c in v.split("：")]

    data = utils.read_seed(seed)
    faculty = None
    outs = []
    for d in data:
        if "学院" in d:
            faculty, link = _split(d)
            if len(link) == 0:
                continue
        outs.append((faculty, *_split(d)))
    return outs

def run_faculties(seed, func, dup_keys = [ "link" ]):
    l = logging.getLogger(seed)
    spath = path.join(
            utils.ROOT, "sources/index", seed + ".txt")
    outs = []
    data = read_faculties(spath)
    for (faculty, tag, link) in data:
        l.info("process {} > {} > {}".format(
            faculty, tag, link))
        _f = utils.index_cache(
            func, cache=False,
            fname=utils.temp_file(seed + link))
        out = _f(faculty, tag, link)
        assert out, "output is empty"
        out = [{
            "faculty": faculty, "tag": tag, "base": link,
            **v} for v in out]
        outs.extend(out)

    l.info("{} output teachers: {}".format(seed, len(outs)))
    outs = utils.remove_duplicate(outs, keys=dup_keys)
    l.info("{} dedupl teachers: {}".format(seed, len(outs)))
    for (_, _, link) in data:
        fpath = utils.temp_file(seed + link)
        path.exists(fpath) and os.remove(fpath)
    return outs

def validate_index_attrs(
        base: str,
        data: typing.List[PatAttrsT]
        ) -> typing.List[PatAttrsT]:
    outs = []
    for d in data:
        assert "name" in d, "attrs no key:name"
        assert "link" in d, "attrs no key:link"
        name = d["name"]
        name = name.removesuffix("副教授")
        name = name.removesuffix("教授")
        name = name.removesuffix("讲师")
        if len(name) == 0:
            continue
        if "·" in name:
            assert len(name) < 10, d
        else:
            assert len(name) < 6, d
        d["name"] = name
        d["link"] = urljoin(base, d["link"])
        outs.append(d)

    assert outs, "data output is empty"
    return outs


def title(url_or_path: str, **kw):
    attrs = {
            "url_or_path": url_or_path,
            "root_pat": "//title",
            "pat_dict": { "text": ".//text()" },
            **kw,
            }
    data = xpath_select(**attrs)
    return [d["text"] for d in data]
