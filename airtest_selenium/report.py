# -*- coding: utf-8 -*-
import os
import airtest.report.report as report

LOGDIR = "log"

old_trans_screen = report.LogToHtml._translate_screen
old_trans_desc = report.LogToHtml._translate_desc
old_trans_code = report.LogToHtml._translate_code

screen_func = ["find_element_by_xpath", "find_element_by_id", "find_element_by_name", "assert_exist",
               "back", "forward", "switch_to_last_window", "switch_to_latest_window", "get",
               "click", "send_keys"]

second_screen_func = ["click", "send_keys"]
other_func = []

def new_trans_screen(self, step, code):
    trans = old_trans_screen(self, step, code)
    if "name" in step['data'] and step['data']["name"] in screen_func:
        screen = {
            "src": None,
            "rect": [],
            "pos": [],
            "vector": [],
            "confidence": None,
        }

        if step["data"]["name"] in second_screen_func:
            res = step["data"]['ret']
            screen["src"] = res["screen"]
            if "pos" in res:
                screen["pos"] = res["pos"]

        for item in step["__children__"]:
            if item["data"]["name"] == "_gen_screen_log":
                res = item["data"]['ret']
                screen["src"] = res["screen"]
                if "pos" in res:
                    screen["pos"] = res["pos"]
                break
        return screen
    else:
        print("old result:", trans)
        return trans

def new_translate_desc(self, step, code):
    trans = old_trans_desc(self, step, code)
    if "name" in step['data'] and (step['data']["name"] in screen_func or step["data"]["name"] in other_func):
        name = step["data"]["name"]
        args = {i["key"]: i["value"] for i in code["args"]}
        desc = {
            "find_element_by_xpath": lambda: u"Find element by xpath: %s" % args.get("xpath"),
            "find_element_by_id": lambda: u"Find element by id: %s" % args.get("id"),
            "find_element_by_name": lambda: u"Find element by name: %s" % args.get("name"),
            "assert_exist": u"Assert element exists.",
            "click": u"Click the element that been found.",
            "send_keys": u"Send some text and keyboard event to the element that been found.",
            "get": lambda: u"Get the web address: %s" % args.get("address"),
            "switch_to_last_window": u"Switch to the last tab.",
            "switch_to_latest_window": u"Switch to the new tab.",
            "back": u"Back to the last page.",
            "forward": u"Forward to the next page.",
            "snapshot": u"Snopshot current page."
        }

        desc_zh = {
            "find_element_by_xpath": lambda: u"寻找指定页面元素: \"%s\"" % args.get("xpath"),
            "find_element_by_id": lambda: u"寻找指定页面元素: \"%s\"" % args.get("id"),
            "find_element_by_name": lambda: u"寻找指定页面元素: \"%s\"" % args.get("name"),
            "assert_exist": u"断言页面元素存在.",
            "click": u"点击找到的页面元素.",
            "send_keys": u"传送文本\"%s\"到选中文本框." % (args.get("text", "")),
            "get": lambda: u"访问网络地址: %s" % args.get("address"),
            "switch_to_last_window": u"切换到上一个标签页.",
            "switch_to_latest_window": u"切换到最新标签页.",
            "back": u"后退到上一个页面.",
            "forward": u"前进到下一个页面.",
            "snapshot": u"截取当前页面."
        }

        if self.lang == 'zh':
            desc = desc_zh
        ret = desc.get(name)
        if callable(ret):
            ret = ret()
        return ret
    else:
        return trans

def new_translate_code(self, step):
    trans = old_trans_code(self, step)
    print("this is args*************************************", trans)
    for idx, item in enumerate(trans["args"]):
        if item["key"] == "self":
            trans["args"].pop(idx)
    return trans


report.LogToHtml._translate_screen = new_trans_screen
report.LogToHtml._translate_desc = new_translate_desc
report.LogToHtml._translate_code = new_translate_code


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
