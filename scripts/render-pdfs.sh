set -euo pipefail
set -x

lessons=(
  notebooks/02-flood/flood-stars.qmd
  notebooks/02-flood/flood-download-stars.qmd
  notebooks/03-migration/migration-stars.qmd
  notebooks/03-migration/migration-download-stars.qmd
  notebooks/05-vegetation/vegetation-stars.qmd
  notebooks/05-vegetation/vegetation-download-stars.qmd
  # Shortcourse
  notebooks/01-climate/climate-shortcourse.qmd
  notebooks/01-climate/climate-download-shortcourse.qmd
  notebooks/05-vegetation/vegetation-shortcourse.qmd
  notebooks/05-vegetation/vegetation-download-shortcourse.qmd
  # EDA
  notebooks/01-climate/climate-eda.qmd
  notebooks/01-climate/climate-download-eda.qmd
  #notebooks/03-migration/migration-eda.qmd
  #notebooks/03-migration/migration-download-eda.qmd
)

for f in "${lessons[@]}"; do
  quarto render "$f" --profile release --to pdf
done
