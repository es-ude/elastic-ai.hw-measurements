from pathlib import Path

from elasticai.fpga_testing import get_path_to_project
from elasticai.fpga_testing.scripts_build import (
    translate_bit_to_bin,
    read_bitstream_file_amd,
    write_bitstream_into_cheader
)


if __name__ == "__main__":
    data = read_bitstream_file_amd(
        Path(get_path_to_project("fpga_design")) / "design_project.runs" / "impl_1" / "TOP_MODULE.bit", False)
    write_bitstream_into_cheader(Path(get_path_to_project()) / "TOP_MODULE.bit", data)

    translate_bit_to_bin(
        path_to_bitstream_folder=Path(get_path_to_project("fpga_design")) / "design_project.runs" / "impl_1",
        path_to_source=Path(get_path_to_project())
    )
