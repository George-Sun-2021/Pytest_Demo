#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import yaml
import config.configs as conf
from config.path_manager import pm


class Element(object):
    """get element from yaml file"""

    def __init__(self, name):
        self.file_name = '%s.yaml' % name
        self.element_path = os.path.join(pm.ELEMENT_PATH, self.file_name)
        if not os.path.exists(self.element_path):
            raise FileNotFoundError("%s file does not exist！" % self.element_path)
        with open(self.element_path, encoding='utf-8') as f:
            self.data = yaml.safe_load(f)

    def __getitem__(self, item):
        """get property"""
        data = self.data.get(item)
        if data:
            name, value = data.split('==')
            return conf.LOCATE_MODE[name], value
        raise ArithmeticError("The keyword: {} is not in {}".format(item, self.file_name))


if __name__ == '__main__':
    search = Element('search')
    print(search['搜索框'])
