#!/usr/bin/python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

dayOfEachMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
htmlDownloadPath = 'D:/Code/MouseProjectDB/Download/'
downloadLogPath = 'D:/Code/MouseProjectDB/Download/downloadLog.txt'

def GetDateStr(year, month, day, splitSymbol):
    monthStr = ''
    dayStr = ''

    if month < 10:
        monthStr = '0' + str(month)
    else:
        monthStr = str(month)

    if day < 10:
        dayStr = '0' + str(day)
    else:
        dayStr = str(day)

    dateStr = monthStr + splitSymbol + dayStr + splitSymbol + str(year)

    return dateStr

def GetDaysOfCurrentYearAndMonth(year, month):
    days = 0

    if year % 4 == 0 and month == 2:
        days = 29
    else:
        days = dayOfEachMonth[month - 1]

    return days

def SearchDate(fromDateStr, toDateStr, driver):
    # fill fromDateStr and toDateStr into the form and click the SearchButton
    def FillAndClick():
        driver.find_element_by_id('hlinkClear').click()
        driver.find_element_by_id('txtOriginalDateFrom').send_keys(fromDateStr)
        driver.find_element_by_id('txtOriginalDateTo').send_keys(toDateStr)
        driver.find_element_by_id('btnSearch').click()

    # if something wrong when click, try three more times
    try:
        FillAndClick()
    except Exception:
        driver.refresh()
        try:
            FillAndClick()
        except Exception:
            driver.refresh()
            try:
                FillAndClick()
            except Exception:
                driver.refresh()
                FillAndClick()
    return

def DownloadPage(year, month, day, driver):
    mainrowList = driver.find_elements_by_class_name('mainrow')
    dateStr = GetDateStr(year, month, day, '-')
    fileName = dateStr + '.html'

    if len(mainrowList) == 0:
        return 0

    if len(driver.find_element_by_id('lblError').text) == 0:
        # no error, download
        # save files to dir by year
        targetDir = htmlDownloadPath + str(year) + '/'
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)

        with open(targetDir + fileName, 'wb') as f:
            try:
                f.write(driver.page_source.encode('utf-8'))
            except UnicodeEncodeError as e:
                errStr = ' has UnicodeEncodeError, written failed...\n'
                logFile = open(downloadLogPath, 'a')
                logFile.write(fileName + errStr)
                logFile.flush()
                logFile.close()
        return len(mainrowList)
    else:
        # items > 50 in one page
        errStr = ' contains more than 50 items!\n'
        logFile = open(downloadLogPath, 'a')
        logFile.write(fileName + errStr)
        logFile.flush()
        logFile.close()
        return 666

def MainDownloadFunc():
    ghelper = r'D:\Code\MouseProjectDB\Ghelper-v2.8.9\Ghelper_v2.8.9.crx'
    userData = r'--user-data-dir=C:\Users\32687\AppData\Local\Google\Chrome\User Data'
    chromeDriver = r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
    retractiondb = 'http://retractiondatabase.org/RetractionSearch.aspx?'
    beginYear = 2003
    finalYear = 2023

    # open target website in Chrome
    option = webdriver.ChromeOptions()
    option.add_extension(ghelper)
    option.add_argument(userData)
    option.add_argument('--profile-directory=Default')
    driver = webdriver.Chrome(executable_path=chromeDriver, options=option)
    driver.set_page_load_timeout(10)
    driver.get(retractiondb)

    try:
        # wait until the btnSearch ready
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'btnSearch')))
    finally:
        for year in range(beginYear, finalYear + 1):
            for month in range(1, 12 + 1):
                # judge 28 or 29 days in February
                for day in range(1, GetDaysOfCurrentYearAndMonth(year, month) + 1):
                    fromDateStr = GetDateStr(year, month, day, '/')
                    toDateStr = fromDateStr
                    SearchDate(fromDateStr, toDateStr, driver)
                    time.sleep(0.5)
                    DownloadPage(year, month, day, driver)

    driver.close()

if __name__ == '__main__':
    MainDownloadFunc()