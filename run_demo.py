# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import json
import os
import sys
import subprocess
import zipfile

from config.path_manager import pm
from common.readconfig import ini

# WIN = sys.platform.startswith('win')

# def main():
#     """主函数"""
#     steps = [
#         "venv\\Script\\activate" if WIN else "source venv/bin/activate",
#         "copy config\\environment.xml allure-results\\environment.xml"
#         "pytest -m demo --alluredir allure-results --clean-alluredir",
#         "allure generate allure-results -c -o allure-report",
#         "allure open allure-report"
#     ]
#     for step in steps:
#         subprocess.run("call " + step if WIN else step, shell=True)

WIN = sys.platform.startswith('win')
allure_history = pm.ALLURE_HISTORY
allure_result = pm.ALLURE_RESULT
allure_report = pm.ALLURE_REPORT
history_file = pm.ALLURE_HISTORY_FILE

environment_info = [
    {"name": 'System version', "values": [sys.platform]},
    {"name": 'python version', "values": [sys.version]},
    {"name": 'Test version', "values": [ini.allure_env('version')]},
    {"name": 'Test case reference', "values": [ini.allure_env('reference')]},
    {"name": 'Project name', "values": [ini.allure_env('project')]},
    {"name": 'Tester', "values": [ini.allure_env('author')]},
    {"name": 'Description', "values": [ini.allure_env('description')]}
]


# 获取历史数据和构建次数
def get_history():
    if os.path.exists(history_file):
        with open(history_file) as f:
            li = eval(f.read())
        # 根据构建次数进行排序，从大到小
        li.sort(key=lambda x: x['buildOrder'], reverse=True)
        # 返回下一次的构建次数，所以要在排序后的历史数据中的buildOrder+1
        return li[0]["buildOrder"] + 1, li
    else:
        # 首次进行生成报告，肯定会进到这一步，先创建history.json,然后返回构建次数1（代表首次）
        print("This is the first time running！！！history.json is initializing!!!")
        with open(history_file, "w") as f:
            pass
        return 1, None


def update_trend_data(build_order, old_data: list):
    """
    dirname：构建次数
    old_data：备份的数据
    update_trend_data(get_history())
    """
    report_widgets = os.path.join(allure_report, f"{str(build_order)}/widgets")
    # 将环境信息写入environment.json
    with open(report_widgets + '/environment.json', 'w', encoding='utf-8') as f:
        json.dump(environment_info, f, ensure_ascii=False, indent=4)

    # 读取最新生成的history-trend.json数据
    with open(os.path.join(report_widgets, "history-trend.json")) as f:
        data = f.read()

    new_data = eval(data)
    if old_data is not None:
        new_data[0]["buildOrder"] = old_data[0]["buildOrder"] + 1
    else:
        old_data = []
        new_data[0]["buildOrder"] = 1
    # 给最新生成的数据添加reportUrl key，reportUrl要根据自己的实际情况更改
    new_data[0]["reportUrl"] = f"http://127.0.0.1:63342/{allure_report}/{str(build_order)}/index.html"
    # 把最新的数据，插入到备份数据列表首位
    old_data.insert(0, new_data[0])
    # 把所有生成的报告中的history-trend.json都更新成新备份的数据old_data，这样的话，点击历史趋势图就可以实现新老报告切换
    for i in range(1, build_order + 1):
        with open(os.path.join(allure_report, f"{str(i)}/widgets/history-trend.json"), "w+") as f:
            f.write(json.dumps(old_data))
    # 把数据备份到history.json
    with open(history_file, "w+") as f:
        f.write(json.dumps(old_data))
    return old_data, new_data[0]["reportUrl"]


# 压缩文件
def compress_file(zip_file_name, dir_name):
    """
    目录压缩
    :param zip_file_name: 压缩文件名称和位置
    :param dir_name: 要压缩的目录
    :return:
    """
    with zipfile.ZipFile(zip_file_name, 'w') as z:
        for root, dirs, files in os.walk(dir_name):
            file_path = root.replace(dir_name, '')
            file_path = file_path and file_path + os.sep or ''
            for filename in files:
                z.write(os.path.join(root, filename), os.path.join(file_path, filename))
    print('压缩成功！')


def main():
    """主函数"""
    cat_file = os.path.join(pm.CONFIG_PATH, 'categories.json')
    run_test_steps = [
        "venv\\Script\\activate" if WIN else "source venv/bin/activate",
        f"copy {cat_file} {allure_result}",
        f"pytest -m demo --alluredir {allure_result}"
        # f"copy {config_env_file} {allure_result}",
        # f"pytest -m demo --alluredir {allure_result}"
    ]
    for step in run_test_steps:
        subprocess.run("call " + step if WIN else step, shell=True)
    build_order, old_data = get_history()
    report_gen_steps = [
        f"allure generate {allure_result} -c -o {os.path.join(allure_report, str(build_order))}"
        # f"allure open {allure_report}"
    ]
    for step in report_gen_steps:
        subprocess.run("call " + step if WIN else step, shell=True)
    all_data, report_url = update_trend_data(build_order, old_data)


if __name__ == "__main__":
    main()
