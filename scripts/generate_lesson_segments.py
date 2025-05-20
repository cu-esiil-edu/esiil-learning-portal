import os
from pathlib import Path
import re

from parsing import get_included_files

# Read Quarto input files
input_files = os.getenv("QUARTO_PROJECT_INPUT_FILES", "")
if not input_files:
    raise RuntimeError("QUARTO_PROJECT_INPUT_FILES is not set.")

# Parse the list of files (comma-separated paths)
qmd_files = [
    Path(f.strip()) 
    for f in input_files.split("\n") 
    if f.strip().endswith(".qmd")]

# Skip files already in 'segments/' or hidden files
qmd_files = [
    f for f in qmd_files 
    if "segments" not in f.parts and not f.name.startswith(".")]

# Load boilerplate
boilerplate_dir = Path("boilerplate")
start_boilerplate = (
    boilerplate_dir / "start.qmd").read_text(encoding="utf-8").strip()
end_boilerplate = (
    boilerplate_dir / "end.qmd").read_text(encoding="utf-8").strip()

segment_count = 0

for top_file in qmd_files:
    lines = top_file.read_text(encoding="utf-8").splitlines()
    if not lines:
        continue

    # Extract YAML front matter
    if lines[0].strip() == "---":
        end_idx = lines.index("---", 1)
        yaml_header = "\n".join(lines[:end_idx + 1])
        rest = lines[end_idx + 1:]
    else:
        print(f"⚠️  Skipping {top_file.name}: missing YAML front matter")
        continue

    # Find included files
    included_files = get_included_files(top_file)[1:]
    if not included_files:
        print(f"ℹ️  No includes found in {top_file.name}, skipping.")
        continue
    print(included_files)
    included_files.sort()

    # Prepare output directory
    segment_output_dir = Path(os.path.dirname(top_file), "segments")
    segment_output_dir.mkdir(exist_ok=True)

    for i, file_name in enumerate(included_files):
        segment_file = Path(file_name)
        segment_name = segment_file.stem.lstrip("_")
        output_path = segment_output_dir / f"{segment_name}.qmd"

        content_lines = segment_file.read_text(encoding="utf-8").splitlines()
        header_index = next((
            j for j, line in enumerate(content_lines) 
            if line.strip().startswith("##")), 0)

        pre_header = content_lines[:header_index]
        post_header = content_lines[header_index:]

        middle = []
        if i != 0:
            middle.append("")
            middle.append(start_boilerplate)
            middle.append("")

        end = ["", end_boilerplate, ""]

        final_content = "\n".join(
            [yaml_header, ""] + pre_header + middle + post_header + end
        )

        output_path.write_text(final_content, encoding="utf-8")
        segment_count += 1

print(f"✅ Wrote {segment_count} segment files to {segment_output_dir}")
