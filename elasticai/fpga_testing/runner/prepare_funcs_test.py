import numpy as np
import pytest

from .prepare_funcs import DataProcessor


@pytest.fixture
def dp() -> DataProcessor:
    return DataProcessor()


def n_packets(data: bytes, dp: DataProcessor) -> int:
    return len(dp.slice_data_to_packet_size(data))


class TestPreparingDataStreamingArchitecture:
    def test_basic_two_values(self, dp):
        result = dp.preparing_data_streaming_architecture(
            np.array([1, 2]), bit_position_start=1, is_signed=False
        )
        expected = bytes()
        for val in (1, 2):
            expected += dp._data_to_hex(reg=dp._cmds.Write, adr=0, data=val * 1, is_signed=False)
            expected += dp._data_to_hex(reg=dp._cmds.Control, adr=1, data=0, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Control, adr=0, data=0, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Control, adr=0, data=0, is_signed=False)
        assert result == expected

    def test_packet_count_scales_with_signal_length(self, dp):
        for length in (1, 3, 5):
            result = dp.preparing_data_streaming_architecture(
                np.zeros(length), bit_position_start=1, is_signed=False
            )
            assert n_packets(result, dp) == length * 2 + 2

    def test_empty_signal_still_emits_trailing_control_packets(self, dp):
        result = dp.preparing_data_streaming_architecture(
            np.array([]), bit_position_start=1, is_signed=False
        )
        assert n_packets(result, dp) == 2

    def test_bit_position_start_scales_data(self, dp):
        result = dp.preparing_data_streaming_architecture(
            np.array([3]), bit_position_start=4, is_signed=False
        )
        decoded = dp._data_from_hex(dp.slice_data_to_packet_size(result)[0], is_signed=False)
        assert decoded == 3 * 4

    def test_signed_negative_values_roundtrip(self, dp):
        result = dp.preparing_data_streaming_architecture(
            np.array([-2]), bit_position_start=1, is_signed=True
        )
        decoded = dp._data_from_hex(dp.slice_data_to_packet_size(result)[0], is_signed=True)
        assert decoded == -2


class TestPreparingDataCallingArchitecture:
    def test_basic(self, dp):
        result = dp.preparing_data_calling_architecture(num_repeat=2)
        expected = bytes()
        expected += dp._data_to_hex(reg=dp._cmds.Write, adr=0, data=1, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Control, adr=1, data=1, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Control, adr=1, data=1, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Control, adr=0, data=0, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Control, adr=0, data=0, is_signed=False)
        assert result == expected

    def test_packet_count_scales_with_num_repeat(self, dp):
        for num_repeat in (0, 1, 4):
            result = dp.preparing_data_calling_architecture(num_repeat=num_repeat)
            assert n_packets(result, dp) == 1 + num_repeat + 2

    def test_num_repeat_zero_skips_loop_but_keeps_framing(self, dp):
        result = dp.preparing_data_calling_architecture(num_repeat=0)
        expected = bytes()
        expected += dp._data_to_hex(reg=dp._cmds.Write, adr=0, data=1, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Control, adr=0, data=0, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Control, adr=0, data=0, is_signed=False)
        assert result == expected


class TestPreparingDataMemoryWriteArchitecture:
    def test_basic(self, dp):
        result = dp.preparing_data_memory_write_architecture(
            np.array([5, 10]), adr_start=3, bit_position_start=2, is_signed=False
        )
        expected = bytes()
        expected += dp._data_to_hex(reg=dp._cmds.Write, adr=3, data=10, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Write, adr=4, data=20, is_signed=False)
        assert result == expected

    def test_address_increments_per_element(self, dp):
        result = dp.preparing_data_memory_write_architecture(
            np.array([1, 1, 1]), adr_start=10, bit_position_start=1, is_signed=False
        )
        packets = dp.slice_data_to_packet_size(result)
        addresses = [p[0] & 0b0011_1111 for p in packets]
        assert addresses == [10, 11, 12]

    def test_no_trailing_control_packet(self, dp):
        result = dp.preparing_data_memory_write_architecture(
            np.array([1]), adr_start=0, bit_position_start=1, is_signed=False
        )
        assert n_packets(result, dp) == 1


