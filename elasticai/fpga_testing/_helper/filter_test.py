import numpy as np
import pytest

from .filter import FilterElement


@pytest.fixture
def signal():
    rng = np.random.default_rng(42)
    return rng.standard_normal(500)


def test_iir_bandpass_filter_returns_same_length(signal):
    f = FilterElement(N=4, fs=1000.0, f_filter=[50.0, 150.0], use_iir_filter=True, btype="bandpass")
    y = f.filter(signal)
    assert len(y) == len(signal)


def test_iir_bandstop_filter_returns_same_length(signal):
    f = FilterElement(N=4, fs=1000.0, f_filter=[50.0, 150.0], use_iir_filter=True, btype="bandstop")
    y = f.filter(signal)
    assert len(y) == len(signal)


def test_fir_lowpass_filter_returns_same_length(signal):
    f = FilterElement(N=31, fs=1000.0, f_filter=[50.0], use_iir_filter=False, btype="low")
    y = f.filter(signal)
    assert len(y) == len(signal)


def test_iir_allpass_first_order(signal):
    f = FilterElement(N=1, fs=1000.0, f_filter=[50.0], use_iir_filter=True, btype="all")
    y = f.filter(signal)
    assert len(y) == len(signal)


def test_iir_allpass_second_order(signal):
    f = FilterElement(N=2, fs=1000.0, f_filter=[50.0, 20.0], use_iir_filter=True, btype="all")
    y = f.filter(signal)
    assert len(y) == len(signal)


def test_iir_allpass_unsupported_order_raises():
    with pytest.raises(NotImplementedError):
        FilterElement(N=3, fs=1000.0, f_filter=[50.0], use_iir_filter=True, btype="all")


def test_fir_allpass_is_pure_delay():
    N = 5
    f = FilterElement(N=N, fs=1000.0, f_filter=[50.0], use_iir_filter=False, btype="all")
    x = np.arange(1, 11, dtype=float)
    y = f.filter(x)
    expected = np.concatenate([np.zeros(N), x])[: len(x)]
    np.testing.assert_array_equal(y, expected)


def test_invalid_btype_raises():
    with pytest.raises(NotImplementedError):
        FilterElement(N=4, fs=1000.0, f_filter=[50.0, 150.0], use_iir_filter=True, btype="nonsense")


def test_invalid_ftype_raises():
    with pytest.raises(NotImplementedError):
        FilterElement(N=4, fs=1000.0, f_filter=[50.0, 150.0], use_iir_filter=True, ftype="nonsense")


def test_filtfilt_flag_changes_output(signal):
    f_lfilter = FilterElement(
        N=4, fs=1000.0, f_filter=[50.0, 150.0], use_iir_filter=True, btype="bandpass", use_filtfilt=False
    )
    f_filtfilt = FilterElement(
        N=4, fs=1000.0, f_filter=[50.0, 150.0], use_iir_filter=True, btype="bandpass", use_filtfilt=True
    )
    y1 = f_lfilter.filter(signal)
    y2 = f_filtfilt.filter(signal)
    assert len(y1) == len(y2) == len(signal)
    assert not np.allclose(y1, y2)


def test_freq_response_iir_low_with_single_corner_frequency():
    f = FilterElement(N=4, fs=1000.0, f_filter=[50.0], use_iir_filter=True, btype="low")
    freq = np.array([10.0, 50.0, 100.0])
    result = f.freq_response(freq)
    assert set(result.keys()) == {"freq", "gain", "phase"}
    assert len(result["gain"]) == len(freq)


def test_freq_response_iir_keys_and_shape():
    f = FilterElement(N=4, fs=1000.0, f_filter=[50.0, 150.0], use_iir_filter=True, btype="bandpass")
    freq = np.array([10.0, 50.0, 100.0])
    result = f.freq_response(freq)
    assert set(result.keys()) == {"freq", "gain", "phase"}
    assert len(result["gain"]) == len(freq)
    assert len(result["phase"]) == len(freq)


def test_freq_response_fir_keys_and_shape():
    f = FilterElement(N=31, fs=1000.0, f_filter=[50.0], use_iir_filter=False, btype="low")
    freq = np.array([10.0, 50.0, 100.0])
    result = f.freq_response(freq)
    assert set(result.keys()) == {"freq", "gain", "phase"}
    assert len(result["gain"]) == len(freq)
    assert len(result["phase"]) == len(freq)


def test_iir_low_with_single_corner_frequency(signal):
    f = FilterElement(N=4, fs=1000.0, f_filter=[50.0], use_iir_filter=True, btype="low")
    y = f.filter(signal)
    assert len(y) == len(signal)


def test_iir_high_with_single_corner_frequency(signal):
    f = FilterElement(N=4, fs=1000.0, f_filter=[50.0], use_iir_filter=True, btype="high")
    y = f.filter(signal)
    assert len(y) == len(signal)
