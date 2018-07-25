# -*- coding: utf-8 -*-

import time
import os
from airtest.core.helper import G, logwrap
from airtest import aircv
from airtest.aircv import get_resolution
from airtest.core.error import TargetNotFoundError
from airtest.core.settings import Settings as ST

@logwrap
def loop_find(query, driver=None, timeout=10, threshold=None, interval=0.5, intervalfunc=None):
    """
    Search for image template in the screen until timeout

    Args:
        query: image template to be found in screenshot
        timeout: time interval how long to look for the image template
        threshold: default is None
        interval: sleep interval before next attempt to find the image template
        intervalfunc: function that is executed after unsuccessful attempt to find the image template

    Raises:
        TargetNotFoundError: when image template is not found in screenshot

    Returns:
        TargetNotFoundError if image template not found, otherwise returns the position where the image template has
        been found in screenshot

    """
    threshold = 0.6
    start_time = time.time()
    while True:
        screen = driver.screenshot()
        query.resolution = get_resolution(screen)
        if screen is None:
            print("Screen is None, may be locked")
        else:
            if threshold:
                query.threshold = threshold
            match_pos = query.match_in(screen)
            if match_pos:
                try_log_screen(screen)
                return match_pos

        if intervalfunc is not None:
            intervalfunc()

        # 超时则raise，未超时则进行下次循环:
        if (time.time() - start_time) > timeout:
            try_log_screen(screen)
            raise TargetNotFoundError('Picture %s not found in screen' % query)
        else:
            time.sleep(interval)

@logwrap
def try_log_screen(screen=None):
    """
    Save screenshot to file

    Args:
        screen: screenshot to be saved

    Returns:
        None

    """
    if not ST.LOG_DIR:
        return
    if screen is None:
        screen = G.DEVICE.snapshot()
    filename = "%(time)d.jpg" % {'time': time.time() * 1000}
    filepath = os.path.join(ST.LOG_DIR, filename)
    aircv.imwrite(filepath, screen)
    return filename

if __name__ == "__main__":
    from airtest.core.api import connect_device
    from airtest.core.error import AdbError, InstallMultipleError
    dev = connect_device("android://10.252.60.147:5039/AAQKYTY9MVRGOFIV")
    dev.install_multiple_app("E://windows//Test.apk")