#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
selenium基类
本文件存放了selenium基类的封装方法
"""

import re
import sys

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotVisibleException,
    NoSuchAttributeException,
    NoSuchFrameException,
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

    def click(self, selector, by=By.CSS_SELECTOR, delay=0, scroll=True):
        """
        click the button/link
        @Params
        selector - the selector of the text field
        by - the type of selector to search by (Default: CSS_SELECTOR)
        delay - delay some time before perform the click (Default: 0)
        scroll - scroll to the element after click (Default: true)
        """
        selector, by = self.__recalculate_selector(selector, by)
        if delay and (type(delay) in [int, float]) and delay > 0:
            time.sleep(delay)
        element = self.wait_for_element_visible(selector, by)
        if scroll:
            self.__scroll_to_element(element, selector, by)
        try:
            element.click()  # Normal click
        except StaleElementReferenceException:
            time.sleep(0.16)
            element = self.wait_for_element_visible(selector, by)
            try:
                self.__scroll_to_element(element, selector, by)
            except Exception:
                pass
            else:
                element.click()
        except ENI_Exception:
            time.sleep(0.1)
            element = self.wait_for_element_visible(selector, by)
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
                            self.visit(href)
                        except Exception:
                            pass
                        self.switch_to_window(current_window)
                        return
            except Exception:
                pass
            self.__scroll_to_element(element, selector, by)
            element.click()

    def type(self, selector, by=By.CSS_SELECTOR, text=None):
        """Same as self.update_text()
        This method updates an element's text field with new text.
        Has multiple parts:
        * Waits for the element to be visible.
        * Waits for the element to be interactive.
        * Clears the text field.
        * Types in the new text.
        * Hits Enter/Submit (if the text ends in "\n").
        @Params
        selector - the selector of the text field
        text - the new text to type into the text field
        by - the type of selector to search by (Default: CSS_SELECTOR)
        """
        selector, by = self.__recalculate_selector(selector, by)
        self.update_text(selector, by=by, text=text)

    def clear(self, selector, by=By.CSS_SELECTOR):
        """This method clears an element's text field.
        A clear() is already included with most methods that type text,
        such as self.type(), self.update_text(), etc.
        Does not use Demo Mode highlights, mainly because we expect
        that some users will be calling an unnecessary clear() before
        calling a method that already includes clear() as part of it.
        In case websites trigger an autofill after clearing a field,
        add backspaces to make sure autofill doesn't undo the clear.
        @Params
        selector - the selector of the text field
        by - the type of selector to search by (Default: CSS_SELECTOR)
        """
        selector, by = self.__recalculate_selector(selector, by)
        element = self.wait_for_element_visible(selector, by=by)
        self.scroll_to(selector, by=by)
        try:
            element.clear()
            backspaces = Keys.BACK_SPACE * 42  # Autofill Defense
            element.send_keys(backspaces)
        except (StaleElementReferenceException, ENI_Exception):
            time.sleep(0.16)
            element = self.wait_for_element_visible(selector, by=by)
            element.clear()
            try:
                backspaces = Keys.BACK_SPACE * 42  # Autofill Defense
                element.send_keys(backspaces)
            except Exception:
                pass
        except Exception:
            element.clear()

    def submit(self, selector, by=By.CSS_SELECTOR):
        """ Alternative to self.driver.find_element_by_*(SELECTOR).submit() """
        selector, by = self.__recalculate_selector(selector, by)
        element = self.wait_for_element_visible(selector, by=by)
        element.submit()

    def get_title(self):
        """ The shorter version of self.get_page_title() """
        return self.get_page_title()

    def scroll_to(self, selector, by=By.CSS_SELECTOR):
        """ Fast scroll to destination """
        element = self.wait_for_element_visible(selector, by=by)
        try:
            self.__scroll_to_element(element, selector, by)
        except (StaleElementReferenceException, ENI_Exception):
            time.sleep(0.12)
            element = self.wait_for_element_visible(selector, by=by)
            self.__scroll_to_element(element, selector, by)

    def go_back(self):
        self.driver.back()

    def go_forward(self):
        self.driver.forward()

    def refresh(self):
        """ The shorter version of self.refresh_page() """
        self.refresh_page()

    def get_text(self, selector, by=By.CSS_SELECTOR):
        selector, by = self.__recalculate_selector(selector, by)
        element = self.wait_for_element_visible(selector, by)
        try:
            element_text = element.text
        except (StaleElementReferenceException, ENI_Exception):
            time.sleep(0.14)
            element = self.wait_for_element_visible(selector, by)
            element_text = element.text
        return element_text

    def add_text(self, selector, by=By.CSS_SELECTOR, text=None):
        """The more-reliable version of driver.send_keys()
        Similar to update_text(), but won't clear the text field first."""
        selector, by = self.__recalculate_selector(selector, by)
        element = self.wait_for_element_visible(selector, by=by)
        self.__scroll_to_element(element, selector, by)
        if type(text) is int or type(text) is float:
            text = str(text)
        try:
            if not text.endswith("\n"):
                element.send_keys(text)
            else:
                element.send_keys(text[:-1])
                element.send_keys(Keys.RETURN)
        except (StaleElementReferenceException, ENI_Exception):
            time.sleep(0.16)
            element = self.wait_for_element_visible(selector, by=by)
            if not text.endswith("\n"):
                element.send_keys(text)
            else:
                element.send_keys(text[:-1])
                element.send_keys(Keys.RETURN)

    def find_visible_elements(self, selector, by=By.CSS_SELECTOR):
        """
        Finds all WebElements that match a selector and are visible.
        Similar to webdriver.find_elements.
        @Params
        driver - the webdriver object (required)
        selector - the locator for identifying the page element (required)
        by - the type of selector being used (Default: By.CSS_SELECTOR)
        """
        selector, by = self.__recalculate_selector(selector, by)
        locator = (by, selector)
        try:
            # return self.wait.until(self.driver.find_element(*locator))
            return self.wait.until(EC.presence_of_all_elements_located(locator))
        except Exception:
            message = "Elements {%s} were not visible after %s seconds!" % (selector, self.timeout)
            logging.info(page_utils.timeout_exception(ElementNotVisibleException, message))

    @property
    def get_page_source(self):
        """
        get page resource
        """
        return self.driver.page_source

    def set_window_size(self, width, height):
        self.driver.set_window_size(width, height)

    def maximize_window(self):
        self.driver.maximize_window()

    def switch_to_frame(self, frame):
        """Wait for an iframe to appear, and switch to it. This should be
        usable as a drop-in replacement for driver.switch_to.frame().
        The iframe identifier can be a selector, an index, an id, a name,
        or a web element, but scrolling to the iframe first will only occur
        for visible iframes with a string selector.
        @Params
        frame - the frame element, name, id, index, or selector
        timeout - the time to wait for the alert in seconds
        """
        if type(frame) is str and self.is_element_visible(frame):
            try:
                self.scroll_to(frame)
            except Exception:
                pass
        try:
            self.wait.until(EC.frame_to_be_available_and_switch_to_it(self.driver.switch_to.frame(frame)))
            return True
        except NoSuchFrameException:
            if type(frame) is str:
                by = None
                if page_utils.is_xpath_selector(frame):
                    by = By.XPATH
                else:
                    by = By.CSS_SELECTOR
                if page_utils.is_element_visible(self.driver, frame, by=by):
                    try:
                        element = self.driver.find_element(by=by, value=frame)
                        self.driver.switch_to.frame(element)
                        return True
                    except Exception:
                        pass
            time.sleep(0.1)
        message = "Frame {%s} was not visible after %s seconds!" % (frame, self.timeout)
        page_utils.timeout_exception(Exception, message)

    def switch_to_window(self, window):
        """ Switches control of the browser to the specified window.
            The window can be an integer: 0 -> 1st tab, 1 -> 2nd tab, etc...
                Or it can be a list item from self.driver.window_handles """
        if isinstance(window, int):
            try:
                window_handle = self.wait.until(self.driver.window_handles[window])
                self.driver.switch_to.window(window_handle)
                return True
            except Exception:
                message = "Window {%s} was not present after %s seconds!" % (window, self.timeout)
                page_utils.timeout_exception(Exception, message)
        else:
            window_handle = window
            try:
                self.wait.until(self.driver.switch_to.window(window_handle))
                return True
            except Exception:
                message = "Window {%s} was not present after %s seconds!" % (window, self.timeout)
                page_utils.timeout_exception(Exception, message)

    def hover_on_element(self, selector, by=By.CSS_SELECTOR):
        selector, by = self.__recalculate_selector(selector, by)
        if page_utils.is_xpath_selector(selector):
            selector = self.convert_to_css_selector(selector, By.XPATH)
            by = By.CSS_SELECTOR
        self.wait_for_element_visible(selector, by=by)
        self.scroll_to(selector, by=by)
        time.sleep(0.05)  # Settle down from scrolling before hovering
        try:
            return page_utils.hover_on_element(self.driver, selector)
        except WebDriverException as e:
            driver_capabilities = self.driver.__dict__["capabilities"]
            if "version" in driver_capabilities:
                chrome_version = driver_capabilities["version"]
            else:
                chrome_version = driver_capabilities["browserVersion"]
            major_chrome_version = chrome_version.split(".")[0]
            chrome_dict = self.driver.__dict__["capabilities"]["chrome"]
            chromedriver_version = chrome_dict["chromedriverVersion"]
            chromedriver_version = chromedriver_version.split(" ")[0]
            major_chromedriver_version = chromedriver_version.split(".")[0]
            if major_chromedriver_version < major_chrome_version:
                # Upgrading the driver is required for performing hover actions
                message = (
                        "\n"
                        "You need a newer chromedriver to perform hover actions!\n"
                        "Your version of chromedriver is: %s\n"
                        "And your version of Chrome is: %s\n"
                        "You can fix this issue by install the right version of chrome driver\n"
                        % (chromedriver_version, chrome_version)
                )
                raise Exception(message)
            else:
                raise Exception(e)

    def hover_and_click(
            self,
            hover_selector,
            click_selector,
            hover_by=By.CSS_SELECTOR,
            click_by=By.CSS_SELECTOR
    ):
        """When you want to hover over an element or dropdown menu,
        and then click an element that appears after that."""
        hover_selector, hover_by = self.__recalculate_selector(
            hover_selector, hover_by
        )
        hover_selector = self.convert_to_css_selector(hover_selector, hover_by)
        hover_by = By.CSS_SELECTOR
        click_selector, click_by = self.__recalculate_selector(click_selector, click_by)
        dropdown_element = self.wait_for_element_visible(hover_selector, by=hover_by)
        self.scroll_to(hover_selector, by=hover_by)
        pre_action_url = self.driver.current_url
        pre_window_count = len(self.driver.window_handles)
        outdated_driver = False
        element = None
        try:
            page_utils.hover_element(self.driver, dropdown_element)
        except Exception:
            outdated_driver = True
            element = self.wait_for_element_present(click_selector, click_by)
            if click_by == By.LINK_TEXT:
                self.visit(self.__get_href_from_link_text(click_selector))
            elif click_by == By.PARTIAL_LINK_TEXT:
                self.visit(self.__get_href_from_partial_link_text(click_selector))
            else:
                self.js_click(click_selector, by=click_by)
        if outdated_driver:
            pass  # Already did the click workaround
        elif not outdated_driver:
            element = page_utils.hover_and_click(self.driver, hover_selector, click_selector, hover_by, click_by)
        latest_window_count = len(self.driver.window_handles)
        if (latest_window_count > pre_window_count
                and self.driver.current_url == pre_action_url):
            self.__switch_to_newest_window_if_not_blank()
        return element

    def hover_and_double_click(
            self,
            hover_selector,
            click_selector,
            hover_by=By.CSS_SELECTOR,
            click_by=By.CSS_SELECTOR,
            timeout=None,
    ):
        """When you want to hover over an element or dropdown menu,
        and then double-click an element that appears after that."""
        self.__check_scope()
        if not timeout:
            timeout = settings.SMALL_TIMEOUT
        if self.timeout_multiplier and timeout == settings.SMALL_TIMEOUT:
            timeout = self.__get_new_timeout(timeout)
        original_selector = hover_selector
        original_by = hover_by
        hover_selector, hover_by = self.__recalculate_selector(
            hover_selector, hover_by
        )
        hover_selector = self.convert_to_css_selector(hover_selector, hover_by)
        hover_by = By.CSS_SELECTOR
        click_selector, click_by = self.__recalculate_selector(
            click_selector, click_by
        )
        dropdown_element = self.wait_for_element_visible(
            hover_selector, by=hover_by, timeout=timeout
        )
        self.__demo_mode_highlight_if_active(original_selector, original_by)
        self.scroll_to(hover_selector, by=hover_by)
        pre_action_url = self.driver.current_url
        pre_window_count = len(self.driver.window_handles)
        outdated_driver = False
        element = None
        try:
            page_actions.hover_element(self.driver, dropdown_element)
        except Exception:
            outdated_driver = True
            element = self.wait_for_element_present(
                click_selector, click_by, timeout
            )
            if click_by == By.LINK_TEXT:
                self.open(self.__get_href_from_link_text(click_selector))
            elif click_by == By.PARTIAL_LINK_TEXT:
                self.open(
                    self.__get_href_from_partial_link_text(click_selector)
                )
            else:
                self.__dont_record_js_click = True
                self.js_click(click_selector, click_by)
                self.__dont_record_js_click = False
        if not outdated_driver:
            element = page_actions.hover_element_and_double_click(
                self.driver,
                dropdown_element,
                click_selector,
                click_by=By.CSS_SELECTOR,
                timeout=timeout,
            )
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
        if self.demo_mode:
            if self.driver.current_url != pre_action_url:
                self.__demo_mode_pause_if_active()
            else:
                self.__demo_mode_pause_if_active(tiny=True)
        elif self.slow_mode:
            self.__slow_mode_pause_if_active()
        return element

    def drag_and_drop(
            self,
            drag_selector,
            drop_selector,
            drag_by=By.CSS_SELECTOR,
            drop_by=By.CSS_SELECTOR,
            timeout=None,
    ):
        """ Drag and drop an element from one selector to another. """
        self.__check_scope()
        if not timeout:
            timeout = settings.SMALL_TIMEOUT
        if self.timeout_multiplier and timeout == settings.SMALL_TIMEOUT:
            timeout = self.__get_new_timeout(timeout)
        drag_selector, drag_by = self.__recalculate_selector(
            drag_selector, drag_by
        )
        drop_selector, drop_by = self.__recalculate_selector(
            drop_selector, drop_by
        )
        drag_element = self.wait_for_element_visible(
            drag_selector, by=drag_by, timeout=timeout
        )
        self.__demo_mode_highlight_if_active(drag_selector, drag_by)
        self.wait_for_element_visible(
            drop_selector, by=drop_by, timeout=timeout
        )
        self.__demo_mode_highlight_if_active(drop_selector, drop_by)
        self.scroll_to(drag_selector, by=drag_by)
        drag_selector = self.convert_to_css_selector(drag_selector, drag_by)
        drop_selector = self.convert_to_css_selector(drop_selector, drop_by)
        drag_and_drop_script = js_utils.get_drag_and_drop_script()
        self.safe_execute_script(
            drag_and_drop_script
            + (
                    "$('%s').simulateDragDrop("
                    "{dropTarget: "
                    "'%s'});" % (drag_selector, drop_selector)
            )
        )
        if self.demo_mode:
            self.__demo_mode_pause_if_active()
        elif self.slow_mode:
            self.__slow_mode_pause_if_active()
        return drag_element

    def drag_and_drop_with_offset(
            self, selector, x, y, by=By.CSS_SELECTOR, timeout=None
    ):
        """ Drag and drop an element to an {X,Y}-offset location. """
        self.__check_scope()
        if not timeout:
            timeout = settings.SMALL_TIMEOUT
        if self.timeout_multiplier and timeout == settings.SMALL_TIMEOUT:
            timeout = self.__get_new_timeout(timeout)
        selector, by = self.__recalculate_selector(selector, by)
        css_selector = self.convert_to_css_selector(selector, by=by)
        element = self.wait_for_element_visible(css_selector, timeout=timeout)
        self.__demo_mode_highlight_if_active(css_selector, By.CSS_SELECTOR)
        css_selector = re.escape(css_selector)  # Add "\\" to special chars
        css_selector = self.__escape_quotes_if_needed(css_selector)
        script = js_utils.get_drag_and_drop_with_offset_script(
            css_selector, x, y
        )
        self.safe_execute_script(script)
        if self.demo_mode:
            self.__demo_mode_pause_if_active()
        elif self.slow_mode:
            self.__slow_mode_pause_if_active()
        return element

    def select_option_by_text(self, dropdown_selector, option, dropdown_by=By.CSS_SELECTOR):
        """Selects an HTML <select> option by option text.
        @Params
        dropdown_selector - the <select> selector.
        option - the text of the option.
        """
        self.__select_option(dropdown_selector, option, dropdown_by=dropdown_by, option_by="text")

    def select_option_by_index(self, dropdown_selector, option, dropdown_by=By.CSS_SELECTOR):
        """Selects an HTML <select> option by option index.
        @Params
        dropdown_selector - the <select> selector.
        option - the index number of the option.
        """
        self.__select_option(dropdown_selector, option, dropdown_by=dropdown_by, option_by="index")

    def select_option_by_value(self, dropdown_selector, option, dropdown_by=By.CSS_SELECTOR):
        """Selects an HTML <select> option by option value.
        @Params
        dropdown_selector - the <select> selector.
        option - the value property of the option.
        """
        self.__select_option(dropdown_selector, option, dropdown_by=dropdown_by, option_by="value")

    ############

    # if conditions for elements

    def is_element_present(self, selector, by=By.CSS_SELECTOR):
        return page_utils.is_element_present(self.driver, selector, by)

    def is_element_visible(self, selector, by=By.CSS_SELECTOR):
        return page_utils.is_element_visible(self.driver, selector, by)

    def is_element_enabled(self, selector, by=By.CSS_SELECTOR):
        return page_utils.is_element_enabled(self.driver, selector, by)

    def is_text_visible(self, text, selector="html", by=By.CSS_SELECTOR):
        return page_utils.is_text_visible(self.driver, text, selector, by)

    def is_attribute_present(self, selector, attribute, value=None, by=By.CSS_SELECTOR):
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

    def is_link_text_present(self, link_text):
        """Returns True if the link text appears in the HTML of the page.
        The element doesn't need to be visible,
        such as elements hidden inside a dropdown selection."""
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
        soup = self.get_beautiful_soup()
        html_links = soup.find_all("a")
        for html_link in html_links:
            if link_text.strip() in html_link.text.strip():
                return True
        return False

    ############

    # Bases (Basic page actions)

    def __recalculate_selector(self, selector, by, xp_ok=True):
        """Use auto-detection to return the correct selector with "by" updated.
        If "xp_ok" is False, don't call convert_css_to_xpath(), which is
        used to make the ":contains()" selector valid outside JS calls."""
        _type = type(selector)  # First make sure the selector is a string
        not_string = False
        if _type is tuple:
            if len(selector) is not 2:
                msg = "Expecting a selector with length of 2!"
                raise Exception('Invalid selector type: "%s"\n%s' % (_type, msg))
            selector, by = selector[0], selector[1]
            return selector, by
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
        return selector, by

    @staticmethod
    def convert_css_to_xpath(css):
        return css_to_xpath.convert_css_to_xpath(css)

    def convert_to_css_selector(self, selector, by):
        """This method converts a selector to a CSS_SELECTOR.
        jQuery commands require a CSS_SELECTOR for finding elements.
        This method should only be used for jQuery/JavaScript actions.
        Pure JavaScript doesn't support using a:contains("LINK_TEXT")."""
        if by == By.CSS_SELECTOR:
            return selector
        elif by == By.ID:
            return "#%s" % selector
        elif by == By.CLASS_NAME:
            return ".%s" % selector
        elif by == By.NAME:
            return '[name="%s"]' % selector
        elif by == By.TAG_NAME:
            return selector
        elif by == By.XPATH:
            return self.convert_xpath_to_css(selector)
        elif by == By.LINK_TEXT:
            return 'a:contains("%s")' % selector
        elif by == By.PARTIAL_LINK_TEXT:
            return 'a:contains("%s")' % selector
        else:
            raise Exception(
                "Exception: Could not convert {%s}(by=%s) to CSS_SELECTOR!"
                % (selector, by)
            )

    @staticmethod
    def __looks_like_a_page_url(url):
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

    def get_beautiful_soup(self, source=None):
        """BeautifulSoup is a toolkit for dissecting an HTML document
        and extracting what you need. It's great for screen-scraping!
        See: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        """
        from bs4 import BeautifulSoup

        if not source:
            source = self.get_page_source()
        soup = BeautifulSoup(source, "html.parser")
        return soup

    def execute_script(self, script, *args, **kwargs):
        return self.driver.execute_script(script, *args, **kwargs)

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

    ############

    # find element(s) with wait timeout

    def wait_for_element_present(self, selector, by=By.CSS_SELECTOR):
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
            return self.wait.until(EC.presence_of_element_located(locator))
        except Exception:
            message = "Element {%s} was not present after %s seconds!" % (selector, self.timeout)
        logging.info(page_utils.timeout_exception(NoSuchElementException, message))

    def wait_for_element_visible(self, selector, by=By.CSS_SELECTOR):
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
            return self.wait.until(EC.visibility_of_element_located(locator))
        except Exception:
            message = "Element {%s} was not visible after %s seconds!" % (selector, self.timeout)
            logging.info(page_utils.timeout_exception(ElementNotVisibleException, message))

    def wait_for_element_clickable(self, selector, by=By.CSS_SELECTOR):
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
            return self.wait.until(EC.element_to_be_clickable(locator))
        except Exception:
            message = "Element {%s} was not clickable after %s seconds!" % (selector, self.timeout)
            logging.info(page_utils.timeout_exception(ElementNotVisibleException, message))

    def wait_for_text_visible(self, text, selector, by=By.CSS_SELECTOR):
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
            return self.wait.until(EC.text_to_be_present_in_element(locator, text))
        except ElementNotVisibleException:
            message = "Expected text {%s} for {%s} was not visible after %s seconds!" % (text, selector, self.timeout)
            logging.info(page_utils.timeout_exception(ElementNotVisibleException, message))

    def wait_for_text_visible_in_value(self, text, selector, by=By.CSS_SELECTOR):
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
            return self.wait.until(EC.text_to_be_present_in_element_value(locator, text))
        except ElementNotVisibleException:
            message = "Expected text {%s} in {%s} value was not visible after %s seconds!" % (
                text, selector, self.timeout)
            logging.info(page_utils.timeout_exception(ElementNotVisibleException, message))

    def wait_for_attribute(self, selector, attribute, value=None, by=By.CSS_SELECTOR):
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

    def wait_for_element_absent(self, selector, by=By.CSS_SELECTOR):
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

    def wait_for_element_not_visible(self, selector, by=By.CSS_SELECTOR):
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
            return self.wait.until(EC.invisibility_of_element_located(locator))
        except Exception:
            message = "Element {%s} was still visible after %s seconds!" % (selector, self.timeout)
            logging.info(page_utils.timeout_exception(Exception, message))

    def wait_for_text_not_visible(self, text, selector, by=By.CSS_SELECTOR):
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

    def wait_for_attribute_not_present(self, selector, attribute, value=None, by=By.CSS_SELECTOR):
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

    def __scroll_to_element(self, element, selector=None, by=By.CSS_SELECTOR):
        success = page_utils.scroll_to_element(self.driver, element)
        if not success and selector:
            element = self.wait_for_element_visible(selector, by)

    def open_new_window(self, switch_to=True):
        """ Opens a new browser tab/window and switches to it by default. """
        self.__check_browser()  # Current window must exist to open a new one
        self.driver.execute_script("window.open('');")
        time.sleep(0.01)
        if switch_to:
            self.switch_to_newest_window()
            time.sleep(0.01)

    def switch_to_newest_window(self):
        self.switch_to_window(len(self.driver.window_handles) - 1)

    def __switch_to_newest_window_if_not_blank(self):
        current_window = self.driver.current_window_handle
        try:
            self.switch_to_window(len(self.driver.window_handles) - 1)
            if self.get_current_url() == "about:blank":
                self.switch_to_window(current_window)
        except Exception:
            self.switch_to_window(current_window)

    def update_text(self, selector, by=By.CSS_SELECTOR, text=None):
        """This method updates an element's text field with new text.
        Has multiple parts:
        * Waits for the element to be visible.
        * Waits for the element to be interactive.
        * Clears the text field.
        * Types in the new text.
        * Hits Enter/Submit (if the text ends in "\n").
        @Params
        selector - the selector of the text field
        text - the new text to type into the text field
        by - the type of selector to search by (Default: CSS Selector)
        timeout - how long to wait for the selector to be visible
        retry - if True, use JS if the Selenium text update fails
        """
        selector, by = self.__recalculate_selector(selector, by)
        element = self.wait_for_element_visible(selector, by=by)
        self.__scroll_to_element(element, selector, by)
        try:
            element.clear()
            backspaces = Keys.BACK_SPACE * 42  # Is the answer to everything
            element.send_keys(backspaces)  # In case autocomplete keeps text
        except (StaleElementReferenceException, ENI_Exception):
            time.sleep(0.16)
            element = self.wait_for_element_visible(selector, by=by)
            try:
                element.clear()
            except Exception:
                pass  # Clearing the text field first might not be necessary
        except Exception:
            pass  # Clearing the text field first might not be necessary
        if type(text) is int or type(text) is float:
            text = str(text)
        try:
            if not text.endswith("\n"):
                element.send_keys(text)
            else:
                element.send_keys(text[:-1])
                element.send_keys(Keys.RETURN)
        except (StaleElementReferenceException, ENI_Exception):
            time.sleep(0.16)
            element = self.wait_for_element_visible(selector, by=by)
            element.clear()
            if not text.endswith("\n"):
                element.send_keys(text)
            else:
                element.send_keys(text[:-1])
                element.send_keys(Keys.RETURN)

    def js_click(self, selector, by=By.CSS_SELECTOR, all_matches=False, scroll=True):
        """Clicks an element using JavaScript.
        Can be used to click hidden / invisible elements.
        If "all_matches" is False, only the first match is clicked.
        If "scroll" is False, won't scroll unless running in Demo Mode."""
        selector, by = self.__recalculate_selector(selector, by, xp_ok=False)
        if by == By.LINK_TEXT:
            message = (
                "Pure JavaScript doesn't support clicking by Link Text. "
                "You may want to use self.jquery_click() instead, which "
                "allows this with :contains(), assuming jQuery isn't blocked. "
                "For now, self.js_click() will use a regular WebDriver click."
            )
            logging.debug(message)
            self.click(selector, by=by)
            return
        element = self.wait_for_element_present(selector, by=by)
        if self.is_element_visible(selector, by=by):
            if scroll:
                success = page_utils.scroll_to_element(self.driver, element)
                if not success:
                    element = self.wait_for_element_present(selector, by)
        css_selector = self.convert_to_css_selector(selector, by=by)
        css_selector = re.escape(css_selector)  # Add "\\" to special chars
        css_selector = self.__escape_quotes_if_needed(css_selector)
        pre_action_url = self.driver.current_url
        pre_window_count = len(self.driver.window_handles)
        if not all_matches:
            if ":contains\\(" not in css_selector:
                self.__js_click(selector, by=by)
            else:
                click_script = """jQuery('%s')[0].click();""" % css_selector
                self.safe_execute_script(click_script)
        else:
            if ":contains\\(" not in css_selector:
                self.__js_click_all(selector, by=by)
            else:
                click_script = """jQuery('%s').click();""" % css_selector
                self.safe_execute_script(click_script)
        latest_window_count = len(self.driver.window_handles)
        if (latest_window_count > pre_window_count
                and self.driver.current_url == pre_action_url):
            self.__switch_to_newest_window_if_not_blank()

    def __js_click(self, selector, by=By.CSS_SELECTOR):
        """ Clicks an element using pure JS. Does not use jQuery. """
        selector, by = self.__recalculate_selector(selector, by)
        css_selector = self.convert_to_css_selector(selector, by=by)
        css_selector = re.escape(css_selector)  # Add "\\" to special chars
        css_selector = self.__escape_quotes_if_needed(css_selector)
        script = (
                """var simulateClick = function (elem) {
                       var evt = new MouseEvent('click', {
                           bubbles: true,
                           cancelable: true,
                           view: window
                       });
                       var canceled = !elem.dispatchEvent(evt);
                   };
                   var someLink = document.querySelector('%s');
                   simulateClick(someLink);"""
                % css_selector
        )
        self.execute_script(script)

    def __js_click_all(self, selector, by=By.CSS_SELECTOR):
        """ Clicks all matching elements using pure JS. (No jQuery) """
        selector, by = self.__recalculate_selector(selector, by)
        css_selector = self.convert_to_css_selector(selector, by=by)
        css_selector = re.escape(css_selector)  # Add "\\" to special chars
        css_selector = self.__escape_quotes_if_needed(css_selector)
        script = (
                """var simulateClick = function (elem) {
                       var evt = new MouseEvent('click', {
                           bubbles: true,
                           cancelable: true,
                           view: window
                       });
                       var canceled = !elem.dispatchEvent(evt);
                   };
                   var $elements = document.querySelectorAll('%s');
                   var index = 0, length = $elements.length;
                   for(; index < length; index++){
                   simulateClick($elements[index]);}"""
                % css_selector
        )
        self.execute_script(script)

    def safe_execute_script(self, script, *args, **kwargs):
        """When executing a script that contains a jQuery command,
        it's important that the jQuery library has been loaded first.
        This method will load jQuery if it wasn't already loaded."""
        self.__check_browser()
        if not page_utils.is_jquery_activated(self.driver):
            self.activate_jquery()
        return self.driver.execute_script(script, *args, **kwargs)

    def activate_jquery(self):
        """If "jQuery is not defined", use this method to activate it for use.
        This happens because jQuery is not always defined on web sites."""
        page_utils.activate_jquery(self.driver)

    @staticmethod
    def __escape_quotes_if_needed(string):
        return page_utils.escape_quotes_if_needed(string)

    def refresh_page(self):
        page_utils.clear_out_console_logs(self.driver)
        self.driver.refresh()

    def get_page_title(self):
        self.wait_for_element_present("title")
        time.sleep(0.03)
        return self.driver.title

    def __select_option(self, dropdown_selector, option, dropdown_by=By.CSS_SELECTOR, option_by="text"):
        """Selects an HTML <select> option by specification.
        Option specifications are by "text", "index", or "value".
        Defaults to "text" if option_by is unspecified or unknown."""
        from selenium.webdriver.support.ui import Select
        dropdown_selector, dropdown_by = self.__recalculate_selector(dropdown_selector, dropdown_by)
        element = self.wait_for_element_present(dropdown_selector, by=dropdown_by)
        try:
            if option_by == "index":
                Select(element).select_by_index(option)
            elif option_by == "value":
                Select(element).select_by_value(option)
            else:
                Select(element).select_by_visible_text(option)
        except (StaleElementReferenceException, ENI_Exception):
            time.sleep(0.14)
            element = self.wait_for_element_present(dropdown_selector, by=dropdown_by)
            if option_by == "index":
                Select(element).select_by_index(option)
            elif option_by == "value":
                Select(element).select_by_value(option)
            else:
                Select(element).select_by_visible_text(option)

    def get_link_attribute(self, link_text, attribute, hard_fail=True):
        """Finds a link by link text and then returns the attribute's value.
        If the link text or attribute cannot be found, an exception will
        get raised if hard_fail is True (otherwise None is returned)."""
        soup = self.get_beautiful_soup()
        html_links = soup.find_all("a")
        for html_link in html_links:
            if html_link.text.strip() == link_text.strip():
                if html_link.has_attr(attribute):
                    attribute_value = html_link.get(attribute)
                    return attribute_value
                if hard_fail:
                    raise Exception(
                        "Unable to find attribute {%s} from link text {%s}!"
                        % (attribute, link_text)
                    )
                else:
                    return None
        if hard_fail:
            raise Exception("Link text {%s} was not found!" % link_text)
        else:
            return None

    def __get_href_from_link_text(self, link_text, hard_fail=True):
        href = self.get_link_attribute(link_text, "href", hard_fail)
        if not href:
            return None
        if href.startswith("//"):
            link = "http:" + href
        elif href.startswith("/"):
            url = self.driver.current_url
            domain_url = self.get_domain_url(url)
            link = domain_url + href
        else:
            link = href
        return link

    def get_partial_link_text_attribute(self, link_text, attribute, hard_fail=True):
        """Finds a link by partial link text and then returns the attribute's
        value. If the partial link text or attribute cannot be found, an
        exception will get raised if hard_fail is True (otherwise None
        is returned)."""
        soup = self.get_beautiful_soup()
        html_links = soup.find_all("a")
        for html_link in html_links:
            if link_text.strip() in html_link.text.strip():
                if html_link.has_attr(attribute):
                    attribute_value = html_link.get(attribute)
                    return attribute_value
                if hard_fail:
                    raise Exception(
                        "Unable to find attribute {%s} from "
                        "partial link text {%s}!" % (attribute, link_text)
                    )
                else:
                    return None
        if hard_fail:
            raise Exception(
                "Partial Link text {%s} was not found!" % link_text
            )
        else:
            return None

    def __get_href_from_partial_link_text(self, link_text, hard_fail=True):
        href = self.get_partial_link_text_attribute(
            link_text, "href", hard_fail
        )
        if not href:
            return None
        if href.startswith("//"):
            link = "http:" + href
        elif href.startswith("/"):
            url = self.driver.current_url
            domain_url = self.get_domain_url(url)
            link = domain_url + href
        else:
            link = href
        return link

    def get_current_url(self):
        current_url = self.driver.current_url
        if "%" in current_url and sys.version_info[0] >= 3:
            try:
                from urllib.parse import unquote
                current_url = unquote(current_url, errors="strict")
            except Exception:
                pass
        return current_url

    @staticmethod
    def get_domain_url(url):
        return page_utils.get_domain_url(url)

    ############

    # deal with link texts


if __name__ == "__main__":
    pass
