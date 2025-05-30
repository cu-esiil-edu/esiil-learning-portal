import os
import re
import yaml
from pathlib import Path

from parsing import get_included_files, extract_yaml

def build_param_code(params):
    # Convert Python values with proper syntax
    return "\n".join(f"{key} = {repr(value)}" for key, value in params.items())

def replace_parameters_cell(qmd_path, new_code):
    # Match a python code block with tags: 
    # [parameters] on a `#|` line (can be followed by other `#|` lines too)
    pattern = (
        r"(```\{python\}\n(?:#\|.*\n)*"
        r"#\|\s*tags:\s*\[parameters\]\s*\n)(.*?)(\n```)"
    )
    with open(qmd_path, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content, count = re.subn(
        pattern, r"\1" + new_code + r"\3", content, flags=re.DOTALL)
    if count == 0:
        print(f"⚠️ No parameters code cell found. Skipping file {qmd_path}.")
        
    with open(qmd_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return


def sync_params_to_qmd(qmd_path):
    qmd_path = Path(qmd_path)
    if not qmd_path.exists() or qmd_path.suffix != ".qmd":
        return
        
    try:
        yaml_data, _ = extract_yaml(qmd_path)
    except Exception as e:
        print(f"⚠️ Skipping {qmd_path.name}: {e}")
        return

    if not yaml_data:
        print(f"ℹ️ No YAML header found in {qmd_path.name}.")
        return

    params = yaml_data.get("params", {})
    if not params:
        print(f"ℹ️ No params found in {qmd_path.name}.")
        return

    new_code = build_param_code(params)
    
    replace_parameters_cell(qmd_path, new_code)
    
    # Get all included files too
    included_files = get_included_files(qmd_path)
    for file in included_files:
        if file.suffix=='.qmd':
            replace_parameters_cell(file, new_code)
            print(f"✅ Synced parameters in {file}")

    print(f"✅ Synced params in {qmd_path}")

def main():
    file_list = os.getenv("QUARTO_PROJECT_INPUT_FILES")
    if not file_list:
        print("❌ QUARTO_PROJECT_INPUT_FILES not set. "
              "This should be run as a Quarto pre-render hook.")
        return

    for path in file_list.split("\n"):
        sync_params_to_qmd(path.strip())

if __name__ == "__main__":
    main()
