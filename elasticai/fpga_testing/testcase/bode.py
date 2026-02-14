from dataclasses import dataclass
import numpy as np
from matplotlib import pyplot as plt
from scipy import signal as scft
from scipy.signal import find_peaks

from elasticai.fpga_testing import get_path_to_project
from elasticai.fpga_testing.src.exp_dut import DeviceUnderTestHandler
from elasticai.fpga_testing.src.exp_runner import ExperimentMain
from elasticai.fpga_testing.src.plotting import get_color_plot, save_figure
from elasticai.fpga_testing.src.signal_generator import generate_sinusoidal_waveform, generate_noise
from elasticai.fpga_testing.src.yaml_handler import YamlConfigHandler


@dataclass
class SettingsBode:
    # Parameters for Sweep
    sampling_rate: float
    freq_start: float
    freq_stop: float
    total_steps: int
    num_iterations_period: int
    bitwidth_filter: int
    signed_data: bool
    # Parameters for Reference Filter Design
    ref_filter_apply: bool
    ref_filter_order: int
    ref_filter_iir: bool
    ref_filter_corner: list
    ref_filter_ftype: str
    ref_filter_btype: str
    # Plot Options
    plot_transient: bool

    @property
    def get_frequency_range_log(self) -> list:
        return [float(np.log10(self.freq_start)), float(np.log10(self.freq_stop))]


DefaultSettingsBode = SettingsBode(
    sampling_rate=2e3,
    freq_start=1e1,
    freq_stop=1e3,
    total_steps=11,
    num_iterations_period=10,
    bitwidth_filter=16,
    signed_data=True,
    ref_filter_apply=True,
    ref_filter_order = 2,
    ref_filter_iir=True,
    ref_filter_corner=[100],
    ref_filter_ftype='butter',
    ref_filter_btype='low',
    plot_transient=True
)


