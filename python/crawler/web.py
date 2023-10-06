import typing

import os
import time
import sys
import logging
from hashlib import sha1

from functools import wraps
import tempfile
from os import path

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

from . import utils, log

web_logger = logging.getLogger("web")
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

def get_static_url(url: str, error=True) -> str:
    headers = {
        # "Cookie": "JSESSIONID=9B3164D332A2416164EB6CB48BE97E99; EdaP18tkVMlRT=0_YhUKYx8W09P3vZn9SEJSVUzIG8EoiEb5y97SvzyiwaHfnr15nC3__xhHkzIve2EiwSpUKo2mSwDvTOJoAsrMbNUih9QMAgBqAaW_L0.Ea9YR_I7MJxv0MqMpa1S0ewSuwjA.Xk3tRp83MWumCP43hBq3ESO8U15fHqe1j91yAQGC_pASdhUmnfD126zcafyVmyUVpy8KKz3zhXc59YyxSZXGNBMmNRbuwYi.fUPDlPhbT25BQsW9.D716NNJZ7PnkKrm4JA5E7NsvoTca72em3GowyH52jziWgF8L0YVg7NzfYEK9tHoPWzd9qousT_rrYOTNcBtllEzQdU5cNrTT1PZ9OtLvEhykZbhVt.EGxkTYhaXrOC6aqBzq4j0FiD",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            }
    resp = requests.get(url, verify=False, headers=headers)
    if not resp.ok:
        if error:
            raise RuntimeError("static url get failed")
        #  print("url: ", url, "curl failed", resp.status_code)
        #  print(resp.reason)
        #  print(resp.content)
        return ""
    return resp.content.decode("utf-8")

def _get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("-headless")
    options.add_argument("--disable-extensions")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox") # linux only
    dic={ "profile.managed_default_content_settings.images": 2}
    #设置driver不加载图片
    options.add_experimental_option("prefs", dic)

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

def get_url_content(
        url: str,
        dyn_type: typing.Optional[str] = None,
        **kwargs) -> str:
    cache = utils.temp_file(url)
    web_logger.log(
            log.TRACE, "cache {} from {}".format(cache, url))

    if path.exists(cache):
        with open(cache, "r") as f:
            return f.read()

    assert dyn_type in [None, "Chrome"]
    if dyn_type is None:
        data = get_static_url(url, **kwargs)
    else:
        data = get_dynamic_url(url, **kwargs)

    time.sleep(1)
    with open(cache, "w") as f:
        f.write(data)
    return data
