# -*- coding: utf-8 -*-

from selenium.webdriver import Chrome, ActionChains, Firefox, Remote
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

    def __init__(self, executable_path="chromedriver", port=0,
                 options=None, service_args=None,
                 desired_capabilities=None, service_log_path=None,
                 chrome_options=None):
        if "darwin" in sys.platform:
            os.environ['PATH'] += ":/Applications/AirtestIDE.app/Contents/Resources/selenium_plugin"
        super(WebChrome, self).__init__(chrome_options=chrome_options, executable_path=executable_path,
                                        port=port, options=options, service_args=service_args,
                                        service_log_path=service_log_path, desired_capabilities=desired_capabilities)
        self.father_number = {0: 0}
        self.action_chains = ActionChains(self)
        self.number = 0
        self.mouse = Controller()
        self.operation_to_func = {"xpath": self.find_element_by_xpath, "id": self.find_element_by_id,
                                  "name": self.find_element_by_name, "css": self.find_element_by_css_selector}

    def loop_find_element(self, func, text, timeout=10, interval=0.5):
        """
        Loop to find the target web element by func.

        Args:
            func: function to find element
            text: param of function
            timeout: time to find the element
            interval: interval between operation
        Returns:
            element that been found
        """
        start_time = time.time()
        while True:
            try:
                element = func(text)
            except NoSuchElementException:
                print("Element not found!")
                # 超时则raise，未超时则进行下次循环:
                if (time.time() - start_time) > timeout:
                    # try_log_screen(screen)
                    raise NoSuchElementException(
                        'Element %s not found in screen' % text)
                else:
                    time.sleep(interval)
            else:
                return element

    @logwrap
    def find_element_by_xpath(self, xpath):
        """
        Find the web element by xpath.

        Args:
            xpath: find the element by xpath.
        Returns:
            Web element of current page.
        """
        web_element = self.loop_find_element(
            super(WebChrome, self).find_element_by_xpath, xpath)
        # web_element = super(WebChrome, self).find_element_by_xpath(xpath)
        log_res = self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def find_element_by_id(self, id):
        """
        Find the web element by id.

        Args:
            id: find the element by attribute id.
        Returns:
            Web element of current page.
        """
        web_element = self.loop_find_element(
            super(WebChrome, self).find_element_by_id, id)
        log_res = self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def find_element_by_css_selector(self, css_selector):
        """
        Find the web element by css_selector.

        Args:
            css_selector: find the element by attribute css_selector.
        Returns:
            Web element of current page.
        """
        web_element = self.loop_find_element(
            super(WebChrome, self).find_element_by_css_selector, css_selector)
        log_res = self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def find_element_by_name(self, name):
        """
        Find the web element by name.

        Args:
            name: find the element by attribute name.
        Returns:
            Web element of current page.
        """
        web_element = self.loop_find_element(
            super(WebChrome, self).find_element_by_name, name)
        log_res = self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def switch_to_new_tab(self):
        """
        Switch to the new tab.
        """
        _father = self.number
        self.number = len(self.window_handles) - 1
        self.father_number[self.number] = _father
        self.switch_to.window(self.window_handles[self.number])
        self._gen_screen_log()
        time.sleep(0.5)

    @logwrap
    def switch_to_previous_tab(self):
        """
        Switch to the previous tab(which to open current tab).
        """
        self.number = self.father_number[self.number]
        self.switch_to.window(self.window_handles[self.number])
        self._gen_screen_log()
        time.sleep(0.5)

    @logwrap
    def airtest_touch(self, v):
        """
        Perform the touch action on the current page by image identification.

        Args:
            v: target to touch, either a Template instance or absolute coordinates (x, y)
        Returns:
            Finial position to be clicked.
        """
        if isinstance(v, Template):
            _pos = loop_find(v, timeout=ST.FIND_TIMEOUT, driver=self)
        else:
            _pos = v
        x, y = _pos
        # self.action_chains.move_to_element_with_offset(root_element, x, y)
        # self.action_chains.click()
        pos = self._get_left_up_offset()
        pos = (pos[0] + x, pos[1] + y)
        self._move_to_pos(pos)
        self._click_current_pos()
        time.sleep(1)
        return _pos

    @logwrap
    def assert_template(self, v, msg=""):
        """
        Assert target exists on the current page.

        Args:
            v: target to touch, either a Template instance
        Raise:
            AssertionError - if target not found.
        Returns:
            Position of the template.
        """
        if isinstance(v, Template):
            try:
                pos = loop_find(v, timeout=ST.FIND_TIMEOUT, driver=self)
            except TargetNotFoundError:
                raise AssertionError("Target template not found on screen.")
            else:
                return pos
        else:
            raise IsNotTemplateError("args is not a template")

    @logwrap
    def assert_exist(self, param, operation, msg=""):
        """
        Assert element exist.

        Args:
            operation: the method that to find the element.
            param: the param of method.
        Raise:
            AssertionError - if assertion failed.
        """
        try:
            func = self.operation_to_func[operation]
        except Exception:
            raise AssertionError("There was no operation: %s" % operation)
        try:
            func(param)
        except Exception as e:
            raise AssertionError("Target element not find.")

    @logwrap
    def get(self, address):
        """
        Access the web address.

        Args:
            address: the address that to accesss
        """
        super(WebChrome, self).get(address)
        time.sleep(2)

    @logwrap
    def back(self):
        """
        Back to last page.
        """
        super(WebChrome, self).back()
        self._gen_screen_log()
        time.sleep(1)

    @logwrap
    def forward(self):
        """
        Forward to next page.
        """
        super(WebChrome, self).forward()
        self._gen_screen_log()
        time.sleep(1)

    @logwrap
    def snapshot(self, filename=None):
        self._gen_screen_log(filename=filename)

    @logwrap
    def _gen_screen_log(self, element=None, filename=None,):
        if ST.LOG_DIR is None:
            return None
        if filename:
            self.screenshot(filename)
        jpg_file_name = str(int(time.time())) + '.jpg'
        jpg_path = os.path.join(ST.LOG_DIR, jpg_file_name)
        print("this is jpg path:", jpg_path)
        self.screenshot(jpg_path)
        saved = {"screen": jpg_file_name}
        if element:
            size = element.size
            location = element.location
            x = size['width'] / 2 + location['x']
            y = size['height'] / 2 + location['y']
            if "darwin" in sys.platform:
                x, y = x * 2, y * 2
            saved.update({"pos": [[x, y]], })
        return saved

    def screenshot(self, file_path=None):
        if file_path:
            self.save_screenshot(file_path)
        else:
            if not ST.LOG_DIR:
                file_path = "temp.jpg"
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
        offset = window_size["width"] - \
            screen_size[0], window_size["height"] - screen_size[1]
        pos = (int(offset[0] / 2 + window_pos['x']),
               int(offset[1] + window_pos['y'] - offset[0] / 2))
        return pos

    def _move_to_pos(self, pos):
        self.mouse.position = pos

    def _click_current_pos(self):
        self.mouse.click(Button.left, 1)

    def to_json(self):
        # add this method for json encoder in logwrap
        return repr(self)


