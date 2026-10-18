"""Capture actual discoverable tools; missing tools remain null, never guessed."""

import argparse
import json
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def inspect() -> dict:
    tools = {}
    for name in ("g++", "make", "cmake", "vitis_hls", "vitis-run", "vitis", "vivado"):
        path = shutil.which(name)
        entry = {"path": path, "version_output": None}
        if path:
            try:
                flag = "-version" if name in {"vivado", "vitis_hls"} else "--version"
                result = subprocess.run([path, flag], capture_output=True, text=True, timeout=20)
                entry["version_output"] = (result.stdout + result.stderr).strip()[:4000]
                entry["version_command_exit"] = result.returncode
            except (OSError, subprocess.SubprocessError) as exc:
                entry["error"] = str(exc)
        tools[name] = entry
    return {
        "captured_at_utc": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "python": sys.version,
        "tools": tools,
        "hardware_connected": "not_probed",
        "selected_part": None,
        "clock_constraint_ns": None,
        "hardware_measurements": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = inspect()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
