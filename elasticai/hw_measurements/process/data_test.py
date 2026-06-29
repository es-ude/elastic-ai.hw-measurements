import unittest

import numpy as np
import pytest

from elasticai.hw_measurements import get_path_to_project
from elasticai.hw_measurements.process.data import (
    MetricCalculator,
    do_fft,
    window_method,
)


@pytest.mark.parametrize(
    "method",
    ["hamming", "hanning", "bartlett", "blackman", "gaussian"],
)
def test_output_length_matches_window_size(method):
    window = window_method(64, method)
    assert isinstance(window, np.ndarray)
    assert len(window) == 64


def test_default_method_is_hamming():
    np.testing.assert_array_equal(window_method(50), np.hamming(50))


def test_hamming_matches_numpy_reference():
    np.testing.assert_array_equal(window_method(32, "hamming"), np.hamming(32))


def test_guassian_matches_scipy_reference():
    try:
        from scipy.signal.windows import gaussian
    except ImportError:
        from scipy.signal import gaussian

    window_size = 32
    expected = gaussian(window_size, int(0.16 * window_size), sym=True)
    np.testing.assert_array_equal(window_method(window_size, "gaussian"), expected)


def test_invalid_method_raises_value_error():
    with pytest.raises(ValueError, match="not available"):
        window_method(10, "not_a_real_method")


