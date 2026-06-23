from pathlib import Path

import pytest

from elasticai.hw_measurements import get_path_to_project

from .copy_template import copy_characterization_template


@pytest.fixture(scope="session", autouse=True)
def path():
    path = get_path_to_project("temp_files")
    yield path


def test_template_copy_adc(path: Path) -> None:
    copy_characterization_template(type="ADC", path2save=path)
    path2file = path / "adc.py"
    assert path2file.exists()


def test_template_copy_amp(path: Path) -> None:
    copy_characterization_template(type="AmP", path2save=path)
    path2file = path / "amp.py"
    assert path2file.exists()


def test_template_copy_dac(path: Path) -> None:
    copy_characterization_template(type="Dac", path2save=path)
    path2file = path / "dac.py"
    assert path2file.exists()


def test_template_copy_noise(path: Path) -> None:
    copy_characterization_template(type="noise", path2save=path)
    path2file = path / "noise.py"
    assert path2file.exists()


def test_template_copy_wrong(path: Path) -> None:
    try:
        copy_characterization_template(type="dump", path2save=path)
    except ValueError:
        assert True
    else:
        assert False
