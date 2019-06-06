# -*- coding: utf-8 -*-
"""
@ Author：YueC
@ Description：driver 驱动
"""

from appium import webdriver
from base.action import ElementActions
from utils import shell
from utils.shell import Device


class Singleton(object):
    """单例模式
    """
    Action = None

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            udid = Device.get_android_devices()[0]
            host = "http://localhost:4723/wd/hub"
            desired_caps = {'appActivity': '.SplashActivity',
                            'appPackage': 'com.sina.weibo',
                            'autoGrantPermissions': True,
                            'autoLaunch': False,
                            'automationName': 'UiAutomator2',
                            'deviceName': udid,
                            'noReset': True,
                            'platformName': 'Android',
                            'platformVersion': '9.0',
                            'udid': udid}

            driver = webdriver.Remote(host, desired_caps)
            ADB = shell.ADB(udid)
            desired_caps['platformVersion'] = ADB.get_android_version()
            Action = ElementActions(driver, ADB, Parameterdict=desired_caps)
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
            cls._instance.Action = Action
        return cls._instance


class DriverClient(Singleton):
    pass
