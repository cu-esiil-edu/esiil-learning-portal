import os
import re
from pathlib import Path

def get_included_files(file_path, seen=None):
    seen = seen or set()
    seen.add(file_path)
    all_files = [file_path]
    
    include_re = re.compile(r"{{<\s*include\s+([^\s>]+)\s*>}}")
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = include_re.search(line)
            if match:
                include_path = os.path.join(
                    os.path.dirname(file_path), match.group(1))

                if include_path in seen:
                    raise RecursionError(
                        f"Recursive include detected: {include_path}")

                included = get_included_files(include_path, seen)
                all_files.extend(included)

    return [Path(f) for f in all_files]
