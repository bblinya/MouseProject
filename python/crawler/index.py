import typing
import logging
from functools import wraps
from dataclasses import dataclass

import json
from os import path

import lxml.html
from lxml import html, etree

from . import web

logger = logging.getLogger("index")

def xpath_select(
        url_or_path: str,
        root_pat: str,
        pat_dict: dict,
        target_process = str,
        allow_empty: bool = False,
        dyn_type: typing.Optional[str] = None) -> list:
    if path.exists(url_or_path):
        with open(url_or_path, "r") as f:
            data = f.read()
    else:
        data = web.get_url_content(url_or_path, dyn_type)
    data = html.fromstring(data)
    matches = data.xpath(root_pat)
    #  if not matches:
    #      logger.warning((
    #          "matches is empty for pattern: {}"
    #      ).format(root_pat))

    teacher_infos = []
    for ele in matches:
        info = {k: ele.xpath(v) for k,v in pat_dict.items()}
        out = {}
        for k, v in info.items():
            v = v[0] if v else None
            assert allow_empty or (v is not None), (
                "pat_dict match {} failed: {}"
                    ).format(html.tostring(ele), pat_dict[k])
            out[k] = target_process(v) if v else None
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
