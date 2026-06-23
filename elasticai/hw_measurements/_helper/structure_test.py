from .structure import get_path_to_project, init_project_folder


def test_path_to_project_basic() -> None:
    checks = ["elastic-ai", "hw-measurements"]
    rslt = get_path_to_project(new_folder="")

    assert rslt.is_dir()
    assert rslt.parts[-1] == f"{checks[0]}.{checks[1]}"


def test_path_to_project_ref() -> None:
    checks = ["elastic-ai", "hw-measurements", "test"]
    rslt = get_path_to_project(new_folder=checks[2])

    assert not rslt.exists()
    assert rslt.parts[-1] == f"{checks[2]}"
    assert rslt.parts[-2] == f"{checks[0]}.{checks[1]}"


def test_creates_runs_and_config_folders():
    init_project_folder(new_folder="temp_build")
    assert (get_path_to_project() / "temp_build" / "runs").is_dir()
    assert (get_path_to_project() / "temp_build" / "config").is_dir()


def test_creates_folders_inside_new_folder():
    init_project_folder(new_folder="temp_build/testrun")
    assert (get_path_to_project() / "temp_build" / "testrun" / "runs").is_dir()
    assert (get_path_to_project() / "temp_build" / "testrun" / "config").is_dir()
