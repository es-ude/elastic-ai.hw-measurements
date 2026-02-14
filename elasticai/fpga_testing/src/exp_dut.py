import numpy as np
from dataclasses import dataclass
from elasticai.fpga_testing.src.interface_serial import HandlerUSB


@dataclass
class ConfigurationDUT:
    bitwidth_input: int
    bitwidth_output: int
    dut_type: int
    num_duts: int
    num_outputs: int
    num_inputs: int


class DeviceUnderTestHandler:
    def __init__(self, com_port: str="AUTOCOM", buffer_size:int=10, baudrate: int=115200) -> None:
        """Class for handling the FPGA for testing different digital accelerators (enabling System-Tests)
        Args:
            com_port:       String with COM Port / device name
            buffer_size:    Number of packet bytes for collecting data for serial communication in each way [Default: 10]
            baudrate:       Integer with Baudrate for UART communication [Default: 115.200]
        :returns:
            None
        """
        self.__bitwidth_cmds = 2
        self.__bitwidth_adr = 6
        self.__bitwidth_data = 16

        self.__bytes_frame_head = int((self.__bitwidth_cmds + self.__bitwidth_adr) / 8)
        self.__bytes_frame_data = int(self.__bitwidth_data / 8)
        self.__bytes_frame_total = self.__bytes_frame_head + self.__bytes_frame_data
        self.__buffer_size = buffer_size
        self.__device = HandlerUSB(
            com_name=com_port,
            baud=baudrate,
            buffer_bytesize=self.__bytes_frame_total
        )

        # --- Protocol Header
        self.__START_SLICING_POSITION = 3
        self.__REG_DUT_CNTRL = 0
        self.__REG_DUT_WR = 1
        self.__REG_DUT_RD = 2
        self.__REG_DUT_HEAD = 3

        # --- DUT Device Number
        self._device_types = {
            0: 'EchoClient',
            1: 'Multiplier',
            2: 'Division',
            3: 'ROM/LUT',
            4: 'RAM',
            5: 'Filter Stages',
            6: 'Processing Pipeline',
            7: 'Creator (DNN)'
        }

    @property
    def get_bitwidth_data(self) -> int:
        return self.__bitwidth_data

    def get_device_type(self, device_id: int) -> str:
        out_type = self._device_types.get(device_id)
        print(out_type)
        return out_type

    @property
    def is_open(self) -> bool:
        """Checking if serial communication is open"""
        return self.__device.com_port_active

    def open_serial(self) -> None:
        """Open a serial communication to device"""
        if self.__device.com_port_active:
            self.__device.close()
        self.__device.open()


    def close_serial(self) -> None:
        """Close a serial communication from device"""
        if self.__device.com_port_active:
            self.__device.close()

    # --------------------------------------- FUNCTIONS FOR HANDLING DEVICE ---------------------------------
    def _get_bytes_dut_selection(self, device_id: int) -> bytes:
        return self.data_to_hex(self.__REG_DUT_CNTRL, 2, device_id<<1, False)

    def select_device_for_testing(self, device_id: int) -> None:
        """Function for selecting the Device under Test (DUT) on target device
        :return:        None
        """
        data = self._get_bytes_dut_selection(device_id)
        self.__device.write_wofb(data)

    def do_led_control(self, state: bool) -> None:
        """Controlling the LED on FPGA using led_state
        :param state:    State of the LED
        :return:        None
        """
        data = self.data_to_hex(self.__REG_DUT_CNTRL, 4, int(state), False)
        self.__device.write_wofb(data)

    def do_led_toggle(self) -> None:
        """Toggling the LED on Board
        :return:        None
        """
        data = self.data_to_hex(self.__REG_DUT_CNTRL, 8, 0, False)
        self.__device.write_wofb(data)

    def do_test_trial(self) -> None:
        """Starting test trial on selected dut
        :return:        None
        """
        data = self.data_to_hex(self.__REG_DUT_CNTRL, 1, 0, False)
        self.__device.write_wfb(data)

    def do_inference(self, data: bytes) -> bytes:
        """Doing the inference from Computer to FPGA with sending data frame
        :return:        Bytes with data from board
        """
        return self.__device.write_wfb(data)

    def do_inference_delay(self, num_cycles:int=2) -> bytes:
        """Doing the inference from Computer to FPGA just to get last samples from experiment
        :return:        Bytes with data from board
        """
        result = bytes()
        for cycle in range(num_cycles):
            result += self.__device.write_wfb_hex(0, 0)
        return result

    # --------------------------------------- FUNCTIONS FOR GETTING HEADER INFORMATION ---------------------------------
    def get_dut_config(self, sel_target: int) -> ConfigurationDUT:
        """Function for calling the header configuration of implemented device on target device"""
        self.__device.empty_input_buffer()
        data_send = bytes()
        data_send += self._get_bytes_dut_selection(sel_target)
        data_send += self.data_to_hex(self.__REG_DUT_HEAD, 1, False)
        data_send += self.data_to_hex(self.__REG_DUT_HEAD, 0, False)
        data_send += self.data_to_hex(0, 0, False)

        data_fb0 = self.slice_data_to_packet_size(self.__device.write_wfb(data_send))[2:]
        data_head = bytes()
        for data in data_fb0:
            data_head += data[1:]
        return self.__process_dut_config(int.from_bytes(data_head, byteorder='big'))

    @staticmethod
    def __process_dut_config(data: int) -> ConfigurationDUT:
        return ConfigurationDUT(
            num_duts=(data & 0xFC00_0000) >> 26,
            dut_type=(data & 0x03C0_0000) >> 22,
            num_inputs=(data & 0x003F_0000) >> 16,
            num_outputs=(data & 0x0000_FC00) >> 10,
            bitwidth_input=(data & 0x0000_03E0) >> 5,
            bitwidth_output=(data & 0x0000_001F) >> 0,
        )

    def get_dut_config_all(self, print_results: bool = True) -> dict:
        """Loading the header information of each implemented test device (skeleton) on target device
        :param print_results:   Printing the results of each test device
        :returns:               Dict with Dataclass with ConfigurationDUT ['num_duts', 'dut_type', 'num_input', 'num_output', 'bit_input', 'bit_output']
        """
        config0 = self.get_dut_config(0)

        dict_config = dict()
        for idx in range(config0.num_duts+1):
            dict_config.update({f'dev{idx:02d}': self.get_dut_config(idx)})
        if print_results:
            self.__print_dict_config(dict_config)
        return dict_config

    @staticmethod
    def __print_dict_config(config: dict) -> None:
        print('\nAvailable DUTs on Target:\n=====================================')
        for idx, config in enumerate(config.values()):
            print(f'Properties of DUT #{idx:02d}:')
            for key, value in config.items():
                print(f'\t{key}: {value}')

    # -------------------------------------------- FUNCTIONS FOR DATA TRANSFORMATION ------------------------------------------
    def data_to_hex(self, reg: int, adr: int, data: int, is_signed: bool=False) -> bytes:
        """Processing hex data for device
        Args:
            reg:        Value for selecting Register (2 bit)
            adr:        Value for selecting address (6 bit)
            data:       Value for data (16 bit)
            is_signed:  Signed data structure
        """
        head = int(bin(reg)[2:].zfill(self.__bitwidth_cmds) + bin(adr)[2:].zfill(self.__bitwidth_adr), 2)
        out = head.to_bytes(self.__bytes_frame_head, 'big')
        out0 = int(data).to_bytes(self.__bytes_frame_data, 'big', signed=is_signed)
        return out + out0

    def data_from_hex(self, data: bytes, is_signed: bool) -> int:
        """Processing hex data from device"""
        val = data[self.__bytes_frame_head:]
        return int.from_bytes(val, byteorder='big', signed=is_signed)

    # -------------------------------------------- FUNCTIONS FOR SLICING DATA ------------------------------------------
    @property
    def get_slicing_position(self) -> int:
        """Getting the number to start slicing data due to delay in data transmission"""
        return self.__START_SLICING_POSITION

    def slice_data_for_transmission(self, data: bytes) -> list[int | bytes]:
        """Preparing the data stream to FPGA by converting the numpy input"""
        buffer_to_send = list()
        no_of_repetitions = int(np.ceil(len(data) / self.__buffer_size))
        for rep in range(0, no_of_repetitions):
            buffer_to_send.append(data[rep * self.__buffer_size: (rep + 1) * self.__buffer_size])
        return buffer_to_send

    def slice_data_from_transmission(self, data: bytes, is_signed: bool, stepsize: int=1) -> np.ndarray:
        """Slicing the data from FPGA and transfer it into numpy format"""
        data_sliced = self.slice_data_to_packet_size(data=data)
        data_out = list()
        for data in data_sliced[self.get_slicing_position*stepsize::stepsize]:
            val = self.data_from_hex(data, is_signed)
            data_out.append(val)

        data_out = np.array(data_out, dtype=int)
        return data_out

    def slice_data_to_packet_size(self, data: bytes) -> list:
        """Slicing the data bytes from FPGA into list"""
        data_sliced = list()
        for i in range(0, len(data), self.__bytes_frame_total):
            data_sliced.append(data[i:i + self.__bytes_frame_total])
        return data_sliced

    # -------------------------------------------- FUNCTIONS FOR TESTING ------------------------------------------
    def preparing_data_streaming_architecture(self, signal: np.ndarray, bit_position_start: int, is_signed: bool = False) -> bytes:
        """Preparing the data stream to FPGA by converting the numpy input (1:1)"""
        data = bytes()
        self.__device.empty_input_buffer()
        for val in signal:
            data += self.data_to_hex(reg=self.__REG_DUT_WR, adr=0, data=val * bit_position_start, is_signed=is_signed)
            data += self.data_to_hex(reg=self.__REG_DUT_CNTRL, adr=1, data=0, is_signed=False)
        data += self.data_to_hex(reg=0, adr=0, data=0, is_signed=False)
        data += self.data_to_hex(reg=0, adr=0, data=0, is_signed=False)
        return data

    def preparing_data_calling_architecture(self, num_repeat: int) -> bytes:
        """Preparing the data stream to FPGA by converting the numpy input (1:1)"""
        data = bytes()
        self.__device.empty_input_buffer()
        data += self.data_to_hex(reg=self.__REG_DUT_WR, adr=0, data=1, is_signed=False)
        for val in range(num_repeat):
            data += self.data_to_hex(reg=self.__REG_DUT_CNTRL, adr=1, data=1, is_signed=False)
        data += self.data_to_hex(reg=0, adr=0, data=0, is_signed=False)
        data += self.data_to_hex(reg=0, adr=0, data=0, is_signed=False)
        return data

    def preparing_data_memory_write_architecture(self, signal: np.ndarray, adr_start: int, bit_position_start: int, is_signed: bool = False) -> bytes:
        """Preparing the data stream to FPGA by converting the numpy input (1:1)"""
        data = bytes()
        for ite, val in enumerate(signal):
            data += self.data_to_hex(reg=self.__REG_DUT_WR, adr=adr_start + ite, data=val * bit_position_start, is_signed=is_signed)
        return data

    def preparing_data_memory_read_architecture(self, signal: np.ndarray, adr_start: int, bit_position_start: int,
                                              is_signed: bool=False) -> bytes:
        """Preparing the data stream to FPGA by converting the numpy input (1:1)"""
        data = bytes()
        for ite, val in enumerate(signal):
            data += self.data_to_hex(reg=self.__REG_DUT_RD, adr=adr_start+ite, data=val*bit_position_start, is_signed=is_signed)
        data += self.data_to_hex(reg=0, adr=0, data=0, is_signed=False)
        return data

    def preparing_data_creator_architecture(self, signal: list, num_input_layer: int, num_output_layer: int,
                                            bit_position_start: int, is_signed: bool=False) -> bytes:
        """Preparing the data stream to FPGA by converting the numpy input"""
        # --- Data Input
        data = bytes()
        for idx, val in enumerate(signal):
            data += self.data_to_hex(reg=self.__REG_DUT_WR, adr=18+(idx % num_input_layer), data=val*bit_position_start, is_signed=is_signed)
            if (idx % num_input_layer == num_input_layer - 1):
                data += self.data_to_hex(reg=self.__REG_DUT_WR, adr=16, data=bit_position_start, is_signed=False)
                data += self.data_to_hex(reg=self.__REG_DUT_WR, adr=16, data=0, is_signed=False)
                for idy in range(num_output_layer):
                    data += self.data_to_hex(reg=self.__REG_DUT_RD, adr=18+idy, data=0, is_signed=False)
        return data

    def preparing_data_arithmetic_architecture(self, signal: list, num_input_layer: int,
                                               bit_position_start: int, is_signed: bool=False,
                                               mode_same_input: bool=False, mode_slow: bool=False) -> bytes:
        """Preparing the data stream to FPGA by converting the numpy input"""
        # --- Data Input
        data = bytes()
        num_repeats_call = 2 if mode_slow else 1
        if mode_same_input:
            for val in signal:
                # --- Sending data
                for idy in range(num_input_layer):
                    data += self.data_to_hex(reg=self.__REG_DUT_WR, adr=idy, data=val*bit_position_start, is_signed=is_signed)
                # --- Do pipelined calculation
                for idy in range(num_repeats_call):
                    data += self.data_to_hex(reg=self.__REG_DUT_CNTRL, adr=1, data=0, is_signed=False)
                # --- Getting the value
                for idy in range(num_repeats_call):
                    data += self.data_to_hex(reg=self.__REG_DUT_CNTRL, adr=0, data=0, is_signed=False)
        else:
            for valx in signal:
                for valy in signal:
                    # --- Sending data
                    data += self.data_to_hex(reg=self.__REG_DUT_WR, adr=0, data=valx*bit_position_start, is_signed=is_signed)
                    data += self.data_to_hex(reg=self.__REG_DUT_WR, adr=1, data=valy*bit_position_start, is_signed=is_signed)
                    # --- Do pipelined calculation
                    for idz in range(2):
                        data += self.data_to_hex(reg=self.__REG_DUT_CNTRL, adr=1, data=0, is_signed=False)
                    # --- Getting the value
                    for idz in range(2):
                        data += self.data_to_hex(reg=self.__REG_DUT_CNTRL, adr=0, data=0, is_signed=False)
        return data

    def preparing_data_reading_skeleton_id(self, length: int=16) -> bytes:
        """Function for preparing reading ID from skeleton"""
        data = bytes()
        for idx in range(length):
            data += self.data_to_hex(reg=self.__REG_DUT_RD, adr=idx, data=0, is_signed=False)
        return data