class WebRemote(Remote):           

    def __init__(self, command_executor='http://127.0.0.1:4444/wd/hub',
                 desired_capabilities=None, browser_profile=None, proxy=None,
                 keep_alive=False, file_detector=None, options=None):
        super(WebRemote,self).__init__(command_executor=command_executor,
                 desired_capabilities=desired_capabilities, browser_profile=browser_profile, proxy=proxy,
                 keep_alive=keep_alive, file_detector=file_detector, options=options)

        self.father_number = {0: 0}
        self.action_chains = ActionChains(self)
        self.number = 0
        self.mouse=Controller()
        self.operation_to_func={"xpath": self.find_element_by_xpath, "id": self.find_element_by_id,
                                  "name": self.find_element_by_name, "css": self.find_element_by_css_selector}

    def loop_find_element(self, func, text, timeout=10, interval=0.5):
        """
        Loop to find the target web element by func.

        Args:
            func: function to find element
            text: param of function
            timeout: time to find the element
            interval: interval between operation
        Returns:
            element that been found
        """
        start_time=time.time()
        while True:
            try:
                element=func(text)
            except NoSuchElementException:
                print("Element not found!")
                # 超时则raise，未超时则进行下次循环:
                if (time.time() - start_time) > timeout:
                    # try_log_screen(screen)
                    raise NoSuchElementException(
                        'Element %s not found in screen' % text)
                else:
                    time.sleep(interval)
            else:
                return element

    @logwrap
    def find_element_by_xpath(self, xpath):
        """
        Find the web element by xpath.

        Args:
            xpath: find the element by xpath.
        Returns:
            Web element of current page.
        """
        web_element=self.loop_find_element(
            super(WebRemote, self).find_element_by_xpath, xpath)
        log_res=self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def find_element_by_id(self, id):
        """
        Find the web element by id.

        Args:
            id: find the element by attribute id.
        Returns:
            Web element of current page.
        """
        web_element=self.loop_find_element(
            super(WebRemote, self).find_element_by_id, id)
        log_res=self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def find_element_by_css_selector(self, css_selector):
        """
        Find the web element by css_selector.

        Args:
            css_selector: find the element by attribute css_selector.
        Returns:
            Web element of current page.
        """
        web_element=self.loop_find_element(
            super(WebRemote, self).find_element_by_css_selector, css_selector)
        log_res=self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def find_element_by_name(self, name):
        """
        Find the web element by name.

        Args:
            name: find the element by attribute name.
        Returns:
            Web element of current page.
        """
        web_element=self.loop_find_element(
            super(WebRemote, self).find_element_by_name, name)
        log_res=self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def switch_to_new_tab(self):
        """
        Switch to the new tab.
        """
        _father=self.number
        self.number=len(self.window_handles) - 1
        self.father_number[self.number]=_father
        self.switch_to.window(self.window_handles[self.number])
        self._gen_screen_log()
        time.sleep(0.5)

    @logwrap
    def switch_to_previous_tab(self):
        """
        Switch to the previous tab(which to open current tab).
        """
        self.number=self.father_number[self.number]
        self.switch_to.window(self.window_handles[self.number])
        self._gen_screen_log()
        time.sleep(0.5)

    @logwrap
    def airtest_touch(self, v):
        """
        Perform the touch action on the current page by image identification.

        Args:
            v: target to touch, either a Template instance or absolute coordinates (x, y)
        Returns:
            Finial position to be clicked.
        """
        if isinstance(v, Template):
            _pos=loop_find(v, timeout=ST.FIND_TIMEOUT, driver=self)
        else:
            _pos=v
        x, y=_pos
        # self.action_chains.move_to_element_with_offset(root_element, x, y)
        # self.action_chains.click()
        pos=self._get_left_up_offset()
        pos=(pos[0] + x, pos[1] + y)
        self._move_to_pos(pos)
        self._click_current_pos()
        time.sleep(1)
        return _pos

    @logwrap
    def assert_template(self, v, msg=""):
        """
        Assert target exists on the current page.

        Args:
            v: target to touch, either a Template instance
        Raise:
            AssertionError - if target not found.
        Returns:
            Position of the template.
        """
        if isinstance(v, Template):
            try:
                pos=loop_find(v, timeout=ST.FIND_TIMEOUT, driver=self)
            except TargetNotFoundError:
                raise AssertionError("Target template not found on screen.")
            else:
                return pos
        else:
            raise IsNotTemplateError("args is not a template")

    @logwrap
    def assert_exist(self, param, operation, msg=""):
        """
        Assert element exist.

        Args:
            operation: the method that to find the element.
            param: the param of method.
        Raise:
            AssertionError - if assertion failed.
        """
        try:
            func=self.operation_to_func[operation]
        except Exception:
            raise AssertionError("There was no operation: %s" % operation)
        try:
            func(param)
        except Exception as e:
            raise AssertionError("Target element not find.")

    @logwrap
    def get(self, address):
        """
        Access the web address.

        Args:
            address: the address that to accesss
        """
        super(WebRemote, self).get(address)
        time.sleep(2)

    @logwrap
    def back(self):
        """
        Back to last page.
        """
        super(WebRemote, self).back()
        self._gen_screen_log()
        time.sleep(1)

    @logwrap
    def forward(self):
        """
        Forward to next page.
        """
        super(WebRemote, self).forward()
        self._gen_screen_log()
        time.sleep(1)

    @logwrap
    def snapshot(self, filename=None):
        self._gen_screen_log(filename=filename)

    @logwrap
    def _gen_screen_log(self, element=None, filename=None,):
        if ST.LOG_DIR is None:
            return None
        if filename:
            self.screenshot(filename)
        jpg_file_name=str(int(time.time())) + '.jpg'
        jpg_path=os.path.join(ST.LOG_DIR, jpg_file_name)
        print("this is jpg path:", jpg_path)
        self.screenshot(jpg_path)
        saved={"screen": jpg_file_name}
        if element:
            size=element.size
            location=element.location
            x=size['width'] / 2 + location['x']
            y=size['height'] / 2 + location['y']
            if "darwin" in sys.platform:
                x, y=x * 2, y * 2
            saved.update({"pos": [[x, y]], })
        return saved

    def screenshot(self, file_path=None):
        if file_path:
            self.save_screenshot(file_path)
        else:
            if not ST.LOG_DIR:
                file_path="temp.jpg"
            else:
                file_path=os.path.join(ST.LOG_DIR, "temp.jpg")
            self.save_screenshot(file_path)
            screen=aircv.imread(file_path)
            return screen

    def _get_left_up_offset(self):
        window_pos=self.get_window_position()
        window_size=self.get_window_size()
        mouse=Controller()
        screen=self.screenshot()
        screen_size=get_resolution(screen)
        offset=window_size["width"] - \
            screen_size[0], window_size["height"] - screen_size[1]
        pos=(int(offset[0] / 2 + window_pos['x']),
               int(offset[1] + window_pos['y'] - offset[0] / 2))
        return pos

    def _move_to_pos(self, pos):
        self.mouse.position=pos

    def _click_current_pos(self):
        self.mouse.click(Button.left, 1)

    def to_json(self):
        # add this method for json encoder in logwrap
        return repr(self)



