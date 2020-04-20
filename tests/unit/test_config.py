import os

import pytest

from data.configurations import ConfigurationManager, Config


@pytest.fixture
def config_path(tmpdir):
    return tmpdir / "config.json"


def verify_default_config(cm, config_path, source):
    default_config = Config()
    assert cm == default_config, "Loaded Configuration is not default"
    assert Config.parse_file(config_path) == default_config, \
        "Saved config file differs from default config"
    assert cm.source == source


def test_default_is_used_when_no_config_file_exist(config_path):
    """
    Test that when Manager is initialized with a path to a file that does
    not exist - the default configuration is used and saved at that path.
    """
    assert not os.path.exists(config_path),\
        "Config file exists. Precondition failed"
    cm = ConfigurationManager(config_path=config_path)
    assert os.path.exists(config_path),\
        "Config file does not exist after manager initialization"
    verify_default_config(cm, config_path, cm.Source.Default_NoFileFound)


def test_default_is_used_when_file_invalid(config_path):
    """
    Test that when a Manager is initialized with a path to file that contains
    an invalid json - it loads default config and save it to the path specified.
    """
    invalid_json = ",this is {not} a valid: [json] in }} any {,{,{ way"
    with open(config_path, "w") as f:
        f.write(invalid_json)

    cm = ConfigurationManager(config_path=config_path)
    verify_default_config(cm, config_path, cm.Source.Default_InvalidConfigFile)


def test_partial_config(config_path):
    """
    Test that Manager initialized with partial config file (that is - file that
    contains only a subset of the configuration), will use the configuration
    values for items present in the file, and default values for items which
    does not present in the file.
    """
    partial = "{\"graph_seconds\": 123.456}"
    with open(config_path, "w") as f:
        f.write(partial)
    partial_config = Config.parse_raw(partial)
    assert partial_config.graph_seconds == 123.456
    cm = ConfigurationManager(config_path=config_path)
    assert cm == partial_config
    assert cm.source == cm.Source.ValidFile


def test_valid_config(config_path):
    """
    Test that Manager initialized with a path to a valid configuration file
    loads it properly.
    """
    config = Config()
    # Change some fields so that it won't be the same as default.
    config.thresholds.pressure.max += config.thresholds.pressure.step
    config.thresholds.volume.min += config.thresholds.volume.step

    # Save the valid-but-not-default config
    with open(config_path, "w") as f:
        f.write(config.json())

    cm = ConfigurationManager(config_path=config_path)
    assert cm == config
    assert cm.source == cm.Source.ValidFile


def test_modify_and_save(config_path):
    """
    Test that if you modify configuration item and save - the changes are
    actually saved.
    """
    cm = ConfigurationManager(config_path=config_path)
    # Just change some values
    cm.graph_seconds = 123.456
    cm.telemetry.url = "http://localhost:5000"
    cm.state_machine.max_pressure_slope_for_exhale = 100
    cm.save()

    cm2 = ConfigurationManager(config_path=config_path)
    assert cm2 == cm
