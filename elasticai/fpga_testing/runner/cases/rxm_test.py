from copy import deepcopy

from .rxm import DefaultSettingsRxM, SettingsRxM


def test_settings_num_cycles() -> None:
    sets: SettingsRxM = deepcopy(DefaultSettingsRxM)
    rslt = sets.get_num_cycles
    assert rslt == 640
