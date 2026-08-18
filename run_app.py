from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
VENV_DIR = ROOT_DIR / ".venv"
REQUIREMENTS_FILE = ROOT_DIR / "requirements.txt"
HOST = "127.0.0.1"
PORT = "8000"

REQUIRED_MODULES = ("fastapi", "uvicorn", "multipart", "pypdf", "jinja2")


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def current_python_is_venv() -> bool:
    return Path(sys.prefix).resolve() == VENV_DIR.resolve()


def missing_modules() -> list[str]:
    return [module for module in REQUIRED_MODULES if importlib.util.find_spec(module) is None]


def run_command(command: list[str]) -> None:
    print("$", " ".join(command), flush=True)
    subprocess.check_call(command, cwd=ROOT_DIR)


def ensure_venv() -> None:
    if current_python_is_venv():
        return

    python_bin = venv_python()
    if not python_bin.exists():
        print("Membuat virtual environment lokal di .venv ...")
        run_command([sys.executable, "-m", "venv", str(VENV_DIR)])

    print("Menjalankan ulang aplikasi memakai Python di .venv ...")
    os.execv(str(python_bin), [str(python_bin), str(Path(__file__).resolve())])


def ensure_dependencies() -> None:
    modules = missing_modules()
    if not modules:
        return

    print("Menginstall dependency aplikasi. Ini hanya perlu dilakukan pertama kali ...")
    print("Dependency yang belum ada:", ", ".join(modules))
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run_command([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])


def open_browser_later() -> None:
    time.sleep(1.5)
    webbrowser.open(f"http://{HOST}:{PORT}")


def main() -> None:
    if sys.version_info < (3, 10):
        raise SystemExit("Python minimal 3.10 diperlukan. Disarankan Python 3.14.")

    ensure_venv()
    ensure_dependencies()

    import threading

    threading.Thread(target=open_browser_later, daemon=True).start()
    run_command([
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        HOST,
        "--port",
        PORT,
    ])


if __name__ == "__main__":
    main()
