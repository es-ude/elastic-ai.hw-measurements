from pathlib import Path
from shutil import copyfile


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

    path2save.mkdir(parents=True, exist_ok=True)
    for file in file_copy:
        copyfile(src=file.absolute(), dst=path2save / file.name)
