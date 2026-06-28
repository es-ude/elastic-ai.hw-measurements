from dataclasses import dataclass
from enum import IntEnum


class ProtocolRegisterID(IntEnum):
    DUT_CNTRL = 0
    DUT_WR = 1
    DUT_RD = 2
    DUT_HEAD = 3


class ConfigurationID(IntEnum):
    Nothing = 0
    Echo = 1
    ROM_LUT = 2
    RAM = 3
    Math = 4
    Filters = 5
    EventWindower = 6
    CreatorDNN = 7
    ProcessingPipeline = 8


@dataclass
class ConfigurationDUT:
    """Dataclass with information from the active DUT structure
    Attributes:
        bitwidth_input:     Integer with bitwidth of input
        bitwidth_output:    Integer with bitwidth of output
        dut_type:           DUT ID of active selected structure
        num_duts:           Number of DUTs implemented on the device
        num_outputs:        number of output samples
        num_inputs:         number of input samples
    """

    bitwidth_input: int
    bitwidth_output: int
    dut_type: int
    num_duts: int
    num_outputs: int
    num_inputs: int

    @property
    def get_dut_name(self) -> str:
        return ConfigurationID(self.dut_type).name
