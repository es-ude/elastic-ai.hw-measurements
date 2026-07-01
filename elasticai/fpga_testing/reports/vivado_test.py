from pathlib import Path

import pytest

from elasticai.hw_measurements import get_path_to_project

from .vivado import VivadoMetrics, VivadoPowerReport, VivadoTimingSummary, VivadoUtilizationSummary


@pytest.fixture(autouse=True)
def vivado_path():
    yield get_path_to_project("artefact") / "arty7"


def test_extract_timing_report(vivado_path: Path):
    summary = VivadoTimingSummary.from_rpt(vivado_path)

    assert type(summary) == VivadoTimingSummary
    assert summary.device == '7a35ti-csg324'
    assert summary.tns == 0.0
    assert summary.tpws == 0.0
    assert summary.whs == 0.117
    assert summary.wns == 0.759
    assert summary.wpws == 4.5


def test_extract_utilization_report(vivado_path: Path):
    summary = VivadoUtilizationSummary.from_rpt(vivado_path)

    assert type(summary) == VivadoUtilizationSummary
    assert summary.device == 'xc7a35ticsg324-1L'
    assert summary.bram_tiles_used == 0
    assert summary.bram_tiles_available == 50
    assert summary.slice_luts_used == 636
    assert summary.slice_luts_available == 20800
    assert summary.registers_used == 1186
    assert summary.registers_available == 41600


def test_extract_power_report(vivado_path: Path):
    summary = VivadoPowerReport.from_rpt(vivado_path)
    assert type(summary) == VivadoPowerReport
    assert summary.summary.device == 'xc7a35ticsg324-1L'
    assert summary.summary.total_on_chip_power_w == 0.072
    assert len(summary.hierarchy) == 4


def test_extract_all_metrics(vivado_path: Path):
    summary = VivadoMetrics.from_rpt(vivado_path)
    assert type(summary) == VivadoMetrics
    assert summary.device == 'xc7a35ticsg324-1L'
    assert summary.timing.tns == 0.0
    assert summary.timing.tpws == 0.0
    assert summary.power_summary.total_on_chip_power_w == 0.072
    assert len(summary.power_hierarchy) == 4
