#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
selenium基类
本文件存放了selenium基类的封装方法
"""
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    ElementClickInterceptedException as ECI_Exception,
    ElementNotInteractableException as ENI_Exception,
    MoveTargetOutOfBoundsException,
    NoSuchWindowException,
    StaleElementReferenceException,
    WebDriverException,
)

from config.conf import cm
from Utils.times import sleep
from Utils.logger import log


class BasePage(object):
    """selenium基类"""

    def __init__(self, *args, **kwargs):
        super(BasePage, self).__init__(*args, **kwargs)

        # self.driver = webdriver.Chrome()
        self.driver = None
        self.environment = None
        self.env = None  # Add a shortened version of self.environment

        self.timeout = 20
        self.wait = WebDriverWait(self.driver, self.timeout)

    def open(self, url):
        """ Navigates the current browser window to the specified page. """
        self.__check_scope()
        self.__check_browser()
        pre_action_url = None
        try:
            pre_action_url = self.driver.current_url
        except Exception:
            pass
        if type(url) is str:
            url = url.strip()  # Remove leading and trailing whitespace
        if (type(url) is not str) or not self.__looks_like_a_page_url(url):
            # url should start with one of the following:
            # "http:", "https:", "://", "data:", "file:",
            # "about:", "chrome:", "opera:", or "edge:".
            msg = 'Did you forget to prefix your URL with "http:" or "https:"?'
            raise Exception('Invalid URL: "%s"\n%s' % (url, msg))
        self.__last_page_load_url = None
        self.driver.get_log("browser")
        if url.startswith("://"):
            # Convert URLs such as "://google.com" into "https://google.com"
            url = "https" + url
        try:
            self.driver.get(url)
        except Exception as e:
            if "ERR_CONNECTION_TIMED_OUT" in e.msg:
                self.sleep(0.5)
                self.driver.get(url)
            else:
                raise Exception(e.msg)
        if (
                self.driver.current_url == pre_action_url
                and pre_action_url != url
        ):
            time.sleep(0.1)  # Make sure load happens
        if settings.WAIT_FOR_RSC_ON_PAGE_LOADS:
            self.wait_for_ready_state_complete()
        self.__demo_mode_pause_if_active()

    def get_url(self, url):
        """打开网址并验证"""
        self.driver.maximize_window()
        self.driver.set_page_load_timeout(60)
        try:
            self.driver.get(url)
            self.driver.implicitly_wait(10)
            log.info("打开网页：%s" % url)
        except TimeoutException:
            raise TimeoutException("打开%s超时请检查网络或网址服务器" % url)

    @staticmethod
    def element_locator(func, locator):
        """元素定位器"""
        name, value = locator
        return func(cm.LOCATE_MODE[name], value)

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


    def sleep(self, seconds):
        self.__check_scope()
        if not config.time_limit:
            time.sleep(seconds)
        elif seconds < 0.4:
            shared_utils.check_if_time_limit_exceeded()
            time.sleep(seconds)
            shared_utils.check_if_time_limit_exceeded()
        else:
            start_ms = time.time() * 1000.0
            stop_ms = start_ms + (seconds * 1000.0)
            for x in range(int(seconds * 5)):
                shared_utils.check_if_time_limit_exceeded()
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.2)

    ############

    def __check_scope(self):
        if hasattr(self, "browser"):  # self.browser stores the type of browser
            return  # All good: setUp() already initialized variables in "self"
        else:
            from common.exceptions import OutOfScopeException

            message = (
                "\n It looks like you are trying to call a SeleniumBase method"
                "\n from outside the scope of your test class's `self` object,"
                "\n which is initialized by calling BaseCase's setUp() method."
                "\n The `self` object is where all test variables are defined."
                "\n If you created a custom setUp() method (that overrided the"
                "\n the default one), make sure to call super().setUp() in it."
                "\n When using page objects, be sure to pass the `self` object"
                "\n from your test class into your page object methods so that"
                "\n they can call BaseCase class methods with all the required"
                "\n variables, which are initialized during the setUp() method"
                "\n that runs automatically before all tests called by pytest."
            )
            raise OutOfScopeException(message)

    ############

    def __check_browser(self):
        """This method raises an exception if the window was already closed."""
        active_window = None
        try:
            active_window = self.driver.current_window_handle  # Fails if None
        except Exception:
            pass
        if not active_window:
            raise NoSuchWindowException("Active window was already closed!")

    ############

    def __looks_like_a_page_url(self, url):
        """Returns True if the url parameter looks like a URL. This method
        is slightly more lenient than page_utils.is_valid_url(url) due to
        possible typos when calling self.get(url), which will try to
        navigate to the page if a URL is detected, but will instead call
        self.get_element(URL_AS_A_SELECTOR) if the input in not a URL."""
        if (
            url.startswith("http:")
            or url.startswith("https:")
            or url.startswith("://")
            or url.startswith("chrome:")
            or url.startswith("about:")
            or url.startswith("data:")
            or url.startswith("file:")
            or url.startswith("edge:")
            or url.startswith("opera:")
            or url.startswith("view-source:")
        ):
            return True
        else:
            return False



if __name__ == "__main__":
    pass
