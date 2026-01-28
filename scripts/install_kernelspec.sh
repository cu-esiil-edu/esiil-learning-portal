#!/usr/bin/env bash
set -euo pipefail

ENV_DIR="${ENV_DIR:-environments/base}"
LOCK_DIR="${LOCK_DIR:-environments/locks}"
TOOLS_ENV_NAME="${TOOLS_ENV_NAME:-esiil-tools}"
TOOLS_ENV_FILE="${TOOLS_ENV_FILE:-environments/tools.yml}"
RENDER_INPUT="${QUARTO_RENDER_INPUT:-${QUARTO_INPUT:-}}"
ENV_FILES=()

# Collect environment definition files.
if [[ -d "$ENV_DIR" ]]; then
  while IFS= read -r -d '' file; do
    ENV_FILES+=("$file")
  done < <(find "$ENV_DIR" -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) -print0 | sort -z)
fi

if [[ ${#ENV_FILES[@]} -eq 0 ]]; then
  echo "No environment files found in '$ENV_DIR'." >&2
  exit 1
fi

# Ensure conda is available.
if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found on PATH. Please install conda or activate a shell where conda is available." >&2
  exit 1
fi

# Ensure conda-lock is available, bootstrapping tools env if needed.
if ! command -v conda-lock >/dev/null 2>&1; then
  if [[ ! -f "$TOOLS_ENV_FILE" ]]; then
    echo "conda-lock not found and tools env file missing at '$TOOLS_ENV_FILE'." >&2
    exit 1
  fi
  echo "conda-lock not found. Bootstrapping tools environment '$TOOLS_ENV_NAME' from $TOOLS_ENV_FILE..."
  if env_exists "$TOOLS_ENV_NAME"; then
    conda env update -n "$TOOLS_ENV_NAME" -f "$TOOLS_ENV_FILE"
  else
    conda env create -f "$TOOLS_ENV_FILE"
  fi
  CONDA_LOCK_CMD=(conda run -n "$TOOLS_ENV_NAME" conda-lock)
else
  CONDA_LOCK_CMD=(conda-lock)
fi

mkdir -p "$LOCK_DIR"

# Detect conda-lock output flag (varies by version).
LOCKFILE_FLAG=""
lock_help="$("${CONDA_LOCK_CMD[@]}" lock --help 2>/dev/null || true)"
if [[ "$lock_help" == *"--lockfile"* ]]; then
  LOCKFILE_FLAG="--lockfile"
elif [[ "$lock_help" == *"--output"* ]]; then
  LOCKFILE_FLAG="--output"
elif [[ "$lock_help" == *"-o"* ]]; then
  LOCKFILE_FLAG="-o"
else
  echo "Unable to determine conda-lock output flag. Please upgrade conda-lock." >&2
  exit 1
fi

# Read kernelspec.name from a .qmd YAML header (if present).
env_name_from_file() {
  local file="$1"
  python scripts/get_env_name.py "$file"
}

title_case() {
  echo "$1" | tr '-' ' ' | awk '{for (i=1; i<=NF; i++) $i=toupper(substr($i,1,1)) substr($i,2)}1'
}

# True if env already exists.
env_exists() {
  local env_name="$1"
  conda env list | awk '{print $1}' | grep -qx "$env_name"
}

# True if a kernelspec already exists (checks global dirs if jupyter isn't on PATH).
kernel_exists() {
  local kernel_name="$1"
  if command -v jupyter >/dev/null 2>&1; then
    jupyter kernelspec list 2>/dev/null | grep -qE "^${kernel_name}[[:space:]]"
    return $?
  fi

  [[ -d "${HOME}/.local/share/jupyter/kernels/${kernel_name}" ]] || \
    [[ -d "${HOME}/Library/Jupyter/kernels/${kernel_name}" ]]
}

# If Quarto is rendering a single page, only set up that page's kernel.
if [[ -n "$RENDER_INPUT" && -f "$RENDER_INPUT" ]]; then
  kernel_name=""
  kernel_name="$(python scripts/get_qmd_kernel.py "$RENDER_INPUT")"
  if [[ -z "$kernel_name" ]]; then
    kernel_name="$(python scripts/get_quarto_default_kernel.py _quarto.yml)"
  fi
  if [[ -z "$kernel_name" ]]; then
    echo "Unable to determine kernel name from '$RENDER_INPUT' or _quarto.yml." >&2
    exit 1
  fi

  selected_env_file=""
  for env_file in "${ENV_FILES[@]}"; do
    [[ "$env_file" == "$TOOLS_ENV_FILE" ]] && continue
    env_name="$(env_name_from_file "$env_file")"
    if [[ "$env_name" == "$kernel_name" ]]; then
      selected_env_file="$env_file"
      break
    fi
  done

  if [[ -z "$selected_env_file" ]]; then
    echo "No environment file found for kernel '$kernel_name'." >&2
    exit 1
  fi

  ENV_FILES=("$selected_env_file")
fi

# Create/update envs from lockfiles, then register kernels.
for env_file in "${ENV_FILES[@]}"; do
  if [[ "$env_file" == "$TOOLS_ENV_FILE" ]]; then
    continue
  fi
  env_name="$(env_name_from_file "$env_file")"

  platform="$(python scripts/get_conda_platform.py)"
  lock_file="${LOCK_DIR}/${env_name}-${platform}.yml"

  if [[ -f "$lock_file" ]]; then
    if env_exists "$env_name"; then
      echo "Conda environment '$env_name' already exists. Skipping create."
    else
      echo "Creating conda environment '$env_name' from lockfile $lock_file..."
      "${CONDA_LOCK_CMD[@]}" install -n "$env_name" "$lock_file"
    fi
  else
    echo "Lockfile not found for $env_name ($platform). Creating $lock_file..."
    "${CONDA_LOCK_CMD[@]}" lock -f "$env_file" -p "$platform" "$LOCKFILE_FLAG" "$lock_file"

    if env_exists "$env_name"; then
      echo "Conda environment '$env_name' already exists. Skipping create."
    else
      echo "Creating conda environment '$env_name' from lockfile $lock_file..."
      "${CONDA_LOCK_CMD[@]}" install -n "$env_name" "$lock_file"
    fi
  fi

  if [[ "$env_name" == "$TOOLS_ENV_NAME" ]]; then
    continue
  fi

  if kernel_exists "$env_name"; then
    echo "Kernel '$env_name' already registered. Skipping kernelspec install."
  else
    display_name="$(title_case "$env_name")"
    echo "Registering kernel '$env_name' (display name: '$display_name')..."
    conda run -n "$env_name" python -m ipykernel install --user --name "$env_name" --display-name "$display_name"
  fi
done

echo "Kernel installation complete!"
