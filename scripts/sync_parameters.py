import os
import re
import yaml
from pathlib import Path

from parsing import extract_yaml

def build_param_code(params):
    # Convert Python values with proper syntax
    return "\n".join(f"{key} = {repr(value)}" for key, value in params.items())

def replace_parameters_cell(qmd_path, new_code):
    with open(qmd_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Match a python code block with tags: 
    # [parameters] on a `#|` line (can be followed by other `#|` lines too)
    pattern = re.compile(
        # Multiline and dotall mode
        r'(?ms)'
        # Opening fence at BOLs
        r'(^```{python}[^\n]*\r?\n'
        # Any number of Quarto option lines
        r'(?:(?:#\|.*)\r?\n)*'
        # Parameters tags line
        r'\s*#\|\s*tags:\s*\[\s*parameters\s*\]\s*\r?\n)'
        # The cell body (non-greedy)
        r'(.*?)'
        # Closing fence at EOL                  
        r'(\r?\n```[ \t]*$)'                       
    )
    def repl(m):
        start, body, end = m.groups()
        return f"{start}{new_code}{end}"
    updated = pattern.sub(repl, content, count=1)
    
    with open(qmd_path, 'w', encoding='utf-8') as f:
        f.write(updated)
    
    return


def sync_params_to_qmd(qmd_path):
    qmd_path = Path(qmd_path)
    if not qmd_path.exists() or qmd_path.suffix != ".qmd":
        return
        
    try:
        yaml_data, _, _ = extract_yaml(qmd_path)
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
