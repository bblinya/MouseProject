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

def main(args):
    print("Load config from {}".format(args.conf))
    with open(args.conf, "r") as f:
        conf = json.load(f)

    for name, c in conf.items():
        print("run config: {}".format(
            json.dumps(c, indent=2)))
        out = run_config(c)
        out_dir = "sources/index"
        if not path.exists(out_dir):
            os.makedirs(out_dir)
        out_path = path.join(out_dir, name)
        print("Dump index into {}".format(out_path))
        with open(out_path, "w") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)


@register_method
def apply_pattern(
        url: str,
        root_pat: str,
        pat_dict: dict,
        dyn_type: typing.Optional[str] = None) -> list:
    data = web.get_url_content(url, dyn_type)
    data = html.fromstring(data)
    matches = data.xpath(root_pat)

    teacher_infos = []
    for ele in matches:
        info = {k: str(ele.xpath(v)[0]) \
                for k, v in pat_dict.items()}
        info.setdefault("base", url)
        # teacher_infos.append(teacher(**info))
        teacher_infos.append(info)
    return teacher_infos
