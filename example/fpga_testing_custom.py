from elasticai.fpga_testing import (
    InterfaceRunner,
    ConfigurationDUT,
    run_embedded_test
)


class DeviceAPI(InterfaceRunner):
    def __init__(self, com_port="AUTOCOM") -> None:
        super().__init__(com_port=com_port, num_delay_messages=0)

    @property
    def is_active(self) -> bool:
        return True

    def get_data_scaling_value(self, bitwidth_data: int) -> int:
        return 0

    def do_reset(self) -> None:
        pass

    def open_serial(self) -> None:
        pass

    def close_serial(self) -> None:
        pass

    def get_dut_config(self, num_target: int) -> ConfigurationDUT:
        pass

    def select_device_for_testing(self, num_dut: int) -> None:
        pass

    def set_led_mcu(self, state: bool) -> None:
        pass

    def set_led_fpga(self, state: bool) -> None:
        pass

    def toggle_led_fpga(self) -> None:
        pass

    def do_inference(self, data: bytes) -> bytes:
        pass

    def do_inference_empty(self, num_cycles: int) -> bytes:
        pass


if __name__ == "__main__":
    run_embedded_test(
        device=DeviceAPI,
        show_plots=False
    )
