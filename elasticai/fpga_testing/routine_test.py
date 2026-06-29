import pytest

from elasticai.fpga_testing.runner.interface_runner_test import DummyRunner

from .routine import run_embedded_test


@pytest.mark.hardware
def test_embedded_test() -> None:
    run_embedded_test(device=DummyRunner, show_plots=False)
