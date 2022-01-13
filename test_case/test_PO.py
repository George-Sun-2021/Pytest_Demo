#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import re
import pytest
import allure
from utils.logger import log
from common.readconfig import ini
from page_object.searchpage import SearchPage


@allure.title("执行测试用例用于登录模块")
@allure.epic("v1.0.0 - automation test")
@allure.feature("Pytest测试demo")
@allure.description("简单测试登录baidu")
@allure.link("https://www.baidu.com", name="连接跳转百度")
@pytest.mark.demo
class TestSearch:
    @pytest.fixture(scope='function', autouse=True)
    def open_baidu(self, drivers):
        """打开百度"""
        search = SearchPage(drivers)
        search.visit(ini.url)

    @allure.story("测试百度搜索selenium结果")
    @allure.severity("critical")
    @allure.testcase("https://www.confluence.xxx.com", name="测试用例位置")
    def test_001(self, drivers):
        """测试百度搜索selenium结果"""
        search = SearchPage(drivers)
        search.input_search("selenium")
        search.click_search()
        result = re.search(r'selenium', search.get_page_source)
        log.info(result)
        assert result

    @allure.story("测试搜索候选")
    @allure.severity("normal")
    @allure.testcase("https://www.confluence.xxx.com", name="测试用例位置")
    def test_002(self, drivers):
        """测试搜索候选"""
        search = SearchPage(drivers)
        search.input_search("selenium")
        log.info(list(search.imagine))
        assert all(["selenium" in i for i in search.imagine])


# if __name__ == '__main__':
#     pytest.main(['TestCase/test_PO.py'])
if __name__ == '__main__':
    # 下面的代码使用pycharm运行可能会没有生成报告，建议使用vscode执行
    import os

    pytest.main(['test_case/test_PO.py', '--alluredir', './allure'])
    os.system('allure serve allure')
