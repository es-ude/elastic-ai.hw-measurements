from elasticai.fpga_testing.testcase import (
    extract_available_structures_on_device,
    run_echo_on_target,
    run_filter_on_target,
    run_inference_on_target,
    run_math_on_target,
    run_ram_test_on_target,
    run_rom_test_on_target,
)


def run_embedded_test(print_rqst_results: bool=False, show_plots: bool=True) -> None:
    """Function for running the test cases which are implemented on device
    :param print_rqst_results:  Printing the device structure characteristics
    :param show_plots:          If true, showing and blocking the results
    :return:                    None
    """
    test_type, test_to_run = extract_available_structures_on_device(print_rqst=print_rqst_results)
    for idx, used_skeleton in enumerate(test_to_run):
        do_plot = idx == len(test_to_run)-1 and show_plots
        match(test_type[used_skeleton]):
            case 0:
                raise ValueError("This testcase uses no structure - It is just disabling the environment")
            case 1:
                run_echo_on_target(device_id=used_skeleton, block_plot=do_plot)
            case 2:
                run_rom_test_on_target(device_id=used_skeleton, block_plot=do_plot)
            case 3:
                run_ram_test_on_target(device_id=used_skeleton, block_plot=do_plot)
            case 4:
                run_math_on_target(device_id=used_skeleton, block_plot=do_plot)
            case 5:
                run_filter_on_target(device_id=used_skeleton, block_plot=do_plot)
            case 6:
                raise NotImplementedError("Test Code for Event-Detection and Windowing is not implemented")
            case 7:
                run_inference_on_target(device_id=used_skeleton, block_plot=do_plot)
            case 8:
                raise NotImplementedError("Test Code for End-To-End Processors is not implemented")


if __name__ == "__main__":
    run_embedded_test()
