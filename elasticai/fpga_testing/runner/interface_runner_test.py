import pytest

from .interface_runner import ConfigurationDUT, InterfaceRunner, ProtocolRegisterID


class DummyRunner(InterfaceRunner):
    def __init__(self, com_port: str = "AUTOCOM") -> None:
        super().__init__(com_port, num_delay_messages=0)
        self._active = False

    @property
    def is_active(self) -> bool:
        return self._active

    def do_reset(self) -> None:
        self._active = False

    def open_serial(self) -> None:
        self._active = True

    def close_serial(self) -> None:
        self._active = False

    def get_dut_config(self, num_target: int) -> ConfigurationDUT:
        return ConfigurationDUT(
            bitwidth_input=16, bitwidth_output=8, dut_type=1, num_duts=1, num_inputs=1, num_outputs=1
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
        return bytes(data)

    def do_inference_empty(self, num_cycles: int) -> bytes:
        val = bytes()
        for _ in range(num_cycles):
            val += b"dly"
        return val


@pytest.mark.parametrize("value, expected", [(1, 2**15), (15, 2**1)])
def test_get_scaling_value(value: int, expected: int) -> None:
    rslt = DummyRunner()._get_data_scaling_value(value)
    assert rslt == expected


@pytest.mark.parametrize("value", [0, 18])
def test_get_scaling_value_outofrange(value: int) -> None:
    try:
        DummyRunner()._get_data_scaling_value(value)
    except ValueError:
        assert True
    else:
        assert False


def test_dut_selection() -> None:
    rslt = DummyRunner()._get_bytes_dut_selection(device_id=1)
    assert rslt == b"\x02\x00\x02"


def test_data_to_hex() -> None:
    rslt = DummyRunner()._data_to_hex(
        reg=ProtocolRegisterID.Header,
        adr=10,
        data=2,
        is_signed=True,
    )
    assert rslt == b"\xca\x00\x02"


def test_data_from_hex() -> None:
    rslt = DummyRunner()._data_from_hex(
        data=b"\xca\x00\x02",
        is_signed=True,
    )
    assert rslt == 2


def test_prozess_configuration_dut() -> None:
    rslt = DummyRunner()._process_dut_config(2**26 + 923152)
    assert rslt == ConfigurationDUT(
        num_duts=1, dut_type=0, num_inputs=14, num_outputs=5, bitwidth_input=16, bitwidth_output=16
    )


def test_do_reset() -> None:
    dut = DummyRunner()
    dut.do_reset()
    assert not dut.is_active


def test_serial_is_available():
    dut = DummyRunner()
    dut.open_serial()
    assert dut.is_active
    dut.close_serial()
    assert not dut.is_active


def test_enable_disable_led():
    DummyRunner().set_led_fpga(True)
    DummyRunner().set_led_fpga(False)


def test_toggle_led():
    for _ in range(2):
        DummyRunner().toggle_led_fpga()


def test_get_slicing_position() -> None:
    rslt = DummyRunner().get_slicing_position
    assert rslt == 0


def test_slice_data_to_packetsize() -> None:
    data = bytes([val for val in range(12)])
    chck = [b"\x00\x01\x02", b"\x03\x04\x05", b"\x06\x07\x08", b"\t\n\x0b"]
    rslt = DummyRunner().slice_data_to_packet_size(
        data=data,
    )
    assert rslt == chck


def test_slice_data_for_transmit() -> None:
    data = bytes([val for val in range(15)])
    chck = [b"\x00\x01\x02\x03\x04\x05", b"\x06\x07\x08\t\n\x0b", b"\x0c\r\x0e"]
    rslt = DummyRunner().slice_data_for_transmission(
        data=data,
    )
    assert rslt == chck


def test_do_inference() -> None:
    data = bytes([val for val in range(15)])
    rslt = DummyRunner().do_inference(
        data=data,
    )
    assert rslt == data


@pytest.mark.parametrize("value", [0, 1, 2, 100])
def test_do_inference_empty(value: int) -> None:
    ref = DummyRunner().do_inference_empty(1)

    rslt = DummyRunner().do_inference_empty(
        num_cycles=value,
    )
    chck = value * ref
    assert rslt == chck


def test_slice_data_from_transmit() -> None:
    data = bytes([val for val in range(12)])
    chck = [258, 1029, 1800, 2571]
    rslt = DummyRunner().slice_data_from_transmission(data=data, is_signed=True)
    assert rslt == chck
