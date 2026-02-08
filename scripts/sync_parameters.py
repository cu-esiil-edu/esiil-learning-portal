import os
import re
import yaml
from tempfile import NamedTemporaryFile
from pathlib import Path

from parsing import extract_yaml

PARAM_CELL_RE = re.compile(
    r"(?ms)"
    r"(^```{python}[^\n]*\r?\n"
    r"(?:(?:#\|.*)\r?\n)*"
    r"\s*#\|\s*tags:\s*\[\s*parameters\s*\]\s*\r?\n)"
    r"(.*?)"
    r"(\r?\n```[ \t]*$)"
)

CLASS_OPT_RE = re.compile(r"^(\s*#\|\s*)(class|classes)\s*:\s*(.*)$")
TAGS_OPT_RE = re.compile(r"^(\s*#\|\s*)tags\s*:")


def build_param_code(params):
    # Convert Python values with proper syntax
    return "\n".join(f"{key} = {repr(value)}" for key, value in params.items())

def ensure_solution_class(cell_header):
    lines = cell_header.splitlines()
    if not lines:
        return cell_header

    class_idx = None
    class_match = None
    for i, line in enumerate(lines[1:], start=1):
        match = CLASS_OPT_RE.match(line)
        if match:
            class_idx = i
            class_match = match
            break

    if class_match:
        prefix, _, value = class_match.groups()
        if re.search(r"\bsolution-code\b", value):
            return cell_header

        stripped = value.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            inner = stripped[1:-1].strip()
            new_value = f"[{inner}, solution-code]" if inner else "[solution-code]"
        elif stripped:
            token = stripped.strip("'\"")
            new_value = f"[{token}, solution-code]" if token else "[solution-code]"
        else:
            new_value = "[solution-code]"

        lines[class_idx] = f"{prefix}class: {new_value}"
        return "\n".join(lines) + "\n"

    tags_idx = None
    option_prefix = "#| "
    for i, line in enumerate(lines[1:], start=1):
        match = TAGS_OPT_RE.match(line)
        if match:
            tags_idx = i
            option_prefix = match.group(1)
            break

    class_line = f"{option_prefix}class: solution-code"
    if tags_idx is None:
        lines.append(class_line)
    else:
        lines.insert(tags_idx, class_line)

    return "\n".join(lines) + "\n"

def replace_parameters_cell(qmd_path, new_code):
    with open(qmd_path, "r", encoding="utf-8") as f:
        content = f.read()

    matches = list(PARAM_CELL_RE.finditer(content))
    if not matches:
        raise ValueError("No Python parameters cell found (`#| tags: [parameters]`).")
    if len(matches) > 1:
        raise ValueError("Multiple Python parameters cells found; expected exactly one.")

    match = matches[0]
    start, _, end = match.groups()
    updated_start = ensure_solution_class(start)
    replacement = f"{updated_start}{new_code}{end}"
    updated = content[: match.start()] + replacement + content[match.end() :]

    if updated == content:
        return False

    with NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(Path(qmd_path).parent)) as tmp:
        tmp.write(updated)
        tmp_path = Path(tmp.name)

    tmp_path.replace(qmd_path)
    return True


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

    try:
        changed = replace_parameters_cell(qmd_path, new_code)
    except ValueError as e:
        # Some generated student segments intentionally have no parameters code cell.
        if "No Python parameters cell found" in str(e):
            print(f"ℹ️ No Python parameters cell in {qmd_path}; skipping sync.")
            return
        print(f"❌ Failed to sync params in {qmd_path}: {e}")
        raise
    except Exception as e:
        print(f"❌ Failed to sync params in {qmd_path}: {e}")
        raise

    if changed:
        print(f"✅ Synced params in {qmd_path}")
    else:
        print(f"ℹ️ Params already in sync for {qmd_path}")

def main():
    file_list = os.getenv("QUARTO_PROJECT_INPUT_FILES")
    if not file_list:
        print("❌ QUARTO_PROJECT_INPUT_FILES not set. "
              "This should be run as a Quarto pre-render hook.")
        raise SystemExit(1)

    for path in file_list.split("\n"):
        sync_params_to_qmd(path.strip())

if __name__ == "__main__":
    main()
