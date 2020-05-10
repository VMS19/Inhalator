import time
from threading import Event
from unittest.mock import patch, Mock

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

    def __call__(self, tmp=None):
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
    
    time.sleep = Mock()
    with pytest.raises(CallableExhausted):
        watchdog.run()

    assert time.sleep.call_count == ITERATIONS


@patch('threading.Event.isSet', side_effect=[False] * ITERATIONS)
@patch('time.sleep', side_effect=ErrorAfter(ITERATIONS))
def test_wd_task_unarmed(mocked_wd, mocked_event):
    """
    Test the wd task when the application doesn't respond.

    Expect:
        wd will not arm.
    """
    wd_mock = DriverFactory.get_mock_wd_driver()
    watchdog = WdTask(wd_mock, Event())

    wd_mock.arm = Mock()

    with pytest.raises(CallableExhausted):
        watchdog.run()
    
    # There is always one arm right at the begging of the function.
    assert wd_mock.arm.call_count == 1