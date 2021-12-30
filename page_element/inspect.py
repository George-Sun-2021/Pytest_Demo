#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import yaml
from config.path_manager import cm
from utils.time import running_time


@running_time
def inspect_element():
    """

    Simple verify if the element is in correct format
    Mainly checked xpath and css
    """
    for files in os.listdir(cm.ELEMENT_PATH):
        if files.endswith(".yaml"):
            _path = os.path.join(cm.ELEMENT_PATH, files)
            with open(_path, encoding='utf-8') as f:
                data = yaml.safe_load(f)
            for k in data.values():
                try:
                    pattern, value = k.split('==')
                except ValueError:
                    raise Exception("no `==` in the element expression")
                if pattern not in cm.LOCATE_MODE:
                    raise Exception('There is not specific type of 【%s】 in file %s' % (k, _path))
                elif pattern == 'xpath':
                    assert '//' in value, 'Element【%s】 in file %s is not in correct xpath format' % (k, _path)
                elif pattern == 'css':
                    assert '//' not in value, 'Element【%s】 in file %s is not in correct css format' % (k, _path)
                else:
                    assert value, 'Element【%s】 in file %s is not matching between its type and format' % (k, _path)


if __name__ == '__main__':
    inspect_element()
