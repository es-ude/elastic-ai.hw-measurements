import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from copy import deepcopy
from pathlib import Path

import elasticai.fpga_testing as test_dut
from elasticai.fpga_testing.tests import cocotb_settings_dev
from elasticai.creator.testing.cocotb_runner import run_cocotb_sim_for_src_dir


cocotb_settings = deepcopy(cocotb_settings_dev)
cocotb_settings['path2src'] = Path(test_dut.__file__).parent / 'design_arty7'
cocotb_settings['cocotb_test_module'] = "elasticai.fpga_testing.tests.arty7_led_tb"


@cocotb.test()
async def top_module(dut):
    period_clk = 5
    bitwidth = dut.UART_BITWIDTH.value.to_unsigned()
    num_bytes = dut.UART_FIFO_BYTE_SIZE.value.to_unsigned()
    baudrate = dut.UART_CNT_BAUDRATE.value.to_unsigned() * dut.UART_MOD.NSAMP.value.to_unsigned()
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
    dut.UART_RX.value = 1
    # Start clock and making reset
    cocotb.start_soon(Clock(dut.CLK_100MHz, period_clk, unit='ns').start())
    for _ in range(8):
        await RisingEdge(dut.CLK_100MHz)
    for idx in range(4):
        await RisingEdge(dut.CLK_100MHz)
        dut.RSTN.value = idx % 2
        await RisingEdge(dut.CLK_100MHz)
    dut.RSTN.value = 1
    for _ in range(2):
        await RisingEdge(dut.CLK_100MHz)

    # make UART package transmission
    for data_send, state in zip(data_send_list, state_led):
        # Idle time
        for _ in range(baudrate):
            await RisingEdge(dut.CLK_100MHz)

        # Do UART transmission
        for data_tx in data_send:
            # Start bit
            dut.UART_RX.value = 0
            for _ in range(baudrate):
                await RisingEdge(dut.CLK_100MHz)
            # Data Transmission
            for val in data_tx[::-1]:
                dut.UART_RX.value = val
                for _ in range(baudrate):
                    await RisingEdge(dut.CLK_100MHz)
            # Stop bit
            dut.UART_RX.value = 1
            await RisingEdge(dut.uart_mod_rdy)
            for _ in range(int(baudrate/2)):
                await RisingEdge(dut.CLK_100MHz)

        # Idle time
        for _ in range(baudrate):
            await RisingEdge(dut.CLK_100MHz)
        test_data = dut.LED.value.to_unsigned()
        assert test_data & 0x01 == state

    # Checking Ending
    for _ in range(baudrate):
        await RisingEdge(dut.CLK_100MHz)


if __name__ == "__main__":
    run_cocotb_sim_for_src_dir (**cocotb_settings)
