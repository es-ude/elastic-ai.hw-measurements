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
