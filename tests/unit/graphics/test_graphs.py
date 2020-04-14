from unittest.mock import MagicMock

import pytest
from tkinter import *

from pytest import approx

from algo import Sampler
from data.events import Events
from data.measurements import Measurements
from drivers.driver_factory import DriverFactory
from graphics.graphs import AirPressureGraph, FlowGraph, BlankGraph
from graphics.themes import Theme, DarkTheme


@pytest.fixture
def events():
    return Events()

@pytest.fixture
def measurements():
    return Measurements()

@pytest.fixture
def driver_factory():
    return DriverFactory(simulation_mode=True,
                         simulation_data="sinus")

@pytest.fixture
def sampler(measurements, events, driver_factory):
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    return Sampler(measurements, events, flow_sensor, pressure_sensor,
                   a2d, timer, average_window=1)

@pytest.fixture
def pressure_graph(measurements) -> AirPressureGraph:
    Theme.ACTIVE_THEME = DarkTheme()
    root = Frame()
    parent = MagicMock()
    parent.element = root

    blank = BlankGraph(root)
    graph = AirPressureGraph(parent=parent, measurements=measurements, blank=blank)
    graph.axis = MagicMock()
    graph.figure = MagicMock()
    return graph


def test_graph_doesnt_autoscale_when_it_shouldnt(pressure_graph: AirPressureGraph,
                                                 sampler: Sampler):
    original_min = pressure_graph.current_min_y
    original_max = pressure_graph.current_max_y
    for _ in range(100):
        sampler.sampling_iteration()

    pressure_graph.update()

    assert pressure_graph.current_min_y == original_min
    assert pressure_graph.current_max_y == original_max


def test_graph_symmetrically_autoscales_when_value_exceeds_max(pressure_graph: AirPressureGraph):
    pressure_graph.current_min_y = -10.0
    pressure_graph.current_max_y = 10.0
    pressure_graph.LOOSE_GRAPH_FACTOR = 1.2

    x = pressure_graph.measurements._amount_of_samples_in_graph

    pressure_graph.display_values = [10] * x
    pressure_graph.display_values[1] += 3

    pressure_graph.update()

    assert pressure_graph.current_max_y == approx(10 + (3*1.2))
    assert pressure_graph.current_min_y == approx(-10.0 - (3*1.2))


def test_graph_symmetrically_autoscales_when_value_exceeds_min(pressure_graph: AirPressureGraph):
    pressure_graph.current_min_y = -10.0
    pressure_graph.current_max_y = 10.0
    pressure_graph.LOOSE_GRAPH_FACTOR = 1.2

    x = pressure_graph.measurements._amount_of_samples_in_graph

    pressure_graph.display_values = [-10] * x
    pressure_graph.display_values[1] -= 3

    pressure_graph.update()

    assert pressure_graph.current_max_y == approx(10 + (3*1.2))
    assert pressure_graph.current_min_y == approx(-10.0 - (3*1.2))

