from pathlib import Path

from elasticai.fpga_testing import get_path_to_project
from elasticai.fpga_testing.scripts_build import (
    translate_bit_to_bin
)


if __name__ == "__main__":
    translate_bit_to_bin(
        path_to_bitstream_folder=Path(get_path_to_project("fpga_design")) / "design_project.runs" / "impl_1",
        path_to_source=Path(get_path_to_project())
    )
