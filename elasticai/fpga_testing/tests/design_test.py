import unittest
from elasticai.creator.testing import (
    check_cocotb_test_result,
    run_cocotb_sim_for_src_dir
)


class FPGADesignTest(unittest.TestCase):
    def test_led(self):
        from elasticai.fpga_testing.tests.design_led_tb import cocotb_settings
        path2xml = run_cocotb_sim_for_src_dir(**cocotb_settings)
        self.assertTrue(check_cocotb_test_result(str(path2xml)))

    def test_echo(self):
        from elasticai.fpga_testing.tests.design_echo_tb import cocotb_settings
        path2xml = run_cocotb_sim_for_src_dir(**cocotb_settings)
        self.assertTrue(check_cocotb_test_result(str(path2xml)))

    def test_rom(self):
        from elasticai.fpga_testing.tests.design_rom_tb import cocotb_settings
        path2xml = run_cocotb_sim_for_src_dir(**cocotb_settings)
        self.assertTrue(check_cocotb_test_result(str(path2xml)))

    def test_ram(self):
        from elasticai.fpga_testing.tests.design_ram_tb import cocotb_settings
        path2xml = run_cocotb_sim_for_src_dir(**cocotb_settings)
        self.assertTrue(check_cocotb_test_result(str(path2xml)))

    def test_mult(self):
        from elasticai.fpga_testing.tests.design_mult_tb import cocotb_settings
        path2xml = run_cocotb_sim_for_src_dir(**cocotb_settings)
        self.assertTrue(check_cocotb_test_result(str(path2xml)))

    def test_hardtanh(self):
        from elasticai.fpga_testing.tests.design_func_tb import cocotb_settings
        path2xml = run_cocotb_sim_for_src_dir(**cocotb_settings)
        self.assertTrue(check_cocotb_test_result(str(path2xml)))


if __name__ == '__main__':
    unittest.main()
