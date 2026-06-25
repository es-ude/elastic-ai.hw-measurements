from elasticai.fpga_testing import get_path_to_project

cocotb_settings_arty7 = dict(
    src_files=[
        "arty7/top_module.v",
        "arty7/uart_com.v",
        "arty7/uart_fifo.v",
        "arty7/uart_middleware.v",
        "common/test_dut.v",
        "common/00_echo/skeleton_echo.v",
        "common/01_bram/skeleton_ram.v",
        "common/01_bram/bram_single.v",
    ],
    path2src=get_path_to_project() / "elasticai" / "fpga_testing" / "template",
    top_module_name="TOP_MODULE",
    cocotb_test_module="elasticai.fpga_testing.tests.arty7_echo_test",
    params={
        "NUM_DUT": 3,
        "UART_CNT_BAUDRATE": 27,
        "UART_FIFO_BYTE_SIZE": 3,
        "TEST_ENV_CMDS_BITWIDTH": 2,
        "TEST_ENV_ADR_WIDTH": 6,
        "TEST_ENV_DATA_BITWIDTH": 16,
    },
)


cocotb_settings_env5 = dict(
    src_files=[
        "env5/top_module.v",
        "env5/spi_slave_wclk.v",
        "env5/spi_middleware.v",
        "common/test_dut.v",
        "common/00_echo/skeleton_echo.v",
        "common/01_bram/skeleton_ram.v",
        "common/01_bram/bram_single.v",
    ],
    path2src=get_path_to_project() / "elasticai" / "fpga_testing" / "template",
    top_module_name="TOP_MODULE",
    cocotb_test_module="elasticai.fpga_testing.tests.env5_echo_test",
    params={
        "NUM_DUT": 3,
        "TEST_ENV_CMDS_BITWIDTH": 2,
        "TEST_ENV_ADR_WIDTH": 6,
        "TEST_ENV_DATA_BITWIDTH": 16,
    },
)
