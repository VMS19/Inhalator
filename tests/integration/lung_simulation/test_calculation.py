import pytest

from pytest import approx

from algo import VentilationState
from tests.data.files import path_to_file

SAMPLES_AMOUNT = 604
EXPERIMENT_BPM = [0, 15, 15, 15, 15, 15, 15, 15]
EXPERIMENT_VOLUMES = [291, 405, 293, 307, 295, 306, 292,
                      307, 291, 304, 293, 304, 292, 309]


TEST_FILE = path_to_file("03-04-2020.csv")


@pytest.mark.parametrize("data", [TEST_FILE])
def test_sampler_volume_calculation(measurements, sim_sampler, app, data):
    app.render()
    for expected_volume in EXPERIMENT_VOLUMES:
        start_state = sim_sampler.vsm.current_state
        is_pre_inhale = sim_sampler.vsm.current_state == VentilationState.PreInhale
        is_pre_exahle = sim_sampler.vsm.current_state == VentilationState.PreExhale
        is_pre = is_pre_inhale or is_pre_exahle
        while start_state == sim_sampler.vsm.current_state or is_pre:
            app.run_iterations(1, render=False)
            is_pre_inhale = sim_sampler.vsm.current_state == VentilationState.PreInhale
            is_pre_exahle = sim_sampler.vsm.current_state == VentilationState.PreExhale
            is_pre = is_pre_inhale or is_pre_exahle

        breathing_state = sim_sampler.vsm.current_state
        while breathing_state == sim_sampler.vsm.current_state:
            app.run_iterations(1, render=False)

        if breathing_state == VentilationState.Exhale:
            volume = measurements.expiration_volume
        else:
            volume = measurements.inspiration_volume

        msg = f"Received volume of {volume}, expected {expected_volume}"
        assert volume == approx(expected_volume, 0.1), msg


@pytest.mark.parametrize("data", [TEST_FILE])
def test_sampler_bpm_calculation(app, measurements, sim_sampler, data):
    app.render()
    for expected_bpm in EXPERIMENT_BPM:
        while sim_sampler.vsm.current_state != VentilationState.Inhale:
            app.run_iterations(1, render=False)

        bpm = measurements.bpm
        msg = f"Received bpm of {bpm}, expected {expected_bpm}"
        assert bpm == approx(expected_bpm, 0.1), msg

        while sim_sampler.vsm.current_state == VentilationState.Inhale:
            app.run_iterations(1, render=False)
