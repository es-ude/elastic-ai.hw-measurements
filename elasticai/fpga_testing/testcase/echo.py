from dataclasses import dataclass
import numpy as np
from matplotlib import pyplot as plt

from elasticai.fpga_testing.src.exp_dut import DeviceUnderTestHandler
from elasticai.fpga_testing.src.exp_runner import ExperimentMain
from elasticai.fpga_testing.src.plotting import get_color_plot, save_figure
from elasticai.fpga_testing.src.yaml_handler import YamlConfigHandler
from elasticai.fpga_testing.src.signal_generator import generate_sinusoidal_waveform


@dataclass
class SettingsEcho:
    sampling_rate: float
    freq_signal: float
    num_periods: int
    bitwidth_data: int
    signed_data: bool

    @property
    def get_data_in(self) -> np.ndarray:
        return generate_sinusoidal_waveform(f_sig=self.freq_signal, fs=self.sampling_rate, no_periods=self.num_periods,
                                            bitwidth=self.bitwidth_data, signed_out=self.signed_data)[1]

DefaultSettingsEcho = SettingsEcho(
    sampling_rate=2e3,
    freq_signal=1e1,
    num_periods=10,
    bitwidth_data=16,
    signed_data=False,
)


class ExperimentEcho(ExperimentMain):
    _device: DeviceUnderTestHandler
    __settings_echo: SettingsEcho
    __data_scaling_value: int

    def __init__(self, device_id: int) -> None:
        """Class for handling the Echo Function on device
        :param device_id: Integer value with device ID of test structure
        """
        super().__init__()
        self._type_experiment = '_echo'

        self.__header = self._device.get_dut_config(device_id)
        set = DefaultSettingsEcho
        set.bitwidth_data = self.get_bitwidth_data
        yaml_handler = YamlConfigHandler(set, yaml_name=f'Config_Echo{device_id:03d}', start_folder='python')
        self.__settings_echo = yaml_handler.get_class(SettingsEcho)
        self.__data_scaling_value = 2 ** (self._device.get_bitwidth_data - self.__settings_echo.bitwidth_data)

    @property
    def get_bitwidth_data(self) -> int:
        return self.__header['bit_output']

    @property
    def get_settings_func(self) -> SettingsEcho:
        return self.__settings_echo

    def preprocess_data(self, waveform: np.ndarray) -> None:
        """Preprocessing the data in order to have the data stream suitable for tested device (hex and data frame)"""
        self._buffer_data_send = self._device.slice_data_for_transmission(
            data=self._device.preparing_data_streaming_architecture(
                signal=waveform,
                bit_position_start=self.__data_scaling_value,
                is_signed=self.__settings_echo.signed_data
            )
        )

    def postprocess_data(self) -> np.ndarray:
        """Post-processing the data from device to have in readable format and numpy format"""
        data_return = self._device.slice_data_from_transmission(
            data=self._buffer_data_get,
            is_signed=self.__settings_echo.signed_data
        )
        return data_return / self.__data_scaling_value


def run_echo_on_target(device_id: int, block_plot: bool=False) -> None:
    """Function for running the echo server test on target device
    :param device_id:       Device ID (unsigned integer) for calling the right target on device
    :param block_plot:      Blocking and showing plot
    :return:                None
    """
    # --- Preparing Test
    exp0 = ExperimentEcho(device_id)
    settings_echo = exp0.get_settings_func

    # Control Routine
    exp0.init_experiment(f'{device_id:02d}')
    data_dut = {'process_time': [], 'data_in': [], 'data_out': []}

    data_used = settings_echo.get_data_in
    exp0.preprocess_data(waveform=data_used)
    time_run = exp0.do_inference(device_id)
    data_out = exp0.postprocess_data()

    # Saving results
    data_dut['process_time'].append(time_run)
    data_dut['data_in'].append(data_used)
    data_dut['data_out'].append(data_out)

    np.save(f'{exp0.get_path2run}/results_echo.npy', data_dut, allow_pickle=True)
    time0 = np.linspace(0, data_used.shape[0], data_used.shape[0], endpoint=False) / settings_echo.sampling_rate
    plot_transient(t0=time0, xin=data_used, xout=data_out, path=exp0.get_path2run, block_plot=block_plot, is_echo_test=True)


if __name__ == '__main__':
    run_echo_on_target(
        device_id=0,
        block_plot=True
    )


def plot_transient(t0: np.ndarray, xin: np.ndarray, xout: np.ndarray, path: str='', fsig: float=0.0, block_plot: bool=False, is_echo_test: bool=False) -> None:
    """Plotting the transient signals
    Args:
        t0:             Numpy array with transient timestamp
        xin:            Numpy array with transient signal which is transferred to device
        xout:           Numpy array with transient signal which returns from device
        path:           Path for saving the results
        fsig:           Signal frequency
        block_plot:     Blocking and showing plot
        is_echo_test:   Echo test
    Returns:
        None
    """
    plt.figure()

    if fsig:
        xpos0 = np.argwhere(t0 >= 1/fsig).flatten()[0]
        xpos1 = np.argwhere(t0 >= 5/fsig).flatten()[0]

        plt.plot(t0[xpos0:xpos1], xin[xpos0:xpos1], marker='.', markersize=4, color=get_color_plot(0), label='Input')
        plt.plot(t0[xpos0:xpos1], xout[xpos0:xpos1], marker='.', markersize=4, color=get_color_plot(1), label='Output')
    else:
        plt.plot(t0, xin, marker='.', markersize=4, color=get_color_plot(0), label='Input')
        plt.plot(t0, xout, marker='.', markersize=4, color=get_color_plot(1), label='Output')

    plt.xlabel('Time / s')
    plt.ylabel('X_y')
    if is_echo_test:
        plt.title(f'MAE of Echo Test: {np.sum(np.abs(xin - xout))}')
    plt.legend(loc='upper left')

    plt.grid()
    plt.tight_layout(pad=0.5)
    if path:
        save_figure(plt, path, f'transient_{int(fsig)}Hz')
    if block_plot:
        plt.show(block=True)
