import os
import re
from pathlib import Path

from parsing import get_included_files

TEMPLATES = {
    "student": {
        "echo": "true",
        "eval": "false",
        "class": "student-code",
        "highlight": "true"
    },
    "answer": {
        "echo": "true",
        "eval": "true",
        "code-fold": "true",
        "code-summary": "See our solution!",
        "class": "answer-code",
        "highlight": "true"
    }
}

def expand_template_lines(template_name):
    return "\n".join(f"#| {k}: {v}" for k, v in TEMPLATES[template_name].items())

def process_file(path):
    
    def replace_template(match):
        template_name = match.group(1)
        if template_name not in TEMPLATES:
            return match.group(0)
        return expand_template_lines(template_name)
    
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    updated = re.sub(
        r"^#\|\s*template:\s*(\w+)\s*$", replace_template, text,
        flags=re.MULTILINE)
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)

def main():
    files = os.getenv("QUARTO_PROJECT_INPUT_FILES", "").split("\n")
    included_files = []
    for file in files:
        file = Path(file.strip())
        included_files.extend(get_included_files(file))
        included_files.append(file)
    for file in included_files:
        if file.suffix==".qmd":
            process_file(file)
            print(f"✅ Expanded code execution templates in {file}")

if __name__ == "__main__":
    main()
