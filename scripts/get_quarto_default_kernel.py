#!/usr/bin/env python3
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:  # pragma: no cover
    print(f"PyYAML is required: {exc}", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: scripts/get_quarto_default_kernel.py <_quarto.yml>", file=sys.stderr)
        return 1
    path = Path(sys.argv[1])
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    name = (
        data.get("jupyter", {})
        .get("kernelspec", {})
        .get("name")
    )
    if name:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
