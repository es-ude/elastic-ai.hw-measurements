from pathlib import Path
from shutil import copyfile, copytree

import elasticai.fpga_testing as dut
from elasticai.fpga_testing import get_path_to_project


def _get_template_path() -> Path:
    return Path(dut.__file__).parent / "template"


def _get_basic_path() -> Path:
    return get_path_to_project() / "designs"


def _copy_design_files(src_device: Path, src_common: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    if not src_common == Path("."):
        copytree(src=src_common, dst=dest, dirs_exist_ok=True)
    if not src_device == Path("."):
        copytree(src=src_device, dst=dest, dirs_exist_ok=True)


def copy_design_arty7_files(dest: Path = _get_basic_path()) -> None:
    """Function for copying the design files to test structures on FPGA (here: DevBoard Digilent Arty A7)
    :param dest:    Path with destination folder to copy all files into
    :return:        None
    """
    path2device = _get_template_path() / "arty7"
    path2common = _get_template_path() / "common"
    _copy_design_files(
        src_device=path2device,
        src_common=path2common,
        dest=dest,
    )


def copy_design_env5_files(dest: Path = _get_basic_path()) -> None:
    """Function for copying the design files to test structures on FPGA (here: elasticAI.env5)
    :param dest:    Path with destination folder to copy all files into
    :return:        None
    """
    path2device = _get_template_path() / "env5"
    path2common = _get_template_path() / "common"
    _copy_design_files(
        src_device=path2device,
        src_common=path2common,
        dest=dest,
    )


def copy_design_env6mini_files(dest: Path = _get_basic_path()) -> None:
    """Function for copying the design files to test structures on FPGA (here: elasticAI.env6-mini)
    :param dest:    Path with destination folder to copy all files into
    :return:        None
    """
    path2device = _get_template_path() / "env6_mini"
    path2common = _get_template_path() / "common"
    _copy_design_files(
        src_device=path2device,
        src_common=path2common,
        dest=dest,
    )


def copy_design_olimex_gatemate_files(dest: Path = _get_basic_path()) -> None:
    """Function for copying the design files to test structures on FPGA (here: Olimex EVB Gatemate-A1)
    :param dest:    Path with destination folder to copy all files into
    :return:        None
    """
    path2device = _get_template_path() / "olimex_gatemate"
    path2common = Path(".")  # _get_template_path() / "common"
    _copy_design_files(
        src_device=path2device,
        src_common=path2common,
        dest=dest,
    )


def copy_skeleton(name: str, num_id: int, dest: Path) -> None:
    """Function for copying a skeleton to test structures on FPGAs
    :param name:    Name of skeleton file [dnn, filter, math, ram, rom]
    :param num_id:  ID number of skeleton
    :param dest:    Path with destination folder to copy all files into
    :return:        None
    """
    if name.lower() not in ["dnn", "filter", "math", "ram", "rom"]:
        raise ValueError(f"{name} is not a valid skeleton name")

    path2design = _get_template_path() / "skeleton"
    dest.mkdir(parents=True, exist_ok=True)
    copyfile(
        src=path2design / f"skeleton_{name}.v".lower(),
        dst=dest / f"skeleton_{name}_{num_id}.v".lower(),
    )
