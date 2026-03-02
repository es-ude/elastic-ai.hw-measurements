from pathlib import Path
from shutil import copytree, copyfile


def copy_design_arty7_files(dest: Path) -> None:
    """Function for copying the design files to test structures on FPGA (here: DevBoard Digilent Arty A7)
    :param dest:    Path with destination folder to copy all files into
    :return:        None
    """
    import elasticai.fpga_testing as dut
    path2design = Path(dut.__file__).parent / "design_arty7"

    dest.mkdir(
        parents=True,
        exist_ok=True
    )
    copytree(
        src=path2design,
        dst=dest,
        dirs_exist_ok=True
    )


def copy_design_env5_files(dest: Path) -> None:
    """Function for copying the design files to test structures on FPGA (here: elasticAI ENV5)
    :param dest:    Path with destination folder to copy all files into
    :return:        None
    """
    import elasticai.fpga_testing as dut
    path2design = Path(dut.__file__).parent / "design_env5"

    dest.mkdir(
        parents=True,
        exist_ok=True
    )
    copytree(
        src=path2design,
        dst=dest,
        dirs_exist_ok=True
    )


def copy_skeleton(name: str, dest: Path) -> None:
    """Function for copying a skeleton to test structures on FPGAs
    :param name:    Name of skeleton file [dnn, echo, filter, math, ram, rom]
    :param dest:    Path with destination folder to copy all files into
    :return:        None
    """
    if name.lower() not in ["dnn", "echo", "filter", "math", "ram", "rom"]:
        raise ValueError(f"{name} is not a valid skeleton name")

    import elasticai.fpga_testing as dut
    path2design = Path(dut.__file__).parent / "design_skeleton"
    copyfile(
        src=path2design / f"skeleton_{name}.v",
        dst=dest / f"skeleton_{name}.v",
    )


def copy_vivado_implementation_results(path2project: Path, path2save: Path) -> None:
    """Function for copying a skeleton to test structures on FPGAs
    :param path2project:    Path to Vivado project
    :param path2save:       Path with destination folder to copy all files into
    :return:                None
    """
    if not path2project.exists() and not path2project.is_dir():
        raise FileNotFoundError(f"Folder {path2project} does not exist")
    list_folder = list(path2project.glob("*.runs"))
    if not list_folder:
        raise FileNotFoundError(f"Vivado project in {path2project} does not exist")

    path2results = list_folder[0] / "impl_1"
    if not path2results.exists():
        raise FileNotFoundError("No implementation results found")

    file_copy = list()
    file_copy.append(list(path2results.glob("*.bit"))[0])
    file_copy.append(list(path2results.glob("*_clock_utilization_routed.rpt"))[0])
    file_copy.append(list(path2results.glob("*_io_placed.rpt"))[0])
    file_copy.append(list(path2results.glob("*_power_routed.rpt"))[0])
    file_copy.append(list(path2results.glob("*_timing_summary_routed.rpt"))[0])
    file_copy.append(list(path2results.glob("*_utilization_placed.rpt"))[0])

    path2save.mkdir(
        parents=True,
        exist_ok=True
    )
    for file in file_copy:
        copyfile(
            src=file.absolute(),
            dst=path2save / file.name
        )


if __name__ == "__main__":
    from elasticai.fpga_testing import get_path_to_project
    import elasticai.fpga_testing as dut
    copy_vivado_implementation_results(
        path2project=Path(get_path_to_project("fpga_design")),
        path2save=Path(get_path_to_project("artefact")) / "env5"
    )
