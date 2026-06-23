import numpy as np
import pytest

from .plots import (
    get_font_size,
    get_plot_color,
    get_plot_marker,
    save_figure,
    scale_auto_value,
)


class TestGetPlotColor:
    def test_returns_expected_color_for_index(self):
        assert get_plot_color(0) == "k"
        assert get_plot_color(1) == "r"
        assert get_plot_color(7) == "gray"

    def test_wraps_around_when_index_exceeds_list_length(self):
        assert get_plot_color(8) == get_plot_color(0)
        assert get_plot_color(9) == get_plot_color(1)

    def test_returns_string(self):
        assert isinstance(get_plot_color(3), str)


class TestGetFontSize:
    def test_returns_14(self):
        assert get_font_size() == 14

    def test_returns_int(self):
        assert isinstance(get_font_size(), int)


class TestGetPlotMarker:
    def test_returns_expected_marker_for_index(self):
        assert get_plot_marker(0) == "."
        assert get_plot_marker(1) == "+"
        assert get_plot_marker(2) == "x"
        assert get_plot_marker(3) == "_"

    def test_wraps_around_when_index_exceeds_list_length(self):
        assert get_plot_marker(4) == get_plot_marker(0)
        assert get_plot_marker(5) == get_plot_marker(1)

    def test_returns_string(self):
        assert isinstance(get_plot_marker(2), str)


class TestSaveFigure:
    def test_calls_savefig_for_each_format(self, tmp_path):
        calls = []

        class DummyFig:
            def savefig(self, filename, format):
                calls.append((filename, format))

        save_figure(DummyFig(), str(tmp_path), "myplot", formats=("pdf", "svg"))
        assert len(calls) == 2
        assert calls[0][1] == "pdf"
        assert calls[1][1] == "svg"

    def test_creates_path_if_missing(self, tmp_path):
        new_dir = tmp_path / "subdir"

        class DummyFig:
            def savefig(self, filename, format):
                pass

        save_figure(DummyFig(), str(new_dir), "myplot", formats=("pdf",))
        assert new_dir.exists()

    def test_filename_contains_name_and_format(self, tmp_path):
        calls = []

        class DummyFig:
            def savefig(self, filename, format):
                calls.append(filename)

        save_figure(DummyFig(), str(tmp_path), "result", formats=("png",))
        assert calls[0].endswith("result.png")


class TestScaleAutoValue:
    def test_value_around_one(self):
        scale, unit = scale_auto_value(1.0)
        assert scale == pytest.approx(1.0)
        assert unit == ""

    def test_value_in_thousands(self):
        scale, unit = scale_auto_value(2500.0)
        assert unit == "k"

    def test_value_in_millions(self):
        scale, unit = scale_auto_value(2_500_000.0)
        assert unit == "M"

    def test_small_value_in_milli_range(self):
        scale, unit = scale_auto_value(0.005)
        assert unit == "m"

    def test_accepts_numpy_array_uses_max_abs(self):
        scale, unit = scale_auto_value(np.array([-50.0, 200.0, 10.0]))
        assert unit == "k"

    def test_returns_tuple_of_float_and_str(self):
        scale, unit = scale_auto_value(42.0)
        assert isinstance(unit, str)
        assert float(scale) == scale

    def test_scaled_value_reconstructs_original_order_of_magnitude(self):
        scale, unit = scale_auto_value(2500.0)
        scaled_value = 2500.0 * scale
        assert 0.1 <= scaled_value < 1000
