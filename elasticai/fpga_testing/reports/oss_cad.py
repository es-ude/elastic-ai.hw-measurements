import re
from dataclasses import dataclass
from pathlib import Path
from shutil import copyfile


def copy_osscad_implementation_results(path2project: Path, path2save: Path) -> None:
    """Function for copying a skeleton to test structures on FPGAs
    :param path2project:    Path to OSS CAD build folder
    :param path2save:       Path with destination folder to copy all files into
    :return:                None
    """
    if not path2project.exists() and not path2project.is_dir():
        raise FileNotFoundError(f"Folder {path2project} does not exist")

    list_folder = list(path2project.glob("*.rpt"))
    if not list_folder:
        raise FileNotFoundError("No reports results found")

    file_copy = list()
    file_copy.append(list(path2project.glob("*.bin"))[0])
    file_copy.append(list(path2project.glob("*_timing.rpt"))[0])
    file_copy.append(list(path2project.glob("*_util_impl.rpt"))[0])
    file_copy.append(list(path2project.glob("*_util_sync.rpt"))[0])

    path2save.mkdir(parents=True, exist_ok=True)
    for file in file_copy:
        copyfile(src=file.absolute(), dst=path2save / file.name)


@dataclass(frozen=True)
class NextpnrTimingSummary:
    logic_levels: int
    total_path_delay_ns: float
    max_frequency_mhz: float

    @classmethod
    def from_rpt(cls, path: Path) -> "NextpnrTimingSummary":
        files = list(path.glob("*_timing.rpt"))
        text = files[0].read_text()

        levels_match = re.search(r"Total number of logic levels:\s*(\d+)", text)
        if not levels_match:
            raise ValueError("Total number of logic levels not found")

        delay_match = re.search(r"Total path delay:\s*([\d.]+)\s*ns\s*\(([\d.]+)\s*MHz\)", text)
        if not delay_match:
            raise ValueError("Total path delay not found")

        return cls(
            logic_levels=int(levels_match.group(1)),
            total_path_delay_ns=float(delay_match.group(1)),
            max_frequency_mhz=float(delay_match.group(2)),
        )


@dataclass(frozen=True)
class NextpnrUtilizationEntry:
    used: int
    available: int


@dataclass(frozen=True)
class NextpnrUtilizationSummary:
    entries: dict[str, NextpnrUtilizationEntry]

    @classmethod
    def from_rpt(cls, path: Path) -> "NextpnrUtilizationSummary":
        files = list(path.glob("*_util_impl.rpt"))
        text = files[0].read_text()

        section_match = re.search(r"Info: Device utilisation:\n((?:Info:.*\n?)+)", text)
        if not section_match:
            raise ValueError("Device utilisation section not found")

        entries: dict[str, NextpnrUtilizationEntry] = {}
        line_pattern = re.compile(r"Info:\s*([A-Za-z0-9_]+):\s*(\d+)/\s*(\d+)\s*(\d+)%")
        for line in section_match.group(1).splitlines():
            m = line_pattern.match(line.strip())
            if not m:
                continue
            name, used, available, percent = m.groups()
            entries[name] = NextpnrUtilizationEntry(used=int(used), available=int(available))

        return cls(entries=entries)


@dataclass(frozen=True)
class NextpnrMetrics:
    utilization: NextpnrUtilizationSummary
    timing: NextpnrTimingSummary

    @classmethod
    def from_rpt(cls, path: Path) -> "NextpnrMetrics":
        return cls(
            utilization=NextpnrUtilizationSummary.from_rpt(path),
            timing=NextpnrTimingSummary.from_rpt(path),
        )
