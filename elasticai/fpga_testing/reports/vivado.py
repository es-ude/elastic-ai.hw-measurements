import re
from dataclasses import dataclass
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


def _find_section_start(text: str, section_title: str) -> int:
    pattern = re.compile(rf"^{re.escape(section_title)}\s*\n-+\n", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        raise ValueError(f"Section '{section_title}' not found")
    return match.end()


def _collect_table_lines(text: str, start: int) -> list[str]:
    table_lines: list[str] = []
    border_count = 0

    for line in text[start:].splitlines():
        stripped = line.strip()
        is_border = stripped.startswith("+") and set(stripped) <= {"+", "-"}

        if is_border:
            table_lines.append(line)
            border_count += 1
            if border_count == 3:
                break
        elif border_count >= 1:
            table_lines.append(line)
    return table_lines


def _parse_pipe_table(lines: list[str], exclude_header: bool = True) -> dict[str, list[str]]:
    rows = [l for l in lines if l.strip().startswith("|")]
    data: dict[str, list[str]] = {}
    start_idx = 1 if exclude_header else 0
    for line in rows[start_idx:]:
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if cols[0]:
            data[cols[0]] = cols[1:]
    return data


def _extract_table(text: str, section_title: str, exclude_header: bool = True) -> dict[str, list[str]]:
    start = _find_section_start(text, section_title)
    return _parse_pipe_table(_collect_table_lines(text, start), exclude_header)


def _extract_hierarchy_table(text: str, section_title: str) -> dict[str, "VivadoHierarchyPowerEntry"]:
    start = _find_section_start(text, section_title)
    lines = _collect_table_lines(text, start)
    rows = [l for l in lines if l.strip().startswith("|")]

    entries: dict[str, VivadoHierarchyPowerEntry] = {}
    for line in rows[1:]:
        parts = line.strip().strip("|").split("|")
        if len(parts) < 2:
            continue

        name_field = parts[0]
        leading_spaces = len(name_field) - len(name_field.lstrip(" "))
        depth = max(0, (leading_spaces - 1) // 2)

        entries.update(
            {
                f"{name_field.strip()}": VivadoHierarchyPowerEntry(
                    name=name_field.strip(),
                    power_w=float(parts[1].strip()),
                    depth=depth,
                )
            }
        )
    return entries


def _extract_device(text: str) -> str:
    match = re.search(r"^\|\s*Device\s*:\s*(.+?)\s*$", text, re.MULTILINE)
    if not match:
        raise ValueError("Device information not found")
    return match.group(1)


def _reconstruct_headers(header_line: str) -> list[str]:
    _KNOWN_HEADERS = [
        "WNS(ns)",
        "TNS(ns)",
        "TNS Failing Endpoints",
        "TNS Total Endpoints",
        "WHS(ns)",
        "THS(ns)",
        "THS Failing Endpoints",
        "THS Total Endpoints",
        "WPWS(ns)",
        "TPWS(ns)",
        "TPWS Failing Endpoints",
        "TPWS Total Endpoints",
    ]
    remaining = header_line
    ordered = []
    for h in _KNOWN_HEADERS:
        idx = remaining.find(h)
        if idx == -1:
            raise ValueError(f"Header '{h}' not found in timing summary")
        ordered.append(h)
        remaining = remaining[idx + len(h) :]
    return ordered


@dataclass(frozen=True)
class VivadoTimingSummary:
    device: str
    wns: float
    tns: float
    tns_failing_endpoints: int
    tns_total_endpoints: int
    whs: float
    ths: float
    ths_failing_endpoints: int
    ths_total_endpoints: int
    wpws: float
    tpws: float
    tpws_failing_endpoints: int
    tpws_total_endpoints: int

    @classmethod
    def from_rpt(cls, path: Path) -> "VivadoTimingSummary":
        files = list(path.glob("*_timing_summary*.rpt"))
        text = files[0].read_text()

        device = _extract_device(text)

        section_match = re.search(r"Design Timing Summary.*?\n-+\n(.*?)\n-+\n", text, re.DOTALL)
        if not section_match:
            raise ValueError("Design Timing Summary section not found")

        lines = [l for l in section_match.group(1).splitlines() if l.strip()]
        header_line = lines[0]
        value_line = lines[2] if len(lines) > 2 else lines[1]

        raw = dict(zip(_reconstruct_headers(header_line), value_line.split()))

        def f(key: str) -> float:
            return float(raw[key])

        def i(key: str) -> int:
            return int(raw[key])

        return cls(
            device=device,
            wns=f("WNS(ns)"),
            tns=f("TNS(ns)"),
            tns_failing_endpoints=i("TNS Failing Endpoints"),
            tns_total_endpoints=i("TNS Total Endpoints"),
            whs=f("WHS(ns)"),
            ths=f("THS(ns)"),
            ths_failing_endpoints=i("THS Failing Endpoints"),
            ths_total_endpoints=i("THS Total Endpoints"),
            wpws=f("WPWS(ns)"),
            tpws=f("TPWS(ns)"),
            tpws_failing_endpoints=i("TPWS Failing Endpoints"),
            tpws_total_endpoints=i("TPWS Total Endpoints"),
        )


@dataclass(frozen=True)
class VivadoUtilizationSummary:
    device: str
    slice_luts_used: int
    slice_luts_available: int
    registers_used: int
    registers_available: int
    f7_muxes_used: int
    f7_muxes_available: int
    f8_muxes_used: int
    f8_muxes_available: int
    bram_tiles_used: int
    bram_tiles_available: int
    dsp_used: int
    dsp_available: int
    io_used: int
    io_available: int

    @classmethod
    def from_rpt(cls, path: Path) -> "VivadoUtilizationSummary":
        files = list(path.glob("*_utilization_placed.rpt"))
        text = files[0].read_text()

        device = _extract_device(text)

        slice_logic = _extract_table(text, "1. Slice Logic")
        memory = _extract_table(text, "3. Memory")
        dsp = _extract_table(text, "4. DSP")
        io = _extract_table(text, "5. IO and GT Specific")

        luts = slice_logic["Slice LUTs"]
        regs = slice_logic["Slice Registers"]
        f7 = slice_logic["F7 Muxes"]
        f8 = slice_logic["F8 Muxes"]
        bram = memory["Block RAM Tile"]
        dsps = dsp["DSPs"]
        iob = io["Bonded IOB"]

        return cls(
            device=device,
            slice_luts_used=int(luts[0]),
            slice_luts_available=int(luts[3]),
            registers_used=int(regs[0]),
            registers_available=int(regs[3]),
            f7_muxes_used=int(f7[0]),
            f7_muxes_available=int(f7[3]),
            f8_muxes_used=int(f8[0]),
            f8_muxes_available=int(f8[3]),
            bram_tiles_used=int(bram[0]),
            bram_tiles_available=int(bram[3]),
            dsp_used=int(dsps[0]),
            dsp_available=int(dsps[3]),
            io_used=int(iob[0]),
            io_available=int(iob[3]),
        )


@dataclass(frozen=True)
class VivadoPowerSummary:
    device: str
    total_on_chip_power_w: float
    design_power_budget_w: str
    power_budget_margin_w: str
    dynamic_w: float
    device_static_w: float
    effective_tja_c_per_w: float
    max_ambient_c: float
    junction_temperature_c: float
    confidence_level: str
    setting_file: str
    simulation_activity_file: str
    design_nets_matched: str


@dataclass(frozen=True)
class VivadoHierarchyPowerEntry:
    name: str
    power_w: float
    depth: int


@dataclass(frozen=True)
class VivadoPowerReport:
    summary: VivadoPowerSummary
    hierarchy: list[VivadoHierarchyPowerEntry]

    @classmethod
    def from_rpt(cls, path: Path) -> "VivadoPowerReport":
        files = list(path.glob("*_power_routed.rpt"))
        text = files[0].read_text()

        device = _extract_device(text)

        summary_kv = _extract_table(text, "1. Summary", exclude_header=False)
        hierarchy = _extract_hierarchy_table(text, "3.1 By Hierarchy")

        def num(key: str) -> float:
            return float(summary_kv[key][0])

        def raw(key: str) -> str:
            return summary_kv[key][0]

        summary = VivadoPowerSummary(
            device=device,
            total_on_chip_power_w=num("Total On-Chip Power (W)"),
            design_power_budget_w=raw("Design Power Budget (W)"),
            power_budget_margin_w=raw("Power Budget Margin (W)"),
            dynamic_w=num("Dynamic (W)"),
            device_static_w=num("Device Static (W)"),
            effective_tja_c_per_w=num("Effective TJA (C/W)"),
            max_ambient_c=num("Max Ambient (C)"),
            junction_temperature_c=num("Junction Temperature (C)"),
            confidence_level=raw("Confidence Level"),
            setting_file=raw("Setting File"),
            simulation_activity_file=raw("Simulation Activity File"),
            design_nets_matched=raw("Design Nets Matched"),
        )
        return cls(summary=summary, hierarchy=hierarchy)


@dataclass(frozen=True)
class VivadoMetrics:
    device: str
    utilization: VivadoUtilizationSummary
    timing: VivadoTimingSummary
    power_summary: VivadoPowerSummary
    power_hierarchy: dict[str, VivadoHierarchyPowerEntry]

    @classmethod
    def from_rpt(cls, path: Path) -> "VivadoMetrics":
        power = VivadoPowerReport.from_rpt(path)
        return cls(
            device=power.summary.device,
            utilization=VivadoUtilizationSummary.from_rpt(path),
            timing=VivadoTimingSummary.from_rpt(path),
            power_summary=power.summary,
            power_hierarchy=power.hierarchy,
        )
