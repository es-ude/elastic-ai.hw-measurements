cocotb_settings_dev = dict(
    src_files=[
        "top_module.v", "uart_com.v", "uart_fifo.v", "uart_middleware.v", 'test_dut.v',
        '00_echo/skeleton_echo.v',
        '01_rom/skeleton_rom.v', '01_rom/waveform_lut0.v',
        '02_bram/skeleton_ram.v', '02_bram/bram_single.v',
        '03_mult/skeleton_math.v', '03_mult/mult_lut_signed.v', '03_mult/adder_full.v', '03_mult/adder_half.v',
        '04_actfunc/skeleton_math.v', '04_actfunc/hardtanh.v'
    ],
    path2src=".",
    top_module_name='TOP_MODULE',
    cocotb_test_module="elasticai.fpga_testing.tests.arty7_echo_tb",
    params={
        'NUM_DUT': 5, 'UART_CNT_BAUDRATE': 27, 'UART_FIFO_BYTE_SIZE': 3,
        'TEST_ENV_CMDS_BITWIDTH': 2, 'TEST_ENV_ADR_WIDTH': 6, 'TEST_ENV_DATA_BITWIDTH': 16
    }
)


cocotb_settings_env5 = dict(
    src_files=[
        "top_module.v", "spi_slave_wclk.v", "spi_middleware.v", 'test_dut.v',
        '00_echo/skeleton_echo.v',
        '01_rom/skeleton_rom.v', '01_rom/waveform_lut0.v',
        '02_bram/skeleton_ram.v', '02_bram/bram_single.v',
        '03_mult/skeleton_math.v', '03_mult/mult_lut_signed.v', '03_mult/adder_full.v', '03_mult/adder_half.v',
        '04_actfunc/skeleton_math.v', '04_actfunc/hardtanh.v'
    ],
    path2src=".",
    top_module_name='TOP_MODULE',
    cocotb_test_module="elasticai.fpga_testing.tests.env5_echo_tb",
    params={
        'NUM_DUT': 5, 'SPI_BITWIDTH': 24,
        'TEST_ENV_CMDS_BITWIDTH': 2, 'TEST_ENV_ADR_WIDTH': 6, 'TEST_ENV_DATA_BITWIDTH': 16
    }
)
