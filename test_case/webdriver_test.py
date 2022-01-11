#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By


def login():
    driver = webdriver.Chrome()

    driver.delete_all_cookies()
    driver.get('https://www.baidu.com/')
    driver.find_element(By.ID, 'kw')


if __name__ == '__main__':
    login()