class TestDataAnalysis(unittest.TestCase):
    path2data = get_path_to_project(new_folder="test_data")
    hndl = MetricCalculator()
    ovr = hndl.get_data_overview(path=path2data, acronym="dac")
    trns = hndl.process_data_from_file(path=path2data.as_posix(), file_name=ovr[0])

    def test_get_data_overview(self):
        self.assertTrue(len(self.ovr) > 0)

    def test_get_data_length(self):
        self.assertTrue(
            self.trns["stim"].size == self.trns["ch00"]["mean"].size == self.trns["ch00"]["std"].size
        )

    def test_get_data_mean_value(self):
        np.testing.assert_array_equal(self.trns["stim"], self.trns["ch00"]["mean"])

    def test_get_data_std_value(self):
        np.testing.assert_array_equal(self.trns["ch00"]["std"], np.zeros_like(self.trns["ch00"]["mean"]))

    def test_lsb_constructor_size(self):
        rslt = self.hndl.calculate_lsb(stim_input=self.trns["stim"], daq_output=self.trns["ch00"]["mean"])
        self.assertTrue(rslt.size == self.trns["stim"].size - 1)

    def test_lsb_constructor_value(self):
        rslt = self.hndl.calculate_lsb(stim_input=self.trns["stim"], daq_output=self.trns["ch00"]["mean"])
        np.testing.assert_array_equal(rslt, np.ones_like(rslt))

    def test_lsb_constructor_float(self):
        rslt = self.hndl.calculate_lsb_mean(
            stim_input=self.trns["stim"], daq_output=self.trns["ch00"]["mean"]
        )
        self.assertEqual(rslt, 1.0)

    def test_dnl_constructor_size(self):
        rslt = self.hndl.calculate_dnl(stim_input=self.trns["stim"], daq_output=self.trns["ch00"]["mean"])
        self.assertTrue(rslt.size == self.trns["stim"].size - 1)

    def test_dnl_constructor_value(self):
        rslt = self.hndl.calculate_dnl(stim_input=self.trns["stim"], daq_output=self.trns["ch00"]["mean"])
        np.testing.assert_array_equal(rslt, np.zeros_like(rslt))

    def test_inl_is_zero_for_perfectly_linear_data_through_origin(self):
        stim_input = np.arange(0, 10, dtype=float)
        daq_output = 2.0 * stim_input
        inl = self.hndl.calculate_inl(stim_input, daq_output)
        np.testing.assert_allclose(inl, np.zeros_like(stim_input), atol=1e-9)

    def test_inl_is_nonzero_for_linear_data_with_offset(self):
        stim_input = np.arange(1, 10, dtype=float)
        daq_output = 2.0 * stim_input + 5.0
        inl = self.hndl.calculate_inl(stim_input, daq_output)
        assert not np.allclose(inl, np.zeros_like(stim_input))

    def test_metric_mbe_float(self):
        rslt = self.hndl.calculate_error_mbe(
            y_pred=2.0,
            y_true=-2.0,
        )
        chck = type(rslt) == float and rslt == 4.0
        self.assertTrue(chck)

    def test_metric_mbe_numpy(self):
        rslt = self.hndl.calculate_error_mbe(
            y_pred=np.linspace(1.0, 5.0, endpoint=True, num=10),
            y_true=np.linspace(2.0, 6.0, endpoint=True, num=10),
        )
        chck = type(rslt) == float and rslt == -1.0
        self.assertTrue(chck)

    def test_metric_mae_float(self):
        rslt = self.hndl.calculate_error_mae(
            y_pred=2.0,
            y_true=-2.0,
        )
        chck = type(rslt) == float and rslt == 4.0
        self.assertTrue(chck)

    def test_metric_mae_numpy(self):
        rslt = self.hndl.calculate_error_mae(
            y_pred=np.linspace(1.0, 5.0, endpoint=True, num=10),
            y_true=np.linspace(2.0, 6.0, endpoint=True, num=10),
        )
        chck = type(rslt) == float and rslt == 1.0
        self.assertTrue(chck)

    def test_metric_mse_float(self):
        rslt = self.hndl.calculate_error_mse(
            y_pred=2.0,
            y_true=-2.0,
        )
        chck = type(rslt) == float and rslt == 16.0
        self.assertTrue(chck)

    def test_metric_mse_numpy(self):
        rslt = self.hndl.calculate_error_mse(
            y_pred=np.linspace(1.0, 5.0, endpoint=True, num=10),
            y_true=np.linspace(2.0, 6.0, endpoint=True, num=10),
        )
        chck = type(rslt) == float and rslt == 1.0
        self.assertTrue(chck)

    def test_metric_mape_float(self):
        rslt = self.hndl.calculate_error_mape(
            y_pred=2.0,
            y_true=-2.0,
        )
        chck = type(rslt) == float and rslt == 2.0
        self.assertTrue(chck)

    def test_metric_mape_numpy(self):
        rslt = self.hndl.calculate_error_mape(
            y_pred=np.linspace(1.0, 5.0, endpoint=True, num=10),
            y_true=np.linspace(2.0, 6.0, endpoint=True, num=10),
        )
        chck = type(rslt) == float and rslt == 0.28133972977262783
        self.assertTrue(chck)

    def test_metric_thd_one_harmonic(self):
        sampling_rate = 1000
        t = np.linspace(start=0, stop=1, num=int(sampling_rate), endpoint=True)
        signal = (
            np.sin(2 * np.pi * 50 * t)
            + 0.1 * np.sin(2 * np.pi * 100 * t)
            + 0.05 * np.sin(2 * np.pi * 150 * t)
        )

        rslt = self.hndl.calculate_total_harmonics_distortion_from_transient(
            signal=signal, fs=sampling_rate, num_harmonics=1
        )
        self.assertEqual(rslt, -20.21920586821124)

    def test_metric_thd_two_harmonic(self):
        sampling_rate = 1000.0
        t = np.linspace(start=0, stop=1.0, num=int(sampling_rate), endpoint=True)
        signal = (
            np.sin(2 * np.pi * 50 * t)
            + 0.1 * np.sin(2 * np.pi * 100 * t)
            + 0.05 * np.sin(2 * np.pi * 150 * t)
        )

        rslt = self.hndl.calculate_total_harmonics_distortion_from_transient(
            signal=signal, fs=sampling_rate, num_harmonics=2
        )
        self.assertAlmostEqual(rslt, -19.300251257175265, delta=1e-6)

    def test_calculate_cosine_match(self):
        t = np.linspace(0, 1, 1000, endpoint=True)
        rslt = self.hndl.calculate_cosine_similarity(
            y_pred=np.sin(2 * np.pi * 50 * t),
            y_true=np.sin(2 * np.pi * 50 * t),
        )
        self.assertEqual(rslt, 1.0)

    def test_calculate_cosine_half(self):
        t = np.linspace(0, 1, 1000, endpoint=True)
        rslt = self.hndl.calculate_cosine_similarity(
            y_pred=np.sin(2 * np.pi * 50 * t),
            y_true=np.sin(2 * np.pi * 100 * t),
        )
        self.assertAlmostEqual(rslt, -4.439780764141639e-17, delta=1e-18)

    def test_metric_thd_one_harmonic_spec(self):
        sampling_rate = 1000.0
        t = np.linspace(start=0.0, stop=1.0, num=int(sampling_rate), endpoint=True)
        signal = (
            np.sin(2 * np.pi * 50 * t)
            + 0.1 * np.sin(2 * np.pi * 100 * t)
            + 0.05 * np.sin(2 * np.pi * 150 * t)
        )

        spectrum = do_fft(
            y=signal,
            fs=sampling_rate,
        )
        rslt = self.hndl.calculate_total_harmonics_distortion_from_spec(signal=spectrum, num_harmonics=2)
        self.assertEqual(rslt, -19.300251257175265)

    def test_metric_thd_one_harmonic_spec_with_window(self):
        sampling_rate = 1000.0
        t = np.linspace(start=0.0, stop=1.0, num=int(sampling_rate), endpoint=True)
        signal = (
            np.sin(2 * np.pi * 50 * t)
            + 0.1 * np.sin(2 * np.pi * 100 * t)
            + 0.05 * np.sin(2 * np.pi * 150 * t)
        )

        spectrum = do_fft(
            y=signal,
            fs=sampling_rate,
            method_window="hamming",
        )
        rslt = self.hndl.calculate_total_harmonics_distortion_from_spec(signal=spectrum, num_harmonics=2)
        self.assertEqual(rslt, -19.11810872201894)

    def test_gain_transfer_one(self):
        amp_input = np.linspace(start=-1.0, stop=1.0, num=101, endpoint=True)
        amp_output = np.linspace(start=-2.0, stop=2.0, num=101, endpoint=True)

        rslt = self.hndl.calculate_gain_from_transfer(
            stim_input=amp_input,
            src_output=amp_output,
        )
        self.assertTrue(rslt.shape == (100,))
        self.assertEqual(rslt.mean(), 2.0)
