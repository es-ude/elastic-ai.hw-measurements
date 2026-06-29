from shutil import rmtree

import pytest

from elasticai.fpga_testing import get_path_to_project
from elasticai.fpga_testing.definitions import ConfigurationID
from elasticai.fpga_testing.runner.interface_runner_test import DummyRunner

from .routine import run_embedded_test


@pytest.fixture(scope="module", autouse=True)
def path() -> None:
    path2root = get_path_to_project("runs")
    path2conf = get_path_to_project("config")
    rmtree(path2root, ignore_errors=True)
    rmtree(path2conf, ignore_errors=True)
    path2root.mkdir(parents=True, exist_ok=True)
    path2conf.mkdir(parents=True, exist_ok=True)


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


def test_embedded_echo_test() -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.Echo)

    path2test = run_embedded_test(device=dut, show_plots=False)
    assert path2test.is_dir()
    assert (path2test / "results_echo.npy").exists()


def test_embedded_rom_test() -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.ROM_LUT)

    run_embedded_test(device=dut, show_plots=False)


def test_embedded_ram_test() -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.RAM)

    run_embedded_test(device=dut, show_plots=False)


def test_embedded_math_test() -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.Math)

    run_embedded_test(device=dut, show_plots=False)


def test_embedded_filter_test() -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.Filters)

    run_embedded_test(device=dut, show_plots=False)


def test_embedded_dnn_test() -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.CreatorDNN)

    run_embedded_test(device=dut, show_plots=False)
