import numpy as np
from math import pi
from scipy import signal


def generate_sinusoidal_waveform(f_sig: float, fs: float, no_periods=1, bitwidth=16, signed_out=False) -> [np.ndarray, np.ndarray]:
    """Function to generate a sinusoidal waveform for testing digital filter responses
    Args:
        f_sig:      Frequency of the sinusoidal input
        fs:         Desired sampling frequency
        no_periods: Number of periods
        bitwidth:   Effective bitwidth of signal
        signed_out: Signed integer output
    """
    t_end = no_periods / f_sig
    time0 = np.arange(0, t_end, 1 / fs)
    amp = 0.95 * (2 ** (bitwidth-1))-2
    offset = (2 ** (bitwidth-1)) if not signed_out else 0

    data_in = np.array(offset + amp * np.cos(2 * pi * time0 * f_sig), dtype=int)
    return time0, data_in

#
def generate_triangular_waveform(f_sig: float, fs: float, no_periods=1, bit=16) -> [np.ndarray, np.ndarray]:
    """Function to generate a triangular waveform for testing digital filters

    Args:
        f_sig: Frequency of the triangular input
        fs: Desired sampling frequency
        no_periods: Number of periods
    """
    t_end = no_periods / f_sig
    time0 = np.arange(0, t_end, 1 / fs)
    offset = (2 ** (bit-1))-1

    data_in = np.array(offset * (1 + 0.9 * signal.sawtooth(2 * pi * time0 * f_sig, 0.5)), dtype='uint16')
    return time0, data_in


def generate_rectangular_waveform(f_sig: float, fs: float, no_periods=1, bit=16) -> [np.ndarray, np.ndarray]:
    """Function to generate a rectangular waveform for testing digital filters

    Args:
        f_sig: Frequency of the triangular input
        fs: Desired sampling frequency
        no_periods: Number of periods
    """
    t_end = no_periods / f_sig
    time0 = np.arange(0, t_end, 1 / fs)
    offset = (2 ** (bit-1))-1

    ref_sig = np.sin.step(2 * pi * time0 * f_sig, 0.5)
    ref_sig[ref_sig > 0] = 1.0
    ref_sig[ref_sig <= 0] = -1.0
    data_in = np.array(offset * (1 + 0.9 * ref_sig), dtype='uint16')
    return time0, data_in


def generate_noise(time: np.ndarray, sigma: float, bit=16) -> np.ndarray:
    """Function to generate noise for testing digital filters

    Args:
        time: numpy array
    """
    return np.array(np.random.normal(0, sigma, time.size), dtype='int16')
