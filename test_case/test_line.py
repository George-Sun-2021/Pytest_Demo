#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import re
import pytest
# import allure

from common.readelement import Element
from page.basepage import BasePage
from utils.logger import log
from common.readconfig import ini
from utils.time import sleep


class TestSimple:
    @pytest.fixture(scope='function', autouse=True)
    def open_page(self, drivers):
        """打开百度"""
        base_page = BasePage(drivers)
        base_page.visit(ini.url)

    def test_003(self, drivers):
        """搜索"""
        base_page = BasePage(drivers)
        base_page.type("#kw", text="selenium")
        sleep(1)
        base_page.click(*Element('search')['搜索按钮'])
        result = re.search(r'selenium', base_page.get_page_source)
        log.info(result)
        assert result


# if __name__ == '__main__':
#     pytest.main(['TestCase/test_PO.py'])
if __name__ == '__main__':
    # pycharm does not support allure report very well，better in vscode
    pytest.main()

    # import os
    # pytest.main(['test_case/test_line.py', '--alluredir', './allure'])
    # os.system('allure serve allure')
