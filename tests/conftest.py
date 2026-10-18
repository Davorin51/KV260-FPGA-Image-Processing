import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def cpp_binary() -> Path:
    subprocess.run(["make", "build/grayscale_cpu"], cwd=ROOT, check=True)
    return ROOT / "build/grayscale_cpu"
