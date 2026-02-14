from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import time_ns
from tqdm import tqdm

from elasticai.fpga_testing.src.helper import get_path_to_project
from elasticai.fpga_testing.src.exp_dut import DeviceUnderTestHandler
from elasticai.fpga_testing.src.yaml_handler import YamlConfigHandler


@dataclass
class ExperimentSettings:
    """Class for handling the experiment
    Attributes:
        com_port:       String with COM port name
        selected_dut:   List with DUT numbers for testing
    """
    com_port: str
    selected_dut: list


class ExperimentMain:
    _device: DeviceUnderTestHandler
    __device_buf:       int
    __path2run:         Path
    _settings: ExperimentSettings
    _type_experiment: str
    _buffer_data_send: list
    _buffer_data_get: bytes

    def __init__(self, buffer_size:int=10) -> None:
        """Class for handling the Experiment Main Setup
        Args:
            buffer_size:    Number of transmission which will be done once using Serial Package
                            [Default: 10, best performance using PySerial]
        Returns:
            None
        """
        DefaultSettings = ExperimentSettings(
            com_port="AUTOCOM",
            selected_dut=[1, 2]
        )
        yaml_data = YamlConfigHandler(
            yaml_template=DefaultSettings,
            path2yaml='config',
            yaml_name=f'Config_Exp',
            start_folder=get_path_to_project()
        )
        self._settings = yaml_data.get_class(ExperimentSettings)
        self.__device_buf = buffer_size

        self._device = DeviceUnderTestHandler(self._settings.com_port, self.__device_buf)

    @property
    def get_path2run(self) -> str:
        """Getting the path for saving the results"""
        return str(self.__path2run.absolute())

    @property
    def get_settings(self) -> ExperimentSettings:
        """Getting the settings loaded from yaml-file"""
        return self._settings

    def get_dut_type(self, print_results: bool = False) -> list:
        result = self._device.get_dut_config_all(print_results=print_results)
        return [info.dut_type for info in result.values()]

    def __generate_saving_folder(self, index='') -> None:
        """Generating the folder for saving the results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder = timestamp + f'{self._type_experiment}{index}'
        self.__path2run = Path(get_path_to_project('runs')) / folder
        self.__path2run.mkdir(parents=True, exist_ok=True)

    def init_experiment(self, index='', generate_folder:bool=True) -> str:
        """Initialization of the experiment with enabling the communication"""
        if generate_folder:
            self.__generate_saving_folder(index)
            return self.get_path2run
        else:
            return ''

    def do_inference(self, device_test: int) -> float:
        """Doing the inference from Computer to Device for testing accelerators with number of selected target"""
        self._device.open_serial()
        self._device.select_device_for_testing(device_test)
        self._device.do_led_control(True)

        self._buffer_data_get = bytes()
        if self._device.is_open:
            # --- Active data transmission
            process_duration = time_ns()
            for data in (pbar := tqdm(self._buffer_data_send)):
                pbar.set_description(f"Processing")
                self._buffer_data_get += self._device.do_inference(data)
            process_duration = time_ns() - process_duration
            # --- Delay for getting last samples
            self._buffer_data_get += self._device.do_inference_delay(self._device.get_slicing_position)
        else:
            raise RuntimeError("Device not open - Please check communication!")

        self._device.do_led_control(False)
        self._device.close_serial()
        return process_duration
