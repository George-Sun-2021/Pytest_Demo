#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
selenium基类
本文件存放了selenium基类的封装方法
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    ElementClickInterceptedException as ECI_Exception,
    ElementNotInteractableException as ENI_Exception,
    MoveTargetOutOfBoundsException,
    NoSuchWindowException,
    StaleElementReferenceException,
    WebDriverException,
    TimeoutException,
)

from config import constants
from config.conf import cm
from Utils.times import sleep
from Utils.logger import log
from page import page_actions


class BasePage(object):
    """selenium base methods"""

    def __init__(self, driver, *args, **kwargs):
        # super(BasePage, self).__init__(*args, **kwargs)

        # self.driver = webdriver.Chrome()
        self.driver = driver
        self.environment = None
        self.env = None  # Add a shortened version of self.environment
        self.timeout = 20
        self.wait = WebDriverWait(self.driver, self.timeout)

    @staticmethod
    def element_locator(func, locator):
        """元素定位器"""
        name, value = locator
        return func(cm.LOCATE_MODE[name], value)

    def open(self, url):
        """打开网址并验证"""
        try:
            self.driver.get(url)
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            log.info("打开网页：%s" % url)
        except TimeoutException:
            raise TimeoutException("打开%s超时请检查网络或网址服务器" % url)

    def find_element(self, locator):
        """寻找单个元素"""
        return BasePage.element_locator(lambda *args: self.wait.until(
            EC.presence_of_element_located(args)), locator)

    def find_elements(self, locator):
        """查找多个相同的元素"""
        return BasePage.element_locator(lambda *args: self.wait.until(
            EC.presence_of_all_elements_located(args)), locator)

    def elements_num(self, locator):
        """获取相同元素的个数"""
        number = len(self.find_elements(locator))
        log.info("相同元素：{}".format((locator, number)))
        return number

    def input_text(self, locator, txt):
        """输入(输入前先清空)"""
        sleep(0.5)
        ele = self.find_element(locator)
        ele.clear()
        ele.send_keys(txt)
        log.info("输入文本：{}".format(txt))

    def is_click(self, locator):
        """点击"""
        self.find_element(locator).click()
        sleep()
        log.info("点击元素：{}".format(locator))

    def is_element_visible(self, selector, by=By.CSS_SELECTOR):
        self.wait_for_ready_state_complete()
        selector, by = self.__recalculate_selector(selector, by)
        return page_actions.is_element_visible(self.driver, selector, by)

    def element_text(self, locator):
        """获取当前的text"""
        _text = self.find_element(locator).text
        log.info("获取文本：{}".format(_text))
        return _text

    @property
    def get_source(self):
        """获取页面源代码"""
        return self.driver.page_source

    def refresh(self):
        """刷新页面F5"""
        self.driver.refresh()
        self.driver.implicitly_wait(30)

    def set_window_size(self, width, height):
        self.__check_scope()
        self.driver.set_window_size(width, height)
        self.__demo_mode_pause_if_active()

    def maximize_window(self):
        self.__check_scope()
        self.driver.maximize_window()
        self.__demo_mode_pause_if_active()

    def switch_to_frame(self, frame, timeout=None):
        """Wait for an iframe to appear, and switch to it. This should be
        usable as a drop-in replacement for driver.switch_to.frame().
        The iframe identifier can be a selector, an index, an id, a name,
        or a web element, but scrolling to the iframe first will only occur
        for visible iframes with a string selector.
        @Params
        frame - the frame element, name, id, index, or selector
        timeout - the time to wait for the alert in seconds
        """
        if not timeout:
            timeout = constants.SMALL_TIMEOUT
        if type(frame) is str and self.is_element_visible(frame):
            try:
                self.scroll_to(frame, timeout=1)
            except Exception:
                pass
        page_actions.switch_to_frame(self.driver, frame, timeout)


if __name__ == "__main__":
    pass
