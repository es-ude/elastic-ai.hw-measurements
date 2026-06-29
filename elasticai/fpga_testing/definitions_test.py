from .definitions import ConfigurationDUT, ConfigurationID, ProtocolBitwidth


def test_configuration_dut() -> None:
    dut = ConfigurationDUT(
        bitwidth_input=12,
        bitwidth_output=12,
        dut_type=ConfigurationID.Echo,
        num_duts=2,
        num_inputs=1,
        num_outputs=1,
    )
    rslt = dut.get_dut_name
    assert rslt == "Echo"


def test_protocol_bitwidth_total_bytes() -> None:
    rslt = ProtocolBitwidth().bytes_total
    assert rslt == 3


def test_protocol_bitwidth_data_bytes() -> None:
    rslt = ProtocolBitwidth().bytes_data
    assert rslt == 2


def test_protocol_bitwidth_data_head() -> None:
    rslt = ProtocolBitwidth().bytes_head
    assert rslt == 1
