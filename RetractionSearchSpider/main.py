#!/usr/bin/python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
import time
import os

dayOfEachMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
htmlDownloadPath = 'D:/Code/MouseProjectDB/Download/'
downloadLogPath = 'D:/Code/MouseProjectDB/Download/downloadLog.txt'
csvPath = 'D:/Code/MouseProjectDB/Target.csv'
write2csvLogPath = 'D:/Code/MouseProjectDB/write2csvLog.txt'

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

def MainDownloadFunc(beginYear, finalYear):
    ghelper = r'D:\Code\MouseProjectDB\Ghelper-v2.8.9\Ghelper_v2.8.9.crx'
    userData = r'--user-data-dir=C:\Users\32687\AppData\Local\Google\Chrome\User Data'
    chromeDriver = r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
    retractiondb = 'http://retractiondatabase.org/RetractionSearch.aspx?'

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

def ParseMainrowAndWrite2CSV(mainrow, writer, htmlName):
    logFile = open(write2csvLogPath, 'a')

    # title
    try:
        title = mainrow.find('span', {'class': 'rTitleNotIE'}).get_text()
    except AttributeError as e:
        title = mainrow.find('span', {'class': 'rTitle'}).get_text()

    # subject
    try:
        subject = mainrow.find('span', {'class': 'rSubject'}).get_text()
    except AttributeError as e:
        subject = 'Fuck!'
        logFile.write(htmlName + ' write rSubject failed...\n')
        logFile.flush()

    # journal
    journal = mainrow.find('span', {'class': 'rJournal'}).get_text()

    # publisher
    try:
        publisher = mainrow.find('span', {'class': 'rPublisher'}).get_text()
    except AttributeError as e:
        publisher = 'Fuck!'
        logFile.write(htmlName + ' write rPublisher failed...\n')
        logFile.flush()

    # institution
    institutions = mainrow.findAll('span', {'class': 'rInstitution'})
    institution = ''
    for item in institutions:
        # delete \n
        institution += (item.get_text().replace('\n', '') + 'ROWSPLIT')

    col1 = title + 'COLSPLIT'
    col2 = subject + 'COLSPLIT'
    col3 = journal + 'COLSPLIT'
    col4 = publisher + 'COLSPLIT'
    col5 = institution + 'COLSPLIT'

    # reason
    reasons = mainrow.findAll('div', {'class': 'rReason'})
    col6 = ''
    for reason in reasons:
        col6 += (reason.get_text() + 'ROWSPLIT')
    col6 += 'COLSPLIT'

    # authors
    authors = mainrow.findAll('a', {'class': 'authorLink'})
    col7 = ''
    for author in authors:
        col7 += (author.get_text() + 'ROWSPLIT')
    col7 += 'COLSPLIT'

    # date, nature, midNum
    str = mainrow.findAll('td')[4]
    date = str.get_text()[:10]
    nature = str.find('span').get_text()
    mid_num = str.get_text()[10:len(str.get_text()) - len(nature)]
    col8 = date + 'COLSPLIT'
    col9 = mid_num + 'COLSPLIT'
    col10 = nature + 'COLSPLIT'

    str = mainrow.findAll('td')[5]
    date = str.get_text()[:10]
    nature = str.find('span').get_text()
    mid_num = str.get_text()[10:len(str.get_text()) - len(nature)]
    col11 = date + 'COLSPLIT'
    col12 = mid_num + 'COLSPLIT'
    col13 = nature + 'COLSPLIT'

    # nature, other_text
    str = mainrow.findAll('td')[6]
    nature = str.find('span').get_text()
    other_text = str.get_text()[:len(str.get_text()) - len(nature)]
    col14 = other_text + 'COLSPLIT'
    col15 = nature + 'COLSPLIT'

    # country, pay_walled
    str = mainrow.findAll('td')[7].find('span')
    pay_walled = str.find('span', {'class': 'rPaywalled'}).get_text()
    country = str.get_text()[:len(str.get_text()) - len(pay_walled)]
    col16 = country + 'COLSPLIT'
    col17 = pay_walled

    colList = [col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13, col14, col15, col16, col17]
    writer.writerow(colList)

    logFile.close()

def ParseHtmlAndWrite2CSV(htmlPath):
    htmlName = htmlPath.split('/')[-1]
    print('Parse file: ' + htmlName)

    html = urlopen('file:///' + htmlPath)
    bs = BeautifulSoup(html.read(), 'html.parser')
    mainrowList = bs.findAll('tr', { 'class':'mainrow' })

    with open(csvPath, 'a', newline='', encoding='UTF-8') as f:
        writer = csv.writer(f)
        # write mainrow in mainrowList to csv one by one
        for mainrow in mainrowList:
            ParseMainrowAndWrite2CSV(mainrow, writer, htmlName)

    return

def MainParseAndWriteFunc():
    dirList = os.listdir(htmlDownloadPath)
    for dir in dirList:
        if not dir.isdigit():
            continue
        # dir named 9999 stores html contain over 50 items
        # parse html files in this year one by one
        curDir = htmlDownloadPath + '/' + dir
        htmlList = os.listdir(curDir)
        for html in htmlList:
            htmlPath = curDir + '/' + html
            ParseHtmlAndWrite2CSV(htmlPath)

if __name__ == '__main__':
    # MainDownloadFunc(1923, 2023)
    MainParseAndWriteFunc()