class ExperimentBode(ExperimentMain):
    _device: DeviceUnderTestHandler
    __settings_bode: SettingsBode
    __data_scaling_value: int

    def __init__(self, device_id: int) -> None:
        """Class for handling the Experiment Setup for extracting the Bode Diagram of filter/amplifier circuits
        :param device_id:   Integer value with device ID of test structure
        """
        super().__init__()
        self._type_experiment = '_bode'

        self.__header = self._device.get_dut_config(device_id)
        set = DefaultSettingsBode
        set.bitwidth_filter = self.get_bitwidth_filter
        yaml_handler = YamlConfigHandler(set, yaml_name=f'Config_Bode{device_id:03d}', start_folder=get_path_to_project())
        self.__settings_bode = yaml_handler.get_class(SettingsBode)
        self.__data_scaling_value = 2 ** (self._device.get_bitwidth_data - self.__settings_bode.bitwidth_filter)

    @property
    def get_bitwidth_filter(self) -> int:
        return self.__header.bitwidth_output

    @property
    def get_settings_func(self) -> SettingsBode:
        return self.__settings_bode

    def generate_sinusoidal_signal(self, f_sig: float, no_periods: int=10, sigma_noise=0.0) -> tuple[np.ndarray, np.ndarray]:
        """Generating a Numpy array with sinusoidal waveform and time vector for testing
        Args:
            f_sig:          Target frequency
            no_periods:     Number of periods for testing
            sigma_noise:    Noise distribution (if 0.0 then disabled)
        Return:
            Two numpy arrays (time and signal)
        """
        discrete_time, data_signal = generate_sinusoidal_waveform(
            f_sig=f_sig,
            fs=self.__settings_bode.sampling_rate,
            no_periods=no_periods,
            bitwidth=self.__settings_bode.bitwidth_filter,
            signed_out=self.__settings_bode.signed_data
        )
        if sigma_noise > 0.0:
            data_signal += generate_noise(
                time=discrete_time,
                sigma=sigma_noise,
                bit=self.__settings_bode.bitwidth_filter
            )
        return discrete_time, data_signal

    def preprocess_data(self, f_sig: float, no_periods: int, sigma_noise=0.0, is_signed=False) -> dict:
        """Preprocessing the data in order to have the data stream suitable for tested device (hex and data frame)"""

        time, waveform_ana = self.generate_sinusoidal_signal(f_sig, no_periods, sigma_noise)
        self._buffer_data_send = self._device.slice_data_for_transmission(
            self._device.preparing_data_streaming_architecture(
                signal=waveform_ana,
                bit_position_start=self.__data_scaling_value,
                is_signed=is_signed
            )
        )
        return {'t': time, 'wvf': waveform_ana}

    def postprocess_data(self) -> np.ndarray:
        """Post-processing the data from device to have in readable format and numpy format"""
        data_return = self._device.slice_data_from_transmission(
            data=self._buffer_data_get,
            is_signed=self.__settings_bode.signed_data
        )
        return data_return / self.__data_scaling_value

    def extract_gain_phase(self, f_sig: float, xin: np.ndarray, xout: np.ndarray, start_period=3) -> tuple[float, float]:
        """Extracting Gain und Phase from two transient signal (original and feedback from device)
        Args:
            f_sig:          Frequency of target waveform
            xin:            Transient signal from original input
            xout:           Transient signal get from device
            start_period:   Number of period to start processing
        Return:
            Two floating values with Gain (dB) and Phase (°)
        """
        # --- Cutting signals to specific time range
        start_look = round(start_period * self.__settings_bode.sampling_rate / f_sig) - 1
        end_look = round(self.__settings_bode.sampling_rate / f_sig) - 1
        xin0 = xin[start_look:-end_look]
        xout0 = xout[start_look:-end_look]

        # --- Calculation of total amplitudes
        in_max = np.max(xin0)
        in_min = np.min(xin0)
        out_max = np.max(xout0)
        out_min = np.min(xout0)

        # --- Calculation of total delay
        dly0 = []
        period_length = round(0.5 * self.__settings_bode.sampling_rate / f_sig)
        x0 = find_peaks(xin0, distance=period_length)[0]
        x1 = find_peaks(xout0, distance=period_length)[0]
        try:
            for idx, (val0, val1) in enumerate(zip(x0, x1)):
                dt = val0 - val1
                dly0.append(dt)
        except:
            dly0 = [0, 0]

        # Converting signals to metric
        dly = np.mean(np.array(dly0))
        phase = float(360 * dly * f_sig / self.__settings_bode.sampling_rate)
        gain = float(20 * np.log10((out_max - out_min) / (in_max - in_min)))

        return gain, phase

    def generate_func_variables(self) -> tuple[np.ndarray, dict]:
        """Generating the reference design variables for run sweep (from YAML settings)"""
        f_sig = np.logspace(
            start=self.__settings_bode.get_frequency_range_log[0],
            stop=self.__settings_bode.get_frequency_range_log[1],
            num=self.__settings_bode.total_steps,
            endpoint=True
        )
        emu_filter = filter_stage(
            N=self.__settings_bode.ref_filter_order,
            fs=self.__settings_bode.sampling_rate,
            f_filter=self.__settings_bode.ref_filter_corner,
            ftype=self.__settings_bode.ref_filter_ftype,
            btype=self.__settings_bode.ref_filter_btype,
            use_iir_filter=self.__settings_bode.ref_filter_iir
        )
        emu_bode = emu_filter.freq_response(f_sig)
        return f_sig, emu_bode


def run_filter_on_target(device_id: int, block_plot: bool=False) -> None:
    """Function for running the filter test with structures on target device
    :param device_id:               Device ID (unsigned integer) for calling the right target on device
    :param block_plot:              Blocking and showing plot
    :return:                        None
    """
    # --- Preparing Test
    exp0 = ExperimentBode(device_id)
    settings_bode = exp0.get_settings_func
    f_sig, bode_ref = exp0.generate_func_variables()

    # Control Routine
    exp0.init_experiment(f'{device_id:02d}')
    data_dut = {'process_time': [], 'data_in': [], 'data_out': [],
                'gain_dut': [], 'phase_dut': [], 'gain_emu': bode_ref['gain'], 'phase_emu': bode_ref['phase'],
                'f_sig': f_sig, 'f_smp': settings_bode.sampling_rate}

    for f_sig_used in f_sig:
        data_norm = exp0.preprocess_data(
            f_sig=f_sig_used,
            no_periods=settings_bode.num_iterations_period,
            is_signed=settings_bode.signed_data
        )
        time_run = exp0.do_inference(device_id)
        data_out = exp0.postprocess_data()
        gain, phase = exp0.extract_gain_phase(
            f_sig=f_sig_used,
            xin=data_norm['wvf'],
            xout=data_out
        )

        # Saving results
        data_dut['process_time'].append(time_run)
        data_dut['data_in'].append(data_norm['wvf'])
        data_dut['data_out'].append(data_out)
        data_dut['gain_dut'].append(gain)
        data_dut['phase_dut'].append(phase)

    # --- Ending
    np.save(f'{exp0.get_path2run}/results_bode.npy', data_dut, allow_pickle=True)
    plot_bode(f_sig, data_dut, exp0.get_path2run, block_plot=block_plot)


