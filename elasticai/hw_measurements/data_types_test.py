import numpy as np

from .data_types import TransientData


class TestSizeProperty:
    def test_size_returns_last_dimension(self):
        rawdata = np.zeros((4, 250))
        td = TransientData(
            rawdata=rawdata,
            timestamps=np.arange(250),
            channels=["a", "b", "c", "d"],
            sampling_rate=500.0,
        )
        assert td.size == 250

    def test_size_for_1d_array(self):
        rawdata = np.zeros(64)
        td = TransientData(
            rawdata=rawdata,
            timestamps=np.arange(64),
            channels=["a"],
            sampling_rate=100.0,
        )
        assert td.size == 64

    def test_size_for_single_sample(self):
        rawdata = np.zeros((2, 1))
        td = TransientData(
            rawdata=rawdata,
            timestamps=np.array([0.0]),
            channels=["a", "b"],
            sampling_rate=1.0,
        )
        assert td.size == 1


class TestNumChannelsProperty:
    def test_num_channels_returns_first_dimension(self):
        rawdata = np.zeros((5, 200))
        td = TransientData(
            rawdata=rawdata,
            timestamps=np.arange(200),
            channels=["a", "b", "c", "d", "e"],
            sampling_rate=1000.0,
        )
        assert td.num_channels == 5

    def test_num_channels_for_single_channel(self):
        rawdata = np.zeros((1, 100))
        td = TransientData(
            rawdata=rawdata,
            timestamps=np.arange(100),
            channels=["a"],
            sampling_rate=1000.0,
        )
        assert td.num_channels == 1

    def test_num_channels_for_1d_array_matches_size_not_channel_count(self):
        rawdata = np.zeros(64)
        td = TransientData(
            rawdata=rawdata,
            timestamps=np.arange(64),
            channels=["a"],
            sampling_rate=100.0,
        )
        assert td.num_channels == 64
        assert td.num_channels == td.size
