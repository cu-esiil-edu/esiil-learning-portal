import os
from pathlib import Path
import re

from parsing import get_included_files, extract_yaml

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
    # Get lesson id
    yaml_data, _, yaml_lines = extract_yaml(top_file)
    if yaml_data is None:
        print(f"⚠️  Skipping {top_file.name}: missing YAML header")
        continue
    if 'params' in yaml_data:
        try:
            lesson_id = yaml_data['params']['id']
        except KeyError:
            print(f"⚠️  Skipping {top_file.name}:"
                  " missing required id parameter in YAML header")
            continue
        
    yaml_lines = ['---'] + [line[:-1] for line in yaml_lines] + ['---']

    # Find included files
    included_files = get_included_files(top_file)[1:]
    nested_included_files = []
    for f in included_files:
        nested_included_files.extend(get_included_files(f)[1:])
        for g in nested_included_files:
            nested_included_files.extend(get_included_files(g)[1:])
        
    if not included_files:
        print(f"ℹ️  No includes found in {top_file.name}, skipping.")
        continue
    included_files.sort()

    # Prepare output directory
    segment_output_dir = top_file.parent / f"segments-{lesson_id}"
    segment_output_dir.mkdir(exist_ok=True)

    for i, segment_file in enumerate(included_files):
        segment_name = segment_file.stem.lstrip("_")
        output_path = segment_output_dir / f"{segment_name}.qmd"

        content_lines = segment_file.read_text(encoding="utf-8").splitlines()
        header_index = next((
            j for j, line in enumerate(content_lines) 
            if line.strip().startswith("##")), 0)
            
        # Fix paths for includes
        content_lines = [
            line.replace('{{< include ', '{{< include ../')
            for line in content_lines]

        pre_header = content_lines[:header_index]
        post_header = content_lines[header_index:]

        middle = []
        if i != 0:
            middle.append("")
            middle.append(start_boilerplate)
            middle.append("")

        end = ["", end_boilerplate, ""]

        final_content = "\n".join(
             yaml_lines + pre_header + middle + post_header + end
        )

        output_path.write_text(final_content, encoding="utf-8")
        segment_count += 1
    
    print(f"✅ Wrote {segment_count} segment files to {segment_output_dir}")
