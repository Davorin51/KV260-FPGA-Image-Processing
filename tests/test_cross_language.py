import json
import subprocess

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from kv260_image.cli import demo
from kv260_image.fixtures import fixture
from kv260_image.formats import pack_rgbx, unpack_gray32
from kv260_image.reference import grayscale


def run_cpp(binary, directory, image):
    source = directory / "input.rgbx"
    result = directory / "output.gray32"
    source.write_bytes(pack_rgbx(image))
    process = subprocess.run(
        [str(binary), str(source), str(result), str(image.shape[0]), str(image.shape[1])],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert process.returncode == 0, process.stderr
    actual = unpack_gray32(result.read_bytes(), image.shape[0], image.shape[1])
    np.testing.assert_array_equal(actual, grayscale(image))
    return actual


@pytest.mark.parametrize(
    "rows,cols", [(1, 1), (1, 37), (29, 1), (2, 2), (13, 17), (64, 128), (1080, 1920)]
)
def test_cpp_matches_independent_reference(cpp_binary, tmp_path, rows, cols):
    run_cpp(cpp_binary, tmp_path, fixture(rows, cols, pattern="random"))


@settings(max_examples=25, deadline=None)
@given(
    st.lists(
        st.tuples(st.integers(0, 255), st.integers(0, 255), st.integers(0, 255)),
        min_size=1,
        max_size=50,
    )
)
def test_cpp_randomized_crosscheck(cpp_binary, pixels):
    from pathlib import Path
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as folder:
        run_cpp(cpp_binary, Path(folder), np.array([pixels], dtype=np.uint8))


def test_cpu_rejects_malformed_input_and_dimensions(cpp_binary, tmp_path):
    source = tmp_path / "in"
    destination = tmp_path / "out"
    for contents in [b"", b"\0" * 3, b"\0" * 5]:
        source.write_bytes(contents)
        result = subprocess.run(
            [str(cpp_binary), str(source), str(destination), "1", "1"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1 and "Input" in result.stderr
        assert not destination.exists()
    source.write_bytes(b"\0" * 4)
    for rows, cols in [
        ("0", "1"),
        ("1081", "1"),
        ("1", "1921"),
        ("-1", "1"),
        ("1.5", "2"),
        ("4294967296", "1"),
    ]:
        result = subprocess.run(
            [str(cpp_binary), str(source), str(destination), rows, cols],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
    result = subprocess.run(
        [str(cpp_binary), str(source), str(source), "1", "1"], capture_output=True
    )
    assert result.returncode == 1
    assert source.read_bytes() == b"\0" * 4
    assert subprocess.run([str(cpp_binary)], capture_output=True).returncode == 1
    assert (
        subprocess.run(
            [str(cpp_binary), str(tmp_path / "missing"), str(destination), "1", "1"],
            capture_output=True,
        ).returncode
        == 1
    )
    assert (
        subprocess.run(
            [str(cpp_binary), str(source), str(tmp_path / "missing_dir/out"), "1", "1"],
            capture_output=True,
        ).returncode
        == 1
    )


def test_demo_report_comes_from_cpp_and_is_not_hardware(cpp_binary, tmp_path):
    output = tmp_path / "demo"
    report = demo(output, cpp_binary, 13, 17, 51)
    saved = json.loads((output / "report.json").read_text())
    assert report == saved
    assert saved["comparison"]["exact_match"]
    assert saved["hardware_fps"] is None and saved["hardware"] == "not_run"
    assert saved["hls_csim"] == "not_run" and saved["synthesis_metrics"] is None
    assert len(saved["cpp_binary_sha256"]) == 64
    assert (output / "comparison.csv").is_file() and (output / "report.html").is_file()
    with pytest.raises(FileExistsError):
        demo(output, cpp_binary)
    with pytest.raises(ValueError):
        demo(tmp_path / "unused", tmp_path / "missing")
