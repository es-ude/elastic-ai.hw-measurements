from shutil import rmtree

import pytest

from elasticai.fpga_testing import get_path_to_project
from elasticai.fpga_testing.definitions import ConfigurationID
from elasticai.fpga_testing.runner import ExperimentSettings
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


@pytest.fixture(scope="module", autouse=True)
def sets() -> None:
    settings = ExperimentSettings(
        com_port="AUTOCOM",
        selected_dut=[int(val) for val in ConfigurationID],
    )
    yield settings


def test_embedded_nothing_test(sets: ExperimentSettings) -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.Nothing)

    try:
        run_embedded_test(device=dut, settings=sets, show_plots=False)
    except ValueError:
        assert True
    else:
        assert False


def test_embedded_pipeline_test(sets: ExperimentSettings) -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.ProcessingPipeline)

    try:
        run_embedded_test(device=dut, settings=sets, show_plots=False)
    except NotImplementedError:
        assert True
    else:
        assert False


def test_embedded_windower_test(sets: ExperimentSettings) -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.EventWindower)

    try:
        run_embedded_test(device=dut, settings=sets, show_plots=False)
    except NotImplementedError:
        assert True
    else:
        assert False


def test_embedded_echo_test(sets: ExperimentSettings) -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.Echo)

    path2test = run_embedded_test(device=dut, settings=sets, show_plots=False)[-1]
    assert "echo" in path2test.as_posix()
    assert path2test.is_dir()
    assert (path2test / "results_echo.npy").exists()


def test_embedded_rom_test(sets: ExperimentSettings) -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.ROM_LUT)

    path2test = run_embedded_test(device=dut, settings=sets, show_plots=False)[-1]
    assert "rom" in path2test.as_posix()
    assert path2test.is_dir()
    assert (path2test / "results_rom.npy").exists()


def test_embedded_ram_test(sets: ExperimentSettings) -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.RAM)

    path2test = run_embedded_test(device=dut, settings=sets, show_plots=False)[-1]
    assert "ram" in path2test.as_posix()
    assert path2test.is_dir()
    assert (path2test / "results_ram.npy").exists()


def test_embedded_math_test(sets: ExperimentSettings) -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.Math)

    path2test = run_embedded_test(device=dut, settings=sets, show_plots=False)[-1]
    assert "math" in path2test.as_posix()
    assert path2test.is_dir()
    assert (path2test / "results_math.npy").exists()


def test_embedded_filter_test(sets: ExperimentSettings) -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.Filters)

    path2test = run_embedded_test(device=dut, settings=sets, show_plots=False)[-1]
    assert "filter" in path2test.as_posix()
    assert path2test.is_dir()
    assert (path2test / "results_filter.npy").exists()


def test_embedded_dnn_test(sets: ExperimentSettings) -> None:
    dut = DummyRunner
    dut.set_dut_mode(dut, ConfigurationID.CreatorDNN)

    path2test = run_embedded_test(device=dut, settings=sets, show_plots=False)[-1]
    assert "dnn" in path2test.as_posix()
    assert path2test.is_dir()
    assert (path2test / "results_dnn.npy").exists()
