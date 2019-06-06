Pytest 运行 Yaml 来驱动 Appium 进行 UI 测试

Yaml 使用方式规则
---

```yaml
test_index:
  -
    method: launchApp # 启动 APP
  -
    method: 方法名称 例如：click （必填）
    element: 查找元素id,class等 （选填，配合 method 如需要点击元素，查找元素等必填）
    type: 元素类型 id,xpath,class  name,accessibility id （选填，会自动识别，如识别错误则自行填写）
    name: 测试步骤的名称 例如：点击搜索按钮 （选填）
    text: 需要输入或者查找的文本 （选填，配合部分 method 使用）
    time: 查找该元素需要的时间，默认 5s （选填）
    index: 页面有多个id，class时，不为空则查找元素数组下标 （选填）
    is_displayed: 默认 True ，当为 False 时元素未找到也不会抛异常（选填）
```
```
 需要参数的 method
 |  click(self, locator)
 |      基础的点击事件
 |  is_element_displayed(self, locator)
 |      控件是否显示e
 |  get_text(self, locator)
 |      获取元素文本
 |  screenshot_element(self, locator)
 |      区域截图
 |  set_text(self, locator)
 |      输入文本
 
 不需要参数的 method
 |  launchApp(self)
 |      重启应用程序
 |  photograph(self)
 |      拍照
 |  set_keycode_enter(self)
 |      回车键
 |  set_keycode_search(self)
 |      搜索键 
 |  swip_down(self)
 |      向下滑动,常用于下拉刷新
 |  swip_left(self)
 |      向左滑动
 |  swip_right(self)
 |      向右滑动
 |  swip_up(self)
 |      向上刷新
 |  click_shoot_windows(self)
 |      检测权限窗口 
```
#### 运行方式
> pytest -s ./test_case/test_ranking.yml --alluredir './report/test'

或者直接运行文件目录

使用方法和基本 pytest 用法没有太大区别
> pytest -s ./test_case --alluredir './report/test'