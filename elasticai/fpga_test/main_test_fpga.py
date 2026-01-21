from elasticai.creator_plugins.test_env.testcase.handler import extract_available_structures_on_device
from elasticai.creator_plugins.test_env.testcase.echo import run_echo_on_target
from elasticai.creator_plugins.test_env.testcase.mult import run_mult_on_target
from elasticai.creator_plugins.test_env.testcase.rxm import run_rom_test_on_target
from elasticai.creator_plugins.test_env.testcase.bode import run_filter_on_target
from elasticai.creator_plugins.test_env.testcase.creator import run_creator_inference_on_target


def run_embedded_test(print_rqst_results: bool=False, show_plots: bool=True) -> None:
    """Function for running the test cases which are implemented on device
    :param print_rqst_results:  Printing the device structure characteristics
    :param show_plots:          If true, showing and blocking the results
    :return:                    None
    """
    test_type, test_to_run = extract_available_structures_on_device(
        print_rqst=print_rqst_results
    )
    for idx, used_skeleton in enumerate(test_to_run):
        do_plot = idx == len(test_to_run)-1 and show_plots
        match(test_type[used_skeleton]):
            case 0:
                run_echo_on_target(device_id=used_skeleton, block_plot=do_plot)
            case 1:
                run_mult_on_target(device_id=used_skeleton, block_plot=do_plot)
            case 2:
                raise NotImplementedError
            case 3:
                run_rom_test_on_target(device_id=used_skeleton, block_plot=do_plot)
            case 4:
                raise NotImplementedError
            case 5:
                run_filter_on_target(device_id=used_skeleton, block_plot=do_plot)
            case 6:
                raise NotImplementedError
            case 7:
                run_creator_inference_on_target(device_id=used_skeleton, block_plot=do_plot)


if __name__ == "__main__":
    run_embedded_test()
