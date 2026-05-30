# Earth Analytics Lessons  

This repo contains all of the courses, lessons, workshop materials and blogposts
that support the earthdatascience.org website. 

## Conda environments

This project uses per-platform lockfiles for reproducible builds. Author-provided
environment files live in `environments/`, and lockfiles are generated into
`environments/locks/`. The site build runs `scripts/install_kernelspec.sh`, which
creates lockfiles as needed and installs environments from those lockfiles.

To bootstrap the lockfile tooling:

```bash
conda env create -f environments/tools.yml
```

## GitHub Actions workflows

The site uses one reusable build workflow plus several small entry-point
workflows. Most editors should use the entry-point workflows and avoid calling
the reusable build directly.

| Workflow | File | When it runs | Purpose |
| --- | --- | --- | --- |
| Quarto Publish | `.github/workflows/publish-from-cache.yml` | Pushes to `main`, plus manual runs | Publish from existing frozen/cached execution. If a push includes files under `notebooks/`, the workflow starts but skips the build. |
| Quarto Warm Execution Cache | `.github/workflows/release-notebook-development.yml` | Pushes to `main` that touch `notebooks/**`, plus manual runs | Run notebooks as needed, allow external execution dependencies such as Ollama, save execution cache, and deploy if the render succeeds. |
| Quarto Validate Environments | `.github/workflows/validate-environments.yml` | Monthly schedule, plus manual runs | Clear conda environment cache and lockfiles, then rebuild environments without intentionally refreshing notebook execution. Deploys if the render succeeds. |
| Quarto Validate Fresh Execution | `.github/workflows/validate-execution.yml` | Monthly schedule, plus manual runs | Clear Quarto/Jupyter execution cache and rerun notebooks against live external services without rebuilding conda environments. Does not deploy. |
| Quarto Build (Reusable) | `.github/workflows/00-site-build.yml` | Called by the other workflows | Shared checkout, cache restore/save, environment setup, Quarto render, and optional deploy logic. |

Recommended release flow for notebook changes:

1. Push notebook edits to `main`.
2. Let `Quarto Warm Execution Cache` run. It may need more than one run if
   external APIs or network downloads are flaky.
3. If needed, manually rerun `Quarto Warm Execution Cache`; it keeps the
   execution cache unless you explicitly use a validation workflow that clears
   it.
4. Once the warm execution workflow succeeds, the site deploys.

Recommended release flow for non-notebook changes:

1. Push edits to `main`.
2. `Quarto Publish` deploys from existing cache/freeze state and does not allow
   automatic Ollama installation.

Environment changes:

- Pushes that include files under `environments/**` automatically clear cached
  conda environments and generated lockfiles before rendering.
- Manual environment validation is available through `Quarto Validate
  Environments`.
- Manual fresh notebook validation is available through `Quarto Validate Fresh
  Execution`; use it when you want to prove notebooks still run from scratch.
