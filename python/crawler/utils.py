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

CACHE_ROOT = path.join(ROOT, "sources/index")
def cache_json_file(func, fname=None):
    @wraps(func)
    def _wrapper(*args, **kw):
        fpath = fname or path.join(
            CACHE_ROOT, func.__name__ + ".json")
        ulogger.info(
            "cache function: {} with file: {}".format(
                func.__name__, fpath))
        if path.exists(fpath):
            with open(fpath, "r") as f:
                return json.load(f)
        data = func(*args, **kw)
        with open(fpath, "w") as f:
            json.dump(data, f,
                      ensure_ascii=False, indent=2)
        return data
    return _wrapper

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

