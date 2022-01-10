#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from page.basepage import BasePage
from time import sleep
from common.readelement import Element

search = Element('search')


class SearchPage(BasePage):
    """搜索类"""

    def input_search(self, content):
        """输入搜索"""
        self.type(search['搜索框'], text=content)
        sleep(1)

    @property
    def imagine(self):
        """搜索联想"""
        return [x.text for x in self.find_visible_elements(search['候选'])]

    def click_search(self):
        """点击搜索"""
        self.click(search['搜索按钮'])


if __name__ == '__main__':
    pass
