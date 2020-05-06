import pytest
from pytest import approx
from algo import VentilationState
from tests.data.files import path_to_file

SAMPLES_AMOUNT = 118
SIMULATION_FOLDER = "simulation"


@pytest.fixture
def config(default_config):
    c = default_config
    c.state_machine.min_exp_volume_for_exhale = 0
    return c


@pytest.fixture
def data(scenario):
    return path_to_file(f"pig_sim_extreme_in_{scenario}.csv")


@pytest.mark.parametrize(
    ["scenario", "state", "entry_time"],
    [('exhale_pressure', VentilationState.Inhale, 4.41),
     ('exhale_flow', VentilationState.Inhale, 4.41),
     ("exhale_both", VentilationState.Inhale, 4.41),
     ("inhale_below_threshold", VentilationState.Exhale, 6.09),
     pytest.param(
         "inhale_pass_threshold", VentilationState.Exhale, 6.09,
         marks=pytest.mark.xfail(
             reason="Can't handle error of drop in flow below threshold"))])
def test_state_recognition_with_outliers(app, sim_sampler, scenario, state, entry_time):
    """Test error in exhale doesn't cause the state machine change too early.

    Flow:
        * Run pig simulation with two errors in the peep exhale
            - One error higher value (pressure, flow or together)
            - One error lower value (pressure, flow or together)
        * Check The entry time to inhale wasn't changed.
    """
    app.run_iterations(SAMPLES_AMOUNT)
    inhale_entry = sim_sampler.vsm.entry_points_ts[state][0]
    assert inhale_entry == approx(entry_time, rel=0.1)
