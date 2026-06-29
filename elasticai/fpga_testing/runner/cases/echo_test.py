from copy import deepcopy

from elasticai.fpga_testing.runner.interface_runner_test import DummyRunner

from .echo import DefaultSettingsEcho, ExperimentEcho, SettingsEcho


def test_settings_waveform() -> None:
    sets: SettingsEcho = deepcopy(DefaultSettingsEcho)
    waveform = sets.get_data_in

    assert waveform.shape == (200,)
    assert waveform.min() == 1640
    assert waveform.max() == 63895


def test_echo_init() -> None:
    dut = ExperimentEcho(device=DummyRunner, device_id=0)
    assert dut.get_bitwidth_data == 8
