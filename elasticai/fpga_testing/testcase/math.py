from dataclasses import dataclass
import numpy as np
from matplotlib import pyplot as plt

from elasticai.fpga_testing import get_path_to_project
from elasticai.fpga_testing.src.exp_dut import DeviceUnderTestHandler
from elasticai.fpga_testing.src.exp_runner import ExperimentMain
from elasticai.fpga_testing.src.plotting import get_color_plot, save_figure
from elasticai.fpga_testing.src.yaml_handler import YamlConfigHandler


@dataclass
class SettingsMult:
    input_size: int
    bitwidth_data: int
    step_size: int
    signed_data: bool

    @property
    def generate_data_unsigned(self) -> np.ndarray:
        return np.linspace(start=0, stop=(2 ** self.bitwidth_data) - 1, num=int((2 ** self.bitwidth_data) / self.step_size), endpoint=True, dtype=int)

    @property
    def generate_data_signed(self) -> np.ndarray:
        return self.generate_data_unsigned - 2**(self.bitwidth_data - 1)

    @property
    def get_data(self) -> np.ndarray:
        return self.generate_data_signed if self.signed_data else self.generate_data_unsigned


DefaultSettingsMult = SettingsMult(
    input_size=2,
    bitwidth_data = 8,
    step_size=8,
    signed_data=True
)


class ExperimentMult(ExperimentMain):
    _device: DeviceUnderTestHandler
    __settings_mult: SettingsMult
    __data_scaling_input: int
    __data_scaling_output: int

    def __init__(self, device_id: int) -> None:
        """Class for handling the Echo Function on device
        :param device_id: Integer value with device ID of test structure
        """
        super().__init__()
        self._type_experiment = '_mult'

        self.__header = self._device.get_dut_config(device_id)
        set = DefaultSettingsMult
        set.input_size = self.get_num_input_structure
        set.bitwidth_data = self.get_bitwidth_input_structure
        yaml_handler = YamlConfigHandler(set, yaml_name=f'Config_{device_id:03d}_Math', start_folder=get_path_to_project())
        self.__settings_mult = yaml_handler.get_class(SettingsMult)
        self.__data_scaling_input = 2 ** (self._device.get_bitwidth_data - self.get_bitwidth_input_structure)
        self.__data_scaling_output = 2 ** (self._device.get_bitwidth_data - self.get_bitwidth_output_structure)

    @property
    def get_num_input_structure(self) -> int:
        return self.__header.num_inputs

    @property
    def get_bitwidth_input_structure(self) -> int:
        return self.__header.bitwidth_input

    @property
    def get_bitwidth_output_structure(self) -> int:
        return self.__header.bitwidth_output

    @property
    def get_settings_func(self) -> SettingsMult:
        return self.__settings_mult

    def get_data_input(self, data: np.ndarray) -> np.ndarray:
        match self.get_num_input_structure:
            case 1:
                data_asym = [[x] for x in data]
            case 2:
                data_asym = [[x, y] for x in data for y in data]
            case _:
                data_asym = list()
        return np.array(data_asym, dtype=int)

    def get_data_output_reference(self, data: np.ndarray) -> np.ndarray:
        match self.get_num_input_structure:
            case 1:
                data_asym = data.tolist()
            case 2:
                data_asym = [x for val in data for x in (val * data)]
            case _:
                data_asym = list()
        return np.array(data_asym, dtype=int)

    def preprocess_data(self, waveform: np.ndarray) -> None:
        """Preprocessing the data in order to have the data stream suitable for tested device (hex and data frame)"""
        self._buffer_data_send = self._device.slice_data_for_transmission(
            self._device.preparing_data_arithmetic_architecture(
                signal=waveform.tolist(),
                bit_position_start=self.__data_scaling_input,
                is_signed=self.__settings_mult.signed_data
            )
        )

    def postprocess_data(self) -> np.ndarray:
        """Post-processing the data from device to have in readable format and numpy format"""
        data_return = self._device.slice_data_from_transmission(
            data=self._buffer_data_get,
            is_signed=self.__settings_mult.signed_data,
            stepsize=1
        )
        return data_return[1+self.get_num_input_structure::1+self.get_num_input_structure] / self.__data_scaling_output


def run_math_on_target(device_id: int, block_plot: bool=False) -> None:
    """Function for running the echo server test on target device
    :param device_id:       Device ID (unsigned integer) for calling the right target on device
    :param block_plot:      Blocking and showing plot
    :return:                None
    """
    # --- Preparing Test
    exp0 = ExperimentMult(device_id)
    settings_math = exp0.get_settings_func

    # Control Routine
    exp0.init_experiment(f'{device_id:02d}')
    data_dut = {'process_time': [], 'data_in': [], 'data_out': [], 'data_ref': []}

    data_used = settings_math.get_data
    data_in = exp0.get_data_input(data_used)
    data_ref = exp0.get_data_output_reference(data_used)

    exp0.preprocess_data(waveform=data_in)
    time_run = exp0.do_inference(device_id)
    data_out = exp0.postprocess_data()

    # Saving results
    data_dut['process_time'].append(time_run)
    data_dut['data_in'].append(data_used)
    data_dut['data_out'].append(data_out)
    data_dut['data_ref'].append(data_ref)

    np.save(f'{exp0.get_path2run}/results_math.npy', data_dut, allow_pickle=True)
    plot_mult_arithmetic(data_out, data_ref, path2save=exp0.get_path2run, block_plot=block_plot)


def plot_mult_arithmetic(data_out: np.ndarray, data_ref: np.ndarray,
                         path2save: str='', block_plot: bool=False) -> None:
    """Function for plotting the arithmetic test results
    :param data_out:    Numpy array with output values
    :param data_ref:    Numpy array with reference values
    :param path2save:   Path for saving the results
    :param block_plot:  Blocking and showing plot
    :return:            None
    """
    plt.figure()
    plt.plot(data_ref, data_out, marker='.', linestyle='None', color=get_color_plot(0))
    plt.xlabel(r'Digital Input $x$')
    plt.ylabel(r'Digital Output $y$')

    mae = np.sum(np.abs(data_out - data_ref)) / data_ref.size
    plt.title(f'MAE = {mae:.4f}')

    plt.grid(True)
    plt.tight_layout(pad=0.5)
    if path2save:
        save_figure(plt, path2save, 'arith_test')
    if block_plot:
        plt.show(block=True)
