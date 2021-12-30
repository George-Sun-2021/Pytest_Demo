#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
from utils.time import dt_strftime


class PathManager(object):
    # project directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # page element directory
    ELEMENT_PATH = os.path.join(BASE_DIR, 'page_element')

    # html report file name
    REPORT_FILE = os.path.join(BASE_DIR, 'reports', 'report.html')

    @property
    def screen_path(self):
        """screenshot directory"""
        screenshot_dir = os.path.join(self.BASE_DIR, 'screenshots')
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        now_time = dt_strftime("%Y%m%d%H%M%S")
        screen_file = os.path.join(screenshot_dir, "{}.png".format(now_time))
        return now_time, screen_file

    @property
    def log_file(self):
        """log directory"""
        log_dir = os.path.join(self.BASE_DIR, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return os.path.join(log_dir, '{}.log'.format(dt_strftime()))

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
