import pytest

from elasticai.fpga_testing.definitions import ConfigurationID
from elasticai.fpga_testing.runner.interface_runner_test import DummyRunner

from .routine import run_embedded_test


def test_embedded_nothing_test() -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.Nothing)

    try:
        run_embedded_test(device=dut, show_plots=False)
    except ValueError:
        assert True
    else:
        assert False


def test_embedded_pipeline_test() -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.ProcessingPipeline)

    try:
        run_embedded_test(device=dut, show_plots=False)
    except NotImplementedError:
        assert True
    else:
        assert False


def test_embedded_windower_test() -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.EventWindower)

    try:
        run_embedded_test(device=dut, show_plots=False)
    except NotImplementedError:
        assert True
    else:
        assert False


@pytest.mark.skip(reason="Not implemented")
def test_embedded_echo_test() -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.Echo)

    run_embedded_test(device=dut, show_plots=False)
