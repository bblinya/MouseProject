import typing

import os
import sys
from hashlib import sha1

from functools import wraps
import tempfile
from os import path

import requests
import selenium.webdriver

def get_static_url(url: str) -> str:
    resp = requests.get(url)
    if not resp.ok:
        print("url: ", url, "curl failed")
        return ""
    return resp.content

def get_dynamic_url(url: str, dyn_type: str) -> str:
    driver = getattr(selenium.webdriver, dyn_type)()
    driver.get(url)
    return driver.page_source

def _temp_path(url):
    temp_root = path.join(tempfile.gettempdir(), "mouse_web")
    if not path.exists(temp_root):
        os.makedirs(temp_root, exist_ok=True)
    hash_url = sha1(url.encode()).hexdigest()[:10]
    return path.join(
            tempfile.gettempdir(),
            "mouse_web", hash_url)

def get_url_content(
        url: str,
        dyn_type: typing.Optional[str]) -> str:
    cache = _temp_path(url)
    if path.exists(cache):
        with open(cache, "r") as f:
            return f.read()

    assert dyn_type in [None, "Chrome"]
    if dyn_type is None:
        data = get_static_url(url)
    else:
        data = get_dynamic_url(url, dyn_type)

    with open(cache, "w") as f:
        f.write(data)
    return data
