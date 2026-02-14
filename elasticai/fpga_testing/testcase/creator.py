from dataclasses import dataclass
import numpy as np
from torch import Tensor, ones_like, zeros, cat

from elasticai.creator.arithmetic import FxpArithmetic, FxpParams
from elasticai.creator.nn import Sequential
from elasticai.creator.nn.fixed_point import Linear

from elasticai.fpga_testing import get_path_to_project
from elasticai.fpga_testing.src.exp_dut import DeviceUnderTestHandler
from elasticai.fpga_testing.src.exp_runner import ExperimentMain
from elasticai.fpga_testing.src.yaml_handler import YamlConfigHandler


def get_basic_test_model(num_inputs: int, num_outputs: int, total_bits: int, frac_bits: int) -> Sequential:
    model = Sequential(
        Linear(
            in_features=num_inputs,
            out_features=num_outputs,
            bias=True,
            total_bits=total_bits,
            frac_bits=frac_bits,
        )
    )
    model[0].weight.data = ones_like(model[0].weight) * 2
    model[0].bias.data = Tensor([-1.0, 1.0, 2.0])
    return model


def get_basic_data_model(num_input: int, bit_width: int, frac_width: int, signed_data: bool) -> Tensor:
    max_val = (2**(bit_width - frac_width))
    start_value = -max_val/2 if signed_data else 0
    stop_value = max_val/2 if signed_data else max_val

    # Creating the dummy
    input_tensor = zeros((1, num_input))
    for idx_array in range(0, num_input):
        for value in np.arange(start_value, stop_value, 2**(-frac_width)):
            list_zeros = [0.0 for _ in range(0, num_input)]
            list_zeros[idx_array] = value

            new_input = Tensor([list_zeros])
            input_tensor = cat(
                (input_tensor, new_input), dim=0
            )

    # Converting to fixed point
    fxp_conf = FxpArithmetic(fxp_params=FxpParams(bit_width, frac_width))
    return fxp_conf.as_rational(fxp_conf.cut_as_integer(input_tensor))


@dataclass
class SettingsCreator:
    num_samples_input: int
    num_samples_output: int
    model_bitwidth: int
    model_bitfrac: int
    skeleton_id: bytes

    @property
    def get_model(self) -> Sequential:
        return get_basic_test_model(
            num_inputs=self.num_samples_input,
            num_outputs=self.num_samples_output,
            total_bits=self.model_bitwidth,
            frac_bits=self.model_bitfrac
        )

    @property
    def get_data(self) -> Tensor:
        return get_basic_data_model(
            num_input=self.num_samples_input,
            bit_width=self.model_bitwidth,
            frac_width=self.model_bitfrac,
            signed_data=True
        )

    @property
    def get_skeleton_id_integer(self) -> int:
        return int.from_bytes(self.skeleton_id, byteorder='big')

DefaultSettingsCreator = SettingsCreator(
    num_samples_input=5,
    num_samples_output=3,
    model_bitwidth=8,
    model_bitfrac=2,
    skeleton_id=bytes([idx for idx in range(16)])
)


