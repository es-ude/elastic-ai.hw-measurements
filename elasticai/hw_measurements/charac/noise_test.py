from unittest import TestCase, main

import numpy as np
import pytest

from elasticai.hw_measurements.charac import CharacterizationNoise, TransientNoiseSpectrum


class TestNoise(TestCase):
    def setUp(self):
        self.noise_density = 100e-9  # V/√Hz
        fs = 2e4  # Hz
        duration = 0.5  # seconds

        sigma = self.noise_density * np.sqrt(fs / 2)
        time = np.linspace(start=0.0, stop=duration, num=int(fs * duration), endpoint=True)
        signal = np.random.normal(0, sigma, time.size)
        # signal += np.sin(2*np.pi*time*2)

        self.dut = CharacterizationNoise()
        self.dut.load_data(time=time, signal=np.expand_dims(signal, axis=0), channels=[0])

    def test_load_data_wrong_format_single(self):
        with self.assertRaises(ValueError):
            self.dut.load_data(
                time=np.linspace(start=0.0, stop=1.0, num=101, endpoint=True),
                signal=np.zeros((101,)),
                channels=[0],
            )

    def test_load_data_wrong_format_dual(self):
        with self.assertRaises(ValueError):
            self.dut.load_data(
                time=np.linspace(start=0.0, stop=1.0, num=101, endpoint=True),
                signal=np.zeros((101, 1)),
                channels=[0],
            )

    def test_sampling_rate(self):
        assert self.dut.get_sampling_rate == 19998.0

    def test_get_channels_overview(self):
        assert self.dut.get_channels_overview == [0]

    def test_num_channels(self):
        assert self.dut.get_num_channels == 1

    def test_noise_spectrum_resistor(self):
        rslt = self.dut.extract_noise_power_distribution(scale=1.0, num_segments=1000)
        np.testing.assert_array_almost_equal(
            rslt.spec, np.zeros_like(rslt.spec) + self.noise_density, decimal=7
        )

    def test_noise_rms_resistor_total(self):
        self.dut.extract_noise_power_distribution(scale=1.0, num_segments=100)
        rslt = self.dut.extract_noise_rms()
        print(rslt[0])

        assert len(rslt) == self.dut.get_num_channels
        assert 9.75e-6 < rslt[0] < 10.25e-6

    def test_noise_rms_resistor_range(self):
        self.dut.extract_noise_power_distribution(scale=1.0, num_segments=100)
        rslt = self.dut.extract_noise_rms_specific(100.0, 1000.0)
        print(rslt[0])

        assert len(rslt) == self.dut.get_num_channels
        assert 2.5e-6 < rslt[0] < 3.5e-6


class TestExtractTransientMetrics:
    def test_computes_offset_and_peak_peak_per_channel(self):
        c = CharacterizationNoise()
        signal = np.array(
            [
                [1.0, 3.0, 5.0, 3.0, 1.0],
                [10.0, 10.0, 10.0, 10.0, 10.0],
            ]
        )
        c.load_data(time=np.arange(5), signal=signal, channels=["ch1", "ch2"])
        metric = c.extract_transient_metrics()
        assert metric.offset_mean[0] == pytest.approx(2.6)
        assert metric.peak_peak[0] == pytest.approx(4.0)
        assert metric.peak_peak[1] == pytest.approx(0.0)

    def test_raises_if_no_data_loaded(self):
        c = CharacterizationNoise()
        c._channels = []
        with pytest.raises(ValueError):
            c.extract_transient_metrics()


class TestExcludeChannelsFromSpec:
    def test_removes_single_channel_by_index(self):
        c = CharacterizationNoise()
        c._spec = TransientNoiseSpectrum(
            freq=np.array([[1, 2], [1, 2], [1, 2]]),
            spec=np.array([[10, 20], [30, 40], [50, 60]]),
            chan=["ch1", "ch2", "ch3"],
        )
        c.exclude_channels_from_spec([1])
        assert c._spec.chan == ["ch1", "ch3"]

    def test_removes_multiple_channels_with_correct_index_shift(self):
        c = CharacterizationNoise()
        c._spec = TransientNoiseSpectrum(
            freq=np.array([[1, 2], [1, 2], [1, 2], [1, 2]]),
            spec=np.array([[10, 20], [30, 40], [50, 60], [70, 80]]),
            chan=["ch1", "ch2", "ch3", "ch4"],
        )
        c.exclude_channels_from_spec([0, 2])
        assert c._spec.chan == ["ch2", "ch4"]


class TestRemovePowerLineNoise:
    def test_replaces_peak_at_power_line_frequency(self):
        c = CharacterizationNoise()
        c._channels = ["ch1"]
        freq = np.arange(0, 200, 0.5)
        spec = np.ones_like(freq)
        peak_idx = np.argmin(np.abs(freq - 50.0))
        spec[peak_idx] = 100.0

        c._spec = TransientNoiseSpectrum(freq=np.array([freq]), spec=np.array([spec]), chan=["ch1"])
        result = c.remove_power_line_noise(tolerance=5.0, num_harmonics=10)
        assert result.spec[0, peak_idx] != 100.0

    def test_spectrum_unchanged_when_no_peak_present(self):
        c = CharacterizationNoise()
        c._channels = ["ch1"]
        freq = np.arange(0, 200, 0.5)
        spec = np.ones_like(freq)

        c._spec = TransientNoiseSpectrum(freq=np.array([freq]), spec=np.array([spec]), chan=["ch1"])
        result = c.remove_power_line_noise()
        assert np.array_equal(result.spec[0], spec)


if __name__ == "__main__":
    main()
