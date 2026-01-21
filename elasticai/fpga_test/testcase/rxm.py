from dataclasses import dataclass
import numpy as np

from elasticai.creator_plugins.test_env.src.control_dut import DeviceUnderTestHandler
from elasticai.creator_plugins.test_env.src.yaml_handler import YamlConfigHandler
from elasticai.creator_plugins.test_env.testcase.handler import ExperimentMain
from elasticai.creator_plugins.test_env.src.plotting import plot_call


@dataclass
class SettingsRxM:
    num_repetitions: int
    bitwidth_rom: int
    adrwidth_rom: int
    signed_rom: bool

    @property
    def get_num_cycles(self) -> int:
        return self.num_repetitions * (2 ** self.adrwidth_rom)

DefaultSettingsRxM = SettingsRxM(
    num_repetitions=10,
    bitwidth_rom=16,
    adrwidth_rom=5,
    signed_rom=False,
)


class ExperimentROM(ExperimentMain):
    _device: DeviceUnderTestHandler
    __settings_rom: SettingsRxM
    __data_scaling_value: int

    def __init__(self, device_id: int) -> None:
        """Class for running the ROM/LUT test on target device
        Args:
            device_id:  Integer value with device ID of test structure
        Returns:
            None
        """
        super().__init__()
        self._type_experiment = '_rom_lut'

        self.__header = self._device.get_dut_config(device_id)
        set = DefaultSettingsRxM
        set.adrwidth_rom = self.get_adrwidth_structure
        set.bitwidth_rom = self.get_bitwidth_structure
        yaml_handler = YamlConfigHandler(set, yaml_name=f'Config_ROM{device_id:03d}', start_folder='python')
        self.__settings_rom = yaml_handler.get_class(SettingsRxM)
        self.__data_scaling_value = 2 ** (self._device.get_bitwidth_data - self.__settings_rom.bitwidth_rom)

    @property
    def get_adrwidth_structure(self) -> int:
        return int(np.ceil(np.log2(self.__header['num_output'])))

    @property
    def get_bitwidth_structure(self) -> int:
        return self.__header['bit_output']

    @property
    def get_settings_func(self) -> SettingsRxM:
        return self.__settings_rom

    def preprocess_data(self, num_samples: int) -> None:
        """Preprocessing the data in order to have the data stream suitable for tested device (hex and data frame)"""
        waveform_ana = np.zeros((num_samples, ), dtype=np.int32)
        self._buffer_data_send = self._device.slice_data_for_transmission(
            self._device.preparing_data_streaming_architecture(
                signal=waveform_ana,
                bit_position_start=self.__data_scaling_value,
                is_signed=self.__settings_rom.signed_rom
            )
        )

    def postprocess_data(self) -> np.ndarray:
        """Post-processing the data from device to have in readable format and numpy format"""
        data_return = self._device.slice_data_from_transmission(
            data=self._buffer_data_get,
            is_signed=self.__settings_rom.signed_rom
        )
        return data_return / self.__data_scaling_value


def run_rom_test_on_target(device_id: int, block_plot: bool=False) -> None:
    """Function for testing the ROM on target device (incl. call and plot results)
    :param device_id:   Integer value with device ID of test structure
    :param block_plot:  If true, plot blocks instead of lines
    :return: None
    """
    # --- Preparing Test
    exp0 = ExperimentROM(device_id=device_id)
    settings_test = exp0.get_settings
    settings_rom = exp0.get_settings_func

    # Control Routine
    data_dut = {'process_time': [], 'data_out': []}

    exp0.init_experiment()
    exp0.preprocess_data(settings_rom.get_num_cycles)
    time_run = exp0.do_inference(device_id)
    data_out = exp0.postprocess_data()

    # Saving results
    data_dut['process_time'].append(time_run)
    data_dut['data_out'].append(data_out)
    np.save(f'{exp0.get_path2run}/results_rom.npy', data_dut, allow_pickle=True)
    plot_call(data_out, exp0.get_path2run, block_plot=block_plot)
