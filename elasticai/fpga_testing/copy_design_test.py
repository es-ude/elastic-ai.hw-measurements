from shutil import rmtree

import pytest

from elasticai.fpga_testing import get_path_to_project

from .copy_design import (
    _get_template_path,
    copy_design_arty7_files,
    copy_design_env5_files,
    copy_design_env6mini_files,
    copy_design_olimex_gatemate_files,
    copy_skeleton,
)


@pytest.fixture(scope="module", autouse=True)
def path():
    path2temp = get_path_to_project() / "temp_build"
    if path2temp.exists():
        rmtree(path2temp)
    path2temp.mkdir(parents=True, exist_ok=True)
    yield path2temp


def test_template_path() -> None:
    dst = _get_template_path()
    chck = get_path_to_project() / "elasticai" / "fpga_testing" / "template"
    assert dst.as_posix() == chck.as_posix()


def test_copy_design_arty7_files(path) -> None:
    path2dst = path / "arty7"
    copy_design_arty7_files(dest=path2dst)

    files_available = [file.name for file in path2dst.rglob("*.*")]
    files_available.sort()
    files_check = [
        "io.xdc",
        "test_dut.v",
        "top_module.v",
        "uart_com.v",
        "uart_fifo.v",
        "uart_middleware.v",
        "skeleton_echo.v",
        "bram_single.v",
        "bram_preload.mem",
        "skeleton_ram.v",
    ]
    files_check.sort()

    assert files_available == files_check


def test_copy_design_env5_files(path) -> None:
    path2dst = path / "env5"
    copy_design_env5_files(dest=path2dst)

    files_available = [file.name for file in path2dst.rglob("*.*")]
    files_available.sort()
    files_check = [
        "io.xdc",
        "test_dut.v",
        "top_module.v",
        "spi_middleware.v",
        "spi_slave_wclk.v",
        "skeleton_echo.v",
        "bram_single.v",
        "bram_preload.mem",
        "skeleton_ram.v",
    ]
    files_check.sort()

    assert files_available == files_check


def test_copy_design_env6mini_files(path) -> None:
    path2dst = path / "env6mini"
    copy_design_env6mini_files(dest=path2dst)

    files_available = [file.name for file in path2dst.rglob("*.*")]
    files_available.sort()
    files_check = [
        "io.pcf",
        "test_dut.v",
        "top_module.v",
        "spi_middleware.v",
        "spi_slave_wclk.v",
        "skeleton_echo.v",
        "bram_single.v",
        "bram_preload.mem",
        "skeleton_ram.v",
    ]
    files_check.sort()

    assert files_available == files_check


def test_copy_design_olimex_gatemate_files(path) -> None:
    path2dst = path / "olimex_gatemate"
    copy_design_olimex_gatemate_files(dest=path2dst)

    files_available = [file.name for file in path2dst.rglob("*.*")]
    files_available.sort()
    files_check = [
        "io.ccf",
        "top_module.v",
    ]
    files_check.sort()

    assert files_available == files_check


def test_copy_skeleton_not_available(path) -> None:
    path2dst = path / "skeletons"
    try:
        copy_skeleton(name="wrong", num_id=0, dest=path2dst)
    except ValueError:
        assert True
    else:
        assert False


def test_copy_skeleton_dnn(path) -> None:
    used_modules = ["DnN", "filTer", "mac", "MATH", "RAM", "ROM"]

    for idx, module in enumerate(used_modules):
        path2dst = path / "skeletons" / module.lower()
        copy_skeleton(name=module, num_id=idx, dest=path2dst)

        files_available = [file.name for file in path2dst.rglob("*.*")]
        files_available.sort()
        files_check = [f"skeleton_{module.lower()}_{idx}.v"]
        files_check.sort()
        assert files_available == files_check
