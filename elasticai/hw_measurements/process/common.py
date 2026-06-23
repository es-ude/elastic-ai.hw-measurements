from logging import getLogger
from pathlib import Path

import numpy as np

from elasticai.hw_measurements.data_types import LoadedData


class ProcessCommon:
    def __init__(self):
        """Class with common functions for measurement data processing"""
        self._logger = getLogger(__name__)

    @staticmethod
    def get_data_overview(path: Path, acronym: str) -> list:
        """Function for getting an overview of available data files"""
        return [file for file in path.iterdir() if acronym in file.as_posix()]

    def load_data(self, path: Path, file_name: str, load_settings: bool = False) -> LoadedData:
        """Function for loading the measurement data
        :param path:            Path to measurement in which the files are inside
        :param file_name:       Name of numpy file with measurement results
        :param load_settings:   If True, load settings will be loaded from file
        :return:            Dictionary
        """
        path2file = path / file_name
        self._logger.debug(f"Loading data from: {path2file}")
        if not path2file.exists():
            raise FileNotFoundError(f"File {path2file} does not exist")

        loaded = np.load(file=path2file.as_posix(), allow_pickle=True, mmap_mode="r")
        data = loaded["data"].flatten()[0]
        set = loaded["settings"].flatten()[0] if load_settings else dict()

        return LoadedData(
            data=data,
            settings=set,
        )

    @staticmethod
    def process_data_direct(data: dict) -> dict:
        """Function for processing the measurement data directly
        :param data:        Dictionary of measurement results
        :return:            Dictionary with ['stim': stimulation input array, 'ch<x>': results with 'mean' and 'std']
        """
        rslt = {"stim": data["stim"]}

        keys_test = data.keys()
        for key_used in keys_test:
            if not key_used == "stim":
                daq_rslt = data[key_used]
                mean = np.mean(np.mean(daq_rslt, axis=2), axis=0)
                std = np.std(np.std(daq_rslt, axis=2), axis=0)
                assert mean.size == std.size and mean.size == rslt["stim"].size, (
                    "Length of preprocessed data is not equal"
                )
                rslt.update({key_used: {"mean": mean, "std": std}})

        assert len(data) == len(keys_test), "not all data are processed"
        return rslt

    def process_data_from_file(self, path: Path, file_name: str, load_settings: bool = False) -> dict:
        """Function for processing the measurement data from loading a file
        :param path:            Path to measurement in which the files are inside
        :param file_name:       Name of numpy file with measurement results
        :param load_settings:   If True, load settings will be loaded from file
        :return:                Dictionary with ['stim': stimulation input array, 'ch<x>': results with 'mean' and 'std']
        """
        data = self.load_data(path=path, file_name=file_name, load_settings=load_settings)
        return self.process_data_direct(data=data.data)
