from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import time_ns

from tqdm import tqdm

from elasticai.fpga_testing import get_path_to_project
from elasticai.fpga_testing._helper import YamlConfigHandler
from elasticai.fpga_testing.runner.interface_runner import InterfaceRunner


@dataclass(frozen=True)
class ExperimentSettings:
    """Class for handling the experiment
    Attributes:
        com_port:       String with COM port name
        selected_dut:   List with DUT numbers for testing
    """

    com_port: str
    selected_dut: list


DefaultSettingsExp = ExperimentSettings(
    com_port="AUTOCOM",
    selected_dut=[1, 2],
)


class ExperimentMain:
    _device: InterfaceRunner
    _path2run: Path
    _settings: ExperimentSettings
    _buffer_data_send: list
    _buffer_data_get: bytes

    def __init__(
        self, device: type[InterfaceRunner], settings: ExperimentSettings = DefaultSettingsExp
    ) -> None:
        """Class for handling the Experiment Main Setup
        :param device:      Device class
        :param settings:    ExperimentSettings class
        :return:            None
        """
        self._settings = YamlConfigHandler(
            yaml_template=settings,
            path2yaml=get_path_to_project("config"),
            yaml_name="Config_Exp",
        ).get_class(ExperimentSettings)

        self._path2run = get_path_to_project("runs")

        self._device = device(com_port=self._settings.com_port)

    @property
    def get_path2run(self) -> Path:
        """Getting the path for saving the results"""
        return self._path2run.absolute()

    @property
    def get_settings(self) -> ExperimentSettings:
        """Getting the settings loaded from yaml-file"""
        return self._settings

    def get_dut_type(self) -> list:
        """Returning the number of all DUT types, implemented on the device"""
        result = self._device.get_dut_configs()
        return [info.dut_type for info in result.values()]

    def init_experiment(self, test_name: str) -> Path:
        """Initialization of the experiment with enabling the communication
        :param test_name:   String with test name
        :return:            None
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = timestamp + f"_{test_name}"
        path_test = get_path_to_project("runs") / folder
        if not path_test.exists():
            self._path2run = path_test
            self._path2run.mkdir(parents=True, exist_ok=True)
        return self.get_path2run

    def do_inference(self, target_id: int) -> float:
        """Doing the inference from Computer to Device for testing accelerators with number of selected target
        :param target_id:   Device number
        :return:            Time duration for running test duration
        """
        self._device.open_serial()
        self._device.select_device_for_testing(target_id)
        self._device.set_led_fpga(True)

        self._buffer_data_get = bytes()
        if self._device.is_active:
            # --- Active data transmission
            process_duration = time_ns()
            for data in (pbar := tqdm(self._buffer_data_send)):
                pbar.set_description("Processing")
                self._buffer_data_get += self._device.do_inference(data)
            process_duration = time_ns() - process_duration
            # --- Delay for getting last samples
            self._buffer_data_get += self._device.do_inference_empty(self._device.get_slicing_position)
        else:
            raise RuntimeError("Device not open - Please check communication!")

        self._device.set_led_fpga(False)
        self._device.close_serial()
        return process_duration


def extract_available_structures_on_device(
    device: type[InterfaceRunner], settings: ExperimentSettings = DefaultSettingsExp
) -> tuple[list, list]:
    """Function for extracting available structures on-device
    :param device:      Device class
    :param settings:    ExperimentSettings class
    :return:            Two list with [0] available structures on device and [1] selected test on device
    """
    exp = ExperimentMain(device=device, settings=settings)
    return exp.get_dut_type(), exp.get_settings.selected_dut
