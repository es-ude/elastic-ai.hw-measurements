from pathlib import Path
from shutil import copytree, copyfile


def copy_design_files(dest: Path) -> None:
    import elasticai.fpga_testing as dut
    path2design = Path(dut.__file__).parent / "design_fpga"

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
    if name.lower() not in ["dnn", "echo", "filter", "math_fast", "math_slow", "ram", "rom"]:
        raise ValueError(f"{name} is not a valid skeleton name")

    import elasticai.fpga_testing as dut
    path2design = Path(dut.__file__).parent / "design_skeleton"
    copyfile(
        src=path2design / f"skeleton_{name}.v",
        dst=dest / f"skeleton_{name}.v",
    )


def copy_vivado_implementation_results(path2project: Path, path2save: Path) -> None:
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
    path2project = Path(get_path_to_project("fpga_design"))
    copy_vivado_implementation_results(
        path2project=path2project,
        path2save=Path(dut.__file__).parent / "dummy"
    )
