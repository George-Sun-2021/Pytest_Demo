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
from page import page_actions
from utils.times import sleep
from utils.logger import log


class BasePage(object):
    """selenium base methods"""

    def __init__(self, driver, *args, **kwargs):
        # super(BasePage, self).__init__(*args, **kwargs)

        # self.driver = webdriver.Chrome()
        self.driver = driver
        self.environment = None
        self.env = None  # Add a shortened version of self.environment
        self.poll_frequency = 0.5
        self.timeout = constants.LARGE_TIMEOUT
        self.wait = WebDriverWait(self.driver, self.timeout)  # define WebDriverWait()

    ############

    # Using (Used page Actions)

    def visit(self, url):
        """
        open the url
        @param url:target url to test
        """
        self.driver.set_page_load_timeout(60)
        self.driver.implicitly_wait(constants.EXTREME_TIMEOUT)
        try:
            self.driver.get(url)
            log.info("opening website：%s" % url)
        except TimeoutException:
            raise TimeoutException("open'%s' timeout, please check the network or web server correct or not" % url)

    def find_element(self, locator):
        """
        find target single element
        @param locator:input locator as per format:(By.xx,"value")
        @return:web element
        """
        try:
            return self.wait.until(EC.presence_of_element_located(*locator))

        except Exception as e:
            log.info("Cannot locate the element, error message is ：{}".format(e))

    def find_elements(self, locator):
        """
        find target elements as list
        @param locator:input locator as per format:(By.xx,"value")
        @return:web elements as list
        """
        try:
            return self.wait.until(EC.presence_of_all_elements_located(*locator))

        except Exception as e:
            log.info("Cannot locate the element, error message is ：{}".format(e))

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

    ############

    # Bases (Basic page actions)

    def is_element_present(self, selector, by=By.XPATH):
        selector, by = self.element_locator(selector, by)
        return page_actions.is_element_present(self.driver, selector, by)

    def is_element_visible(self, selector, by=By.CSS_SELECTOR):
        self.wait_for_ready_state_complete()
        selector, by = self.__recalculate_selector(selector, by)
        return page_actions.is_element_visible(self.driver, selector, by)

    def is_element_enabled(self, selector, by=By.CSS_SELECTOR):
        self.wait_for_ready_state_complete()
        selector, by = self.__recalculate_selector(selector, by)
        return page_actions.is_element_enabled(self.driver, selector, by)

    def is_text_visible(self, text, selector="html", by=By.CSS_SELECTOR):
        self.wait_for_ready_state_complete()
        time.sleep(0.01)
        selector, by = self.__recalculate_selector(selector, by)
        return page_actions.is_text_visible(self.driver, text, selector, by)

    def is_attribute_present(
            self, selector, attribute, value=None, by=By.CSS_SELECTOR
    ):
        """Returns True if the element attribute/value is found.
        If the value is not specified, the attribute only needs to exist."""
        self.wait_for_ready_state_complete()
        time.sleep(0.01)
        selector, by = self.__recalculate_selector(selector, by)
        return page_actions.is_attribute_present(
            self.driver, selector, attribute, value, by
        )

    def is_link_text_visible(self, link_text):
        self.wait_for_ready_state_complete()
        time.sleep(0.01)
        return page_actions.is_element_visible(
            self.driver, link_text, by=By.LINK_TEXT
        )

    def is_partial_link_text_visible(self, partial_link_text):
        self.wait_for_ready_state_complete()
        time.sleep(0.01)
        return page_actions.is_element_visible(
            self.driver, partial_link_text, by=By.PARTIAL_LINK_TEXT
        )

    def is_link_text_present(self, link_text):
        """Returns True if the link text appears in the HTML of the page.
        The element doesn't need to be visible,
        such as elements hidden inside a dropdown selection."""
        self.wait_for_ready_state_complete()
        soup = self.get_beautiful_soup()
        html_links = soup.find_all("a")
        for html_link in html_links:
            if html_link.text.strip() == link_text.strip():
                return True
        return False

    def is_partial_link_text_present(self, link_text):
        """Returns True if the partial link appears in the HTML of the page.
        The element doesn't need to be visible,
        such as elements hidden inside a dropdown selection."""
        self.wait_for_ready_state_complete()
        soup = self.get_beautiful_soup()
        html_links = soup.find_all("a")
        for html_link in html_links:
            if link_text.strip() in html_link.text.strip():
                return True
        return False


if __name__ == "__main__":
    pass
