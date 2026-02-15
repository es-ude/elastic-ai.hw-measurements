import unittest
from time import sleep
from elasticai.fpga_testing import (
    get_path_to_project,
    DeviceUnderTestHandler
)


class TestingFPGA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fpga_dut = DeviceUnderTestHandler("AUTOCOM")
        cls.fpga_dut.open_serial()

    @classmethod
    def tearDownClass(cls):
        cls.fpga_dut.close_serial()

    def test_enable_disable_led(self):
        self.fpga_dut.do_led_control(True)
        sleep(0.1)
        self.fpga_dut.do_led_control(False)
        sleep(0.1)

    def test_toggle_led(self):
        for _ in range(20):
            sleep(0.1)
            self.fpga_dut.do_led_toggle()

    def test_header_dut_default(self):
        rslt = self.fpga_dut.get_dut_config(0)
        assert rslt.num_duts == 3
        assert rslt.dut_type == 0
        assert rslt.num_inputs == 0
        assert rslt.num_outputs == 1
        assert rslt.bitwidth_input == 0
        assert rslt.bitwidth_output == 16

    def test_header_dut_echo(self):
        rslt = self.fpga_dut.get_dut_config(1)
        assert rslt.num_duts == 3
        assert rslt.dut_type == 1
        assert rslt.num_inputs == 1
        assert rslt.num_outputs == 1
        assert rslt.bitwidth_input == 16
        assert rslt.bitwidth_output == 16

    def test_header_dut_rom(self):
        rslt = self.fpga_dut.get_dut_config(2)
        assert rslt.num_duts == 3
        assert rslt.dut_type == 2
        assert rslt.num_inputs == 0
        assert rslt.num_outputs == 21
        assert rslt.bitwidth_input == 0
        assert rslt.bitwidth_output == 16


if __name__ == '__main__':
    unittest.main()
