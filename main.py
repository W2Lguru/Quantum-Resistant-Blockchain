"""Launch the Streamlit research laboratory UI using the project virtualenv."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _prepare_environment() -> None:
    oqs = ROOT / "third_party" / "liboqs"
    if oqs.exists():
        os.environ.setdefault("OQS_INSTALL_PATH", str(oqs))
        os.environ["PATH"] = str(oqs / "bin") + os.pathsep + os.environ.get("PATH", "")
    os.chdir(ROOT)


def _project_python() -> Path:
    if os.name == "nt":
        candidate = ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = ROOT / ".venv" / "bin" / "python"
    return candidate if candidate.exists() else Path(sys.executable)


def main() -> None:
    _prepare_environment()
    python = _project_python()
    if Path(sys.executable).resolve() != python.resolve():
        raise SystemExit(subprocess.call([str(python), str(ROOT / "main.py"), *sys.argv[1:]]))
    app = ROOT / "ui" / "app.py"
    cmd = [
        str(python),
        "-m",
        "streamlit",
        "run",
        str(app),
        "--server.headless=false",
        "--browser.gatherUsageStats=false",
    ]
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
