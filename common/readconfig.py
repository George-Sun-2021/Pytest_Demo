#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import configparser
from config.path_manager import pm


class ReadConfig(object):
    """配置文件"""

    def __init__(self):
        self.config = configparser.RawConfigParser()  # 当有%的符号时请使用Raw读取
        self.config.read(pm.ini_file, encoding='utf-8')

    def _get(self, section, option):
        """获取"""
        return self.config.get(section, option)

    def _set(self, section, option, value):
        """更新"""
        self.config.set(section, option, value)
        with open(pm.ini_file, 'w') as f:
            self.config.write(f)

    @property
    def url(self):
        return self._get('HOST', 'host')

    def allure_env(self, args):
        return self._get('ALLURE_ENVIRONMENT', args)


ini = ReadConfig()

if __name__ == '__main__':
    print(ini.url)
    print(ini.allure_env('email'))