def plot_bode(f_sig: np.ndarray, data_dut: dict, path: str='', block_plot: bool=False) -> None:
    """Plotting the bode diagram of selected device under test
    Args:
        f_sig:          Numpy array with signal frequencies
        data_dut:       Dictionary with results
        path:           Path for saving the figure
        block_plot:     Blocking and showing plot
    Return:
        None
    """
    gain_dut = np.array(data_dut['gain_dut'])
    phase_dut = np.array(data_dut['phase_dut'])

    # --- Configure plot
    plt.figure()
    ax0 = plt.subplot(211)
    ax1 = plt.subplot(212)

    # --- Plot: DUT
    ax0.semilogx(f_sig, gain_dut, marker='.', markersize=4, color=get_color_plot(0), label="DUT")
    ax0.set_ylabel('Gain (dB)')
    ax0.grid(True)

    ax1.semilogx(f_sig, phase_dut, marker='.', markersize=4, color=get_color_plot(0))
    ax1.set_ylabel('Phase (°)')
    ax1.set_xlabel('Sampling frequency f_s (Hz)')
    ax1.grid(True)

    ax1.set_ylim(-180, 180)
    ax1.set_yticks(range(-180, 180, 45))

    # --- Plot: EMU
    ax0.semilogx(f_sig, 20*np.log10(data_dut['gain_emu']), marker='.', markersize=4, color=get_color_plot(1), label="Emulation")
    ax1.semilogx(f_sig, data_dut['phase_emu'], marker='.', markersize=4, color=get_color_plot(1))

    ax0.legend()
    plt.tight_layout(pad=0.5)
    if path:
        save_figure(plt, path, 'bode_plot')
    if block_plot:
        plt.show(block=True)


