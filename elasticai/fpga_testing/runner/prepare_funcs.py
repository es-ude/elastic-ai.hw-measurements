import numpy as np

from elasticai.fpga_testing import ConfigurationDUT
from elasticai.fpga_testing.runner.interface_runner import InterfaceRunner


class DataProcessor(InterfaceRunner):
    def __init__(self, com_port="AUTOCOM") -> None:
        super().__init__(com_port=com_port, num_delay_messages=0)

    @property
    def is_active(self) -> bool:
        return True

    def get_data_scaling_value(self, bitwidth_data: int) -> int:
        return 0

    def do_reset(self) -> None:
        pass

    def open_serial(self) -> None:
        pass

    def close_serial(self) -> None:
        pass

    def get_dut_config(self, num_target: int) -> ConfigurationDUT:
        return ConfigurationDUT(
            bitwidth_input=8,
            bitwidth_output=8,
            dut_type=1,
            num_duts=1,
            num_outputs=1,
            num_inputs=1,
        )

    def select_device_for_testing(self, num_dut: int) -> None:
        pass

    def set_led_mcu(self, state: bool) -> None:
        pass

    def set_led_fpga(self, state: bool) -> None:
        pass

    def toggle_led_fpga(self) -> None:
        pass

    def do_inference(self, data: bytes) -> bytes:
        return data

    def do_inference_empty(self, num_cycles: int) -> bytes:
        return bytes(b"000" * num_cycles)

    def preparing_data_streaming_architecture(
        self, signal: np.ndarray, bit_position_start: int, is_signed: bool = False
    ) -> bytes:
        """Preparing the data stream to FPGA by converting the numpy input (1:1)"""
        data = bytes()
        for val in signal:
            data += self._data_to_hex(
                reg=self._cmds.Write, adr=0, data=val * bit_position_start, is_signed=is_signed
            )
            data += self._data_to_hex(reg=self._cmds.Control, adr=1, data=0, is_signed=False)
        data += self._data_to_hex(reg=self._cmds.Control, adr=0, data=0, is_signed=False)
        data += self._data_to_hex(reg=self._cmds.Control, adr=0, data=0, is_signed=False)
        return data

    def preparing_data_calling_architecture(self, num_repeat: int) -> bytes:
        """Preparing the data stream to FPGA by converting the numpy input (1:1)"""
        data = bytes()
        data += self._data_to_hex(reg=self._cmds.Write, adr=0, data=1, is_signed=False)
        for val in range(num_repeat):
            data += self._data_to_hex(reg=self._cmds.Control, adr=1, data=1, is_signed=False)
        data += self._data_to_hex(reg=self._cmds.Control, adr=0, data=0, is_signed=False)
        data += self._data_to_hex(reg=self._cmds.Control, adr=0, data=0, is_signed=False)
        return data

    def preparing_data_memory_write_architecture(
        self, signal: np.ndarray, adr_start: int, bit_position_start: int, is_signed: bool = False
    ) -> bytes:
        """Preparing the data stream to FPGA by converting the numpy input (1:1)"""
        data = bytes()
        for ite, val in enumerate(signal):
            data += self._data_to_hex(
                reg=self._cmds.Write,
                adr=adr_start + ite,
                data=val * bit_position_start,
                is_signed=is_signed,
            )
        return data

    def preparing_data_memory_read_architecture(
        self, signal: np.ndarray, adr_start: int, bit_position_start: int, is_signed: bool = False
    ) -> bytes:
        """Preparing the data stream to FPGA by converting the numpy input (1:1)"""
        data = bytes()
        for ite, val in enumerate(signal):
            data += self._data_to_hex(
                reg=self._cmds.Read,
                adr=adr_start + ite,
                data=val * bit_position_start,
                is_signed=is_signed,
            )
        data += self._data_to_hex(reg=self._cmds.Control, adr=0, data=0, is_signed=False)
        return data

    def preparing_data_creator_architecture(
        self,
        signal: list,
        num_input_layer: int,
        num_output_layer: int,
        bit_position_start: int,
        is_signed: bool = False,
    ) -> bytes:
        """Preparing the data stream to FPGA by converting the numpy input"""
        # --- Data Input
        data = bytes()
        for idx, val in enumerate(signal):
            data += self._data_to_hex(
                reg=self._cmds.Write,
                adr=18 + (idx % num_input_layer),
                data=val * bit_position_start,
                is_signed=is_signed,
            )
            if idx % num_input_layer == num_input_layer - 1:
                data += self._data_to_hex(
                    reg=self._cmds.Write, adr=16, data=bit_position_start, is_signed=False
                )
                data += self._data_to_hex(reg=self._cmds.Write, adr=16, data=0, is_signed=False)
                for idy in range(num_output_layer):
                    data += self._data_to_hex(reg=self._cmds.Read, adr=18 + idy, data=0, is_signed=False)
        return data

    def preparing_data_arithmetic_architecture(
        self, signal: list, bit_position_start: int, is_signed: bool = False
    ) -> bytes:
        """Preparing the data stream to FPGA by converting the numpy input"""
        # --- Data Input
        data = bytes()
        for packet in signal:
            for idx, val in enumerate(packet):
                data += self._data_to_hex(
                    reg=self._cmds.Write, adr=idx, data=val * bit_position_start, is_signed=is_signed
                )
            data += self._data_to_hex(reg=self._cmds.Control, adr=1, data=0, is_signed=False)
        data += self._data_to_hex(reg=self._cmds.Control, adr=0, data=0, is_signed=False)
        return data

    def preparing_data_reading_skeleton_id(self, length: int = 16) -> bytes:
        """Function for preparing reading ID from skeleton"""
        data = bytes()
        for idx in range(length):
            data += self._data_to_hex(reg=self._cmds.Read, adr=idx, data=0, is_signed=False)
        return data
