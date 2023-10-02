import typing
from functools import wraps
from dataclasses import dataclass

import json
from os import path

import lxml.html
from lxml import html, etree

from . import web

def xpath_select(
        url_or_path: str,
        root_pat: str,
        pat_dict: dict,
        target_process = str,
        dyn_type: typing.Optional[str] = None) -> list:
    if path.exists(url_or_path):
        with open(url_or_path, "r") as f:
            data = f.read()
    else:
        data = web.get_url_content(url_or_path, dyn_type)
    data = html.fromstring(data)
    matches = data.xpath(root_pat)

    teacher_infos = []
    for ele in matches:
        info = {k: ele.xpath(v) for k, v in pat_dict.items()}
        info = {k: target_process(v[0]) if v else b'' \
                for k, v in info.items()}
        teacher_infos.append(info)
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
