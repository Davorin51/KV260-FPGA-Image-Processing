import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from kv260_image.cli import load_gray, main
from PIL import Image


def test_cli_reference_pack_unpack_compare(tmp_path, capsys):
    rgb = tmp_path / "rgb.png"
    gray = tmp_path / "gray.png"
    packed = tmp_path / "rgb.bin"
    decoded = tmp_path / "decoded.png"
    Image.fromarray(np.array([[[255, 0, 0]]], dtype=np.uint8)).save(rgb)
    assert main(["gray", str(rgb), "--output", str(gray)]) == 0
    assert main(["pack", str(rgb), "--output", str(packed)]) == 0
    assert packed.read_bytes() == bytes([255, 0, 0, 0])
    raw = tmp_path / "gray.bin"
    raw.write_bytes(bytes([77, 0, 0, 0]))
    assert main(["unpack", str(raw), "--rows", "1", "--cols", "1", "--output", str(decoded)]) == 0
    assert main(["compare", str(gray), str(decoded)]) == 0
    assert json.loads(capsys.readouterr().out)["exact_match"]
    Image.fromarray(np.array([[78]], dtype=np.uint8)).save(decoded)
    assert main(["compare", str(gray), str(decoded)]) == 1
    with pytest.raises(ValueError):
        load_gray(rgb)
    with pytest.raises(SystemExit) as error:
        main(["gray", str(rgb), "--output", str(rgb)])
    assert error.value.code == 2
    with pytest.raises(SystemExit):
        main(["gray", str(tmp_path / "missing"), "--output", str(gray)])


def test_cli_demo_and_module_entry(cpp_binary, tmp_path):
    assert main(["demo", "--cpp", str(cpp_binary), "--output", str(tmp_path / "demo")]) == 0
    result = subprocess.run(
        [sys.executable, "-m", "kv260_image", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0 and "CPU/reference" in result.stdout


def test_optional_hls_runner_fails_explicitly_without_tools(tmp_path):
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "scripts/run_hls.py"), "--stage", "csim"],
        env={"PATH": str(tmp_path)},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2 and "no HLS C simulation" in result.stderr