class TestPreparingDataMemoryReadArchitecture:
    def test_basic(self, dp):
        result = dp.preparing_data_memory_read_architecture(
            np.array([5, 10]), adr_start=3, bit_position_start=2, is_signed=False
        )
        expected = bytes()
        expected += dp._data_to_hex(reg=dp._cmds.Read, adr=3, data=10, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Read, adr=4, data=20, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Control, adr=0, data=0, is_signed=False)
        assert result == expected

    def test_has_exactly_one_trailing_control_packet(self, dp):
        result = dp.preparing_data_memory_read_architecture(
            np.array([1, 2, 3]), adr_start=0, bit_position_start=1, is_signed=False
        )
        assert n_packets(result, dp) == 3 + 1


class TestPreparingDataCreatorArchitecture:
    def test_basic_single_layer_group(self, dp):
        result = dp.preparing_data_creator_architecture(
            signal=[1, 2],
            num_input_layer=2,
            num_output_layer=1,
            bit_position_start=1,
            is_signed=False,
        )
        expected = bytes()
        expected += dp._data_to_hex(reg=dp._cmds.Write, adr=18, data=1, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Write, adr=19, data=2, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Write, adr=16, data=1, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Write, adr=16, data=0, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Read, adr=18, data=0, is_signed=False)
        assert result == expected

    def test_multiple_layer_groups_repeat_trigger_block(self, dp):
        result = dp.preparing_data_creator_architecture(
            signal=[1, 2, 3, 4],
            num_input_layer=2,
            num_output_layer=1,
            bit_position_start=1,
            is_signed=False,
        )
        assert n_packets(result, dp) == 2 * 5

    def test_multiple_output_layers(self, dp):
        result = dp.preparing_data_creator_architecture(
            signal=[1, 2],
            num_input_layer=2,
            num_output_layer=3,
            bit_position_start=1,
            is_signed=False,
        )
        packets = dp.slice_data_to_packet_size(result)
        read_packets = [p for p in packets if (p[0] >> 6) == int(dp._cmds.Read)]
        assert len(read_packets) == 3
        addresses = [p[0] & 0b0011_1111 for p in read_packets]
        assert addresses == [18, 19, 20]


class TestPreparingDataArithmeticArchitecture:
    def test_basic_two_packets(self, dp):
        result = dp.preparing_data_arithmetic_architecture(
            signal=[[1, 2], [3, 4]], bit_position_start=1, is_signed=False
        )
        expected = bytes()
        for packet in ([1, 2], [3, 4]):
            for idx, val in enumerate(packet):
                expected += dp._data_to_hex(reg=dp._cmds.Write, adr=idx, data=val, is_signed=False)
            expected += dp._data_to_hex(reg=dp._cmds.Control, adr=1, data=0, is_signed=False)
        expected += dp._data_to_hex(reg=dp._cmds.Control, adr=0, data=0, is_signed=False)
        assert result == expected

    def test_packet_count(self, dp):
        result = dp.preparing_data_arithmetic_architecture(
            signal=[[1, 2, 3]], bit_position_start=1, is_signed=False
        )
        assert n_packets(result, dp) == 3 + 1 + 1

    def test_empty_outer_signal_still_has_final_control(self, dp):
        result = dp.preparing_data_arithmetic_architecture(
            signal=[], bit_position_start=1, is_signed=False
        )
        assert n_packets(result, dp) == 1


class TestPreparingDataReadingSkeletonId:
    def test_default_length(self, dp):
        result = dp.preparing_data_reading_skeleton_id()
        assert n_packets(result, dp) == 16

    def test_custom_length(self, dp):
        result = dp.preparing_data_reading_skeleton_id(length=5)
        expected = bytes()
        for idx in range(5):
            expected += dp._data_to_hex(reg=dp._cmds.Read, adr=idx, data=0, is_signed=False)
        assert result == expected

    def test_addresses_are_sequential(self, dp):
        result = dp.preparing_data_reading_skeleton_id(length=4)
        packets = dp.slice_data_to_packet_size(result)
        addresses = [p[0] & 0b0011_1111 for p in packets]
        assert addresses == [0, 1, 2, 3]

    def test_length_zero_returns_empty_bytes(self, dp):
        result = dp.preparing_data_reading_skeleton_id(length=0)
        assert result == b""
