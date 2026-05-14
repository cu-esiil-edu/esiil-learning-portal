#!/usr/bin/env python3
"""Check, start, and prepare Ollama for notebook lessons."""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request


OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")


def install_instructions() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return (
            "Install Ollama from a terminal with:\n"
            "  curl -fsSL https://ollama.com/install.sh | sh\n"
            "Then open a new terminal or restart this notebook kernel."
        )
    if system == "windows":
        return (
            "Install Ollama from PowerShell with:\n"
            "  irm https://ollama.com/install.ps1 | iex\n"
            "Or from Git Bash with:\n"
            "  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "
            "\"irm https://ollama.com/install.ps1 | iex\"\n"
            "Then open a new terminal or restart this notebook kernel."
        )
    if system == "linux":
        return (
            "Install Ollama for Linux with:\n"
            "  curl -fsSL https://ollama.com/install.sh | sh\n"
            "Then restart this notebook kernel."
        )
    return "Install Ollama from https://ollama.com/download, then restart this notebook kernel."


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, text=True)


def ollama_bin() -> str | None:
    return shutil.which("ollama")


def install_ollama_linux() -> None:
    if platform.system().lower() != "linux":
        raise RuntimeError("Automatic Ollama installation is only supported on Linux.")
    print("Installing Ollama using the official Linux installer...")
    run(["bash", "-lc", "curl -fsSL https://ollama.com/install.sh | sh"])


def ollama_available() -> bool:
    return ollama_bin() is not None


def server_ready() -> bool:
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


def wait_for_server(timeout: int) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if server_ready():
            return True
        time.sleep(1)
    return False


def start_server(timeout: int) -> None:
    if server_ready():
        print(f"Ollama server is already running at {OLLAMA_URL}.")
        return

    log_path = os.environ.get("OLLAMA_LOG", "ollama.log")
    print(f"Starting Ollama server at {OLLAMA_URL}; logging to {log_path}.")
    log_file = open(log_path, "a", encoding="utf-8")
    subprocess.Popen(
        [ollama_bin() or "ollama", "serve"],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    if not wait_for_server(timeout):
        raise RuntimeError(f"Ollama server did not respond within {timeout} seconds.")
    print("Ollama server is ready.")


def pull_model(model: str) -> None:
    print(f"Ensuring Ollama model is available: {model}")
    run([ollama_bin() or "ollama", "pull", model])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install-if-missing", action="store_true")
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--pull", metavar="MODEL", default="")
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    if not ollama_available():
        auto_install = os.environ.get("OLLAMA_AUTO_INSTALL") == "1"
        if args.install_if_missing and auto_install:
            install_ollama_linux()
        else:
            print("Ollama is not installed or is not on PATH.", file=sys.stderr)
            print(install_instructions(), file=sys.stderr)
            return 1

    if args.start:
        start_server(args.timeout)

    if args.pull:
        pull_model(args.pull)

    print("Ollama setup complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
