#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : JDCrawler.py
import logging

import bs4
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from connMongo import *

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')
browser = webdriver.Firefox()
# 初始化浏览器对象
wait = WebDriverWait(browser, 30)
'''建议设置时长30s以上'''


def index_page(page):
    """
    抓取索引页
    :param page: 页码
    """
    logging.debug('正在爬取第' + str(page) + '页')
    try:
        url = 'https://search.jd.com/Search?keyword=' + KEYWORD

        if page > 1:
            url = url + '&page=' + str(page * 2 - 1)
        browser.get(url)
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'div[class="m-list"]'), str(page)))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="gl-i-wrap"]')))
        get_products()
    except TimeoutException:
        index_page(page)


def get_products():
    """
    提取商品数据
    """
    html = browser.page_source
    soup = bs4.BeautifulSoup(html)
    items = soup.select('div[class="gl-i-wrap"]')

    for item in items:
        try:
            image = 'http:' + item.select('img')[0].get('src')
            price = item.select('div[class="p-price"] i')[0].get_text()
            title = item.select('div[class="p-name p-name-type-2"] em')[0].get_text()
            shop = item.select('div[class="p-shop"] span a')[0].get_text()
            conmit = item.select('div[class="p-commit"] a')[0].get_text() + '评论'
            product = {
                'image': image,
                'price': price,
                'title': title,
                'shop': shop,
                'comments': conmit
            }
            save_to_mongo(product)
        except:
            logging.debug("此项爬取错误，略过!")
            pass
        finally:
            print(product)



def main():
    """
    遍历每一页
    """
    for i in range(1, MAX_PAGE + 1):
        index_page(i)
    browser.close()


if __name__ == '__main__':
    main()
