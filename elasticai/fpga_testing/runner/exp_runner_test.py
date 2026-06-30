from shutil import rmtree

import pytest

from elasticai.fpga_testing import get_path_to_project
from elasticai.fpga_testing.runner.interface_runner_test import DummyRunner

from .exp_runner import (
    DefaultSettingsExp,
    ExperimentMain,
    ExperimentSettings,
    extract_available_structures_on_device,
)


@pytest.fixture(scope="module", autouse=True)
def path() -> None:
    path2conf = get_path_to_project("config")
    rmtree(path2conf, ignore_errors=True)
    path2conf.mkdir(parents=True, exist_ok=True)


def test_get_path2run() -> None:
    rslt = ExperimentMain(device=DummyRunner, settings=DefaultSettingsExp).get_path2run
    check = get_path_to_project("runs")
    assert rslt.as_posix() == check.as_posix()


def test_get_settings() -> None:
    rslt: ExperimentSettings = ExperimentMain(
        device=DummyRunner, settings=DefaultSettingsExp
    ).get_settings
    assert rslt.com_port == "AUTOCOM"
    assert rslt.selected_dut == [1, 2]


def test_get_dut_type() -> None:
    rslt = ExperimentMain(device=DummyRunner, settings=DefaultSettingsExp).get_dut_type()
    assert rslt == [0]


def test_init_experiment() -> None:
    rslt = ExperimentMain(device=DummyRunner, settings=DefaultSettingsExp).init_experiment(
        test_name="test"
    )
    chck = get_path_to_project("runs")
    assert chck.as_posix() in rslt.as_posix()
    assert chck.as_posix() != rslt.as_posix()
    assert "_test" in rslt.name


def test_get_do_inference() -> None:
    dut = ExperimentMain(device=DummyRunner, settings=DefaultSettingsExp)
    dut._buffer_data_send = [b"\x00\x01\x02\x03\x04\x05", b"\x06\x07\x08\t\n\x0b", b"\x0c\r\x0e"]
    rslt = dut.do_inference(1)
    assert rslt > 0.0


def test_exp_get_dut_type() -> None:
    rslt = extract_available_structures_on_device(device=DummyRunner)
    assert rslt[0] == [0]
    assert rslt[1] == [1, 2]
