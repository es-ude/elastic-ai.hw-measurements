from elasticai.fpga_testing.definitions import ConfigurationID
from elasticai.fpga_testing.runner.cases import (
    run_echo_on_target,
    run_filter_on_target,
    run_inference_on_target,
    run_math_on_target,
    run_ram_test_on_target,
    run_rom_test_on_target,
)
from elasticai.fpga_testing.runner.exp_runner import extract_available_structures_on_device
from elasticai.fpga_testing.runner.interface_runner import InterfaceRunner


def run_embedded_test(device: type[InterfaceRunner], show_plots: bool = True) -> None:
    """Function for running the test cases which are implemented on device
    :param device:              Device API to handle all test commands
    :param show_plots:          If true, showing and blocking the results
    :return:                    None
    """
    test_type, test_to_run = extract_available_structures_on_device(device=device)
    for idx, used_skeleton in enumerate(test_to_run):
        do_plot = idx == len(test_to_run) - 1 and show_plots
        match test_type[used_skeleton]:
            case ConfigurationID.Nothing:
                raise ValueError("This testcase uses no structure - It is just disabling the environment")
            case ConfigurationID.Echo:
                run_echo_on_target(device_id=used_skeleton, block_plot=do_plot)
            case ConfigurationID.ROM_LUT:
                run_rom_test_on_target(device_id=used_skeleton, block_plot=do_plot)
            case ConfigurationID.RAM:
                run_ram_test_on_target(device_id=used_skeleton, block_plot=do_plot)
            case ConfigurationID.Math:
                run_math_on_target(device_id=used_skeleton, block_plot=do_plot)
            case ConfigurationID.Filters:
                run_filter_on_target(device_id=used_skeleton, block_plot=do_plot)
            case ConfigurationID.EventWindower:
                raise NotImplementedError(
                    "Test Code for Event-Detection and Windowing is not implemented"
                )
            case ConfigurationID.CreatorDNN:
                run_inference_on_target(device_id=used_skeleton, block_plot=do_plot)
            case ConfigurationID.ProcessingPipeline:
                raise NotImplementedError("Test Code for End-To-End Processors is not implemented")
