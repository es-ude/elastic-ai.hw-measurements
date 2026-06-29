import unittest
from time import sleep

import pytest

from .device_serial import DeviceSerial


class TestingFPGA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fpga_dut = DeviceSerial(com_port="AUTOCOM")
        cls.fpga_dut.open_serial()

    @classmethod
    def tearDownClass(cls):
        cls.fpga_dut.close_serial()

    @pytest.mark.hardware
    def test_serial_is_available(self):
        self.fpga_dut.open_serial()
        assert self.fpga_dut.is_active
        self.fpga_dut.close_serial()
        assert not self.fpga_dut.is_active

    @pytest.mark.hardware
    def test_enable_disable_led(self):
        self.fpga_dut.set_led_fpga(True)
        sleep(0.1)
        self.fpga_dut.set_led_fpga(False)
        sleep(0.1)

    @pytest.mark.hardware
    def test_toggle_led(self):
        for _ in range(20):
            sleep(0.1)
            self.fpga_dut.toggle_led_fpga()

    @pytest.mark.hardware
    def test_header_dut_default(self):
        rslt = self.fpga_dut.get_dut_config(0)
        assert rslt.num_duts == 3
        assert rslt.dut_type == 0
        assert rslt.num_inputs == 0
        assert rslt.num_outputs == 1
        assert rslt.bitwidth_input == 0
        assert rslt.bitwidth_output == 16

    @pytest.mark.hardware
    def test_header_dut_echo(self):
        rslt = self.fpga_dut.get_dut_config(1)
        assert rslt.num_duts == 3
        assert rslt.dut_type == 1
        assert rslt.num_inputs == 1
        assert rslt.num_outputs == 1
        assert rslt.bitwidth_input == 16
        assert rslt.bitwidth_output == 16

    @pytest.mark.hardware
    def test_header_dut_bram(self):
        rslt = self.fpga_dut.get_dut_config(2)
        assert rslt.num_duts == 3
        assert rslt.dut_type == 2
        assert rslt.num_inputs == 0
        assert rslt.num_outputs == 21
        assert rslt.bitwidth_input == 0
        assert rslt.bitwidth_output == 16
