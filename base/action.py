# -*- coding: utf-8 -*-
"""
@ Author：YueC
@ Description：Appium api 封装层
"""

import time
import allure
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from utils import L


def Ldict(element, type, name=None, text=None, time=5, index=0):
    """
    :param element: 查找元素的名称 例如：xxx:id/xx
    :param type: 元素类型 id,xpath,class name,accessibility id
    :param name: 测试步骤的名称
    :param : 需要输入文本的名称
    :param time: 查找该元素需要的时间，默认 5s
    :param index: 不为空则查找元素数组下标
    :return:
    """
    return {'element': element, 'type': type, 'name': name, 'text': text, 'time': time, 'index': index}


class NotFoundElementError(Exception):
    pass


class NotFoundTextError(Exception):
    pass


class ElementActions:
    def __init__(self, driver: webdriver.Remote, adb=None, Parameterdict=None):
        self.Parameterdict = Parameterdict
        self.driver = driver
        self.ADB = adb
        if Parameterdict:
            self.width = self.driver.get_window_size()['width']
            self.height = self.driver.get_window_size()['height']
            self.apppid = self.get_app_pid()

    def reset(self, driver: webdriver.Remote):
        """单例模式下,当driver变动的时候,需要重置一下driver
        单例模式开启装饰器singleton

        Args:
            driver: driver

        """
        self.driver = driver
        self.width = self.driver.get_window_size()['width']
        self.height = self.driver.get_window_size()['height']
        return self

    def adb_shell(self, command, args, includeStderr=False):
        """
        appium --relaxed-security 方式启动
        adb_shell('ps',['|','grep','android'])

        :param command:命令
        :param args:参数
        :param includeStderr: 为 True 则抛异常
        :return:
        """
        result = self.driver.execute_script('mobile: shell', {
            'command': command,
            'args': args,
            'includeStderr': includeStderr,
            'timeout': 5000
            })
        return result['stdout']

    def get_app_pid(self):
        """ 获取包名PID 进程
        :return: int PID
        """
        result = self.ADB.shell('"ps | grep {0}"'.format(self.Parameterdict.get('appPackage')))

        # result = self.adb_shell('ps', ['|', 'grep', self.Parameterdict.get('appPackage')])
        if result:
            return result.split()[1]
        else:
            return False

    def set_keycode_search(self):
        """ 搜索键
        """
        self._send_key_event('KEYCODE_SEARCH')

    def set_keycode_enter(self):
        """ 回车键
        """
        self._send_key_event('KEYCODE_ENTER')

    def clear(self):
        self.driver.quit()

    def launchApp(self):
        """ 重启应用程序
        """
        with allure.step("重启应用程序"):
            self.driver.launch_app()
            self.apppid = self.get_app_pid()

    def open_url(self, locator):
        self.driver.get(locator.get('text'))

    @staticmethod
    def sleep(s):
        if isinstance(s, dict):
            s = s['element']
        return time.sleep(s)

    def back_press(self):
        L.i("系统按键返回上一页")
        self.sleep(1)
        self._send_key_event('KEYCODE_BACK')

    def dialog_ok(self, wait=5):
        locator = {'name': '对话框确认键', 'timeOutInSeconds': wait, 'type': 'id', 'value': 'android:id/button1'}
        self.click(locator)

    def screenshot_element(self, locator):
        # 元素区域截图
        element = self._find_element(locator)
        pngbyte = element.screenshot_as_png
        allure.attach(pngbyte, locator.get('name'), allure.attachment_type.PNG)

    def set_number_by_soft_keyboard(self, nums):
        """模仿键盘输入数字,主要用在输入取餐码类似场景

        Args:
            nums: 数字
        """
        list_nums = list(nums)
        for num in list_nums:
            self._send_key_event('KEYCODE_NUM', num)

    def click(self, locator, count=1):
        """基础的点击事件
        :param locator: 定位器
        :param count: 点击次数
        """
        if locator.get('index'):
            el = self._find_elements(locator)[locator['index']]
        else:
            el = self._find_element(locator)

        if count == 1:
            el.click()
        else:
            touch_action = TouchAction(self.driver)
            try:
                for x in range(count):
                    touch_action.tap(el).perform()
            except:
                pass

    def get_text(self, locator):
        """获取元素中的text文本
        :param locator: 定位器
        """
        L.i("[获取]元素 %s " % locator.get('name'))

        if locator.get('index'):
            el = self._find_elements(locator)[locator['index']]
        else:
            el = self._find_element(locator)

        return el.text

    def set_text(self, locator, clear_first=False, click_first=True):
        """ 输入文本
        :param locator: 定位器
        :param clear_first: 是否先清空原来文本
        :param click_first: 是否先点击选中
        """
        value = locator.get('text')
        if click_first:
            self._find_element(locator).click()
        if clear_first:
            self._find_element(locator).clear()
        L.i("[输入]元素 %s " % value)
        with allure.step("输入元素：{0}".format(value)):
            self._find_element(locator).send_keys(value)

    def swipeElementUp(self, element):
        """ IOS专用 在元素内部滑动
        :param element: 以查找到的元素
        """
        scrolldict = {'direction': 'left', 'element': element.id}
        self.driver.execute_script('mobile: swipe', scrolldict)

    def swip_down(self, count=1, method=None, speed=1000):
        """ 向下滑动,常用于下拉刷新
        :param count: 滑动次数
        :param method: 传入的方法 method(action) ,如果返回为True,则终止刷新
        :param speed: 滑动速度 ms
        """
        if count == 1:
            self.driver.swipe(self.width / 2, self.height * 2 / 5, self.width / 2, self.height * 4 / 5, speed)
            self.sleep(1)
        else:
            for x in range(count):
                self.driver.swipe(self.width / 2, self.height * 2 / 5, self.width / 2, self.height * 4 / 5, speed)
                self.sleep(1)
                try:
                    if method(self):
                        break
                except:
                    pass
        L.i("[滑动]向下刷新 ")

    def swip_up(self, count=1, method=None, speed=1000):
        """ 向上刷新
        :param count: 滑动次数
        :param method: 传入的方法 method(action) ,如果返回为True,则终止刷新
        :param speed: 滑动速度 ms
        :return:

        """
        if count == 1:
            self.sleep(1)
            self.driver.swipe(self.width / 2, self.height * 3 / 4, self.width / 2, self.height / 4, speed)
            self.sleep(2)
        else:
            for x in range(count):
                self.driver.swipe(self.width / 2, self.height * 3 / 4, self.width / 2, self.height / 4, speed)
                self.sleep(2)
                try:
                    if method(self):
                        break
                except:
                    pass
        L.i("[滑动]向上刷新 ")

    def swip_left(self, height=0.5, count=1, speed=1000):
        """ 向左滑动
        :param height: 高度满屏幕为1
        :param count: 滑动次数
        :param speed: 滑动速度 ms
        :return:
        """
        for x in range(count):
            self.sleep(1)
            self.driver.swipe(self.width * 7 / 8, self.height * height, self.width / 8, self.height * height, speed)
            self.sleep(2)
            L.i("[滑动]向左滑动")

    def swip_right(self, height=0.5, count=1, speed=1000):
        """向右滑动
        :param height: 高度满屏幕为1
        :param count: 滑动次数
        :param speed: 滑动速度 ms
        :return:
        """
        for x in range(count):
            self.sleep(1)
            self.driver.swipe(self.width / 8, self.height * height, self.width * 7 / 8, self.height * height, speed)
            self.sleep(2)
            L.i("[滑动]向右滑动 ")

    def is_element_displayed(self, locator, is_raise=False, element=True):
        """ ：控件是否显示e
        :param locator: 定位器
        :param is_raise: 是否抛异常
        :param element:
        :returns:
            true:  显示
            false: 不显示
        """
        try:
            return WebDriverWait(self.driver, 2).until(
                lambda driver: self._get_element_by_type(driver, locator),
                '查找元素{0}失败'.format(locator.get('name'))) if element else WebDriverWait(self.driver, 2).until(
                lambda driver: self._get_element_by_type(driver, locator, element_type=False),
                '查找元素{0}失败'.format(locator.get('name')))

        except Exception as E:
            L.w("页面中未找到 %s " % locator)
            if is_raise:
                raise E
            else:
                return False

    # ======================= private ====================

    def _find_element(self, locator, is_need_displayed=True):
        """ ：单个元素,如果有多个返回第一个
        :param locator: 定位器
        :param is_need_displayed: 是否需要定位的元素必须展示
        :return:
        :raises:NotFoundElementError
        """

        with allure.step("检查：'{0}'".format(locator.get('name'))):
            try:
                if is_need_displayed:
                    return WebDriverWait(self.driver, locator['time']).until(
                        lambda driver: self._get_element_by_type(driver, locator), '查找元素'.format(locator.get('name')))

            except Exception as e:
                print(e)
                L.e("页面中未能找到 %s 元素" % locator)
                raise Exception("页面中未能找到 [%s]" % locator.get('name'))

    def _find_elements(self, locator):
        """ 查找多元素
        :param locator: 定位器
        :return:  []
        """
        with allure.step("检查：'{0}'".format(locator.get('name'))):
            try:
                return WebDriverWait(self.driver, locator['time']).until(
                    lambda driver: self._get_element_by_type(driver, locator, False))
            except:
                L.w("[elements] 页面中未能找到 %s 元素" % locator)
                return []

    @staticmethod
    def _get_element_by_type(driver, locator, element_type=True):
        """
        :param driver: driver session
        :param locator: 定位器
        :param element_type: 查找元素类型
            true：单个元素
            false：多个元素
        :return: 单个元素 或 元素list
        """
        element = locator['element']
        ltype = locator['type']

        return driver.find_element(ltype, element) if element_type else driver.find_elements(ltype, element)

    def _send_key_event(self, arg, num=0):
        """
        操作实体按键
        Code码：https://developer.android.com/reference/android/view/KeyEvent.2018-5-21-18
        Args:
            arg: event_list key
            num: KEYCODE_NUM 时用到对应数字

        """
        event_list = {'KEYCODE_HOME': 3, 'KEYCODE_BACK': 4, 'KEYCODE_MENU': 82, 'KEYCODE_NUM': 8, 'KEYCODE_ENTER': 66,
                      'KEYCODE_SEARCH': 84}
        if arg == 'KEYCODE_NUM':
            self.driver.press_keycode(8 + int(num))
        elif arg in event_list:
            self.driver.press_keycode(int(event_list[arg]))

    def _set_network(self, arg):
        """
        :param arg:可用 Android设置网络模式飞行模式，wifi，移动网络
        :return:
        """
        event_list = {'Nonetwork': 0, 'Airplane': 1, 'wifi': 2, 'network': 4, 'Allnetwork': 6}
        self.driver.set_network_connection(event_list[arg])

    def photograph(self):
        """不同系统手机拍照+确认"""
        str = self.ADB.get_android_brand()
        if 'MI' in str:
            '''
            MIUI
            '''
            self.driver.press_keycode(27)
            self.click(Ldict('com.miui.gallery:id/ok', By.ID, "确认按钮"))
        elif 'vivo' in str:
            self.click(Ldict('com.android.camera:id/shutter_button', By.ID, '拍照按钮'))
            self.click(Ldict('com.android.camera:id/btn_done', By.ID, '确认按钮'))
        # 三星
        elif 'G9350' in str:
            self.driver.press_keycode(27)
            self.click(Ldict('com.sec.android.app.camera:id/okay', By.ID, '保存'))
            self.click(Ldict('com.sec.android.gallery3d:id/save', By.ID, '完成'))

        elif 'Samsung' in str:
            self.click(Ldict('com.android.camera2:id/shutter_button', By.ID, '拍照按钮'))
            self.click(Ldict('com.android.camera2:id/done_button', By.ID, '确认按钮'))

        elif 'honor' in str:
            self.click(Ldict('com.huawei.camera:id/shutter_button', By.ID, '拍照按钮'))
            self.click(Ldict('com.huawei.camera:id/btn_review_confirm', By.ID, '确认按钮'))

        elif 'nubia' in str:
            self.click(Ldict('com.android.camera:id/shutter_button', By.ID, '拍照按钮'))
            self.click(Ldict('com.android.camera:id/btn_done', By.ID, '确认按钮'))

    def click_shoot_windows(self):
        """
        :return:检测权限窗口
        """

        try:
            els = self._find_elements(Ldict('android.widget.Button', By.CLASS_NAME, '获取权限', 2))
            for el in els:
                text1 = el.text
                if text1 == '允许':
                    el.click()
                    return True
                elif text1 == '始终允许':
                    el.click()
                    return True
                elif text1 == '确定':
                    el.click()
                    return True
            return False
        except:
            return False
