import unittest
from pathlib import Path
from shutil import rmtree
from .bin_build import read_bitstream_file_amd, translate_bit_to_bin, write_into_bitstream_text, write_into_bitstream_file
from elasticai.fpga_testing import get_path_to_project


class TestBitStreamTranslator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path_to_template = Path(get_path_to_project("artefact")) / "env5"
        cls.path_to_temp = Path(get_path_to_project("test_dummy"))
        if cls.path_to_temp.exists():
            rmtree(cls.path_to_temp)
        cls.path_to_temp.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        #rmtree(cls.path_to_temp)
        pass

    def test_read_files(self):
        data_bit = read_bitstream_file_amd(
            path_to_bitstream_file=self.path_to_template / "TOP_MODULE.bit",
            remove_header=True
        )
        data_bin = read_bitstream_file_amd(
            path_to_bitstream_file=self.path_to_template / "TOP_MODULE.bin",
            remove_header=False
        )
        self.assertEqual(data_bit, data_bin)

    def test_write_bin_file_with_header(self):
        data = read_bitstream_file_amd(
            path_to_bitstream_file=self.path_to_template / "TOP_MODULE.bit",
            remove_header=False
        )
        write_into_bitstream_file(
            path_to_file=self.path_to_temp / "TOP_MODULE_0.bin",
            data=data
        )
        self.assertTrue((self.path_to_temp / "TOP_MODULE_0.bin").exists())

    def test_translate_bit_to_bin(self):
        files = translate_bit_to_bin(
            path_to_bitstream_folder=self.path_to_template,
            path_to_source=self.path_to_temp
        )
        self.assertTrue(len(files), 1)
        self.assertTrue((self.path_to_temp / "TOP_MODULE.bin").exists())

        data_bit = read_bitstream_file_amd(
            path_to_bitstream_file=self.path_to_template / "TOP_MODULE.bit",
        )
        data_bin = read_bitstream_file_amd(
            path_to_bitstream_file=self.path_to_temp / "TOP_MODULE.bin",
        )
        self.assertEqual(data_bit, data_bin)

    def test_write_text_file_with_header(self):
        data = read_bitstream_file_amd(
            path_to_bitstream_file=self.path_to_template / "TOP_MODULE.bit",
            remove_header=False
        )
        write_into_bitstream_text(
            path_to_file=self.path_to_temp / "TOP_MODULE_0.txt",
            data=data,
            add_lines=True
        )
        self.assertTrue((self.path_to_temp / "TOP_MODULE_0.txt").exists())
        write_into_bitstream_text(
            path_to_file=self.path_to_temp / "TOP_MODULE_1.txt",
            data=data,
            add_lines=False
        )
        self.assertTrue((self.path_to_temp / "TOP_MODULE_1.txt").exists())

    def test_write_text_file_without_header(self):
        data = read_bitstream_file_amd(
            path_to_bitstream_file=self.path_to_template / "TOP_MODULE.bit",
            remove_header=True
        )
        write_into_bitstream_text(
            path_to_file=self.path_to_temp / "TOP_MODULE_2.txt",
            data=data,
            add_lines=True
        )
        self.assertTrue((self.path_to_temp / "TOP_MODULE_2.txt").exists())
        write_into_bitstream_text(
            path_to_file=self.path_to_temp / "TOP_MODULE_3.txt",
            data=data,
            add_lines=False
        )
        self.assertTrue((self.path_to_temp / "TOP_MODULE_3.txt").exists())


if __name__ == '__main__':
    unittest.main()
