import unittest

import pytest

from elasticai.hw_measurements import get_path_to_project
from elasticai.hw_measurements.process.common import LoadedData, ProcessCommon


class TestDataAnalysis(unittest.TestCase):
    path2data = get_path_to_project(new_folder="test_data")

    def test_get_data_overview(self):
        ovr = ProcessCommon().get_data_overview(path=self.path2data, acronym="dac")
        self.assertTrue(len(ovr) > 0)
        self.assertTrue(ovr[0].name == "dac_charac.npz")

    def test_load_data_from_file_wrong_path(self):
        hndl = ProcessCommon()
        try:
            hndl.load_data(path=self.path2data, file_name="dac.npz", load_settings=False)
        except FileNotFoundError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_load_data_from_file_wo_settings(self):
        hndl = ProcessCommon()
        file = hndl.get_data_overview(path=self.path2data, acronym="dac")[0]
        data = hndl.load_data(path=file.parent, file_name=file.name, load_settings=False)

        self.assertTrue(type(data) == LoadedData)
        self.assertTrue(len(data.data) == 17)
        self.assertTrue(len(data.settings) == 0)

    @pytest.mark.xfail(reason="Error due to settings loading")
    def test_load_data_from_file_with_settings(self):
        hndl = ProcessCommon()
        file = hndl.get_data_overview(path=self.path2data, acronym="dac")[0]
        data = hndl.load_data(path=file.parent, file_name=file.name, load_settings=True)

        self.assertTrue(type(data) == LoadedData)
        self.assertTrue(len(data.data) == 17)
        self.assertTrue(len(data.settings) == 0)

    def test_process_data_direct(self):
        hndl = ProcessCommon()
        file = hndl.get_data_overview(path=self.path2data, acronym="dac")[0]
        data = hndl.load_data(path=file.parent, file_name=file.name, load_settings=False)

        data_new = hndl.process_data_direct(data.data)
        self.assertTrue(len(data_new) == len(data.data))
        self.assertTrue(len(data_new["ch00"]) == 2)

    def test_process_data_from_file(self):
        hndl = ProcessCommon()
        file = hndl.get_data_overview(path=self.path2data, acronym="dac")[0]

        data_new = hndl.process_data_from_file(path=file.parent, file_name=file.name, load_settings=False)
        self.assertTrue(len(data_new["ch00"]) == 2)
