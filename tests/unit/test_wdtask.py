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


@patch('time.sleep')
@patch('threading.Event.isSet', side_effect=[True] * ITERATIONS)
def test_wd_task(mocked_event, mock_sleep):
    """
    Test wd task works correctly.

    Expect:
        WD will arm X times in X * WD_TIMEOUT seconds
    """
    wd_mock = Mock()
    wd_mock.arm.side_effect = ErrorAfter(ITERATIONS)

    watchdog = WdTask(wd_mock, Event())

    with pytest.raises(CallableExhausted):
        watchdog.run()

    assert mock_sleep.call_count == ITERATIONS


@patch('threading.Event.isSet', side_effect=[False] * ITERATIONS)
@patch('time.sleep', side_effect=ErrorAfter(ITERATIONS))
def test_wd_task_unarmed(mocked_sleep, mocked_event):
    """
    Test the wd task when the application doesn't respond.

    Expect:
        wd will not arm.
    """
    wd_mock = Mock()
    watchdog = WdTask(wd_mock, Event())

    with pytest.raises(CallableExhausted):
        watchdog.run()
    
    # There is always one arm right at the begging of the function.
    assert wd_mock.arm.call_count == 1

