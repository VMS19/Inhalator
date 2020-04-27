from json import JSONDecodeError

import pytest

from data.alerts import AlertCodes
from data.configurations import ConfigurationManager, Config
from data.events import Events


@pytest.fixture
def invalid_json_file(config_path):
    with open(config_path, "w") as f:
        f.write(",this is {not} a valid: [json] in }} any {,{,{ way")


def verify_default_config(cm, config_path):
    default_config = Config()
    assert cm.config == default_config, "Loaded Configuration is not default"
    assert Config.parse_file(config_path) == default_config, \
        "Saved config file differs from default config"


def test_no_config_file_exists(config_path):
    """
    When:
        `load` called on a manager initialized with a path that does not exist.
    Expect:
        `FileNotFoundError` is raised.
    """
    cm = ConfigurationManager(config_path)
    with pytest.raises(FileNotFoundError):
        cm.load()


@pytest.mark.usefixtures("invalid_json_file")
def test_invalid_config_file(config_path):
    """
    When:
        `load` called on a manager initialized with a path to invalid json file
    Expect:
        `JSONDecodeError` is raised.
    """
    cm = ConfigurationManager(config_path)
    with pytest.raises(JSONDecodeError):
        cm.load()


def test_partial_config(config_path, configuration_manager):
    """
    When:
        Manager initialized with partial config file - meaning a file that
        contains only a subset of the configuration
    Expect:
        The manager will use the configuration values for items present in the
        file, and default values for items which does not present in the file
    """
    # language=JSON
    redacted = """
    {
      "thresholds": {
        "o2": {
          "min": 123,
          "max": 456,
          "step": 1.0
        }
      },
      "state_machine": {
        "min_insp_volume_for_inhale": 37.0
      },
      "calibration": {
        "dp_calibration_timeout_hrs": 5,
        "flow_recalibration_reminder": true
      },
      "graph_seconds": 12.0
    }
    """
    partial_config = Config.parse_raw(redacted)

    with open(config_path, "w") as f:
        f.write(redacted)
    configuration_manager.load()
    assert configuration_manager.config == partial_config


def test_unused_keys_in_config_are_ignored(config_path, configuration_manager):
    unused_key_json = "{\"surely_unused\": 123.456}"
    with open(config_path, "w") as f:
        f.write(unused_key_json)
    configuration_manager.load()
    assert not hasattr(configuration_manager.config, "surely_unused")


def test_valid_config(config_path, configuration_manager):
    """
    Test that Manager initialized with a path to a valid configuration file
    loads it properly.
    """
    valid = Config()
    # Change some fields so that it won't be the same as default.
    valid.thresholds.pressure.max += valid.thresholds.pressure.step
    valid.thresholds.volume.min += valid.thresholds.volume.step

    # Save the valid-but-not-default config
    with open(config_path, "w") as f:
        f.write(valid.json())

    configuration_manager.load()
    assert configuration_manager.config == valid


def test_modify_and_save(config_path, configuration_manager):
    """
    Test that if you modify configuration item and save - the changes are
    actually saved.
    """
    # Just change some values
    configuration_manager.config.graph_seconds = 123.456
    configuration_manager.config.telemetry.url = "http://localhost:5000"
    configuration_manager.config.state_machine.max_pressure_slope_for_exhale = 100
    configuration_manager.save()

    other = ConfigurationManager(config_path)
    other.load()
    assert other.config == configuration_manager.config


def test_default_config_used_when_file_does_not_exist(config_path):
    """
    When:
        `init_configuration` called with a path to a file that does not exist
    Expect:
        1. The default config is used.
        2. The file is created with the default config.
    """
    events = Events()
    cm = ConfigurationManager.initialize(events, config_path)
    verify_default_config(cm, config_path)
    assert len(events.alerts_queue) == 0


@pytest.mark.usefixtures("invalid_json_file")
def test_default_config_used_when_file_is_invalid_json(config_path):
    """
    When:
        `init_configuration` called with a path to invalid JSON file
    Expect:
        1. The default config is used.
        2. The file is created with the default config.
        3. INVALID_CONFIGURATION_FILE Alert is recorded
    """
    events = Events()
    cm = ConfigurationManager.initialize(events, config_path)
    verify_default_config(cm, config_path)
    assert len(events.alerts_queue) == 1
    assert events.alerts_queue.active_alerts[0].code == AlertCodes.INVALID_CONFIGURATION_FILE
