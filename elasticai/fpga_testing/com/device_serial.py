from elasticai.fpga_testing.com.interface_serial import HandlerUSB
from elasticai.fpga_testing.definitions import ConfigurationDUT
from elasticai.fpga_testing.runner.interface_runner import InterfaceRunner


class DeviceSerial(InterfaceRunner):
    def __init__(self, com_port: str = "AUTOCOM") -> None:
        super().__init__(com_port=com_port, num_delay_messages=3)
        self.__device = HandlerUSB(com_name=com_port, baud=115200, buffer_bytesize=self._bits.bytes_total)

    @property
    def is_active(self) -> bool:
        return self.__device.com_port_active

    def do_reset(self) -> None:
        pass

    def open_serial(self) -> None:
        if self.__device.com_port_active:
            self.__device.close()
        self.__device.open()

    def close_serial(self) -> None:
        if self.__device.com_port_active:
            self.__device.close()

    def select_device_for_testing(self, num_dut: int) -> None:
        data = self._get_bytes_dut_selection(num_dut)
        self.__device.write_wofb(data)

    def get_dut_config(self, num_target: int) -> ConfigurationDUT:
        self.__device.empty_input_buffer()
        data_send = bytes()
        data_send += self._get_bytes_dut_selection(num_target)
        data_send += self._data_to_hex(self._cmds.Header, 1, 0, False)
        data_send += self._data_to_hex(self._cmds.Header, 0, 0, False)
        data_send += self._data_to_hex(self._cmds.Header, 0, 0, False)

        data_fb0 = self.slice_data_to_packet_size(self.__device.write_wfb(data_send))
        data_head = [self._data_from_hex(val, is_signed=False) for val in data_fb0[1:]]
        val = int.from_bytes(bytes(data_head), byteorder="big", signed=False)
        return self._process_dut_config(val)

    def set_led_mcu(self, state: bool) -> None:
        pass

    def set_led_fpga(self, state: bool) -> None:
        data = self._data_to_hex(self._cmds.Control, 4, int(state), False)
        self.__device.write_wofb(data)

    def toggle_led_fpga(self) -> None:
        data = self._data_to_hex(self._cmds.Control, 8, 0, False)
        self.__device.write_wofb(data)

    def do_inference(self, data: bytes) -> bytes:
        return self.__device.write_wfb(data)

    def do_inference_empty(self, num_cycles: int = 2) -> bytes:
        result = bytes()
        for cycle in range(num_cycles):
            result += self.__device.write_wfb_hex(0, 0)
        return result
