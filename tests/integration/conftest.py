from threading import Event

import pytest

from application import Application


@pytest.fixture
def config(default_config):
    default_config.thresholds.pressure.min = -1
    default_config.thresholds.volume.min = 0
    default_config.thresholds.respiratory_rate.min = 3.5
    return default_config


@pytest.fixture
def app(config, measurements, events, driver_factory, sim_sampler):
    app = Application(
        config=config,
        measurements=measurements,
        events=events,
        arm_wd_event=Event(),
        drivers=driver_factory,
        sampler=sim_sampler,
        simulation=True)
    yield app
    app.root.destroy()
