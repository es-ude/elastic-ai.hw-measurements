from pathlib import Path

from elasticai.fpga_testing.definitions import ConfigurationID
from elasticai.fpga_testing.runner.cases import (
    run_echo_on_target,
    run_filter_on_target,
    run_inference_on_target,
    run_math_on_target,
    run_ram_test_on_target,
    run_rom_test_on_target,
)
from elasticai.fpga_testing.runner.exp_runner import (
    DefaultSettingsExp,
    ExperimentSettings,
    extract_available_structures_on_device,
)
from elasticai.fpga_testing.runner.interface_runner import InterfaceRunner


def run_embedded_test(
    device: type[InterfaceRunner],
    settings: ExperimentSettings = DefaultSettingsExp,
    show_plots: bool = True,
) -> list[Path]:
    """Function for running the on-device test cases
    :param device:              Device API to handle all test commands
    :param settings:            ExperimentSettings object
    :param show_plots:          If true, showing and blocking the results
    :return:                    List with Path to actual test saving folder
    """
    test_available, test_to_run = extract_available_structures_on_device(device=device, settings=settings)
    runnable_tests = list(set(test_available) & set(test_to_run))

    list_paths = list()
    for idx, run_skeleton in enumerate(runnable_tests):
        do_plot = idx == len(runnable_tests) - 1 and show_plots

        match run_skeleton:
            case ConfigurationID.Nothing:
                raise ValueError("This testcase uses no structure - It is just disabling the environment")
            case ConfigurationID.Echo:
                path = run_echo_on_target(device=device, device_id=run_skeleton, block_plot=do_plot)
            case ConfigurationID.ROM_LUT:
                path = run_rom_test_on_target(device=device, device_id=run_skeleton, block_plot=do_plot)
            case ConfigurationID.RAM:
                path = run_ram_test_on_target(device=device, device_id=run_skeleton, block_plot=do_plot)
            case ConfigurationID.Math:
                path = run_math_on_target(device=device, device_id=run_skeleton, block_plot=do_plot)
            case ConfigurationID.Filters:
                path = run_filter_on_target(device=device, device_id=run_skeleton, block_plot=do_plot)
            case ConfigurationID.EventWindower:
                raise NotImplementedError("Test Code for Event-Detection/Windowing is not implemented")
            case ConfigurationID.CreatorDNN:
                path = run_inference_on_target(device=device, device_id=run_skeleton, block_plot=do_plot)
            case ConfigurationID.ProcessingPipeline:
                raise NotImplementedError("Test Code for End-To-End Processors is not implemented")
            case _:
                raise NotImplementedError("Use case is not available")
        list_paths.append(path)
    return list_paths
