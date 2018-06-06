# -*- coding: utf-8 -*-
import os

LOGDIR = "log"


class SeleniumReport(object):

    def __init__(self, export_dir, log_root):
        self.target_screen = ['click', 'touch', 'assert_exist', 'send_keys']
        self.export_dir = export_dir
        self.log_root = log_root

    def report_parse(self, step):
        """
        按照depth = 1 的name来分类
        touch,swipe,wait,exist 都是搜索图片位置，然后执行操作，包括3层调用
                            3=screenshot 2= _loop_find  1=本身操作
        keyevent,text,sleep 和图片无关，直接显示一条说明就可以
                            1= 本身
        assert 类似于exist
        """
        if step['type'] in self.target_screen:
            # 一般来说会有截图 没有这层就无法找到截图了
            st = 1
            while st in step:
                if 'screen' in step[st]:
                    screenshot = step[st]['screen']
                    if self.export_dir:
                        screenshot = os.path.join(LOGDIR, screenshot)
                    else:
                        screenshot = os.path.join(self.log_root, screenshot)
                    step['screenshot'] = screenshot
                    break
                st += 1

            try:
                target = step[1]['args'][0]
            except (IndexError, KeyError):
                target = None
            if isinstance(target, (tuple, list)):
                step['target_pos'] = target
                step['left'], step['top'] = target

        return step

    def report_desc_zh(self, step):
        desc = {
            "get": u"进入网站{addr}".format(addr=step[1].get("args", "")),
            "assert_exist": u"断言存在页面元素",
            "send_keys": u"输入文本\"{text}\"到指定位置".format(text=step[1].get("data", {}).get("func_args", "")),
            "click": u"寻找目标控件，点击屏幕坐标%s" % repr(step.get('target_pos', '')),
            "back": u"返回上一个页面",
            "forward": u"前进下一个页面"
        }
        return desc

    def report_desc(self, step):
        desc = {
            "send_keys": "Send text {text} to element".format(text=step[1].get("data", {}).get("func_args", "")),
            "assert_exist": u"Assert element exists",
            "get": u"Get url {addr}".format(addr=step[1].get("args", "")),
            "back": u"Back to last page",
            "forward": u"Forward to next page",
            "click": u"Search for target element, touch the screen coordinates %s" % repr(step.get('target_pos', '')),
        }
        return desc

    def report_title(self):
        title = {
            "click": u"Click",
            "send_keys": u"Send keys",
            "assert_text": u"Assert text",
            "back": u"Back",
            "forward": u"Forward",
            "get": u"Get"
        }
        return title