class ExperimentCreator(ExperimentMain):
    _device: DeviceUnderTestHandler
    __settings_dnn: SettingsCreator
    __data_scaling_value: int

    def __init__(self, device_id: int) -> None:
        """Class for handling the Experiment Setup for calling data from LUT device (using skeleton version 1.0)
        :param device_id:   Integer value with device ID of test structure
        """
        super().__init__()
        self._type_experiment = '_dnn'

        self.__header = self._device.get_dut_config(device_id)
        set = DefaultSettingsCreator
        set.model_bitwidth = self.get_bitwidth_creator
        set.num_samples_input = self.get_num_input_creator
        set.num_samples_output = self.get_num_output_creator
        yaml_handler = YamlConfigHandler(set, yaml_name=f'Config_{device_id:03d}_Creator', start_folder=get_path_to_project())
        self.__settings_dnn = yaml_handler.get_class(SettingsCreator)
        self.__data_scaling_value = 2 ** (self._device.get_bitwidth_data - self.__settings_dnn.model_bitwidth)

    @property
    def get_bitwidth_creator(self) -> int:
        return self.__header.bitwidth_input

    @property
    def get_num_input_creator(self) -> int:
        return self.__header.num_inputs

    @property
    def get_num_output_creator(self) -> int:
        return self.__header.num_outputs

    @property
    def get_settings_func(self):
        return self.__settings_dnn

    def __preprocess_read_skeleton_id(self) -> None:
        """Reading the ID from skeleton, implemented on device"""
        self._buffer_data_send = self._device.slice_data_for_transmission(
            self._device.preparing_data_reading_skeleton_id(16)
        )

    def __postprocess_read_skeleton_id(self) -> list:
        """Post-processing the data from device to have in readable format and numpy format"""
        data_return = self._device.slice_data_from_transmission(self._buffer_data_get, False) / self.__data_scaling_value
        return [int(val) for val in data_return]

    def get_skeleton_id(self, device_id: int) -> int:
        """"""
        self.__preprocess_read_skeleton_id()
        self.do_inference(device_id)
        id_list = self.__postprocess_read_skeleton_id()
        return int.from_bytes(bytes(id_list), byteorder='big')


    def preprocess_model_data(self, data_input: Tensor) -> None:
        """Preprocessing the data in order to have the data stream suitable for tested device (hex and data frame)"""
        data_in_numpy = data_input.flatten().cpu().detach().numpy()
        transformed_data = [val*(2**self.__settings_dnn.model_bitfrac) for val in data_in_numpy]

        data_prepared = self._device.preparing_data_creator_architecture(
            signal=transformed_data,
            num_input_layer=self.__settings_dnn.num_samples_input,
            num_output_layer=self.__settings_dnn.num_samples_output,
            bit_position_start=self.__data_scaling_value,
            is_signed=True
        )
        self._buffer_data_send = self._device.slice_data_for_transmission(data_prepared)

    def postprocess_model_data(self) -> np.ndarray:
        """Post-processing the data from device to have in readable format and numpy format"""
        data_return = self._device.slice_data_from_transmission(
            data=self._buffer_data_get,
            is_signed=True
        )

        pattern_repeat = self.__settings_dnn.num_samples_input + 2
        pattern_period = pattern_repeat + self.__settings_dnn.num_samples_output

        data_array = list()
        for idx in range(round(len(data_return) / pattern_period)):
            pos_start = pattern_repeat + idx * pattern_period
            pos_end = (idx + 1) * pattern_period
            data_array.append(data_return[pos_start:pos_end])

        data0 = np.array(data_array) / self.__data_scaling_value / (2 ** self.__settings_dnn.model_bitfrac)
        return data0


def run_inference_on_target(device_id: int, block_plot: bool=False) -> None:
    """Function for running the DNN (quantized) test with structures on target device
    :param device_id:   Integer value with device ID of test structure
    :param block_plot:  If true, blocking and showing plots
    :return:            None
    """
    # --- Preparing Test
    exp0 = ExperimentCreator(device_id)
    settings_dnn = exp0.get_settings_func

    # --- Run Model for Predicting Value
    model_inference_use = settings_dnn.get_model
    data_inference_use = settings_dnn.get_data
    inference_expected = model_inference_use(data_inference_use)

    # --- Control Routine
    print(f'\nSystem Test for Implemented Creator NN Accelerator on FPGA'
          f'\n====================================================================')
    data_dut = {'process_time': [], 'data_in':  [], 'data_out': []}

    exp0.init_experiment(f'{device_id:02d}')
    # --- Step #1: Reading the Skeleton ID
    skeleton_id_device = exp0.get_skeleton_id(device_id)
    print(f'Getting the skeleton ID: {skeleton_id_device.to_bytes(16, "big")}')
    print(f'Right ID available? -->  {(skeleton_id_device == settings_dnn.get_skeleton_id_integer)}')

    # --- Step #2: Inference
    print('\nData Inference:')
    exp0.preprocess_model_data(data_inference_use)
    time_run = exp0.do_inference(device_id)
    data_inference_out = exp0.postprocess_model_data()

    # --- Step #3: Processing
    ite = 0
    cnt_true = 0
    cnt_false = 0
    for tensor_in, data_get, tensor_exp in zip(data_inference_use, data_inference_out, inference_expected):
        data_in = tensor_in.cpu().detach().numpy().flatten()
        data_exp = tensor_exp.cpu().detach().numpy().flatten()

        if not (data_get == data_exp).all():
            cnt_false += 1
            print(f'#{ite:03d} = In: {data_in}, Out: {data_get}, Expected: {data_exp}')
        else:
            cnt_true += 1

        # Saving results
        data_dut['process_time'].append(time_run)
        data_dut['data_in'].append(data_in)
        data_dut['data_out'].append(data_get)
        ite += 1

    # --- Ending
    print(f"=============================================================================================\n"
          f"Results: \tcnt_true = {100 * cnt_true / inference_expected.shape[0]:.2f} %,"
          f"\t\tcnt_false = {100 * cnt_false / inference_expected.shape[0]:.2f} %")
    np.save(f'{exp0.get_path2run}/results.npy', data_dut, allow_pickle=True)
