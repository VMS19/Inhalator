import time
from threading import Event
from unittest.mock import patch

import pytest

from wd_task import WdTask
from drivers.mocks.mock_wd_driver import MockWdDriver
from drivers.driver_factory import DriverFactory

ITERATIONS = 10


class ErrorAfter(object):
    """
    Callable that will raise `CallableExhausted`
    exception after `limit` calls
    """
    def __init__(self, limit):
        self.limit = limit
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.calls > self.limit:
            raise CallableExhausted


class CallableExhausted(Exception):
    pass


@patch('threading.Event.isSet', side_effect=[True] * ITERATIONS)
@patch('drivers.mocks.mock_wd_driver.MockWdDriver.arm', side_effect=ErrorAfter(ITERATIONS))
def test_wd_task(mocked_wd, mocked_event):
    """
    Test wd task works correctly.

    Expect:
        WD will arm X times in X * WD_TIMEOUT seconds
    """
    watchdog = WdTask(DriverFactory.get_mock_wd_driver(), Event())
    
    start = time.time()
    with pytest.raises(CallableExhausted):
        watchdog.run()
    end = time.time()

    assert end - start - ITERATIONS * watchdog.WD_TIMEOUT < 0.02
