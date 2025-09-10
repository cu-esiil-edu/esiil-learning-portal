import os
import re
from pathlib import Path
from expand_templates import TEMPLATES

def parse_metadata_block(block):
    lines = block.strip().split("\n")
    kv = {}
    for line in lines:
        if line.strip().startswith("#|"):
            key_val = line.strip()[2:].strip().split(":", 1)
            if len(key_val) == 2:
                k, v = key_val
                kv[k.strip()] = v.strip()
    return kv, block

def compress_block(block):
    kv, original = parse_metadata_block(block)
    for template_name, settings in TEMPLATES.items():
        if kv == settings:
            if template_name=='hidden-answer':
                template_name = 'answer'
            return "#| template: " + template_name + "\n"
    return block

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace matching full metadata blocks with template line
    def replacer(match):
        return compress_block(match.group(0))

    updated = re.sub(r"((#\|\s*[\w\-]+:\s*.*\n?)+)", replacer, content)
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)

from pathlib import Path

def is_visible_qmd(file: Path) -> bool:
    parts = file.parts
    # Exclude any file or folder that starts with .
    return all(not part.startswith((".")) for part in parts) and file.suffix == ".qmd"

def main():
    project_root = Path.cwd()
    files = [f for f in project_root.rglob("*.qmd") if is_visible_qmd(f)]

    print(f"Restoring files: {len(files)} .qmd files found")

    for file in files:
        process_file(file)

    print("✅ Compressed code execution templates")



if __name__ == "__main__":
    main()
