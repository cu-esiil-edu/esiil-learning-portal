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
