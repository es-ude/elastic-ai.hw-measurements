import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from copy import deepcopy
from pathlib import Path

import elasticai.fpga_testing as test_dut
from elasticai.fpga_testing.tests import cocotb_settings_env5
from elasticai.creator.testing.cocotb_runner import run_cocotb_sim_for_src_dir


cocotb_settings = deepcopy(cocotb_settings_env5)
cocotb_settings['path2src'] = Path(test_dut.__file__).parent / 'design_env5'
cocotb_settings['cocotb_test_module'] = "elasticai.fpga_testing.tests.env5_led_tb"


@cocotb.test()
async def top_module(dut):
    bitwidth = dut.SPI_BITWIDTH.value.to_unsigned()
    baudrate = 16
    data_send_list = [
        ['00000100', '00000000', '00000001'],  # enable LED
        ['00000100', '00000000', '00000000'],  # disable LED
        ['00000100', '00000000', '00000001'],  # enable LED
        ['00000100', '00000000', '00000000'],  # disable LED
        ['00001000', '00000000', '00000000'],  # toggle LED
        ['00001000', '00000000', '00000000'],  # toggle LED
        ['00001000', '00000000', '00000000'],  # toggle LED
        ['00001000', '00000000', '00000000'],  # toggle LED
    ]
    state_led = [
        1,
        0,
        1,
        0,
        1,
        0,
        1,
        0
    ]

    # Initial definition
    dut.CLK_100MHz.value = 0
    dut.RSTN.value = 0
    dut.SPI_CSN.value = 1
    dut.SPI_MOSI.value = "Z"
    dut.SPI_SCLK.value = 0
    # Start clock and making reset
    cocotb.start_soon(Clock(dut.CLK_100MHz, 5, unit='ns').start())
    for _ in range(8):
        await RisingEdge(dut.CLK_100MHz)
    for idx in range(4):
        await RisingEdge(dut.CLK_100MHz)
        dut.RSTN.value = idx % 2
        await RisingEdge(dut.CLK_100MHz)
    dut.RSTN.value = 1
    for _ in range(2):
        await RisingEdge(dut.CLK_100MHz)

    # make SPI package transmission
    for data_send, state in zip(data_send_list, state_led):
        # Idle time
        for _ in range(baudrate):
            await RisingEdge(dut.CLK_100MHz)

        # Do SPI transmission (CPOL = 0, CPHA = 1, MSB = 1)
        dut.SPI_CSN.value = 0
        for _ in range(4):
            await RisingEdge(dut.CLK_100MHz)
        for data_tx in data_send:
            for val in data_tx:
                dut.SPI_MOSI.value = val
                dut.SPI_SCLK.value = 1
                for _ in range(int(baudrate/2)):
                    await RisingEdge(dut.CLK_100MHz)
                dut.SPI_SCLK.value = 0
                for _ in range(int(baudrate / 2)):
                    await RisingEdge(dut.CLK_100MHz)
        for _ in range(4):
            await RisingEdge(dut.CLK_100MHz)
        dut.SPI_MOSI.value = "Z"
        dut.SPI_CSN.value = 1

        # Idle time
        for _ in range(200):
            await RisingEdge(dut.CLK_100MHz)
        assert dut.LED.value.to_unsigned() & 0x01 == state

    # Checking Ending
    for _ in range(baudrate):
        await RisingEdge(dut.CLK_100MHz)


if __name__ == "__main__":
    run_cocotb_sim_for_src_dir (**cocotb_settings)
