import os
import json

from os import path
from functools import wraps

ROOT = path.realpath(path.join(
    path.dirname(__file__), "../../"))

def cache_json_file(fname: str):
    def _wrapper(func):
        @wraps(func)
        def _run(*args, **kw):
            if path.exists(fname):
                with open(fname, "r") as f:
                    return json.load(f)
            data = func(*args, **kw)
            with open(fname, "w") as f:
                json.dump(data, f,
                          ensure_ascii=False, indent=2)
            return data
        return _run
    return _wrapper

def read_json(fpath: str):
    fdir = os.path.dirname(fpath)
    if not os.path.exists(fdir):
        os.makedirs(fdir)
    if not os.path.exists(fpath):
        return None

    with open(fpath, "r") as f:
        return json.load(f)

