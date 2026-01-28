#!/usr/bin/env python3
import json
import subprocess
import sys


def main() -> int:
    try:
        proc = subprocess.run(
            ["conda", "info", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("conda not found on PATH", file=sys.stderr)
        return 1

    if proc.returncode != 0:
        err = proc.stderr.strip() or "conda info --json failed"
        print(err, file=sys.stderr)
        return 1

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        print(f"Failed to parse conda info --json output: {exc}", file=sys.stderr)
        return 1

    platform = data.get("platform")
    if not platform:
        print("unknown")
        return 0
    print(platform)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
