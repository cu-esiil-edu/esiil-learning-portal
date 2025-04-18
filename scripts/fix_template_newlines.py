from pathlib import Path

def fix_template_spacing(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = content.replace("#| template: answer", "#| template: answer\n")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    for file in Path.cwd().rglob("*.qmd"):
        if all(not part.startswith((".")) for part in file.parts):
            fix_template_spacing(file)

if __name__ == "__main__":
    main()