class filter_stage:
    __filt_btype_dict: dict = {'low': 'lowpass', 'high': 'highpass', 'bandpass': 'bandpass',
                    'bandstop': 'bandstop', 'all': 'allpass'}
    __filt_ftype_dict: dict = {'butter': 'butter', 'cheby1': 'cheby1', 'cheby2': 'cheby2',
                    'ellip': 'ellip', 'bessel': 'bessel'}
    __coeff_a: np.ndarray
    __coeff_b: np.ndarray

    def __init__(self, N: int, fs: float, f_filter: list, use_iir_filter: bool,
                 btype='low', ftype='butter', use_filtfilt=False):
        """Class for filtering and getting the filter coefficient
        (If using Allpass
        Args:
            N:                  Order number of used filter
            fs:                 Sampling rate of data stream
            f_filter:           Filter corner frequency as list ('low', 'high', 'all' (1st order) = [f_brk]
                                and 'bandpass', 'bandstop' = [f_c0, f_c1] and 'all' (2nd order)' = [f_brk and f_bw])
            btype:              Used filter type ['low', 'high', 'bandpass', 'bandstop', 'all' (IIR, 1st/2nd Order)]
            ftype:              Used filter design ['butter', 'cheby1', 'cheby2', 'ellip', 'bessel']
            use_iir_filter:     Used filter topology [True: IIR, False: FIR]
            use_filtfilt:       Using filtfilt functionality from scipy.signal (Zero-phase filtering)
        """
        self.__sampling_rate = fs
        self.__coeffb_defined = False
        self.__coeffa_defined = False
        self.__use_filtfilt = use_filtfilt

        self.__filter_type_iir_used = use_iir_filter
        self.__filter_order = N
        self.__filter_corner = np.array(f_filter, dtype='float')
        self.__filt_ftype = self.__get_filter_ftype(ftype)
        self.__filt_btype = self.__get_filter_btype(btype)
        self.__extract_filter_params()

    def __extract_filter_params(self) -> None:
        """Extracting the filter coefficient with used settings"""
        if self.__filter_type_iir_used and not self.__filt_btype == 'allpass':
            # --- Defining an IIR filter (excluding allpass)
            filter_params = scft.iirfilter(
                N=self.__filter_order, Wn=2 * self.__filter_corner / self.__sampling_rate,
                btype=self.__filt_btype, ftype=self.__filt_ftype,
                analog=False, output='ba'
            )
            self.__coeff_b = filter_params[0]
            self.__coeffb_defined = True
            self.__coeff_a = np.array(filter_params[1])
            self.__coeffa_defined = True
        elif self.__filter_type_iir_used and self.__filt_btype == 'allpass':
            match self.__filter_order:
                case 1:
                    # --- Getting the coefficient (First Order)
                    val = np.tan(np.pi * self.__filter_corner[0] / self.__sampling_rate)
                    iir_c0 = (val - 1) / (val + 1)
                    self.__coeff_b = np.array([iir_c0, 1.0])
                    self.__coeffb_defined = True
                    self.__coeff_a = np.array([1.0, iir_c0])
                    self.__coeffa_defined = True
                case 2:
                    # --- Getting the coefficient (Second Order)
                    val = np.tan(np.pi * self.__filter_corner[1] / self.__sampling_rate)
                    iir_c0 = (val - 1) / (val + 1)
                    iir_c1 = -np.cos(2 * np.pi * self.__filter_corner[0] / self.__sampling_rate)
                    self.__coeff_b = np.array([-iir_c0, iir_c1 * (1 - iir_c0), 1.0])
                    self.__coeffb_defined = True
                    self.__coeff_a = np.array([1.0, iir_c1 * (1 - iir_c0), -iir_c0])
                    self.__coeffa_defined = True
                case _:
                    raise NotImplementedError("Allpass IIR-filters are only implemented for 1st and 2nd order! "
                                              "- Please change!")
        elif self.__filter_type_iir_used and self.__filt_btype == 'allpass':
            raise NotImplementedError("Allpass Filter is only implemented for IIR filter types!")
        else:
            # --- Defining a FIR filter
            filter_params = scft.firwin(
                numtaps=self.__filter_order,
                cutoff=self.__filter_corner, fs=self.__sampling_rate,
                pass_zero=self.__filt_btype
            )
            self.__coeff_b = filter_params
            self.__coeffb_defined = True
            self.__coeff_a = np.array(1.0)
            self.__coeffa_defined = False

    def __get_filter_btype(self, type_used: str) -> str:
        """Definition of the filter type used in scipy function"""
        type_out = ''
        for key, type0 in self.__filt_btype_dict.items():
            if type_used == key:
                type_out = type0
                break
        if type_out == '':
            raise NotImplementedError("Type of used filter type is not available")
        return type_out

    def __get_filter_ftype(self, type_used: str) -> str:
        """Definition of the filter type used in scipy function"""
        type_out = ''
        for key, type0 in self.__filt_ftype_dict.items():
            if type_used == key:
                type_out = type0
                break
        if type_out == '':
            raise NotImplementedError("Type of used filter type is not available")
        return type_out

    def filter(self, xin: np.ndarray) -> np.ndarray:
        """Performing the filtering of input data
        Args:
            xin:    Input numpy array
        Returns:
            Numpy array with filtered output
        """
        return scft.lfilter(b=self.__coeff_b, a=self.__coeff_a, x=xin) if not self.__use_filtfilt \
            else scft.filtfilt(b=self.__coeff_b, a=self.__coeff_a, x=xin)

    def freq_response(self, freq: np.ndarray) -> dict:
        """Getting the frequency response of the filter for specific frequency values
        Args:
            freq:       Numpy array with frequency values
        Return:
            Dict with ['freq': frequency, 'gain': gain, 'phase': phase]
        """
        if self.__filter_type_iir_used:
            fout = scft.iirfilter(
                N=self.__filter_order, Wn=self.__filter_corner,
                btype=self.__filt_btype, ftype=self.__filt_ftype, analog=True,
                output='ba'
            )
            w, h = scft.freqs(b=fout[0], a=fout[1], worN=freq)
        else:
            w, h = scft.freqz(b=self.__coeff_b, a=1, fs=self.__sampling_rate, worN=freq)

        h0 = np.array(h)
        gain = np.abs(h0)
        phase = np.angle(h0, deg=True)
        return {'freq': w, 'gain': gain, 'phase': phase}
