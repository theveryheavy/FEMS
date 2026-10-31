# FEMS documentation

FEMS is planned as a Windows application for making and managing False Echo mods. It is not available to download yet, so the guides for using the app will come later.

## Installation

There is no installer or `.exe` yet. The plan is to distribute Windows executables that don't require users to install Python or configure dependencies. FEMS will bundle or download what it needs.

## User and modding guides

Guides for installing FEMS, using its features, making mods, and troubleshooting will be added when those features are ready. The current repository does not include application source or a modding SDK.

## Submitting a mod

Add a mod by opening a pull request in [`mods/`](../mods/README.md). The guide explains the directory layout and metadata to include. FEMS does not host mod downloads, and there is no in-app catalog yet.

Use the [mod catalog issue form](https://github.com/theveryheavy/FEMS/issues/new?template=mod-submission.yml) to ask a question or report a broken or potentially malicious listing. Do not use it to submit a mod.

## FAQ

**Can I download FEMS now?** Not yet. No application or release is available.

**Will I need Python?** No. The plan is to distribute Windows `.exe` files and handle dependencies automatically.

**How do I submit a mod?** Open a pull request adding or updating its directory under [`mods/`](../mods/README.md).

**Does MIT apply to every mod?** No. MIT applies to the FEMS project. Mod authors choose their own licenses.

## Website

There is no documentation website yet. If one is needed, [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) is a lightweight option that can be hosted on GitHub Pages. Any future site should use FEMS's dark, minimal, industrial and retro-terminal style without implying that FEMS is an official False Echo product or using game assets without permission.
