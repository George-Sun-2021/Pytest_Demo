#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import json
import os
from utils.time import dt_strftime


class PathManager(object):
    # project directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # page element directory
    ELEMENT_PATH = os.path.join(BASE_DIR, "page_element")

    # report directory
    REPORT_PATH = os.path.join(BASE_DIR, "reports")
    # html report file name
    REPORT_FILE = os.path.join(REPORT_PATH, "html_reports", "report.html")
    # allure report root path
    ALLURE_ROOT = os.path.join(REPORT_PATH, "allure")
    # allure report result path
    ALLURE_RESULT = os.path.join(ALLURE_ROOT, "allure-results")
    # ALLURE_DIR = os.path.join(ALLURE_ROOT, f"allure-results-{dt_strftime()}")
    # allure result history path under allure result
    ALLURE_RESULT_HISTORY = os.path.join(ALLURE_RESULT, "history")
    # allure report generating path
    ALLURE_REPORT = os.path.join(ALLURE_ROOT, "allure-reports")
    # allure history path saved for legacy running
    ALLURE_HISTORY = os.path.join(ALLURE_ROOT, "allure-history")
    # allure report history file
    ALLURE_HISTORY_FILE = os.path.join(ALLURE_ROOT, "history.json")
    # allure report history path under allure report
    ALLURE_REPORT_HISTORY = os.path.join(ALLURE_REPORT, "history")


    @property
    def screen_path(self):
        """screenshot directory"""
        screenshot_dir = os.path.join(self.BASE_DIR, 'screenshots')
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        now_time = dt_strftime("%Y%m%d%H%M%S")
        screen_file = os.path.join(screenshot_dir, f"{now_time}.png")
        return now_time, screen_file

    @property
    def log_file(self):
        """log directory"""
        log_dir = os.path.join(self.BASE_DIR, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return os.path.join(log_dir, f'{dt_strftime()}.log')

    @property
    def ini_file(self):
        """read config.ini"""
        ini_file = os.path.join(self.BASE_DIR, 'config', 'config.ini')
        if not os.path.exists(ini_file):
            raise FileNotFoundError("Config file: %s does not exist！" % ini_file)
        return ini_file


pm = PathManager()
if __name__ == '__main__':
    print(pm.REPORT_FILE)
