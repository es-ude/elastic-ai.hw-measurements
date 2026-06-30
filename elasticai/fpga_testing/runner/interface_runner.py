from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from elasticai.fpga_testing.definitions import (
    ConfigurationDUT,
    ProtocolBitwidth,
    ProtocolRegisterID,
)


@runtime_checkable
class InterfaceRunnerProtocol(Protocol):
    def __init__(self) -> None: ...

    @property
    def is_active(self) -> bool: ...

    def get_data_scaling_value(self, bitwidth_data: int) -> int: ...

    def do_reset(self) -> None: ...

    def open_serial(self) -> None: ...

    def close_serial(self) -> None: ...

    def get_dut_config(self, num_target: int) -> ConfigurationDUT: ...

    def select_device_for_testing(self, num_dut: int) -> None: ...

    def set_led_mcu(self, state: bool) -> None: ...

    def set_led_fpga(self, state: bool) -> None: ...

    def toggle_led_fpga(self) -> None: ...

    def do_inference(self, data: bytes) -> bytes: ...

    def do_inference_empty(self, num_cycles: int) -> bytes: ...


class InterfaceRunner(ABC):
    _cmds = ProtocolRegisterID
    _bits = ProtocolBitwidth()
    _slicing_start_idx: int
    _buffer_size: int = 2
    _com_port: str

    def __init__(self, com_port: str = "AUTOCOM", num_delay_messages: int = 0) -> None:
        """Class to access the FPGA system for testing different digital accelerators
        :param com_port:            String with COM Port / device name
        :param num_delay_messages:  Number of delay messages to send
        :returns:                   None
        """
        self._com_port = com_port
        self._slicing_start_idx = num_delay_messages

    @staticmethod
    def _process_dut_config(data: int) -> ConfigurationDUT:
        return ConfigurationDUT(
            num_duts=(data & 0xFC00_0000) >> 26,
            dut_type=(data & 0x03C0_0000) >> 22,
            num_inputs=(data & 0x003F_0000) >> 16,
            num_outputs=(data & 0x0000_FC00) >> 10,
            bitwidth_input=(data & 0x0000_03E0) >> 5,
            bitwidth_output=(data & 0x0000_001F) >> 0,
        )

    def _get_bytes_dut_selection(self, device_id: int) -> bytes:
        return self._data_to_hex(self._cmds.Control, 2, device_id << 1, False)

    def _get_data_scaling_value(self, bitwidth_data: int) -> int:
        if not 0 < bitwidth_data <= self._bits.DATA:
            raise ValueError(f"Bitwidth value {bitwidth_data} is out of range")
        return 2 ** (self._bits.DATA - bitwidth_data)

    def _data_to_hex(self, reg: int, adr: int, data: int, is_signed: bool) -> bytes:
        head = int(bin(reg)[2:].zfill(self._bits.CMD) + bin(adr)[2:].zfill(self._bits.ADR), 2)
        out = head.to_bytes(self._bits.bytes_head, "big")
        out0 = int(data).to_bytes(self._bits.bytes_data, "big", signed=is_signed)
        return out + out0

    def _data_from_hex(self, data: bytes, is_signed: bool) -> int:
        val = data[self._bits.bytes_head :]
        return int.from_bytes(val, byteorder="big", signed=is_signed)

    def get_dut_configs(self) -> dict[str, ConfigurationDUT]:
        """Loading the header information of each implemented test device (skeleton) on target device
        :returns:   Dict with Dataclass with ConfigurationDUT of each single structure
        """
        config0 = self.get_dut_config(0)

        dict_config = dict()
        for idx in range(config0.num_duts):
            dict_config.update({idx: self.get_dut_config(idx)})
        return dict_config

    @property
    def get_slicing_position(self) -> int:
        """Returning the slicing position to start extracting information
        :return:     Integer with number of delay messages to get right answer
        """
        return self._slicing_start_idx

    def slice_data_to_packet_size(self, data: bytes) -> list[bytes]:
        """Slicing the byte array to single RX/TX package
        :param data:    Byte array to slicing
        :return:        List of byte array
        """
        data_sliced = list()
        for i in range(0, len(data), self._bits.bytes_total):
            data_sliced.append(data[i : i + self._bits.bytes_total])
        return data_sliced

    def slice_data_for_transmission(self, data: bytes) -> list[bytes]:
        """Preparing the all byte messages with grouped RX/TX packages for transmission
        :param data:    Byte array to slice
        :return:        List of byte array to send
        """
        data_sliced = self.slice_data_to_packet_size(data=data)
        return [
            b"".join(data_sliced[i : i + self._buffer_size])
            for i in range(0, len(data_sliced), self._buffer_size)
        ]

    def slice_data_from_transmission(self, data: bytes, is_signed: bool) -> list[int]:
        """Post-processing the returned bytes from deviced to listed integers
        :param data:        Byte array from device
        :param is_signed:   True if data is signed, False otherwise
        :return:            List of integers with data content from device
        """
        data_sliced = self.slice_data_to_packet_size(data=data)
        data_out = list()
        for data0 in data_sliced[self.get_slicing_position :: 1]:
            val = self._data_from_hex(data0, is_signed)
            data_out.append(val)
        return data_out

    @property
    @abstractmethod
    def is_active(self) -> bool:
        """Checking if serial communication is open
        :return:    True if serial communication is open, False otherwise
        """
        ...

    @abstractmethod
    def do_reset(self) -> None:
        """Resetting actual definitions on the FPGA
        :return:    None
        """
        ...

    @abstractmethod
    def open_serial(self) -> None:
        """Closing the serial communication to device
        :return:    None
        """
        ...

    @abstractmethod
    def close_serial(self) -> None:
        """Opening the serial communication to device
        :return:    None
        """
        ...

    @abstractmethod
    def get_dut_config(self, num_target: int) -> ConfigurationDUT:
        """Function for calling the header configuration of implemented device on target device
        :param num_target:  Number of target device
        :return:            All DUT information for setting the test conditions
        """
        ...

    @abstractmethod
    def select_device_for_testing(self, num_dut: int) -> None:
        """Selecting the Device under Test (DUT) on target device
        :param num_dut: Number of DUT
        :return:        None
        """
        ...

    @abstractmethod
    def set_led_mcu(self, state: bool) -> None:
        """Setting the LED MCU state
        :param state:   True if LED MCU is on, False otherwise
        :return:        None
        """
        ...

    @abstractmethod
    def set_led_fpga(self, state: bool) -> None:
        """Setting the LED FPGA state
        :param state:   True if LED FPGA is on, False otherwise
        :return:        None
        """
        ...

    @abstractmethod
    def toggle_led_fpga(self) -> None:
        """Toggling the LED FPGA state
        :return:        None
        """
        ...

    @abstractmethod
    def do_inference(self, data: bytes) -> bytes:
        """Doing the inference from Computer to FPGA with sending data frame
        :param data:    Data with bytes to send
        :return:        Bytes with data from board
        """
        ...

    @abstractmethod
    def do_inference_empty(self, num_cycles: int) -> bytes:
        """Doing N cycles for empty inference from Computer to FPGA just to get last samples from experiment
        :param num_cycles:  Number of cycles to run
        :return:            Bytes with data from board
        """
        ...
