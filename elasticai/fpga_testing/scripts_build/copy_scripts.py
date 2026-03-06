from pathlib import Path
from shutil import copyfile
from elasticai.fpga_testing import get_path_to_project


def copy_oss_cad_scripts(path_destination: Path | str) -> None:
    if type(path_destination) is str:
        path_used = Path(path_destination)
    else:
        path_used = path_destination
    path_source = Path(get_path_to_project("elasticai")) / "fpga_testing" / "scripts_build" / "oss"
    path_used.mkdir(parents=True, exist_ok=True)
    for file in path_source.glob("*.mk"):
        copyfile(
            src=file.absolute(),
            dst=path_used.absolute() / file.name
        )


if __name__ == "__main__":
    copy_oss_cad_scripts(get_path_to_project("scripts"))


