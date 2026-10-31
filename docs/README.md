# FEMS documentation

FEMS is planned as a Windows-only executable application for creating and managing False Echo mods. The application is not available yet; these pages describe the project direction and contribution paths, not existing application behavior.

## Installation and getting started

There is no FEMS executable or installer to download yet. The intended Windows application will be built from Python code into executable files; users will not need to install Python. FEMS will download or bundle required dependencies automatically, without manual setup. Check [GitHub Releases](https://github.com/theveryheavy/FEMS/releases) for a future intentional release.

## User guide

**Planned:** Document installation, first launch, mod management, discovery, and troubleshooting against the actual Windows application once it is available.

## Modding guide

**Planned:** Document supported game content, editing workflows, compatibility, backups, and safe use after these capabilities are implemented and verified.

## Mod developer guide

**Planned:** Document supported mod formats, metadata, testing, versioning, dependencies, and licensing once the application format is established. Until then, follow the repository's [mod contribution guide](../mods/README.md) to submit a catalog entry by pull request.

## Mod submissions and discovery

Mods are submitted directly as pull requests that add or update entries in the [`mods/`](../mods/README.md) directory. The repository does not currently host downloads or provide an application catalog. Read the [mod catalog guide](../mods/README.md) for the directory structure, required metadata, and review process.

Use the [mod catalog issue form](https://github.com/theveryheavy/FEMS/issues/new?template=mod-submission.yml) for questions or to report a broken or potentially malicious listing; it is not a mod submission channel.

## FAQ

**Is FEMS available to install?** Not yet. No application build or release has been published.

**Will I need Python or install dependencies?** No. The intended Windows user build will be executable files, with required dependencies downloaded or bundled automatically. The application is not available yet.

**How do I submit a mod?** Open a pull request adding or updating the mod's directory under `mods/`. Follow [mods/README.md](../mods/README.md).

**Does MIT apply to every mod?** No. MIT applies to the FEMS project. Mod authors choose their own licenses, and third-party material retains its original terms.

## Development and contribution instructions

The FEMS application source is not currently included in this repository. For repository contributions and mod pull requests, see [CONTRIBUTING.md](../CONTRIBUTING.md) and the [mod guide](../mods/README.md).

## Future documentation website

No website or deployment workflow is configured. If a standalone site is needed, [MkDocs with Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) is a lightweight Markdown-based option that can be hosted on GitHub Pages after maintainers intentionally configure it. Future FEMS documentation should use dark backgrounds, minimal typography, industrial and retro-terminal influences, and restrained colors inspired by False Echo. Do not imply official affiliation or use game assets without permission.
