import os
import re
from pathlib import Path

import yaml

from parsing import get_included_files, extract_yaml


VALID_TYPES = {"overview", "setup", "analysis", "final"}


def qmd_inputs():
    input_files = os.getenv("QUARTO_PROJECT_INPUT_FILES", "")
    if not input_files:
        raise RuntimeError("QUARTO_PROJECT_INPUT_FILES is not set.")

    files = [
        Path(f.strip())
        for f in input_files.split("\n")
        if f.strip().endswith(".qmd")
    ]

    return [
        f for f in files
        if not any("segments" in part for part in f.parts)
        and not f.name.startswith(".")
    ]


def current_profile():
    value = (os.getenv("QUARTO_PROFILE") or "").strip()
    if not value:
        return "default"
    token = re.split(r"[,\s]+", value)[0]
    return token or "default"


def strip_parameters_cell(start_boilerplate):
    # Student builds don't execute code, so keep state-transfer only.
    return re.sub(
        r"\n?```{python}\n#\|\s*echo:\s*false\n#\|\s*eval:\s*true\n#\|\s*tags:\s*\[\s*parameters\s*\]\n```\n?",
        "\n",
        start_boilerplate,
        flags=re.MULTILINE,
    )


def load_manifest(top_file):
    manifest_path = top_file.with_suffix(".segments.yml")
    if not manifest_path.exists():
        return None

    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    segments = data.get("segments")
    if not isinstance(segments, list) or not segments:
        raise ValueError(
            f"{manifest_path} must define a non-empty `segments:` list."
        )
    return data


def infer_segment_type(segment_name, index, total):
    if "0-" in segment_name and "overview" in segment_name:
        return "overview"
    if index == 0:
        return "setup"
    if index == total - 1:
        return "final"
    return "analysis"


def segment_specs(top_file):
    manifest = load_manifest(top_file)
    if manifest:
        specs = []
        for entry in manifest["segments"]:
            include_rel = entry.get("include")
            if not include_rel:
                raise ValueError(
                    f"{top_file.with_suffix('.segments.yml')} has a segment with no `include`."
                )
            include_path = (top_file.parent / include_rel).resolve()
            if not include_path.exists():
                raise FileNotFoundError(
                    f"Segment include not found: {include_path}"
                )
            seg_type = entry.get("type", "analysis")
            if seg_type not in VALID_TYPES:
                raise ValueError(
                    f"Invalid segment type '{seg_type}' for include '{include_rel}'. "
                    f"Expected one of {sorted(VALID_TYPES)}."
                )
            output = entry.get("output", include_path.stem.lstrip("_"))
            specs.append({
                "include": include_path,
                "type": seg_type,
                "output": output,
            })
        return specs

    # Legacy fallback for lessons without a sidecar manifest.
    includes = get_included_files(top_file)[1:]
    if not includes:
        return []
    includes = sorted(includes)
    specs = []
    for i, inc in enumerate(includes):
        name = inc.stem.lstrip("_")
        specs.append({
            "include": inc,
            "type": infer_segment_type(name, i, len(includes)),
            "output": name,
        })
    return specs


def header_lines_for(top_file):
    yaml_data, _, yaml_lines = extract_yaml(top_file)
    if yaml_data is None:
        raise ValueError("missing YAML header")

    params = yaml_data.get("params", {})
    lesson_id = params.get("id")
    if not lesson_id:
        raise ValueError("missing required params.id in YAML header")

    lines = ["---"] + [line.rstrip("\n") for line in yaml_lines] + ["---"]
    return lesson_id, lines


def injected_blocks(seg_type, start_boilerplate, end_boilerplate, finishing_checklist):
    middle = []
    end = [""]

    if seg_type in {"analysis", "final"}:
        middle.extend(["", start_boilerplate, ""])

    if seg_type in {"setup", "analysis"}:
        end = ["", end_boilerplate, ""]
    elif seg_type == "final":
        end = ["", finishing_checklist, ""]

    return middle, end


def write_segments_for(top_file, start_boilerplate, end_boilerplate, finishing_checklist):
    try:
        lesson_id, yaml_lines = header_lines_for(top_file)
    except Exception as exc:
        print(f"⚠️  Skipping {top_file.name}: {exc}")
        return 0

    specs = segment_specs(top_file)
    if not specs:
        print(f"ℹ️  No includes found in {top_file.name}, skipping.")
        return 0

    segment_output_dir = top_file.parent / f"segments-{lesson_id}"
    segment_output_dir.mkdir(exist_ok=True)

    written = 0
    for spec in specs:
        segment_file = Path(spec["include"])
        segment_type = spec["type"]
        output_path = segment_output_dir / f"{spec['output']}.qmd"

        content_lines = segment_file.read_text(encoding="utf-8").splitlines()
        header_index = next(
            (j for j, line in enumerate(content_lines) if line.strip().startswith("##")),
            0,
        )

        content_lines = [
            line.replace("{{< include ", "{{< include ../")
            for line in content_lines
        ]
        pre_header = content_lines[:header_index]
        post_header = content_lines[header_index:]
        middle, end = injected_blocks(
            segment_type, start_boilerplate, end_boilerplate, finishing_checklist
        )

        final_content = "\n".join(yaml_lines + pre_header + middle + post_header + end)
        output_path.write_text(final_content, encoding="utf-8")
        written += 1

    print(f"✅ Wrote {written} segment files to {segment_output_dir}")
    return written


def main():
    boilerplate_dir = Path("boilerplate")
    start_boilerplate = (boilerplate_dir / "start.qmd").read_text(encoding="utf-8").strip()
    end_boilerplate = (boilerplate_dir / "end.qmd").read_text(encoding="utf-8").strip()
    finishing_checklist = (
        boilerplate_dir / "finishing-checklist.qmd"
    ).read_text(encoding="utf-8").strip()

    if current_profile() == "student":
        start_boilerplate = strip_parameters_cell(start_boilerplate).strip()

    total = 0
    for top_file in qmd_inputs():
        total += write_segments_for(
            top_file, start_boilerplate, end_boilerplate, finishing_checklist
        )

    print(f"✅ Segment generation complete: {total} files written.")


if __name__ == "__main__":
    main()
