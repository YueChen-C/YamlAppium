# -*- coding: utf-8 -*-
"""
@ Author：YueC
@ Description：Pytest hook Appium
"""
import datetime
import os
import sys
import allure
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base.driver import DriverClient


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # 用例报错捕捉
    Action = DriverClient().Action
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        f = Action.driver.get_screenshot_as_png()
        allure.attach(f, '失败截图', allure.attachment_type.PNG)
        logcat = Action.driver.get_log('logcat')
        c = '\n'.join([i['message'] for i in logcat])
        allure.attach(c, 'APPlog', allure.attachment_type.TEXT)
        if Action.get_app_pid() != Action.apppid:
            raise Exception('设备进程 ID 变化，可能发生崩溃')


def pytest_runtest_call(item):
    # 每条用例代码执行之前，非用例执行之前
    allure.dynamic.description('用例开始时间:{}'.format(datetime.datetime.now()))
    Action = DriverClient().Action
    if Action.get_app_pid() != Action.apppid:
        raise Exception('设备进程 ID 变化，可能发生崩溃')


def pytest_collect_file(parent, path):
    # 获取文件.yml 文件
    if path.ext == ".yml" and path.basename.startswith("test"):
        return YamlFile(path, parent)


class YamlFile(pytest.File):
    # 读取文件内容
    def collect(self):
        import yaml
        raw = yaml.safe_load(self.fspath.open(encoding='utf-8'))
        for name, values in raw.items():
            yield YamlTest(name, self, values)


@pytest.fixture
def cmdopt(request):
    return request.config.getoption("--cmdopt")


def yamldict(locator):
    """ 自动判断元素类型
    :param locator: 定位器
    :return:
    """
    element = str(locator['element'])
    if not locator.get('type'):
        locator['type'] = 'xpath'
        if '//' in element:
            locator['type'] = 'xpath'
        elif ':id' in element:
            locator['type'] = 'id'
        elif 'android.' in element or 'XCUIElement' in element:
            locator['type'] = 'class name'
        else:
            locator['type'] = 'accessibility id'
    return locator


class YamlTest(pytest.Item):
    def __init__(self, name, parent, values):
        super(YamlTest, self).__init__(name, parent)
        self.values = values
        self.Action = DriverClient().Action
        self.locator = None

    def runtest(self):
        # 运行用例
        for self.locator in self.values:
            self.locator['time'] = 5
            is_displayed = True
            if not self.locator.get('is_displayed'):
                is_displayed = False if str(self.locator.get('is_displayed')).lower() == 'false' else True
            try:
                if self.locator.get('element'):
                    response = self.Action.__getattribute__(self.locator.get('method'))(yamldict(self.locator))
                else:
                    response = self.Action.__getattribute__(self.locator.get('method'))()
                self.assert_response(response, self.locator)
            except Exception as E:
                if is_displayed:
                    raise E
                pass

    def repr_failure(self, excinfo):
        """自定义报错信息，如果没有定义则会默认打印错误堆栈信息，因为比较乱，所以这里自定义一下 """
        if isinstance(excinfo.value, Exception):
            return '测试类名称：{} \n' \
                   '输入参数：{} \n' \
                   '错误信息：{}'.format(self.name, self.locator, excinfo.value.args)

    def assert_response(self, response, locator):
        if locator.get('assert_text'):
            assert locator['assert_text'] in response
        elif locator.get('assert_element'):
            assert response

    def reportinfo(self):
        return self.fspath, 0, "CaseName: %s" % self.name
