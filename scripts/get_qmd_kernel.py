#!/usr/bin/env python3
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:  # pragma: no cover
    print(f"PyYAML is required: {exc}", file=sys.stderr)
    sys.exit(1)


def extract_front_matter(text: str) -> str | None:
    lines = text.splitlines()
    if not lines or not lines[0].lstrip().startswith("---"):
        return None
    for i in range(1, len(lines)):
        if lines[i].lstrip().startswith("---"):
            return "\n".join(lines[1:i])
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: scripts/get_qmd_kernel.py <file.qmd>", file=sys.stderr)
        return 1
    path = Path(sys.argv[1])
    try:
        front_matter = extract_front_matter(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    if not front_matter:
        return 0
    data = yaml.safe_load(front_matter) or {}
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
