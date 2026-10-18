import argparse
import csv
import hashlib
import html
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image

from kv260_image.fixtures import fixture
from kv260_image.formats import pack_gray32, pack_rgbx, unpack_gray32
from kv260_image.metrics import compare
from kv260_image.reference import dimensions, grayscale


def load_rgb(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        dimensions(image.height, image.width)
        return np.array(image.convert("RGB"), dtype=np.uint8)


def load_gray(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        dimensions(image.height, image.width)
        if image.mode != "L":
            raise ValueError("Comparison inputs must be 8-bit grayscale (L) images")
        return np.array(image, dtype=np.uint8)


def save_image(data: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(data).save(path)


def demo(output: Path, cpp: Path, rows: int = 64, cols: int = 128, seed: int = 51) -> dict:
    dimensions(rows, cols)
    binary = cpp.resolve()
    if not binary.is_file():
        raise ValueError("C++ CPU binary missing; run make all first")
    # New directory is required so demo runs never clobber earlier outputs.
    output.mkdir(parents=True, exist_ok=False)
    rgb = fixture(rows, cols, seed)
    expected = grayscale(rgb)
    save_image(rgb, output / "input.png")
    save_image(expected, output / "reference.png")
    (output / "input.rgbx").write_bytes(pack_rgbx(rgb))
    (output / "reference.gray32").write_bytes(pack_gray32(expected))
    command = [
        str(binary),
        str(output / "input.rgbx"),
        str(output / "cpu.gray32"),
        str(rows),
        str(cols),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
    actual = unpack_gray32((output / "cpu.gray32").read_bytes(), rows, cols)
    save_image(actual, output / "cpu.png")
    difference = np.abs(expected.astype(np.int16) - actual.astype(np.int16)).astype(np.uint8)
    save_image(difference, output / "difference.png")
    report = {
        "mode": "software_crosscheck",
        "algorithm": "grayscale_fixed_point_v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "rows": rows,
        "cols": cols,
        "seed": seed,
        "comparison": compare(expected, actual),
        "cpp_binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "cpp_stdout": completed.stdout.strip(),
        "hls_csim": "not_run",
        "rtl_cosim": "not_run",
        "hardware": "not_run",
        "hardware_fps": None,
        "synthesis_metrics": None,
    }
    report["files"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.iterdir())
        if p.is_file()
    }
    (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    with (output / "comparison.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["metric", "value"])
        writer.writerows(report["comparison"].items())
    metrics = "".join(
        f"<tr><th>{html.escape(key)}</th><td>{html.escape(str(value))}</td></tr>"
        for key, value in report["comparison"].items()
    )
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Grayscale software verification</title><style>body{{font:16px/1.6 system-ui;max-width:1050px;margin:40px auto;padding:0 22px;color:#172b3b}}h1{{font-size:30px}}.images{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}}img{{width:100%;image-rendering:pixelated;border:1px solid #ccd6df}}figure{{margin:0}}figcaption{{font-size:13px;color:#475569}}th,td{{padding:7px 20px 7px 0;text-align:left;border-bottom:1px solid #ddd}}@media(max-width:650px){{.images{{grid-template-columns:1fr}}}}</style></head><body><p>KV260 FPGA IMAGE PROCESSING / MILESTONE 1</p><h1>Grayscale: software numerical verification</h1><p>Independent NumPy reference versus the compiled portable C++ frame model. Synthetic deterministic input, seed {seed}. No FPGA execution, HLS synthesis or hardware FPS is represented.</p><div class="images"><figure><img src="input.png" alt="Synthetic RGB color bars and seeded ramp"><figcaption>Input: RGBX32, {cols} x {rows}</figcaption></figure><figure><img src="cpu.png" alt="Actual grayscale output from the compiled C++ model"><figcaption>Portable C++ output</figcaption></figure><figure><img src="reference.png" alt="Independent Python reference grayscale"><figcaption>Independent NumPy reference</figcaption></figure><figure><img src="difference.png" alt="Absolute pixel difference; black indicates zero error"><figcaption>Absolute difference, raw 0..255 scale</figcaption></figure></div><h2>Measured numerical differences</h2><table>{metrics}</table><p>PSNR is infinite for an exact match; JSON uses null plus psnr_infinite=true instead of non-standard Infinity. Hardware and synthesis results are unavailable.</p></body></html>"""
    (output / "report.html").write_text(document)
    if not report["comparison"]["exact_match"]:
        raise ValueError("C++ output does not match the independent Python reference")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="KV260 image tools: CPU/reference mode; no board required"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    gray = commands.add_parser("gray", help="Generate the fixed-point Python reference PNG")
    gray.add_argument("input", type=Path)
    gray.add_argument("--output", type=Path, required=True)
    pack = commands.add_parser("pack", help="Pack an image to explicit little-endian RGBX32")
    pack.add_argument("input", type=Path)
    pack.add_argument("--output", type=Path, required=True)
    unpack = commands.add_parser("unpack", help="Decode GRAY8-in-32 output to PNG")
    unpack.add_argument("input", type=Path)
    unpack.add_argument("--rows", type=int, required=True)
    unpack.add_argument("--cols", type=int, required=True)
    unpack.add_argument("--output", type=Path, required=True)
    check = commands.add_parser("compare", help="Compare two L-mode PNGs; nonzero exit on mismatch")
    check.add_argument("reference", type=Path)
    check.add_argument("candidate", type=Path)
    run = commands.add_parser("demo", help="Cross-check the compiled C++ CPU model, not the FPGA")
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--cpp", type=Path, default=Path("build/grayscale_cpu"))
    run.add_argument("--rows", type=int, default=64)
    run.add_argument("--cols", type=int, default=128)
    run.add_argument("--seed", type=int, default=51)
    args = parser.parse_args(argv)
    try:
        if hasattr(args, "input") and args.input.resolve() == args.output.resolve():
            raise ValueError("Input and output paths must differ")
        if args.command == "gray":
            save_image(grayscale(load_rgb(args.input)), args.output)
        elif args.command == "pack":
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(pack_rgbx(load_rgb(args.input)))
        elif args.command == "unpack":
            save_image(unpack_gray32(args.input.read_bytes(), args.rows, args.cols), args.output)
        elif args.command == "compare":
            result = compare(load_gray(args.reference), load_gray(args.candidate))
            print(json.dumps(result, allow_nan=False))
            return 0 if result["exact_match"] else 1
        else:
            result = demo(args.output, args.cpp, args.rows, args.cols, args.seed)
            print(json.dumps(result["comparison"], allow_nan=False))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
