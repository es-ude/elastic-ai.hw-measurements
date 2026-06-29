import numpy as np
import pytest

from .signal_generator import generate_noise, generate_sinusoidal_waveform


class TestGenerateSinusoidalWaveform:
    def test_returns_tuple_of_ndarrays(self):
        time0, data_in = generate_sinusoidal_waveform(f_sig=1000, fs=48000)
        assert isinstance(time0, np.ndarray)
        assert isinstance(data_in, np.ndarray)

    def test_time_and_data_same_length(self):
        time0, data_in = generate_sinusoidal_waveform(f_sig=1000, fs=48000)
        assert time0.shape == data_in.shape

    @pytest.mark.parametrize("no_periods", [1, 2, 5])
    def test_length_scales_with_no_periods(self, no_periods):
        f_sig, fs = 1000, 48000
        time0, _ = generate_sinusoidal_waveform(f_sig=f_sig, fs=fs, no_periods=no_periods)
        t_end = no_periods / f_sig
        expected_len = len(np.arange(0, t_end, 1 / fs))
        assert len(time0) == expected_len

    def test_time_step_matches_sampling_frequency(self):
        fs = 48000
        time0, _ = generate_sinusoidal_waveform(f_sig=1000, fs=fs, no_periods=3)
        diffs = np.diff(time0)
        np.testing.assert_allclose(diffs, 1 / fs, rtol=1e-9)

    def test_data_dtype_is_integer(self):
        _, data_in = generate_sinusoidal_waveform(f_sig=1000, fs=48000)
        assert np.issubdtype(data_in.dtype, np.integer)

    def test_unsigned_output_offset_is_centered_at_half_range(self):
        bitwidth = 16
        _, data_in = generate_sinusoidal_waveform(
            f_sig=1000, fs=48000, bitwidth=bitwidth, signed_out=False
        )
        offset = 2 ** (bitwidth - 1)
        amp = 0.95 * (2 ** (bitwidth - 1)) - 2
        assert data_in[0] == pytest.approx(offset + amp, abs=1)
        assert np.mean(data_in) == pytest.approx(offset, abs=amp * 0.05)

    def test_unsigned_output_is_nonnegative(self):
        _, data_in = generate_sinusoidal_waveform(f_sig=1000, fs=48000, bitwidth=16, signed_out=False)
        assert np.all(data_in >= 0)

    def test_signed_output_is_centered_at_zero(self):
        _, data_in = generate_sinusoidal_waveform(f_sig=1000, fs=48000, bitwidth=16, signed_out=True)
        assert np.mean(data_in) == pytest.approx(0, abs=1)
        assert np.any(data_in < 0)

    def test_amplitude_does_not_exceed_bitwidth_range(self):
        bitwidth = 16
        _, data_in_unsigned = generate_sinusoidal_waveform(
            f_sig=1000, fs=48000, bitwidth=bitwidth, signed_out=False
        )
        assert data_in_unsigned.max() < 2**bitwidth
        assert data_in_unsigned.min() >= 0

        _, data_in_signed = generate_sinusoidal_waveform(
            f_sig=1000, fs=48000, bitwidth=bitwidth, signed_out=True
        )
        max_amp = 0.95 * (2 ** (bitwidth - 1)) - 2
        assert data_in_signed.max() <= max_amp
        assert data_in_signed.min() >= -max_amp

    @pytest.mark.parametrize("bitwidth", [8, 12, 16, 24])
    def test_works_for_various_bitwidths(self, bitwidth):
        time0, data_in = generate_sinusoidal_waveform(f_sig=1000, fs=48000, bitwidth=bitwidth)
        assert len(time0) == len(data_in)
        assert np.issubdtype(data_in.dtype, np.integer)

    def test_higher_frequency_yields_shorter_time_vector(self):
        fs = 48000
        time_low, _ = generate_sinusoidal_waveform(f_sig=500, fs=fs, no_periods=1)
        time_high, _ = generate_sinusoidal_waveform(f_sig=2000, fs=fs, no_periods=1)
        assert time_high[-1] < time_low[-1]


class TestGenerateNoise:
    def test_returns_ndarray_of_correct_length(self):
        time0 = np.arange(0, 1, 1 / 1000)
        noise = generate_noise(time0, sigma=10)
        assert isinstance(noise, np.ndarray)
        assert len(noise) == len(time0)

    def test_zero_sigma_yields_all_zeros(self):
        time0 = np.arange(0, 1, 1 / 1000)
        noise = generate_noise(time0, sigma=0)
        assert np.all(noise == 0)

    def test_dtype_int8_for_bit_le_8(self):
        time0 = np.arange(0, 1, 1 / 100)
        noise = generate_noise(time0, sigma=5, bit=8)
        assert noise.dtype == np.dtype("int8")

    def test_dtype_int16_for_bit_between_9_and_16(self):
        time0 = np.arange(0, 1, 1 / 100)
        noise = generate_noise(time0, sigma=5, bit=16)
        assert noise.dtype == np.dtype("int16")

    def test_default_bit_argument_is_16(self):
        time0 = np.arange(0, 1, 1 / 100)
        noise_default = generate_noise(time0, sigma=5)
        noise_explicit = generate_noise(time0, sigma=5, bit=16)
        assert noise_default.dtype == noise_explicit.dtype

    def test_dtype_int32_for_bit_greater_than_16(self):
        time0 = np.arange(0, 1, 1 / 100)
        noise = generate_noise(time0, sigma=5, bit=24)
        assert noise.dtype == np.dtype("int32")

    def test_current_buggy_behavior_for_bit_10(self):
        time0 = np.arange(0, 1, 1 / 100)
        noise = generate_noise(time0, sigma=5, bit=10)
        assert noise.dtype == np.dtype("int16")

    def test_noise_standard_deviation_roughly_matches_sigma(self):
        rng_time = np.arange(0, 1, 1 / 100000)
        sigma = 50
        noise = generate_noise(rng_time, sigma=sigma, bit=16)
        assert noise.astype(float).std() == pytest.approx(sigma, rel=0.05)

    def test_empty_time_vector_returns_empty_array(self):
        noise = generate_noise(np.array([]), sigma=10)
        assert len(noise) == 0