class WebFirefox(Firefox):

    def __init__(self, firefox_profile=None, firefox_binary=None,
                 timeout=30, capabilities=None, proxy=None,
                 executable_path="geckodriver", options=None,
                 service_log_path="geckodriver.log", firefox_options=None,
                 service_args=None, desired_capabilities=None, log_path=None,
                 keep_alive=True):
        print("Please make sure your geckodriver is in your path before proceeding using this driver")
        super(WebFirefox, self).__init__(firefox_profile=firefox_profile, firefox_binary=firefox_binary,
                 timeout=timeout, capabilities=capabilities, proxy=proxy,
                 executable_path=executable_path, options=options,
                 service_log_path=service_log_path, firefox_options=firefox_options,
                 service_args=service_args, desired_capabilities=desired_capabilities, log_path=log_path,
                 keep_alive=keep_alive)
        self.father_number = {0: 0}
        self.action_chains = ActionChains(self)
        self.number = 0
        self.mouse = Controller()
        self.operation_to_func = {"xpath": self.find_element_by_xpath, "id": self.find_element_by_id,
                                  "name": self.find_element_by_name, "css": self.find_element_by_css_selector}

    def loop_find_element(self, func, text, timeout=10, interval=0.5):
        """
        Loop to find the target web element by func.

        Args:
            func: function to find element
            text: param of function
            timeout: time to find the element
            interval: interval between operation
        Returns:
            element that been found
        """
        start_time=time.time()
        while True:
            try:
                element=func(text)
            except NoSuchElementException:
                print("Element not found!")
                # 超时则raise，未超时则进行下次循环:
                if (time.time() - start_time) > timeout:
                    # try_log_screen(screen)
                    raise NoSuchElementException(
                        'Element %s not found in screen' % text)
                else:
                    time.sleep(interval)
            else:
                return element

    @logwrap
    def find_element_by_xpath(self, xpath):
        """
        Find the web element by xpath.

        Args:
            xpath: find the element by xpath.
        Returns:
            Web element of current page.
        """
        web_element=self.loop_find_element(
            super(Firefox, self).find_element_by_xpath, xpath)
        log_res=self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def find_element_by_id(self, id):
        """
        Find the web element by id.

        Args:
            id: find the element by attribute id.
        Returns:
            Web element of current page.
        """
        web_element=self.loop_find_element(
            super(Firefox, self).find_element_by_id, id)
        log_res=self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def find_element_by_css_selector(self, css_selector):
        """
        Find the web element by css_selector.

        Args:
            css_selector: find the element by attribute css_selector.
        Returns:
            Web element of current page.
        """
        web_element=self.loop_find_element(
            super(Firefox, self).find_element_by_css_selector, css_selector)
        log_res=self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def find_element_by_name(self, name):
        """
        Find the web element by name.

        Args:
            name: find the element by attribute name.
        Returns:
            Web element of current page.
        """
        web_element=self.loop_find_element(
            super(Firefox, self).find_element_by_name, name)
        log_res=self._gen_screen_log(web_element)
        return Element(web_element, log_res)

    @logwrap
    def switch_to_new_tab(self):
        """
        Switch to the new tab.
        """
        _father=self.number
        self.number=len(self.window_handles) - 1
        self.father_number[self.number]=_father
        self.switch_to.window(self.window_handles[self.number])
        self._gen_screen_log()
        time.sleep(0.5)

    @logwrap
    def switch_to_previous_tab(self):
        """
        Switch to the previous tab(which to open current tab).
        """
        self.number=self.father_number[self.number]
        self.switch_to.window(self.window_handles[self.number])
        self._gen_screen_log()
        time.sleep(0.5)

    @logwrap
    def airtest_touch(self, v):
        """
        Perform the touch action on the current page by image identification.

        Args:
            v: target to touch, either a Template instance or absolute coordinates (x, y)
        Returns:
            Finial position to be clicked.
        """
        if isinstance(v, Template):
            _pos=loop_find(v, timeout=ST.FIND_TIMEOUT, driver=self)
        else:
            _pos=v
        x, y=_pos
        # self.action_chains.move_to_element_with_offset(root_element, x, y)
        # self.action_chains.click()
        pos=self._get_left_up_offset()
        pos=(pos[0] + x, pos[1] + y)
        self._move_to_pos(pos)
        self._click_current_pos()
        time.sleep(1)
        return _pos

    @logwrap
    def assert_template(self, v, msg=""):
        """
        Assert target exists on the current page.

        Args:
            v: target to touch, either a Template instance
        Raise:
            AssertionError - if target not found.
        Returns:
            Position of the template.
        """
        if isinstance(v, Template):
            try:
                pos=loop_find(v, timeout=ST.FIND_TIMEOUT, driver=self)
            except TargetNotFoundError:
                raise AssertionError("Target template not found on screen.")
            else:
                return pos
        else:
            raise IsNotTemplateError("args is not a template")

    @logwrap
    def assert_exist(self, param, operation, msg=""):
        """
        Assert element exist.

        Args:
            operation: the method that to find the element.
            param: the param of method.
        Raise:
            AssertionError - if assertion failed.
        """
        try:
            func=self.operation_to_func[operation]
        except Exception:
            raise AssertionError("There was no operation: %s" % operation)
        try:
            func(param)
        except Exception as e:
            raise AssertionError("Target element not find.")

    @logwrap
    def get(self, address):
        """
        Access the web address.

        Args:
            address: the address that to accesss
        """
        super(WebFirefox, self).get(address)
        time.sleep(2)

    @logwrap
    def back(self):
        """
        Back to last page.
        """
        super(WebFirefox, self).back()
        self._gen_screen_log()
        time.sleep(1)

    @logwrap
    def forward(self):
        """
        Forward to next page.
        """
        super(WebFirefox, self).forward()
        self._gen_screen_log()
        time.sleep(1)

    @logwrap
    def snapshot(self, filename=None):
        self._gen_screen_log(filename=filename)

    @logwrap
    def _gen_screen_log(self, element=None, filename=None,):
        if ST.LOG_DIR is None:
            return None
        if filename:
            self.screenshot(filename)
        jpg_file_name=str(int(time.time())) + '.jpg'
        jpg_path=os.path.join(ST.LOG_DIR, jpg_file_name)
        print("this is jpg path:", jpg_path)
        self.screenshot(jpg_path)
        saved={"screen": jpg_file_name}
        if element:
            size=element.size
            location=element.location
            x=size['width'] / 2 + location['x']
            y=size['height'] / 2 + location['y']
            if "darwin" in sys.platform:
                x, y=x * 2, y * 2
            saved.update({"pos": [[x, y]], })
        return saved

    def screenshot(self, file_path=None):
        if file_path:
            self.save_screenshot(file_path)
        else:
            if not ST.LOG_DIR:
                file_path="temp.jpg"
            else:
                file_path=os.path.join(ST.LOG_DIR, "temp.jpg")
            self.save_screenshot(file_path)
            screen=aircv.imread(file_path)
            return screen

    def _get_left_up_offset(self):
        window_pos=self.get_window_position()
        window_size=self.get_window_size()
        mouse=Controller()
        screen=self.screenshot()
        screen_size=get_resolution(screen)
        offset=window_size["width"] - \
            screen_size[0], window_size["height"] - screen_size[1]
        pos=(int(offset[0] / 2 + window_pos['x']),
               int(offset[1] + window_pos['y'] - offset[0] / 2))
        return pos

    def _move_to_pos(self, pos):
        self.mouse.position=pos

    def _click_current_pos(self):
        self.mouse.click(Button.left, 1)

    def to_json(self):
        # add this method for json encoder in logwrap
        return repr(self)


class Element(WebElement):

    def __init__(self, _obj, log):
        super(Element, self).__init__(
            parent=_obj._parent, id_=_obj._id, w3c=_obj._w3c)
        self.res_log=log

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
