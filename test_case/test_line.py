#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import re
import pytest
from page.basepage import BasePage
from utils.logger import log
from utils.time import sleep


class TestSimple:
    """
    improvement:
    1. using parms of browser and headless as arguments, no need to change manually
    2. the script will auto detect if the selector you passed is css or xpath.(default is css)
    3. some wait timeout is already integrated in the action key words,
    just need to add some simple sleep when necessary
    4. customized exception messages are integrated in the actions
    7. customized logs, reports
    """

    def test_001(self, drivers):
        """测试百度搜索python->选择菜鸟教程进入并简单测试"""
        base = BasePage(drivers)
        log.info("***************************\\/nThe Test is running...")
        base.visit("https://www.baidu.com/")                             # 1. 打开百度
        base.type("#kw", text="python")                                  # 2. 搜索python
        sleep()                                                          # 等一会儿（默认1秒）
        base.click("#su")                                                # 3. 点击搜索按钮
        result = re.search(r'python', base.get_page_source)              # 4. 断言页面查询结果不为空
        assert result
        base.click("link=Python 基础教程 | 菜鸟教程")                       # 5. 点击“Python 基础教程 | 菜鸟教程”超链接
        base.switch_to_newest_window()                                   # 6. 切到最新窗口
        assert base.get_title() == "Python 基础教程 | 菜鸟教程"             # 7. 断言页面标题正确
        base.click("link=Python 3.X 版本的教程")                           # 8. 点击“Python 3.X 版本的教程”超链接
        base.switch_to_newest_window()                                   # 9. 切到最新窗口
        # 10. 滚动到下一页按钮
        base.scroll_to(".previous-next-links:nth-child(4) > .next-design-link > a:nth-child(1)")
        # 11. 点击“下一页“ 按钮
        base.click(".previous-next-links:nth-child(4) > .next-design-link > a:nth-child(1)")
        log.info("***************************\\/nThe Test is finished")


if __name__ == '__main__':
    pytest.main()
