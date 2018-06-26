# -*- coding: utf-8 -*-

from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement
from airtest.core.settings import Settings as ST
from airtest.core.helper import logwrap
import os
import time
import sys


class WebChrome(Chrome):

    def __init__(self, chrome_options=None):
        if "darwin" in sys.platform:
            os.environ['PATH'] += ":/Applications/AirtestIDE.app/Contents/Resources/selenium_plugin"
        super(WebChrome, self).__init__(chrome_options=chrome_options)
        self.father_number = {0: 0}
        self.number = 0
        self.operation_to_func = {"xpath": self.find_element_by_xpath, "id": self.find_element_by_id, "name": self.find_element_by_name}

    @logwrap
    def find_element_by_xpath(self, xpath):
        web_element = super(WebChrome, self).find_element_by_xpath(xpath)
        log_res = self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def find_element_by_id(self, id):
        web_element = super(WebChrome, self).find_element_by_id(id)
        log_res = self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def find_element_by_name(self, name):
        web_element = super(WebChrome, self).find_element_by_name(name)
        log_res = self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def switch_to_latest_window(self):
        _father = self.number
        self.number = len(self.window_handles) - 1
        self.father_number[self.number] = _father
        self.switch_to_window(self.window_handles[self.number])
        self._gen_screen_log()
        time.sleep(0.5)

    @logwrap
    def switch_to_last_window(self):
        self.number = self.father_number[self.number]
        self.switch_to_window(self.window_handles[self.number])
        self._gen_screen_log()
        time.sleep(0.5)

    @logwrap
    def assert_exist(self, path, operation):
        try:
            func = self.operation_to_func[operation]
        except Exception:
            print("There was no operation: ", operation)
            return
        try:
            func(path)
        except Exception as e:
            return False
        return True

    @logwrap
    def get(self, address):
        super(WebChrome, self).get(address)
        time.sleep(2)

    @logwrap
    def back(self):
        super(WebChrome, self).back()
        self._gen_screen_log()
        time.sleep(1)

    @logwrap
    def forward(self):
        super(WebChrome, self).forward()
        self._gen_screen_log()
        time.sleep(1)

    @logwrap
    def snapshot(self):
        self._gen_screen_log()

    @logwrap
    def _gen_screen_log(self, element=None):
        if ST.LOG_DIR is None:
            return None
        jpg_file_name = str(int(time.time())) + '.jpg'
        jpg_path = os.path.join(ST.LOG_DIR, jpg_file_name)
        self.save_screenshot(jpg_path)
        saved = {"screen": jpg_file_name}
        if element:
            size = element.size
            location = element.location
            x = size['width'] / 2 + location['x']
            y = size['height'] / 2 + location['y']
            if "darwin" in sys.platform:
                x, y = x * 2, y * 2
            saved.update({"pos": [[x, y]],})
        return saved

    def to_json(self):
        # add this method for json encoder in logwrap
        return repr(self)


class Element(WebElement):

    def __init__(self, _obj, log):
        super(Element, self).__init__(parent=_obj._parent, id_=_obj._id, w3c=_obj._w3c)
        self.res_log = log

    def click(self):
        super(Element, self).click()
        time.sleep(0.5)
        return self.res_log

    def send_keys(self, text, keyborad=None):
        if keyborad:
            super(Element, self).send_keys(text, keyborad)
        else:
            super(Element, self).send_keys(text)
        time.sleep(0.5)
        return self.res_log