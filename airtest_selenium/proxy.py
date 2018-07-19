# -*- coding: utf-8 -*-

from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from airtest.core.settings import Settings as ST
from airtest.core.helper import logwrap
from airtest import aircv
from airtest.core.cv import Template
from airtest_selenium.utils.airtest_api import loop_find
from airtest_selenium.exceptions import IsNotTemplateError
from airtest.aircv import get_resolution
from pynput.mouse import Controller, Button
from airtest.core.error import TargetNotFoundError
import os
import time
import sys


class WebChrome(Chrome):

    def __init__(self, chrome_options=None):
        if "darwin" in sys.platform:
            os.environ['PATH'] += ":/Applications/AirtestIDE.app/Contents/Resources/selenium_plugin"
        super(WebChrome, self).__init__(chrome_options=chrome_options)
        self.father_number = {0: 0}
        self.action_chains = ActionChains(self)
        self.number = 0
        self.mouse = Controller()
        self.operation_to_func = {"xpath": self.find_element_by_xpath, "id": self.find_element_by_id, "name": self.find_element_by_name}

    def loop_find_element(self, func, text, timeout=10, interval=0.5):
        start_time = time.time()
        while True:
            try:
                element = func(text)
            except NoSuchElementException:
                print("Element not found!")
                # 超时则raise，未超时则进行下次循环:
                if (time.time() - start_time) > timeout:
                    # try_log_screen(screen)
                    raise NoSuchElementException('Element %s not found in screen' % text)
                else:
                    time.sleep(interval)
            else:
                return element

    @logwrap
    def find_element_by_xpath(self, xpath):
        web_element = self.loop_find_element(super(WebChrome, self).find_element_by_xpath, xpath)
        # web_element = super(WebChrome, self).find_element_by_xpath(xpath)
        log_res = self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def find_element_by_id(self, id):
        web_element = self.loop_find_element(super(WebChrome, self).find_element_by_id, id)
        log_res = self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def find_element_by_name(self, name):
        web_element = self.loop_find_element(super(WebChrome, self).find_element_by_name, name)
        log_res = self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def switch_to_new_tab(self):
        _father = self.number
        self.number = len(self.window_handles) - 1
        self.father_number[self.number] = _father
        self.switch_to.window(self.window_handles[self.number])
        self._gen_screen_log()
        time.sleep(0.5)

    @logwrap
    def switch_to_previous_tab(self):
        self.number = self.father_number[self.number]
        self.switch_to.window(self.window_handles[self.number])
        self._gen_screen_log()
        time.sleep(0.5)

    @logwrap
    def airtest_touch(self, v):
        if isinstance(v, Template):
            pos = loop_find(v, timeout=ST.FIND_TIMEOUT, driver=self)
        else:
            pos = v
        x, y = pos
        # self.action_chains.move_to_element_with_offset(root_element, x, y)
        # self.action_chains.click()
        pos = self._get_left_up_offset()
        pos = (pos[0] + x, pos[1] + y)
        self._move_to_pos(pos)
        self._click_current_pos()
        time.sleep(1)

    @logwrap
    def assert_template(self, v):
        if isinstance(v, Template):
            try:
                pos = loop_find(v, timeout=ST.FIND_TIMEOUT, driver=self)
            except TargetNotFoundError:
                raise TargetNotFoundError("Target template not found on screen")
            else:
                return True
        else:
            raise IsNotTemplateError("args is not a template")

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
        self.screenshot(jpg_path)
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

    def screenshot(self, file_path=None):
        if file_path:
            self.save_screenshot(file_path)
        else:
            file_path = os.path.join(ST.LOG_DIR, "temp.jpg")
            self.save_screenshot(file_path)
            screen = aircv.imread(file_path)
            return screen

    def _get_left_up_offset(self):
        window_pos = self.get_window_position()
        window_size = self.get_window_size()
        mouse = Controller()
        screen = self.screenshot()
        screen_size = get_resolution(screen)
        offset = window_size["width"] - screen_size[0], window_size["height"] - screen_size[1]
        pos = (int(offset[0] / 2 + window_pos['x']), int(offset[1] + window_pos['y'] - offset[0] / 2))
        return pos

    def _move_to_pos(self, pos):
        self.mouse.position = pos

    def _click_current_pos(self):
        self.mouse.click(Button.left, 1)

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
