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
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer)

    sampler._config = MagicMock()
    return sampler

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
    graph.config = MagicMock()
    graph.config.autoscale = True

    return graph


@pytest.fixture
def flow_graph(measurements) -> FlowGraph:
    Theme.ACTIVE_THEME = DarkTheme()
    root = Frame()
    parent = MagicMock()
    parent.element = root

    blank = BlankGraph(root)
    graph = FlowGraph(parent=parent, measurements=measurements, blank=blank)
    graph.axis = MagicMock()
    graph.figure = MagicMock()
    graph.config = MagicMock()
    graph.config.autoscale = True
    graph.config.flow_y_scale = (-10, 10)
    return graph


def test_graph_does_not_auto_scale(flow_graph: FlowGraph,
                                   sampler: Sampler):
    original_min = flow_graph.current_min_y
    original_max = flow_graph.current_max_y
    for _ in range(100):
        sampler.sampling_iteration()

    for i in range(flow_graph.ZOOM_OUT_FREQUENCY):
        flow_graph.update()

    assert flow_graph.current_min_y == original_min
    assert flow_graph.current_max_y == original_max


def test_graph_symmetrically_autoscales_when_value_exceeds_max(flow_graph: FlowGraph):
    flow_graph.current_min_y = -10.0
    flow_graph.current_max_y = 10.0
    flow_graph.GRAPH_MARGINS = 1.2

    x = flow_graph.measurements._amount_of_samples_in_graph

    flow_graph.display_values = [10] * x
    flow_graph.display_values[1] += 3

    for i in range(flow_graph.ZOOM_OUT_FREQUENCY):
        flow_graph.update()

    assert flow_graph.current_max_y == approx(13)
    assert flow_graph.current_min_y == approx(-13)


def test_graph_symmetrically_autoscales_when_value_exceeds_min(flow_graph: FlowGraph):
    flow_graph.current_min_y = -10.0
    flow_graph.current_max_y = 10.0
    flow_graph.GRAPH_MARGINS = 1.2

    x = flow_graph.measurements._amount_of_samples_in_graph

    flow_graph.display_values = [-10] * x
    flow_graph.display_values[1] -= 3

    for i in range(flow_graph.ZOOM_OUT_FREQUENCY):
        flow_graph.update()

    assert flow_graph.current_max_y == approx(13)
    assert flow_graph.current_min_y == approx(-13)


def test_loose_graph_behaviour(flow_graph: FlowGraph):
    """Test that we never actually let the graph touch the edge"""
    flow_graph.current_min_y = -10.0
    flow_graph.current_max_y = 10.0
    flow_graph.GRAPH_MARGINS = 1.2

    x = flow_graph.measurements._amount_of_samples_in_graph

    flow_graph.display_values = [-10] * x
    flow_graph.display_values[1] -= 3

    for i in range(flow_graph.ZOOM_OUT_FREQUENCY):
        flow_graph.update()

    assert flow_graph.current_max_y == approx(13)
    assert flow_graph.graph.axes.get_ylim() == (approx(-13 - 1.2), approx(13 + 1.2))
    assert flow_graph.current_min_y == approx(-13)


def test_pressure_graph_doesnt_autoscale(pressure_graph: AirPressureGraph):
    pressure_graph.current_min_y = -10.0
    pressure_graph.current_max_y = 10.0
    pressure_graph.GRAPH_MARGINS = 1.2

    x = pressure_graph.measurements._amount_of_samples_in_graph

    pressure_graph.display_values = [-10] * x
    pressure_graph.display_values[1] -= 3

    for i in range(2000):
        pressure_graph.update()

    assert pressure_graph.current_max_y == approx(10)
    assert pressure_graph.current_min_y == approx(-10)


def test_autoscale_can_be_disabled(flow_graph: FlowGraph):
    flow_graph.config.autoscale = False

    flow_graph.current_min_y = -10.0
    flow_graph.current_max_y = 10.0
    flow_graph.GRAPH_MARGINS = 1.2

    x = flow_graph.measurements._amount_of_samples_in_graph

    flow_graph.display_values = [-10] * x
    flow_graph.display_values[1] -= 3

    for i in range(flow_graph.ZOOM_OUT_FREQUENCY):
        flow_graph.update()

    assert flow_graph.current_min_y == approx(-10)
    assert flow_graph.current_max_y == approx(10)


def test_autoscale_zooms_in(flow_graph: FlowGraph):
    flow_graph.current_min_y = -10.0
    flow_graph.current_max_y = 10.0
    flow_graph.GRAPH_MARGINS = 1.2

    x = flow_graph.measurements._amount_of_samples_in_graph

    flow_graph.display_values = [-10] * x
    flow_graph.display_values[1] -= 3

    for i in range(flow_graph.ZOOM_OUT_FREQUENCY):
        flow_graph.update()

    assert flow_graph.current_min_y < -10
    assert flow_graph.current_max_y > 10

    flow_graph.display_values = [-10] * x

    for i in range(flow_graph.ZOOM_IN_FREQUENCY):
        flow_graph.update()

    assert flow_graph.current_min_y == approx(-10)
    assert flow_graph.current_max_y == approx(10)
