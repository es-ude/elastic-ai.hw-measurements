from pathlib import Path


def read_bitstream_file_amd(path_to_bitstream_file: Path, remove_header: bool = True) -> bytes:
    """Reading the content of a bitstream file (*.bit, *.bin) compiled from AMD Vivado for AMD FPGAs
    :param path_to_bitstream_file:      Path to the bitstream file
    :param remove_header:               Boolean for removing the header information
    :return:                            Byte array with flash content
    """
    if path_to_bitstream_file.suffix not in [".bin", ".bit"]:
        raise ValueError("Bit file must be in binary format")

    data = path_to_bitstream_file.read_bytes()
    if remove_header:
        header = b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
        pos0 = data.find(header)
        if pos0 == -1:
            raise Exception("No padding words")
        sync = b"\xaa\x99\x55\x66"
        pos1 = data.find(sync)
        if pos1 == -1:
            raise Exception("Sync word not found")
        data = data[pos0:]
    return data


def read_bitstream_file_lattice(path_to_bitstream_file: Path) -> bytes:
    """Reading the content of a bitstream file (*.bin) compiled for Lattice FPGAs
    :param path_to_bitstream_file:      Path to the bitstream file
    :return:                            Byte array with flash content
    """
    if path_to_bitstream_file.suffix not in [".bin"]:
        raise ValueError("Bit file must be in binary format (bin)")
    return path_to_bitstream_file.read_bytes()


def write_into_bitstream_file(path_to_file: Path, data: bytes) -> None:
    """Writing the FPGA flash data into new bitstream file (*.bit, *.bin)
    :param path_to_file:    Path to the new generated bitstream file
    :param data:            Byte array with flash content
    :return:                None
    """
    if path_to_file.suffix not in [".bin", ".bit"]:
        raise ValueError("Bit file must be in binary format")

    with open(path_to_file, "wb") as f:
        f.write(data)


def write_into_bitstream_text(path_to_file: Path, data: bytes, add_lines: bool = True) -> None:
    """Writing the FPGA flash into text file in order to read content
    :param path_to_file:    Path to the new generated bitstream file
    :param data:            Byte array with flash content
    :param add_lines:       Boolean for adding line numbers into text file
    :return:                None
    """
    new_file = path_to_file.with_suffix(".txt")
    symbol_per_line = 16
    with open(new_file, "w") as f:
        for i in range(0, len(data), symbol_per_line):
            chunk = data[i : i + symbol_per_line]
            hex_bytes = " ".join(f"{b:02X}" for b in chunk)
            if add_lines:
                f.write(f"{int(i / symbol_per_line):08X}  {hex_bytes}\n")
            else:
                f.write(f"{hex_bytes}\n")


def write_bitstream_into_cheader(path_to_file: Path, data: bytes, symbol_per_line: int = 8) -> None:
    new_file = path_to_file.with_suffix(".h")
    with open(new_file, "w") as f:
        f.write(f"""#include <string.h>
#include <stdio.h>

const uint8_t bitstream[{len(data)}] = {{
""")

        for i in range(0, len(data), symbol_per_line):
            chunk = data[i : i + symbol_per_line]
            hex_bytes = ", ".join(f"0x{b:02X}" for b in chunk)
            f.write(f"\t{hex_bytes}, \n")
        f.write("""};""")


def translate_bit_to_bin(path_to_bitstream_folder: Path, path_to_source: Path) -> list[Path]:
    """Translating a full bitstream file (*.bit) into dedicated file (*.bin) used for direct AMD FPGA flashing
    :param path_to_bitstream_folder:    Path to the generated bitstream file from AMD Vivado
    :param path_to_source:              Path to the new bitstream file
    :return:                            List with paths to bitstream files
    """
    used_bitstream_files = list(path_to_bitstream_folder.glob("*.bit"))

    if len(used_bitstream_files) == 0:
        raise FileNotFoundError(f"No .bitstream files found in {path_to_source}")

    new_path = list()
    for file in used_bitstream_files:
        content = read_bitstream_file_amd(file, remove_header=True)
        new_path.append(path_to_source / f"{file.stem}.bin")
        write_into_bitstream_file(new_path[-1], content)
    return new_path
