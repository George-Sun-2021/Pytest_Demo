#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
selenium基类
本文件存放了selenium基类的封装方法
"""
import sys

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotVisibleException,
    NoSuchAttributeException,
    ElementClickInterceptedException as ECI_Exception,
    ElementNotInteractableException as ENI_Exception,
    MoveTargetOutOfBoundsException,
    NoSuchWindowException,
    StaleElementReferenceException,
    WebDriverException,
    TimeoutException,
)

from utils import css_to_xpath, time
from config import configs
from config.path_manager import pm
from page import page_utils
import logging


class BasePage(object):
    """selenium base methods"""

    def __init__(self, driver, *args, **kwargs):
        # super(BasePage, self).__init__(*args, **kwargs)

        # self.driver = webdriver.Chrome()
        self.driver = driver
        self.environment = None
        self.env = None  # Add a shortened version of self.environment
        self.poll_frequency = configs.POLL_FREQUENCY
        self.timeout = configs.LARGE_TIMEOUT
        self.wait = WebDriverWait(self.driver, self.timeout)  # define WebDriverWait()

    ############

    # Using (Used page Actions)

    def visit(self, url):
        """
        open the url
        @param url:target url to test
        """
        self.driver.set_page_load_timeout(configs.PAGE_LOAD_TIMEOUT)
        self.driver.implicitly_wait(configs.EXTREME_TIMEOUT)
        try:
            self.driver.get(url)
            logging.info("opening website：%s" % url)
        except TimeoutException:
            raise TimeoutException("open'%s' timeout, please check the network or web server correct or not" % url)

    def click(self, selector, by=By.XPATH, delay=0, scroll=True):
        original_selector = selector
        original_by = by
        selector, by = self.__recalculate_selector(selector, by)
        if delay and (type(delay) in [int, float]) and delay > 0:
            time.sleep(delay)
        if page_utils.is_link_text_selector(selector) or by == By.LINK_TEXT:
            if not self.is_link_text_visible(selector):
                # Handle a special case of links hidden in dropdowns
                self.click_link_text(selector, timeout=timeout)
                return
        if (
                page_utils.is_partial_link_text_selector(selector)
                or by == By.PARTIAL_LINK_TEXT
        ):
            if not self.is_partial_link_text_visible(selector):
                # Handle a special case of partial links hidden in dropdowns
                self.click_partial_link_text(selector, timeout=timeout)
                return
        element = page_actions.wait_for_element_visible(
            self.driver, selector, by, timeout=timeout
        )
        if scroll:
            self.__scroll_to_element(element, selector, by)
        pre_action_url = self.driver.current_url
        pre_window_count = len(self.driver.window_handles)
        try:
            if self.browser == "ie" and by == By.LINK_TEXT:
                # An issue with clicking Link Text on IE means using jquery
                self.__jquery_click(selector, by=by)
            elif self.browser == "safari":
                if by == By.LINK_TEXT:
                    self.__jquery_click(selector, by=by)
                else:
                    self.__js_click(selector, by=by)
            else:
                href = None
                new_tab = False
                onclick = None
                try:
                    if self.headless and element.tag_name == "a":
                        # Handle a special case of opening a new tab (headless)
                        href = element.get_attribute("href").strip()
                        onclick = element.get_attribute("onclick")
                        target = element.get_attribute("target")
                        if target == "_blank":
                            new_tab = True
                        if new_tab and self.__looks_like_a_page_url(href):
                            if onclick:
                                try:
                                    self.execute_script(onclick)
                                except Exception:
                                    pass
                            current_window = self.driver.current_window_handle
                            self.open_new_window()
                            try:
                                self.open(href)
                            except Exception:
                                pass
                            self.switch_to_window(current_window)
                            return
                except Exception:
                    pass
                # Normal click
                element.click()
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.16)
            element = page_actions.wait_for_element_visible(
                self.driver, selector, by, timeout=timeout
            )
            try:
                self.__scroll_to_element(element, selector, by)
            except Exception:
                pass
            if self.browser == "safari":
                if by == By.LINK_TEXT:
                    self.__jquery_click(selector, by=by)
                else:
                    self.__js_click(selector, by=by)
            else:
                element.click()
        except ENI_Exception:
            self.wait_for_ready_state_complete()
            time.sleep(0.1)
            element = page_actions.wait_for_element_visible(
                self.driver, selector, by, timeout=timeout
            )
            href = None
            new_tab = False
            onclick = None
            try:
                if element.tag_name == "a":
                    # Handle a special case of opening a new tab (non-headless)
                    href = element.get_attribute("href").strip()
                    onclick = element.get_attribute("onclick")
                    target = element.get_attribute("target")
                    if target == "_blank":
                        new_tab = True
                    if new_tab and self.__looks_like_a_page_url(href):
                        if onclick:
                            try:
                                self.execute_script(onclick)
                            except Exception:
                                pass
                        current_window = self.driver.current_window_handle
                        self.open_new_window()
                        try:
                            self.open(href)
                        except Exception:
                            pass
                        self.switch_to_window(current_window)
                        return
            except Exception:
                pass
            self.__scroll_to_element(element, selector, by)
            if self.browser == "firefox" or self.browser == "safari":
                if by == By.LINK_TEXT or "contains(" in selector:
                    self.__jquery_click(selector, by=by)
                else:
                    self.__js_click(selector, by=by)
            else:
                element.click()
        except (WebDriverException, MoveTargetOutOfBoundsException):
            self.wait_for_ready_state_complete()
            try:
                self.__js_click(selector, by=by)
            except Exception:
                try:
                    self.__jquery_click(selector, by=by)
                except Exception:
                    # One more attempt to click on the element
                    element = page_actions.wait_for_element_visible(
                        self.driver, selector, by, timeout=timeout
                    )
                    element.click()
        latest_window_count = len(self.driver.window_handles)
        if (
                latest_window_count > pre_window_count
                and (
                self.recorder_mode
                or (
                        settings.SWITCH_TO_NEW_TABS_ON_CLICK
                        and self.driver.current_url == pre_action_url
                )
        )
        ):
            self.__switch_to_newest_window_if_not_blank()
        if settings.WAIT_FOR_RSC_ON_CLICKS:
            self.wait_for_ready_state_complete()
        else:
            # A smaller subset of self.wait_for_ready_state_complete()
            self.wait_for_angularjs(timeout=settings.MINI_TIMEOUT)
            if self.driver.current_url != pre_action_url:
                self.__ad_block_as_needed()
        if self.demo_mode:
            if self.driver.current_url != pre_action_url:
                self.__demo_mode_pause_if_active()
            else:
                self.__demo_mode_pause_if_active(tiny=True)
        elif self.slow_mode:
            self.__slow_mode_pause_if_active()

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
            timeout = configs.SMALL_TIMEOUT
        if type(frame) is str and self.is_element_visible(frame):
            try:
                self.scroll_to(frame, timeout=1)
            except Exception:
                pass
        page_utils.switch_to_frame(self.driver, frame, timeout)

    ############

    # if conditions for elements

    def is_element_present(self, selector, by=By.XPATH):
        return page_utils.is_element_present(self.driver, selector, by)

    def is_element_visible(self, selector, by=By.XPATH):
        return page_utils.is_element_visible(self.driver, selector, by)

    def is_element_enabled(self, selector, by=By.XPATH):
        return page_utils.is_element_enabled(self.driver, selector, by)

    def is_text_visible(self, text, selector="html", by=By.XPATH):
        return page_utils.is_text_visible(self.driver, text, selector, by)

    def is_attribute_present(self, selector, attribute, value=None, by=By.XPATH):
        """Returns True if the element attribute/value is found.
        If the value is not specified, the attribute only needs to exist."""
        return page_utils.is_attribute_present(
            self.driver, selector, attribute, value, by
        )

    def is_link_text_visible(self, link_text):
        return page_utils.is_element_visible(
            self.driver, link_text, by=By.LINK_TEXT
        )

    def is_partial_link_text_visible(self, partial_link_text):
        return page_utils.is_element_visible(
            self.driver, partial_link_text, by=By.PARTIAL_LINK_TEXT
        )

    ############

    # Bases (Basic page actions)

    @staticmethod
    def convert_css_to_xpath(css):
        return css_to_xpath.convert_css_to_xpath(css)

    def __recalculate_selector(self, selector, by, xp_ok=True):
        """Use auto-detection to return the correct selector with "by" updated.
        If "xp_ok" is False, don't call convert_css_to_xpath(), which is
        used to make the ":contains()" selector valid outside JS calls."""
        _type = type(selector)  # First make sure the selector is a string
        not_string = False
        if _type is not str:
            not_string = True
        if not_string:
            msg = "Expecting a selector of type: \"<class 'str'>\" (string)!"
            raise Exception('Invalid selector type: "%s"\n%s' % (_type, msg))
        if page_utils.is_xpath_selector(selector):
            by = By.XPATH
        if page_utils.is_link_text_selector(selector):
            selector = page_utils.get_link_text_from_selector(selector)
            by = By.LINK_TEXT
        if page_utils.is_partial_link_text_selector(selector):
            selector = page_utils.get_partial_link_text_from_selector(selector)
            by = By.PARTIAL_LINK_TEXT
        if page_utils.is_name_selector(selector):
            name = page_utils.get_name_from_selector(selector)
            selector = '[name="%s"]' % name
            by = By.CSS_SELECTOR
        if xp_ok:
            if ":contains(" in selector and by == By.CSS_SELECTOR:
                selector = self.convert_css_to_xpath(selector)
                by = By.XPATH
        return (selector, by)

    ############

    # find element(s) with wait timeout

    def wait_for_element_present(self, selector, by=By.XPATH):
        """
        Searches for the specified element by the given selector. Returns the
        element object if it exists in the HTML. (The element can be invisible.)
        Raises NoSuchElementException if the element does not exist in the HTML
        within the specified timeout.
        @Params
        selector - the locator for identifying the page element (required)
        by - the type of selector being used (Default: By.XPATH)
        @Returns
        A web element object
        """
        locator = (by, selector)
        try:
            # return self.wait.until(self.driver.find_element(*locator))
            return self.wait.until(EC.presence_of_element_located(*locator))
        except Exception:
            message = "Element {%s} was not present after %s seconds!" % (selector, self.timeout)
        logging.info(page_utils.timeout_exception(NoSuchElementException, message))

    def wait_for_element_visible(self, selector, by=By.XPATH):
        """
        Searches for the specified element by the given selector. Returns the
        element object if the element is present and visible on the page.
        Raises NoSuchElementException if the element does not exist in the HTML
        within the specified timeout.
        Raises ElementNotVisibleException if the element exists in the HTML,
        but is not visible (eg. opacity is "0") within the specified timeout.
        @Params
        selector - the locator for identifying the page element (required)
        by - the type of selector being used (Default: By.XPATH)
        @Returns
        A web element object
        """
        locator = (by, selector)
        try:
            # return self.wait.until(lambda x: x.find_element(*locator))
            return self.wait.until(EC.visibility_of_element_located(*locator))
        except Exception:
            message = "Element {%s} was not visible after %s seconds!" % (selector, self.timeout)
            logging.info(page_utils.timeout_exception(ElementNotVisibleException, message))

    def wait_for_element_clickable(self, selector, by=By.XPATH):
        """
        Searches for the specified element by the given selector. Returns the
        element object if the element is present and visible on the page.
        Raises NoSuchElementException if the element does not exist in the HTML
        within the specified timeout.
        Raises ElementNotVisibleException if the element exists in the HTML,
        but is not visible (eg. opacity is "0") within the specified timeout.
        @Params
        selector - the locator for identifying the page element (required)
        by - the type of selector being used (Default: By.XPATH)
        @Returns
        A web element object
        """
        locator = (by, selector)
        try:
            # return self.wait.until(lambda x: x.find_element(*locator))
            return self.wait.until(EC.element_to_be_clickable(*locator))
        except Exception:
            message = "Element {%s} was not clickable after %s seconds!" % (selector, self.timeout)
            logging.info(page_utils.timeout_exception(ElementNotVisibleException, message))

    def wait_for_text_visible(self, text, selector, by=By.XPATH):
        """
        Searches for the specified element by the given selector. Returns the
        element object if the text is present in the element and visible
        on the page.
        Raises ElementNotVisibleException if the element exists in the HTML,
        but the text is not visible within the specified timeout.
        @Params
        text - the text that is being searched for in the element (required)
        selector - the locator for identifying the page element (required)
        by - the type of selector being used (Default: By.XPATH)
        @Returns
        A web element object that contains the text searched for
        """
        locator = (by, selector)
        try:
            return self.wait.until(EC.text_to_be_present_in_element(*locator, text))
        except ElementNotVisibleException:
            message = "Expected text {%s} for {%s} was not visible after %s seconds!" % (text, selector, self.timeout)
            logging.info(page_utils.timeout_exception(ElementNotVisibleException, message))

    def wait_for_text_visible_in_value(self, text, selector, by=By.XPATH):
        """
        Searches for the specified element by the given selector. Returns the
        element object if the text is present in the element value attribute and visible
        on the page.
        Raises ElementNotVisibleException if the element exists in the HTML,
        but the text is not visible within the specified timeout.
        @Params
        text - the text that is being searched for in the element (required)
        selector - the locator for identifying the page element (required)
        by - the type of selector being used (Default: By.XPATH)
        @Returns
        A web element object that contains the text searched for
        """
        locator = (by, selector)
        try:
            return self.wait.until(EC.text_to_be_present_in_element_value(*locator, text))
        except ElementNotVisibleException:
            message = "Expected text {%s} in {%s} value was not visible after %s seconds!" % (
                text, selector, self.timeout)
            logging.info(page_utils.timeout_exception(ElementNotVisibleException, message))

    def wait_for_attribute(self, selector, attribute, value=None, by=By.XPATH):
        """
        Searches for the specified element attribute by the given selector.
        Returns the element object if the expected attribute is present
        and the expected attribute value is present (if specified).
        Raises NoSuchElementException if the element does not exist in the HTML
        within the specified timeout.
        Raises NoSuchAttributeException if the element exists in the HTML,
        but the expected attribute/value is not present within the timeout.
        @Params
        selector - the locator for identifying the page element (required)
        attribute - the attribute that is expected for the element (required)
        value - the attribute value that is expected (Default: None)
        by - the type of selector being used (Default: By.XPATH)
        @Returns
        A web element object that contains the expected attribute/value
        """
        locator = (by, selector)
        element = None
        element_present = False
        attribute_present = False
        found_value = None
        try:
            element = self.wait.until(lambda x: x.find_element(*locator))
            element_present = True
            attribute_present = False
            found_value = element.get_attribute(attribute)
            if found_value is not None:
                attribute_present = True
            else:
                element = None
                raise Exception()
            if value is not None:
                if found_value == value:
                    return element
                else:
                    element = None
                    raise Exception()
            else:
                return element
        except Exception:
            if not element:
                if not element_present:
                    # The element does not exist in the HTML
                    message = "Element {%s} was not present after %s seconds!" % (selector, self.timeout)
                    logging.info(page_utils.timeout_exception(NoSuchElementException, message))
                if not attribute_present:
                    # The element does not have the attribute
                    message = ("Expected attribute {%s} of element {%s} was not present after %s seconds!" % (
                        attribute, selector, self.timeout))
                    logging.info(page_utils.timeout_exception(NoSuchAttributeException, message))
            # The element attribute exists, but the expected value does not match
            message = (
                    "Expected value {%s} for attribute {%s} of element {%s} was not present after %s seconds!"
                    "(The actual value was {%s})" % (value, attribute, selector, self.timeout, found_value))
            logging.info(page_utils.timeout_exception(NoSuchAttributeException, message))

    def wait_for_element_absent(self, selector, by=By.XPATH):
        """
        Searches for the specified element by the given selector.
        Raises an exception if the element is still present after the
        specified timeout.
        @Params
        selector - the locator for identifying the page element (required)
        by - the type of selector being used (Default: By.XPATH)
        """
        if not self.is_element_present(selector, by=by):
            return True
        else:
            message = "Element {%s} was still present after %s seconds!" % (selector, self.timeout)
            logging.info(page_utils.timeout_exception(Exception, message))

    def wait_for_element_not_visible(self, selector, by=By.XPATH):
        """
        Searches for the specified element by the given selector.
        Raises an exception if the element is still visible after the
        specified timeout.
        @Params
        driver - the webdriver object (required)
        selector - the locator for identifying the page element (required)
        by - the type of selector being used (Default: By.CSS_SELECTOR)
        timeout - the time to wait for the element in seconds
        """
        locator = (by, selector)
        try:
            return self.wait.until(EC.invisibility_of_element_located(*locator))
        except Exception:
            message = "Element {%s} was still visible after %s seconds!" % (selector, self.timeout)
            logging.info(page_utils.timeout_exception(Exception, message))

    def wait_for_text_not_visible(self, text, selector, by=By.XPATH):
        """
        Searches for the text in the element of the given selector on the page.
        Returns True if the text is not visible on the page within the timeout.
        Raises an exception if the text is still present after the timeout.
        @Params
        text - the text that is being searched for in the element (required)
        selector - the locator for identifying the page element (required)
        by - the type of selector being used (Default: By.XPATH)
        @Returns
        A web element object that contains the text searched for
        """
        if not self.is_text_visible(text, selector, by=by):
            return True
        message = "Text {%s} in {%s} was still visible after %s seconds!" % (text, selector, self.timeout)
        logging.info(page_utils.timeout_exception(Exception, message))

    def wait_for_attribute_not_present(self, selector, attribute, value=None, by=By.XPATH):
        """
        Searches for the specified element attribute by the given selector.
        Returns True if the attribute isn't present on the page within the timeout.
        Also returns True if the element is not present within the timeout.
        Raises an exception if the attribute is still present after the timeout.
        @Params
        selector - the locator for identifying the page element (required)
        attribute - the element attribute (required)
        value - the attribute value (Default: None)
        by - the type of selector being used (Default: By.XPATH)
        """
        if not self.is_attribute_present(selector, attribute, value=value, by=by):
            return True
        message = (
                "Attribute {%s} of element {%s} was still present after %s seconds!" % (
            attribute, selector, self.timeout))
        if value:
            message = (
                    "Value {%s} for attribute {%s} of element {%s} was still present after %s seconds!" % (
                value, attribute, selector, self.timeout))
        logging.info(page_utils.timeout_exception(Exception, message))

    def find_visible_elements(self, selector, by=By.XPATH):
        """
        Finds all WebElements that match a selector and are visible.
        Similar to webdriver.find_elements.
        @Params
        driver - the webdriver object (required)
        selector - the locator for identifying the page element (required)
        by - the type of selector being used (Default: By.CSS_SELECTOR)
        """
        locator = (by, selector)
        try:
            # return self.wait.until(self.driver.find_element(*locator))
            return self.wait.until(EC.presence_of_all_elements_located(*locator))
        except Exception:
            message = "Elements {%s} were not visible after %s seconds!" % (selector, self.timeout)
            logging.info(page_utils.timeout_exception(ElementNotVisibleException, message))


if __name__ == "__main__":
    pass
