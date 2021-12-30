"""
This module contains shared utility methods.
"""
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchAttributeException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import NoSuchWindowException


def format_exc(exception, message):
    """
    Formats an exception message to make the output cleaner.
    """

    if exception == Exception:
        exc = Exception
        return exc, message
    elif exception == ElementNotVisibleException:
        exc = ElementNotVisibleException
    elif exception == "ElementNotVisibleException":
        exc = ElementNotVisibleException
    elif exception == NoSuchElementException:
        exc = NoSuchElementException
    elif exception == "NoSuchElementException":
        exc = NoSuchElementException
    elif exception == NoAlertPresentException:
        exc = NoAlertPresentException
    elif exception == "NoAlertPresentException":
        exc = NoAlertPresentException
    elif exception == NoSuchAttributeException:
        exc = NoSuchAttributeException
    elif exception == "NoSuchAttributeException":
        exc = NoSuchAttributeException
    elif exception == NoSuchFrameException:
        exc = NoSuchFrameException
    elif exception == "NoSuchFrameException":
        exc = NoSuchFrameException
    elif exception == NoSuchWindowException:
        exc = NoSuchWindowException
    elif exception == "NoSuchWindowException":
        exc = NoSuchWindowException
    elif type(exception) is str:
        exc = Exception
        message = "%s: %s" % (exception, message)
        return exc, message
    else:
        exc = Exception
        return exc, message
    message = _format_message(message)
    return exc, message


def _format_message(message):
    message = "\n " + message
    return message
