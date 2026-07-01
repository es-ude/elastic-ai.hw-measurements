from pathlib import Path
from shutil import rmtree

import pytest

from elasticai.fpga_testing import get_path_to_project

from .oss_cad import (
    NextpnrMetrics,
    NextpnrTimingSummary,
    NextpnrUtilizationEntry,
    NextpnrUtilizationSummary,
    copy_osscad_implementation_results,
)


@pytest.fixture(autouse=True)
def osscad_path():
    path = get_path_to_project("artefact") / "env6_mini"
    yield path


@pytest.fixture(autouse=True)
def temp_path():
    path = get_path_to_project("temp_reports") / "osscad"
    if path.exists():
        rmtree(path)
    yield path


def test_copy_reports(osscad_path: Path, temp_path: Path) -> None:
    copy_osscad_implementation_results(
        path2project=osscad_path,
        path2save=temp_path,
    )
    assert temp_path.exists()
    assert temp_path.is_dir()

    files_temp = [file.name for file in temp_path.iterdir()]
    files_temp.sort()
    files_proj = [file.name for file in osscad_path.iterdir()]
    files_proj.sort()
    assert files_temp == files_proj


def test_extract_timing(osscad_path: Path) -> None:
    summary = NextpnrTimingSummary.from_rpt(osscad_path)
    assert type(summary) == NextpnrTimingSummary
    assert summary.logic_levels == 3
    assert summary.max_frequency_mhz == 58.82
    assert summary.total_path_delay_ns == 17.0


def test_extract_utilization(osscad_path: Path) -> None:
    summary = NextpnrUtilizationSummary.from_rpt(osscad_path)
    assert type(summary) == NextpnrUtilizationSummary
    assert len(summary.entries) == 15
    assert type(summary.entries["ICESTORM_LC"]) == NextpnrUtilizationEntry
    assert summary.entries["ICESTORM_LC"].used == 162


def test_extract_metrics(osscad_path: Path) -> None:
    summary = NextpnrMetrics.from_rpt(osscad_path)
    assert type(summary) == NextpnrMetrics
    assert type(summary.timing) == NextpnrTimingSummary
    assert type(summary.utilization) == NextpnrUtilizationSummary
    assert summary.timing.max_frequency_mhz == 58.82
