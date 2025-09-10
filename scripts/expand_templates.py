import os
import re
from pathlib import Path

from parsing import get_included_files, extract_yaml

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
    },
    "hidden-answer": {
        "echo": "false",
        "eval": "true",
        "class": "answer-code",
        "highlight": "true"
    },
}

DEFAULT_HIDE_SOLUTIONS = dict(
            default=False,
            portal=False,
            release=False,
            student=True
        )
def expand_template_lines(template_name):
    return "\n".join(f"#| {k}: {v}" for k, v in TEMPLATES[template_name].items())

def process_file(path, hide_solutions=False):
    
    def replace_template(match, hide_solutions=hide_solutions):
        template_name = match.group(1)
        if hide_solutions and template_name=='answer':
            template_name = 'hidden-answer'
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
    profile = os.getenv("QUARTO_PROFILE", "default")
    print(f'Profile: {profile}')
    files = os.getenv("QUARTO_PROJECT_INPUT_FILES", "").split("\n")
    included_files = []
    for file in files:
        file = Path(file.strip())
        header, _, _ = extract_yaml(file)
        hide_solutions = DEFAULT_HIDE_SOLUTIONS[profile]
        if header:
            if 'hide-solutions' in header:
                if profile in header['hide-solutions']:
                    hide_solutions = header['hide-solutions'][profile]
        included_files.extend(
            [(file, hide_solutions) for  file in get_included_files(file)]
        )
        included_files.append((file, hide_solutions))
    for file, hide_solutions in included_files:
        if file.suffix==".qmd":
            process_file(file, hide_solutions)
            print(f"✅ Expanded code execution templates in {file}")

if __name__ == "__main__":
    main()
