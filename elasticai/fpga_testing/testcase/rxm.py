from dataclasses import dataclass
import numpy as np
from matplotlib import pyplot as plt

from elasticai.fpga_testing import get_path_to_project
from elasticai.fpga_testing.src.exp_dut import DeviceUnderTestHandler
from elasticai.fpga_testing.src.exp_runner import ExperimentMain
from elasticai.fpga_testing.src.plotting import get_color_plot, save_figure
from elasticai.fpga_testing.src.yaml_handler import YamlConfigHandler


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


class ExperimentRxM(ExperimentMain):
    _device: DeviceUnderTestHandler
    __settings_rom: SettingsRxM
    __data_scaling_value: int

    def __init__(self, device_id: int, use_ram: bool=False) -> None:
        """Class for running the ROM/LUT test on target device
        Args:
            device_id:  Integer value with device ID of test structure
        Returns:
            None
        """
        super().__init__()
        self._type_experiment = 'rom' if not use_ram else 'ram'

        self.__header = self._device.get_dut_config(device_id)
        set = DefaultSettingsRxM
        set.adrwidth_rom = self.get_adrwidth_structure
        set.bitwidth_rom = self.get_bitwidth_structure
        yaml_handler = YamlConfigHandler(set, yaml_name=f'Config_{self._type_experiment.upper()}{device_id:03d}', start_folder=get_path_to_project())
        self.__settings_rom = yaml_handler.get_class(SettingsRxM)
        self.__data_scaling_value = 2 ** (self._device.get_bitwidth_data - self.__settings_rom.bitwidth_rom)

    @property
    def get_adrwidth_structure(self) -> int:
        return int(np.ceil(np.log2(self.__header.num_outputs)))

    @property
    def get_bitwidth_structure(self) -> int:
        return self.__header.bitwidth_output

    @property
    def get_settings_func(self) -> SettingsRxM:
        return self.__settings_rom

    @property
    def get_low_bit(self) -> int:
        return 0 if not self.__settings_rom.signed_rom else -2**(self.__settings_rom.bitwidth_rom-1)

    @property
    def get_high_bit(self) -> int:
        return 2**self.__settings_rom.bitwidth_rom-1 if not self.__settings_rom.signed_rom else 2**(self.__settings_rom.bitwidth_rom-1)-1

    def preprocess_rom_data(self, num_samples: int) -> None:
        """Preprocessing the data in order to have the data stream suitable for tested device (hex and data frame)"""
        self._buffer_data_send = self._device.slice_data_for_transmission(
            self._device.preparing_data_calling_architecture(
                num_repeat=num_samples
            )
        )

    def preprocess_ram_data(self, adr_start: int=0) -> np.ndarray:
        """Preprocessing the data in order to have the data stream suitable for tested device (hex and data frame)"""
        waveform_ana = np.random.randint(
            low=self.get_low_bit,
            high=self.get_high_bit,
            size=(2**self.__settings_rom.adrwidth_rom-1-adr_start, ),
            dtype=np.int32
        )

        data_write_into_mem = self._device.preparing_data_memory_write_architecture(
            signal=waveform_ana,
            adr_start=0,
            bit_position_start=self.__data_scaling_value,
            is_signed=self.__settings_rom.signed_rom
        )
        data_read_from_mem = self._device.preparing_data_memory_read_architecture(
            signal=np.zeros_like(waveform_ana) + 1,
            adr_start=0,
            bit_position_start=self.__data_scaling_value,
            is_signed=self.__settings_rom.signed_rom
        )
        self._buffer_data_send = self._device.slice_data_for_transmission(data_write_into_mem + data_read_from_mem)
        return waveform_ana

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
    exp0 = ExperimentRxM(device_id=device_id, use_ram=False)
    settings_test = exp0.get_settings
    settings_rom = exp0.get_settings_func

    # Control Routine
    data_dut = {'process_time': [], 'data_out': []}

    exp0.init_experiment()
    exp0.preprocess_rom_data(settings_rom.get_num_cycles)
    time_run = exp0.do_inference(device_id)
    data_out = exp0.postprocess_data()

    # Saving results
    data_dut['process_time'].append(time_run)
    data_dut['data_out'].append(data_out)
    np.save(f'{exp0.get_path2run}/results_rom.npy', data_dut, allow_pickle=True)
    plot_call(data_out, exp0.get_path2run, block_plot=block_plot)


def run_ram_test_on_target(device_id: int, block_plot: bool=False) -> None:
    """Function for testing the RAM on target device (incl. call and plot results)
    :param device_id:   Integer value with device ID of test structure
    :param block_plot:  If true, plot blocks instead of lines
    :return: None
    """
    # --- Preparing Test
    exp0 = ExperimentRxM(device_id=device_id, use_ram=True)
    settings_test = exp0.get_settings
    settings_rom = exp0.get_settings_func

    # Control Routine
    data_dut = {'process_time': [], 'data_in': [], 'data_out': []}

    exp0.init_experiment()
    data_in = exp0.preprocess_ram_data(0)
    time_run = exp0.do_inference(device_id)
    data_out = exp0.postprocess_data()

    # Saving results
    data_dut['process_time'].append(time_run)
    data_dut['data_in'].append(data_in)
    data_dut['data_out'].append(data_out)
    np.save(f'{exp0.get_path2run}/results_ram.npy', data_dut, allow_pickle=True)

    plot_call(data_in, exp0.get_path2run, block_plot=False)
    plot_call(data_out, exp0.get_path2run, block_plot=block_plot)


def plot_call(xout: np.ndarray, path: str='', block_plot: bool=False) -> None:
    """Plotting the signals from calling the DUT
    Args:
        xout:           Numpy array with transient signal which returns from device
        path:           Path for saving the results
        block_plot:     Blocking and showing plot
    Returns:
        None
    """
    plt.figure()
    plt.plot(xout, marker='.', markersize=4, color=get_color_plot(0), label='Output')

    plt.xlim([0, xout.size])
    plt.xlabel('Call Iteration')
    plt.ylabel(r'X_${out}$')

    plt.grid()
    plt.tight_layout(pad=0.5)
    if path:
        save_figure(plt, path, f'call_lut')
    if block_plot:
        plt.show(block=True)
