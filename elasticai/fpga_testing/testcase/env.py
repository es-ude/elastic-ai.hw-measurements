from elasticai.fpga_testing.src.exp_runner import ExperimentMain


def extract_available_structures_on_device(print_rqst: bool=False) -> tuple[list, list]:
    """Function for extracting available structures on device
    :param print_rqst:  Print request data from device (getting all meta data)
    :return:            Two list with [0] available structures on device and [1] selected test on device
    """
    exp = ExperimentMain()
    exp.init_experiment(index='', generate_folder=False)

    set = exp.get_settings
    return exp.get_dut_type(print_results=print_rqst), set.selected_dut
