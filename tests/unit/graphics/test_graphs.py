import time
from tkinter import Frame

import freezegun
import pytest
from unittest.mock import MagicMock

from data.alerts import Alert, AlertCodes, AlertsQueue
from data.configurations import Configurations
from data.events import Events
from data.measurements import Measurements
from drivers.driver_factory import DriverFactory
from graphics.graphs import FlowGraph, AirPressureGraph, BlankGraph
from graphics.themes import Theme, DarkTheme

@pytest.fixture
def root():
    return Frame()

@pytest.fixture
def blank_graph(root) -> BlankGraph:
    return BlankGraph(root)

@pytest.fixture
def flow_graph(blank_graph, root) -> FlowGraph:
    Theme.ACTIVE_THEME = DarkTheme()
    parent = MagicMock()
    parent.element = root
    measurements = Measurements()
    graph = FlowGraph(parent, measurements, blank=blank_graph)

    return graph

@pytest.fixture
def pressure_graph(blank_graph, root) -> AirPressureGraph:
    Theme.ACTIVE_THEME = DarkTheme()
    parent = MagicMock()
    parent.element = root
    measurements = Measurements()
    graph = AirPressureGraph(parent, measurements, blank=blank_graph)

    return graph


def test_maximum_value_exceeded_in_flow_graph(flow_graph: FlowGraph):
    min_y, max_y = Configurations.instance().flow_y_scale
    flow_graph.measurements.set_flow_value(max_y + 1)

    flow_graph.consume_measurements()

    assert flow_graph.flow_display_values[-1] == max_y + 1

def test_minimum_value_exceeded_in_flow_graph(flow_graph: FlowGraph):
    min_y, max_y = Configurations.instance().flow_y_scale
    flow_graph.measurements.set_flow_value(min_y - 1)

    flow_graph.consume_measurements()

    assert flow_graph.flow_display_values[-1] == min_y - 1


def test_maximum_value_is_exceeded_in_pressure_graph(pressure_graph: AirPressureGraph):
    min_y, max_y = Configurations.instance().pressure_y_scale
    pressure_graph.measurements.set_pressure_value(max_y + 1)

    pressure_graph.consume_measurements()

    assert pressure_graph.pressure_display_values[-1] == max_y + 1

def test_minimum_value_is_exceeded_in_pressure_graph(pressure_graph: AirPressureGraph):
    min_y, max_y = Configurations.instance().pressure_y_scale

    pressure_graph.measurements.set_pressure_value(min_y - 1)

    pressure_graph.consume_measurements()

    assert pressure_graph.pressure_display_values[-1] == min_y - 1
