import shutil

import numpy as np
import pytest

from elasticai.hw_measurements import get_path_to_project
from elasticai.hw_measurements.charac.common import CharacterizationCommon


class Settings:
    lr = 0.01
    batch_size = 32


class TestCommon:
    @pytest.fixture(autouse=True)
    def tmp_path(self):
        tmp_path = get_path_to_project("temp_files")
        if tmp_path.exists():
            shutil.rmtree(tmp_path)
        tmp_path.mkdir(parents=True, exist_ok=True)
        yield tmp_path

    def test_common_charac_func_random_voltage_float(self):
        hndl = CharacterizationCommon()
        result = hndl.dummy_get_daq()
        assert type(result) == float

    def test_common_beep(self):
        CharacterizationCommon().dummy_beep()

    def test_common_reset(self):
        CharacterizationCommon().dummy_reset()

    def test_get_val(self):
        hndl = CharacterizationCommon()
        hndl._input_val = 4.0
        assert hndl.dummy_get_stim_value() == 4.0

    def test_common_charac_func_random_voltage_array(self):
        hndl = CharacterizationCommon()
        result = np.array([hndl.dummy_get_daq() for _ in range(100)])
        assert result.shape == (100,)
        assert result.min() >= -1.0
        assert result.max() <= 1.0

    def test_common_charac_func_dut_adc(self):
        hndl = CharacterizationCommon()
        result = np.array([hndl.dummy_get_dut_adc(0) for _ in range(100)])
        assert result.shape == (100,)
        assert result.min() >= 0.0
        assert result.max() <= 2**16 - 1

    def test_save_results_creates_npz_file(self, tmp_path):
        saver = CharacterizationCommon()
        data = {"a": np.array([1, 2, 3])}
        saver.save_results(file_name="result", settings=Settings(), data=data, folder_name=tmp_path)
        assert (tmp_path / "result.npz").exists()

    def test_save_results_can_be_loaded_with_correct_settings(self, tmp_path):
        saver = CharacterizationCommon()
        data = {"a": np.array([1, 2, 3]), "b": 5}
        saver.save_results(file_name="result", settings=Settings(), data=data, folder_name=tmp_path)

        loaded = np.load(tmp_path / "result.npz", allow_pickle=True)
        loaded_data = loaded["data"].item()
        loaded_settings = loaded["settings"].item()

        assert loaded_data["b"] == 5
        np.testing.assert_array_equal(loaded_data["a"], data["a"])
        assert loaded_settings.lr == 0.01
        assert loaded_settings.batch_size == 32
