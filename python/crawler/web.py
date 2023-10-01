import typing

import os
import sys
import logging
from hashlib import sha1

from functools import wraps
import tempfile
from os import path

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

web_logger = logging.getLogger("web")

def get_static_url(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            }
    resp = requests.get(url)
    if not resp.ok:
        print("url: ", url, "curl failed", resp.status_code)
        print(resp.reason)
        print(resp.content)
        return ""
    return resp.content

def _get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-extensions")
    # options.add_argument("--disable-gpu")
    # #options.add_argument("--no-sandbox") # linux only
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)
    # driver.execute_cdp_cmd("Network.enable", {})
    # driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browserClientA"}})
    # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #     "source": """
    #         Object.defineProperty(navigator, 'webdriver', {
    #             get: () => undefined
    #         })
    #     """
    # })
    # driver.implicitly_wait(30)
    return driver

def get_dynamic_url(url: str) -> str:
    #  options = getattr(webdriver, dyn_type + "Options")()
    #  options.add_argument("--disable-blink-features")
    #  options.add_argument("--disable-blink-features=AutomationControlled")
    driver = _get_driver()
    driver.get(url)
    # driver.find_element(By.XPATH, "//div")
    return driver.page_source

def _temp_path(url):
    temp_root = path.join(tempfile.gettempdir(), "mouse_web")
    if not path.exists(temp_root):
        os.makedirs(temp_root, exist_ok=True)
    hash_url = sha1(url.encode()).hexdigest()[:30]
    return path.join(
            tempfile.gettempdir(),
            "mouse_web", hash_url)

def get_url_content(
        url: str,
        dyn_type: typing.Optional[str]) -> str:
    cache = _temp_path(url)
    web_logger.debug("cache {} from {}".format(cache, url))

    if path.exists(cache):
        with open(cache, "r") as f:
            return f.read()

    assert dyn_type in [None, "Chrome"]
    if dyn_type is None:
        data = get_static_url(url)
    else:
        data = get_dynamic_url(url)

    with open(cache, "w") as f:
        f.write(data)
    return data
