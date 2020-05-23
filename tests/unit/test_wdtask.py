from unittest.mock import patch, Mock, MagicMock

import pytest

from wd_task import WdTask

ITERATIONS = 10


@patch('time.sleep')
def test_wd_task(time_mock):
    """
    Test wd task works correctly.

    Expect:
        WD will arm X times in X * WD_TIMEOUT seconds
    """
    wd_mock = MagicMock()

    event_mock = MagicMock(isSet=MagicMock(side_effect=[True] * ITERATIONS))
    watchdog = WdTask(wd_mock, event_mock)

    with pytest.raises(StopIteration):
        watchdog.run()

    arms_count = wd_mock.arm.call_count
    assert arms_count == ITERATIONS + 1

    sleeps = [call.args[0] for call in time_mock.mock_calls]
    print(sleeps)
    # The arming through the WD driver should be at least 50Hz
    assert all(sleep <= 0.5 for sleep in sleeps)


@patch('time.sleep', MagicMock())
def test_wd_task_unarmed():
    """
    Test the wd task when the application doesn't respond.

    Expect:
        wd will not arm, except from the first arming that it always does.
    """
    wd_mock = Mock()
    event_mock = MagicMock(isSet=MagicMock(side_effect=[False] * ITERATIONS))
    watchdog = WdTask(wd_mock, event_mock)

    with pytest.raises(StopIteration):
        watchdog.run()

    # Make sure we checked ITERATIONS+1 times before the mock has
    # been exhausted
    assert event_mock.isSet.call_count == ITERATIONS + 1

    # Apart from the first arming at start, there should be no arming, as
    # the application is not up and running
    assert wd_mock.arm.call_count == 1
