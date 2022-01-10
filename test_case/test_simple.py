#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import re
import pytest
import allure

from common.readelement import Element
from page.basepage import BasePage
from utils.logger import log
from common.readconfig import ini
from utils.time import sleep


@allure.feature("测试百度模块")
class TestSimple:
    @pytest.fixture(scope='function', autouse=True)
    def open_page(self, drivers):
        """打开百度"""
        base_page = BasePage(drivers)
        base_page.visit(ini.url)

    @allure.story("搜索selenium结果用例")
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
#     pytest.main(['TestCase/test_search.py'])
if __name__ == '__main__':
    # 下面的代码使用pycharm运行可能会没有生成报告，建议使用vscode执行
    import os

    pytest.main(['test_case/test_simple.py', '--alluredir', './allure'])
    os.system('allure serve allure')
