"""
This module contains a set of methods that can be used for page loads and
for waiting for elements to appear on a page.

These methods improve on and expand existing WebDriver commands.
Improvements include making WebDriver commands more robust and more reliable
by giving page elements enough time to load before taking action on them.

The default option for searching for elements is by CSS Selector.
This can be changed by overriding the "By" parameter.
Options are:
By.CSS_SELECTOR
By.CLASS_NAME
By.ID
By.NAME
By.LINK_TEXT
By.XPATH
By.TAG_NAME
By.PARTIAL_LINK_TEXT
"""

import codecs
import os
import sys
import time
import re
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchAttributeException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from utils import exception_messages as em_utils
from config import configs


# url operations
def get_domain_url(url):
    """
    Use this to convert a url like this:
    https://blog.xkcd.com/2014/07/22/what-if-book-tour/
    Into this:
    https://blog.xkcd.com
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        return url
    url_header = url.split("://")[0]
    simple_url = url.split("://")[1]
    base_url = simple_url.split("/")[0]
    domain_url = url_header + "://" + base_url
    return domain_url


# determine selector types
def is_xpath_selector(selector):
    """
    A basic method to determine if a selector is an xpath selector.
    """
    if (
            selector.startswith("/")
            or selector.startswith("./")
            or selector.startswith("(")
    ):
        return True
    return False


def is_link_text_selector(selector):
    """
    A basic method to determine if a selector is a link text selector.
    """
    if (
            selector.startswith("link=")
            or selector.startswith("link_text=")
            or selector.startswith("text=")
    ):
        return True
    return False


def is_partial_link_text_selector(selector):
    """
    A basic method to determine if a selector is a partial link text selector.
    """
    if (
            selector.startswith("partial_link=")
            or selector.startswith("partial_link_text=")
            or selector.startswith("partial_text=")
            or selector.startswith("p_link=")
            or selector.startswith("p_link_text=")
            or selector.startswith("p_text=")
    ):
        return True
    return False


def is_name_selector(selector):
    """
    A basic method to determine if a selector is a name selector.
    """
    if selector.startswith("name=") or selector.startswith("&"):
        return True
    return False


def get_link_text_from_selector(selector):
    """
    A basic method to get the link text from a link text selector.
    """
    if selector.startswith("link="):
        return selector[len("link="):]
    elif selector.startswith("link_text="):
        return selector[len("link_text="):]
    elif selector.startswith("text="):
        return selector[len("text="):]
    return selector


def get_partial_link_text_from_selector(selector):
    """
    A basic method to get the partial link text from a partial link selector.
    """
    if selector.startswith("partial_link="):
        return selector[len("partial_link="):]
    elif selector.startswith("partial_link_text="):
        return selector[len("partial_link_text="):]
    elif selector.startswith("partial_text="):
        return selector[len("partial_text="):]
    elif selector.startswith("p_link="):
        return selector[len("p_link="):]
    elif selector.startswith("p_link_text="):
        return selector[len("p_link_text="):]
    elif selector.startswith("p_text="):
        return selector[len("p_text="):]
    return selector


def get_name_from_selector(selector):
    """
    A basic method to get the name from a name selector.
    """
    if selector.startswith("name="):
        return selector[len("name="):]
    if selector.startswith("&"):
        return selector[len("&"):]
    return selector


def is_valid_url(url):
    regex = re.compile(
        r"^(?:http)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"
        r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    if (
            regex.match(url)
            or url.startswith("about:")
            or url.startswith("data:")
            or url.startswith("chrome:")
            or url.startswith("edge:")
            or url.startswith("opera:")
            or url.startswith("file:")
    ):
        return True
    else:
        return False


# webdriver timeout exception message function
def timeout_exception(exception, message):
    exception, message = em_utils.format_exc(exception, message)
    raise exception(message)


# if conditions for elements
def is_element_present(driver, selector, by=By.XPATH):
    """
    Returns whether the specified element selector is present on the page.
    @Params
    driver - the webdriver object (required)
    selector - the locator for identifying the page element (required)
    by - the type of selector being used (Default: By.CSS_SELECTOR)
    @Returns
    Boolean (is element present)
    """
    try:
        driver.find_element(by=by, value=selector)
        return True
    except Exception:
        return False


def is_element_visible(driver, selector, by=By.XPATH):
    """
    Returns whether the specified element selector is visible on the page.
    @Params
    driver - the webdriver object (required)
    selector - the locator for identifying the page element (required)
    by - the type of selector being used (Default: By.CSS_SELECTOR)
    @Returns
    Boolean (is element visible)
    """
    try:
        element = driver.find_element(by=by, value=selector)
        return element.is_displayed()
    except Exception:
        return False


def is_element_enabled(driver, selector, by=By.XPATH):
    """
    Returns whether the specified element selector is enabled on the page.
    @Params
    driver - the webdriver object (required)
    selector - the locator for identifying the page element (required)
    by - the type of selector being used (Default: By.CSS_SELECTOR)
    @Returns
    Boolean (is element enabled)
    """
    try:
        element = driver.find_element(by=by, value=selector)
        return element.is_enabled()
    except Exception:
        return False


def is_text_visible(driver, text, selector, by=By.XPATH):
    """
    Returns whether the specified text is visible in the specified selector.
    @Params
    driver - the webdriver object (required)
    text - the text string to search for
    selector - the locator for identifying the page element (required)
    by - the type of selector being used (Default: By.CSS_SELECTOR)
    @Returns
    Boolean (is text visible)
    """
    try:
        element = driver.find_element(by=by, value=selector)
        return element.is_displayed() and text in element.text
    except Exception:
        return False


def is_attribute_present(
        driver, selector, attribute, value=None, by=By.XPATH
):
    """
    Returns whether the specified attribute is present in the given selector.
    @Params
    driver - the webdriver object (required)
    selector - the locator for identifying the page element (required)
    attribute - the attribute that is expected for the element (required)
    value - the attribute value that is expected (Default: None)
    by - the type of selector being used (Default: By.CSS_SELECTOR)
    @Returns
    Boolean (is attribute present)
    """
    try:
        element = driver.find_element(by=by, value=selector)
        found_value = element.get_attribute(attribute)
        if found_value is None:
            raise Exception()

        if value is not None:
            if found_value == value:
                return True
            else:
                raise Exception()
        else:
            return True
    except Exception:
        return False


def find_visible_elements(driver, selector, by=By.CSS_SELECTOR):
    """
    Finds all WebElements that match a selector and are visible.
    Similar to webdriver.find_elements.
    @Params
    driver - the webdriver object (required)
    selector - the locator for identifying the page element (required)
    by - the type of selector being used (Default: By.CSS_SELECTOR)
    """
    elements = driver.find_elements(by=by, value=selector)
    try:
        v_elems = [element for element in elements if element.is_displayed()]
        return v_elems
    except (StaleElementReferenceException, ElementNotInteractableException):
        time.sleep(0.1)
        elements = driver.find_elements(by=by, value=selector)
        v_elems = []
        for element in elements:
            if element.is_displayed():
                v_elems.append(element)
        return v_elems


def switch_to_window(driver, window, timeout=configs.SMALL_TIMEOUT):
    """
    Wait for a window to appear, and switch to it. This should be usable
    as a drop-in replacement for driver.switch_to.window().
    @Params
    driver - the webdriver object (required)
    window - the window index or window handle
    timeout - the time to wait for the window in seconds
    """
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    if isinstance(window, int):
        for x in range(int(timeout * 10)):
            em_utils.check_if_time_limit_exceeded()
            try:
                window_handle = driver.window_handles[window]
                driver.switch_to.window(window_handle)
                return True
            except IndexError:
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.1)
        plural = "s"
        if timeout == 1:
            plural = ""
        message = "Window {%s} was not present after %s second%s!" % (
            window,
            timeout,
            plural,
        )
        timeout_exception(Exception, message)
    else:
        window_handle = window
        for x in range(int(timeout * 10)):
            em_utils.check_if_time_limit_exceeded()
            try:
                driver.switch_to.window(window_handle)
                return True
            except NoSuchWindowException:
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.1)
        plural = "s"
        if timeout == 1:
            plural = ""
        message = "Window {%s} was not present after %s second%s!" % (
            window,
            timeout,
            plural,
        )
        timeout_exception(Exception, message)


def clear_out_console_logs(driver):
    try:
        # Clear out the current page log before navigating to a new page
        # (To make sure that assert_no_js_errors() uses current results)
        driver.get_log("browser")
    except Exception:
        pass


def scroll_to_element(driver, element):
    element_location = None
    try:
        element_location = element.location["y"]
    except Exception:
        return False
    element_location = element_location - 130
    if element_location < 0:
        element_location = 0
    scroll_script = "window.scrollTo(0, %s);" % element_location
    try:
        driver.execute_script(scroll_script)
        return True
    except Exception:
        return False


def switch_to_frame(driver, frame):
    """
    Wait for an iframe to appear, and switch to it. This should be
    usable as a drop-in replacement for driver.switch_to.frame().
    @Params
    driver - the webdriver object (required)
    frame - the frame element, name, id, index, or selector
    timeout - the time to wait for the alert in seconds
    """
    try:
        driver.switch_to.frame(frame)
        return True
    except NoSuchFrameException:
        if type(frame) is str:
            by = None
            if is_xpath_selector(frame):
                by = By.XPATH
            else:
                by = By.CSS_SELECTOR
            if is_element_visible(driver, frame, by=by):
                try:
                    element = driver.find_element(by=by, value=frame)
                    driver.switch_to.frame(element)
                    return True
                except Exception:
                    pass
        time.sleep(0.1)
    message = "Frame {%s} was not visible after %s seconds!" % (frame, self.timeout)
    timeout_exception(Exception, message)

    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        em_utils.check_if_time_limit_exceeded()
        try:
            driver.switch_to.frame(frame)
            return True
        except NoSuchFrameException:
            if type(frame) is str:
                by = None
                if page_utils.is_xpath_selector(frame):
                    by = By.XPATH
                else:
                    by = By.CSS_SELECTOR
                if is_element_visible(driver, frame, by=by):
                    try:
                        element = driver.find_element(by=by, value=frame)
                        driver.switch_to.frame(element)
                        return True
                    except Exception:
                        pass
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    plural = "s"
    if timeout == 1:
        plural = ""
    message = "Frame {%s} was not visible after %s second%s!" % (
        frame,
        timeout,
        plural,
    )
    timeout_exception(Exception, message)


#######################################


def hover_on_element(driver, selector, by=By.XPATH):
    """
    Fires the hover event for the specified element by the given selector.
    @Params
    driver - the webdriver object (required)
    selector - the locator for identifying the page element (required)
    by - the type of selector being used (Default: By.CSS_SELECTOR)
    """
    element = driver.find_element(by=by, value=selector)
    hover = ActionChains(driver).move_to_element(element)
    hover.perform()


def hover_element(driver, element):
    """
    Similar to hover_on_element(), but uses found element, not a selector.
    """
    hover = ActionChains(driver).move_to_element(element)
    hover.perform()


def hover_and_click(
        driver,
        hover_selector,
        click_selector,
        hover_by=By.CSS_SELECTOR,
        click_by=By.CSS_SELECTOR,
        timeout=configs.SMALL_TIMEOUT,
):
    """
    Fires the hover event for a specified element by a given selector, then
    clicks on another element specified. Useful for dropdown hover based menus.
    @Params
    driver - the webdriver object (required)
    hover_selector - the css selector to hover over (required)
    click_selector - the css selector to click on (required)
    hover_by - the hover selector type to search by (Default: By.CSS_SELECTOR)
    click_by - the click selector type to search by (Default: By.CSS_SELECTOR)
    timeout - number of seconds to wait for click element to appear after hover
    """
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    element = driver.find_element(by=hover_by, value=hover_selector)
    hover = ActionChains(driver).move_to_element(element)
    for x in range(int(timeout * 10)):
        try:
            hover.perform()
            element = driver.find_element(by=click_by, value=click_selector)
            element.click()
            return element
        except Exception:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    plural = "s"
    if timeout == 1:
        plural = ""
    message = "Element {%s} was not present after %s second%s!" % (
        click_selector,
        timeout,
        plural,
    )
    timeout_exception(NoSuchElementException, message)


def hover_element_and_click(
        driver,
        element,
        click_selector,
        click_by=By.CSS_SELECTOR,
        timeout=configs.SMALL_TIMEOUT,
):
    """
    Similar to hover_and_click(), but assumes top element is already found.
    """
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    hover = ActionChains(driver).move_to_element(element)
    for x in range(int(timeout * 10)):
        try:
            hover.perform()
            element = driver.find_element(by=click_by, value=click_selector)
            element.click()
            return element
        except Exception:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    plural = "s"
    if timeout == 1:
        plural = ""
    message = "Element {%s} was not present after %s second%s!" % (
        click_selector,
        timeout,
        plural,
    )
    timeout_exception(NoSuchElementException, message)


def hover_element_and_double_click(
        driver,
        element,
        click_selector,
        click_by=By.CSS_SELECTOR,
        timeout=configs.SMALL_TIMEOUT,
):
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    hover = ActionChains(driver).move_to_element(element)
    for x in range(int(timeout * 10)):
        try:
            hover.perform()
            element_2 = driver.find_element(by=click_by, value=click_selector)
            actions = ActionChains(driver)
            actions.move_to_element(element_2)
            actions.double_click(element_2)
            actions.perform()
            return element_2
        except Exception:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    plural = "s"
    if timeout == 1:
        plural = ""
    message = "Element {%s} was not present after %s second%s!" % (
        click_selector,
        timeout,
        plural,
    )
    timeout_exception(NoSuchElementException, message)


def save_screenshot(
        driver, name, folder=None, selector=None, by=By.CSS_SELECTOR
):
    """
    Saves a screenshot of the current page.
    If no folder is specified, uses the folder where pytest was called.
    The screenshot will include the entire page unless a selector is given.
    If a provided selector is not found, then takes a full-page screenshot.
    If the folder provided doesn't exist, it will get created.
    The screenshot will be in PNG format: (*.png)
    """
    if not name.endswith(".png"):
        name = name + ".png"
    if folder:
        abs_path = os.path.abspath(".")
        file_path = abs_path + "/%s" % folder
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        screenshot_path = "%s/%s" % (file_path, name)
    else:
        screenshot_path = name
    if selector:
        try:
            element = driver.find_element(by=by, value=selector)
            element_png = element.screenshot_as_png
            with open(screenshot_path, "wb") as file:
                file.write(element_png)
        except Exception:
            if driver:
                driver.get_screenshot_as_file(screenshot_path)
            else:
                pass
    else:
        if driver:
            driver.get_screenshot_as_file(screenshot_path)
        else:
            pass


def save_page_source(driver, name, folder=None):
    """
    Saves the page HTML to the current directory (or given subfolder).
    If the folder specified doesn't exist, it will get created.
    @Params
    name - The file name to save the current page's HTML to.
    folder - The folder to save the file to. (Default = current folder)
    """
    from seleniumbase.core import log_helper

    if not name.endswith(".html"):
        name = name + ".html"
    if folder:
        abs_path = os.path.abspath(".")
        file_path = abs_path + "/%s" % folder
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        html_file_path = "%s/%s" % (file_path, name)
    else:
        html_file_path = name
    page_source = driver.page_source
    html_file = codecs.open(html_file_path, "w+", "utf-8")
    rendered_source = log_helper.get_html_source_with_base_href(
        driver, page_source
    )
    html_file.write(rendered_source)
    html_file.close()


def _get_last_page(driver):
    try:
        last_page = driver.current_url
    except Exception:
        last_page = "[WARNING! Browser Not Open!]"
    if len(last_page) < 5:
        last_page = "[WARNING! Browser Not Open!]"
    return last_page


def save_test_failure_data(driver, name, browser_type, folder=None):
    """
    Saves failure data to the current directory (or to a subfolder if provided)
    If the folder provided doesn't exist, it will get created.
    """
    import traceback

    if folder:
        abs_path = os.path.abspath(".")
        file_path = abs_path + "/%s" % folder
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        failure_data_file_path = "%s/%s" % (file_path, name)
    else:
        failure_data_file_path = name
    failure_data_file = codecs.open(failure_data_file_path, "w+", "utf-8")
    last_page = _get_last_page(driver)
    data_to_save = []
    data_to_save.append("Last_Page: %s" % last_page)
    data_to_save.append("Browser: %s " % browser_type)
    data_to_save.append(
        "Traceback: "
        + "".join(
            traceback.format_exception(
                sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
            )
        )
    )
    failure_data_file.writelines("\r\n".join(data_to_save))
    failure_data_file.close()


def wait_for_and_accept_alert(driver, timeout=configs.LARGE_TIMEOUT):
    """
    Wait for and accept an alert. Returns the text from the alert.
    @Params
    driver - the webdriver object (required)
    timeout - the time to wait for the alert in seconds
    """
    alert = wait_for_and_switch_to_alert(driver, timeout)
    alert_text = alert.text
    alert.accept()
    return alert_text


def wait_for_and_dismiss_alert(driver, timeout=configs.LARGE_TIMEOUT):
    """
    Wait for and dismiss an alert. Returns the text from the alert.
    @Params
    driver - the webdriver object (required)
    timeout - the time to wait for the alert in seconds
    """
    alert = wait_for_and_switch_to_alert(driver, timeout)
    alert_text = alert.text
    alert.dismiss()
    return alert_text


def wait_for_and_switch_to_alert(driver, timeout=configs.LARGE_TIMEOUT):
    """
    Wait for a browser alert to appear, and switch to it. This should be usable
    as a drop-in replacement for driver.switch_to.alert when the alert box
    may not exist yet.
    @Params
    driver - the webdriver object (required)
    timeout - the time to wait for the alert in seconds
    """
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        em_utils.check_if_time_limit_exceeded()
        try:
            alert = driver.switch_to.alert
            # Raises exception if no alert present
            dummy_variable = alert.text  # noqa
            return alert
        except NoAlertPresentException:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    message = "Alert was not present after %s seconds!" % timeout
    timeout_exception(Exception, message)
