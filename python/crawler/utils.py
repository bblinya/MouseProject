import os
import json
import typing
import logging

from os import path
from functools import wraps

ROOT = path.realpath(path.join(
    path.dirname(__file__), "../../"))

ulogger = logging.getLogger("utils")

def cache_json_file(func):
    @wraps(func)
    def _wrapper(*args, **kw):
        fname = path.join(
                "sources/index", func.__name__ + ".json")
        ulogger.info(
            "cache function: {} with file: {}".format(
                func.__name__, fname))
        if path.exists(fname):
            with open(fname, "r") as f:
                return json.load(f)
        data = func(*args, **kw)
        with open(fname, "w") as f:
            json.dump(data, f,
                      ensure_ascii=False, indent=2)
        return data
    return _wrapper

PredFuncT = typing.Callable[typing.List[typing.Any], bool]

#  def pred_file_exist()

def run_if(pred):
    def _run(func):
        @wraps(func)
        def _wrapper(*args, **kw):
            return func(*args, **kw)
        return _wrapper
    return _run

def read_json(fpath: str):
    fdir = os.path.dirname(fpath)
    if not os.path.exists(fdir):
        os.makedirs(fdir)
    if not os.path.exists(fpath):
        return None

    with open(fpath, "r") as f:
        return json.load(f)

