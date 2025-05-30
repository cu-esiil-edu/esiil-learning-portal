import os
import re
from pathlib import Path

import yaml

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

def extract_yaml(qmd_path):
    # Read in file line by line
    with open(qmd_path, 'r') as qmd_file:
        yaml_lines = []
        for i, line in enumerate(qmd_file.readlines()):
            is_yaml_delineator = line.strip()=='---'
            
            # Make sure the YAML starts on the first line
            if i==0:
                if not is_yaml_delineator:
                    return None
                else:
                    continue
            
            # Accumulate YAML lines
            if not is_yaml_delineator:
                yaml_lines.append(line)
            # Stop at the end of the YAML
            else:
                break

    yaml_header = '\n'.join(yaml_lines)
    yaml_data = yaml.safe_load(yaml_header)
    return yaml_data, yaml_header
