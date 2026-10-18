"""Fail explicitly if AMD tools/configuration are missing; never fake a C-sim pass."""

import argparse
import os
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["csim", "synth", "cosim", "export"], default="csim")
    args = parser.parse_args()
    executable = shutil.which("vitis-run") or shutil.which("vitis_hls")
    if not executable:
        parser.exit(2, "AMD tools not found: no HLS C simulation or synthesis was run.\n")
    for variable in ("HLS_PART", "HLS_CLOCK_NS"):
        if not os.getenv(variable):
            parser.exit(2, f"Set {variable} from your actual toolchain/design before running.\n")
    root = Path(__file__).resolve().parent.parent
    script = str(root / "scripts/run_hls.tcl")
    arguments = (
        ["--mode", "hls", "--tcl", script]
        if Path(executable).name == "vitis-run"
        else ["-f", script]
    )
    environment = {**os.environ, "HLS_STAGE": args.stage}
    return subprocess.run(
        [executable, *arguments], cwd=root, env=environment, check=False
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
