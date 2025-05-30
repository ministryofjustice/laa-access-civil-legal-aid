# Deployed documentation docs
These files are used to build the technical documentations using the
[GOV.UK Tech Docs Template](https://github.com/alphagov/tech-docs-template).

The published documentation can be found [here](https://ministryofjustice.github.io/laa-civil-case-api/).

## How to modify the documentation
The docs are build based on the markdown files in `/docs/source/documenation` to modify the published
documentation just modify those files, once your changes have been merged into the main branch they will be published.

## How to build the documentation locally
The makefile contains the commands to spin up a Docker container with the documentation
```bash
cd docs
make preview
```

## How is the documentation published
The `.github/workflows/publish-documenation.yml` workflow is used to publish the documentation using the
[MOJ Tech Docs GitHub Pages Publisher](https://github.com/ministryofjustice/tech-docs-github-pages-publisher) action.