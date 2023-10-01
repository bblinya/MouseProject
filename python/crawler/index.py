import typing
from functools import wraps
from dataclasses import dataclass

import json
from os import path

import lxml.html
from lxml import html, etree

from . import web

ALL_METHOD = {}

def register_method(f):
    ALL_METHOD[f.__name__] = f
    return f

def run_config(conf: dict) -> list:
    method = conf.pop("method")
    assert method in ALL_METHOD, (
            "available methods: {}"
            ).format(ALL_METHOD.keys())
    return ALL_METHOD[method](**conf)

@register_method
def apply_pattern(
        url_or_path: str,
        root_pat: str,
        pat_dict: dict,
        target_process = str,
        dyn_type: typing.Optional[str] = None) -> list:
    if path.exists(url_or_path):
        with open(url_or_path, "r") as f:
            data = f.read()
    else:
        data = web.get_url_content(url, dyn_type)
    data = html.fromstring(data)
    matches = data.xpath(root_pat)

    teacher_infos = []
    for ele in matches:
        info = {k: ele.xpath(v) for k, v in pat_dict.items()}
        info = {k: target_process(v[0]) if v else None \
                for k, v in info.items()}
        teacher_infos.append(info)
    return teacher_infos
