import numpy as np


def generate_sinusoidal_waveform(f_sig: float, fs: float, no_periods=1, bitwidth=16, signed_out=False) -> tuple[np.ndarray, np.ndarray]:
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

    data_in = np.array(offset + amp * np.cos(2 * np.pi * time0 * f_sig), dtype=int)
    return time0, data_in


def generate_noise(time: np.ndarray, sigma: float, bit=16) -> np.ndarray:
    """Function to generate noise for testing digital filters
    Args:
        time:   numpy array with time vector
        sigma:  noise standard deviation
        bit:    effective bitwidth of signal
    """
    if bit > 8:
        data_type = 'int16'
    elif bit > 16:
        data_type = 'int32'
    else:
        data_type = 'int8'
    return np.array(
        object=np.random.normal(0, sigma, time.size),
        dtype=data_type
    )
