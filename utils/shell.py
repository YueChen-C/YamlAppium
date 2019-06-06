# -*- coding: utf-8 -*-
import subprocess


class Shell:
    @staticmethod
    def invoke(cmd):
        output, errors = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        o = output.decode("utf-8")
        return o


class Device:
    @staticmethod
    def get_android_devices():
        android_devices_list = []
        for device in Shell.invoke('adb devices').splitlines():
            if 'device' in device and 'devices' not in device:
                device = device.split('\t')[0]
                android_devices_list.append(device)
        return android_devices_list


class ADB(object):
    """
      参数:  device_id
    """

    def __init__(self, device_id=""):

        if device_id == "":
            self.device_id = ""
        else:
            self.device_id = "-s %s" % device_id

    def adb(self, args):
        cmd = "adb {0} {1}".format(self.device_id, str(args))
        return Shell.invoke(cmd)

    def shell(self, args):

        cmd = "adb {0} shell {1}".format(self.device_id, str(args))
        return Shell.invoke(cmd)

    def get_device_state(self):
        """
        获取设备状态： offline | bootloader | device
        """
        return self.adb("get-state").strip()

    def connect_android_tcp(self, ip):
        """
        绑定设备信息 用于无线测试
        """
        self.adb('tcpip 5555')
        return self.adb('connect {0}:5555'.format(ip)).strip()

    def disconnect_android_tcp(self, ip):
        """
        解除设备信息 用于无线测试
        """
        self.adb('tcpip 5555')
        return self.adb('disconnect {0}:5555'.format(ip)).strip()

    def get_device_id(self):
        """
        获取设备id号，return serialNo
        """
        return self.adb("get-serialno").strip()

    def get_android_version(self):
        """
        获取设备中的Android版本号，如4.2.2
        """
        return self.shell(
            "getprop ro.build.version.release").strip()

    def get_sdk_version(self):
        """
        获取设备SDK版本号
        """
        return self.shell("getprop ro.build.version.sdk").strip()

    def get_android_model(self):
        """
        获取设备型号
        """

        return self.shell('getprop ro.product.model').strip()

    def get_android_ip(self):
        """
        获取设备IP
        """
        return self.shell('netcfg | find "wlan0"').strip().split()[2].split('/')[0]

    def get_rcepageage_version(self):
        """
        :return: (版本日期，版本号)
        """
        return self.shell('dumpsys package cn.rongcloud.rce | findstr version').split()
