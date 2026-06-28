from .definitions import ConfigurationDUT, ConfigurationID


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
