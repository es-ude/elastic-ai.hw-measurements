from dataclasses import dataclass
import numpy as np
from elasticai.creator_plugins.test_env.src.control_dut import DeviceUnderTestHandler
from elasticai.creator_plugins.test_env.src.yaml_handler import YamlConfigHandler
from elasticai.creator_plugins.test_env.testcase.handler import ExperimentMain
from elasticai.creator_plugins.test_env.src.plotting import plot_arithmetic


@dataclass
class SettingsMult:
    input_size: int
    mode_input_same: bool
    mode_slow_calc: bool
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
    mode_input_same=False,
    mode_slow_calc=False,
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
        yaml_handler = YamlConfigHandler(set, yaml_name=f'Config_Mult{device_id:03d}', start_folder='python')
        self.__settings_mult = yaml_handler.get_class(SettingsMult)
        self.__data_scaling_input = 2 ** (self._device.get_bitwidth_data - self.get_bitwidth_input_structure)
        self.__data_scaling_output = 2 ** (self._device.get_bitwidth_data - self.get_bitwidth_output_structure)

    @property
    def get_num_input_structure(self) -> int:
        return self.__header['num_input']

    @property
    def get_bitwidth_input_structure(self) -> int:
        return self.__header['bit_input']

    @property
    def get_bitwidth_output_structure(self) -> int:
        return self.__header['bit_output']

    @property
    def get_settings_func(self) -> SettingsMult:
        return self.__settings_mult

    def get_data_output_reference(self, data: np.ndarray) -> np.ndarray:
        data_sym = np.array(data * data, dtype=int)
        data_asym = list()
        for val in data:
            data_asym.extend(val * data)
        return data_sym if self.__settings_mult.mode_input_same else np.array(data_asym, dtype=int)

    def preprocess_data(self, waveform: np.ndarray) -> None:
        """Preprocessing the data in order to have the data stream suitable for tested device (hex and data frame)"""
        self._buffer_data_send = self._device.slice_data_for_transmission(
            self._device.preparing_data_arithmetic_architecture(
                signal=waveform.tolist(),
                num_input_layer=self.__settings_mult.input_size,
                bit_position_start=self.__data_scaling_input,
                is_signed=self.__settings_mult.signed_data,
                mode_same_input=self.__settings_mult.mode_input_same,
                mode_slow=self.__settings_mult.mode_slow_calc
            )
        )

    def postprocess_data(self) -> np.ndarray:
        """Post-processing the data from device to have in readable format and numpy format"""
        data_return = self._device.slice_data_from_transmission(
            data=self._buffer_data_get,
            is_signed=self.__settings_mult.signed_data
        )

        pattern_repeat = 4
        pattern_period = 6 if not self.__settings_mult.mode_slow_calc else 4
        data_array = list()
        for idx in range(round(len(data_return) / pattern_period)):
            pos_start = pattern_repeat + idx * pattern_period
            pos_end = (idx + 1) * pattern_period
            data_array.append(data_return[pos_start:pos_end])

        data0 = np.array(data_array) / self.__data_scaling_output
        return np.mean(data0, dtype=int, axis=1)


def run_mult_on_target(device_id: int, block_plot: bool=False) -> None:
    """Function for running the echo server test on target device
    :param device_id:       Device ID (unsigned integer) for calling the right target on device
    :param data_in:         Numpy array with
    :param block_plot:      Blocking and showing plot
    :return:                None
    """
    # --- Preparing Test
    exp0 = ExperimentMult(device_id)
    settings_mult = exp0.get_settings_func

    # Control Routine
    exp0.init_experiment(f'{device_id:02d}')
    data_dut = {'process_time': [], 'data_in': [], 'data_out': [], 'data_ref': []}

    data_used = settings_mult.get_data
    exp0.preprocess_data(waveform=data_used)
    time_run = exp0.do_inference(device_id)
    data_out = exp0.postprocess_data()

    data_ref = exp0.get_data_output_reference(data_used)

    # Saving results
    data_dut['process_time'].append(time_run)
    data_dut['data_in'].append(data_used)
    data_dut['data_out'].append(data_out)
    data_dut['data_ref'].append(data_ref)

    np.save(f'{exp0.get_path2run}/results_mult.npy', data_dut, allow_pickle=True)
    plot_arithmetic(data_out, data_ref, path2save=exp0.get_path2run, block_plot=block_plot)

if __name__ == '__main__':
    run_mult_on_target(
        device_id=1,
        block_plot=True
    )
