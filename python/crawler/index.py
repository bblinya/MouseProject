import typing
import logging
from functools import wraps
from dataclasses import dataclass

import json
from os import path

from lxml import html, etree
import lxml.html.clean

from . import web

logger = logging.getLogger("index")

target_str = lambda v: "".join(
    [c for c in str(v).replace(" ", "") if c.isprintable()])
target_multi_str = lambda v: "".join(v)

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

def title(url_or_path: str, **kw):
    attrs = {
            "url_or_path": url_or_path,
            "root_pat": "//title",
            "pat_dict": { "text": ".//text()" },
            **kw,
            }
    data = xpath_select(**attrs)
    return [d["text"] for d in data]
