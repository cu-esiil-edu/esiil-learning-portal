import os
import re
import yaml
from pathlib import Path

def extract_yaml_and_body(qmd_path):
    with open(qmd_path, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.match(r"(?s)^---\n(.*?)\n---\n(.*)", content)
    if not match:
        raise ValueError(f"No YAML front matter found in {qmd_path}")

    yaml_str, body = match.groups()
    yaml_data = yaml.safe_load(yaml_str)
    return yaml_data, body

def build_param_code(params):
    # Convert Python values with proper syntax
    return "\n".join(f"{key} = {repr(value)}" for key, value in params.items())

def replace_parameters_cell(body, new_code):
    # Match a python code block with tags: 
    # [parameters] on a `#|` line (can be followed by other `#|` lines too)
    pattern = (
        r"(```\{python\}\n(?:#\|.*\n)*#\|\s*tags:\s*\[parameters\]\s*\n)(.*?)(\n```)"
    )
    new_body, count = re.subn(pattern, r"\1" + new_code + r"\3", body, flags=re.DOTALL)
    if count == 0:
        print("⚠️ No parameters code cell found. Skipping file.")
    return new_body


def sync_params_to_qmd(qmd_path):
    qmd_path = Path(qmd_path)
    if not qmd_path.exists() or qmd_path.suffix != ".qmd":
        return

    try:
        yaml_data, body = extract_yaml_and_body(qmd_path)
    except Exception as e:
        print(f"⚠️ Skipping {qmd_path.name}: {e}")
        return

    params = yaml_data.get("params", {})
    if not params:
        print(f"ℹ️ No params found in {qmd_path.name}.")
        return

    new_code = build_param_code(params)
    new_body = replace_parameters_cell(body, new_code)

    full_content = f"---\n{yaml.dump(yaml_data, sort_keys=False)}---\n{new_body}"
    with open(qmd_path, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"✅ Synced params in {qmd_path}")

def main():
    file_list = os.getenv("QUARTO_PROJECT_INPUT_FILES")
    if not file_list:
        print("❌ QUARTO_PROJECT_INPUT_FILES not set. This should be run as a Quarto pre-render hook.")
        return

    for path in file_list.split("\n"):
        sync_params_to_qmd(path.strip())

if __name__ == "__main__":
    main()
