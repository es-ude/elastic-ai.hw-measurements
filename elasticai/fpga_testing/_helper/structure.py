from os import remove
from pathlib import Path
from shutil import copyfile

import elasticai.fpga_testing as dut
from elasticai.fpga_testing import get_path_to_project


def init_project_folder(new_folder: str = "") -> None:
    """Generating folder structure in first run
    :param new_folder:      Name of the new folder to create (test case)
    :return:                None
    """

    folder_structure = ["runs", "config", "scripts", "designs"]

    path2start = get_path_to_project(new_folder)
    for folder_name in folder_structure:
        fold = path2start / folder_name
        fold.mkdir(parents=True, exist_ok=True)


def copy_oss_cad_scripts(dst: Path = get_path_to_project()) -> None:
    """Copies oss cad scripts and devenv scripts to destination folder
    :param dst: Path to the destination folder
    :return:    None"""
    path_to_template = Path(dut.__file__).parent / "template" / "oss_cad"

    dst.mkdir(parents=True, exist_ok=True)
    # --- Step #1: Copying script files
    for file in path_to_template.glob("*.mk"):
        path2file = dst.absolute() / "scripts" / file.name
        if path2file.exists():
            remove(path2file.as_posix())
        copyfile(src=file.absolute(), dst=path2file)

    # --- Step #2: Copying main files (which can be updated every time)
    files_updated = ["Makefile", "fpga.nix"]
    for file_name in files_updated:
        path2file = dst.absolute() / file_name
        if path2file.exists():
            remove(path2file.as_posix())
        copyfile(src=(path_to_template / path2file.name).as_posix(), dst=path2file.as_posix())

    # --- Step #3: Copying main files (which will be not updated every time)
    files_non_updated = ["devenv.nix", "devenv.yaml"]
    for file_name in files_non_updated:
        path2file = dst.absolute() / file_name
        if not path2file.exists():
            copyfile(src=(path_to_template / path2file.name).as_posix(), dst=path2file.as_posix())
