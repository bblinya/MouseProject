import os
import json
import typing
import logging
import tempfile

from os import path
from hashlib import sha1
from functools import wraps

ROOT = path.realpath(path.join(
    path.dirname(__file__), "../../"))

ulogger = logging.getLogger("utils")

INDEX_ROOT = path.join(ROOT, "sources/index")
def index_file(func, fname=None):
    return fname or path.join(
            INDEX_ROOT, func.__name__ + ".json")
def index_cache(func, fname=None, cache=True,):
    @wraps(func)
    def _wrapper(*args, **kw):
        fpath = index_file(func, fname)
        ulogger.info(
            "cache function: {} with file: {}".format(
                func.__name__, fpath))
        if cache and path.exists(fpath):
            with open(fpath, "r") as f:
                return json.load(f)
        data = func(*args, **kw)
        with open(fpath, "w") as f:
            json.dump(data, f,
                      ensure_ascii=False, indent=2)
        return data
    return _wrapper

PatAttrsT = typing.Dict[str, str]
def remove_duplicate(
        data: typing.List[PatAttrsT],
        keys: typing.List[str],
        valid_keys: typing.List[str] = [],
        ) -> typing.List[PatAttrsT]:
    key_dict = {}
    for d in data:
        val = "_".join([d[k] for k in keys])
        if val in key_dict:
            assert all([d[k] == key_dict[val][k] \
                    for k in valid_keys]), (
                "{} vs. {}").format(d, key_dict[val])
        else:
            key_dict[val] = d
    return list(key_dict.values())


def temp_file(seed: str):
    temp_root = path.join(tempfile.gettempdir(), "mouse_web")
    if not path.exists(temp_root):
        os.makedirs(temp_root, exist_ok=True)
    hash_url = sha1(seed.encode()).hexdigest()[:30]
    return path.join(
            tempfile.gettempdir(),
            "mouse_web", hash_url)

def read_seed(fpath: str):
    with open(fpath, "r") as f:
        data = f.readlines()
    data = [d.strip() for d in data if d.strip()]
    data = [d for d in data if not d.startswith("//")]
    return data

def read_json(fpath: str):
    fdir = os.path.dirname(fpath)
    if not os.path.exists(fdir):
        os.makedirs(fdir)
    if not os.path.exists(fpath):
        return None

    with open(fpath, "r") as f:
        return json.load(f)

