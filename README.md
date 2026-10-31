# FEMS - False Echo Modding Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Latest release](https://img.shields.io/github/v/release/theveryheavy/FEMS?display_name=tag)](https://github.com/theveryheavy/FEMS/releases)
[![Contributors](https://img.shields.io/github/contributors/theveryheavy/FEMS)](https://github.com/theveryheavy/FEMS/graphs/contributors)

FEMS is an unofficial, community-made modding suite for **False Echo**, intended to help players create, manage, discover, and share mods.

## Project status

The application is not currently published in this repository. The intended user distribution is **Windows-only**: the Python application will be built into executable files, so users will not need to install Python. Required dependencies will be downloaded automatically or bundled by FEMS; users will not need to set them up manually. No application release or downloadable executable is available yet.

The project is being prepared for source publication at a later time. The current repository does not contain the toolkit source code.

## Goals

- Make it easier for players and independent developers to create and use mods.
- Provide clear compatibility, dependency, and license information for each mod.
- Review community mod additions through pull requests to the [`mods/`](mods/README.md) directory.
- Keep each mod's ownership and licensing independent from FEMS.

These are project goals, not a claim that the application or catalog is already available.

## Installation and getting started

There is no installer or executable to download yet. When a Windows build is available, this section will link to its installation instructions. Check [GitHub Releases](https://github.com/theveryheavy/FEMS/releases) for an intentional future release.

## Documentation

- [Project and user documentation](docs/README.md)
- [Mod catalog and pull request guide](mods/README.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog and release policy](CHANGELOG.md)
- [Support](SUPPORT.md)
- [Security policy](SECURITY.md)

## Submitting a mod

Submit new mods and mod updates as a pull request that adds or updates a directory under [`mods/`](mods/). Follow the required metadata and review checklist in the [mod contribution guide](mods/README.md). Issues are for questions or reporting a problem with an existing listing; they do not publish mods.

The catalog is community reviewed. A pull request does not guarantee acceptance, and the repository does not currently host or distribute mod downloads. Each mod author retains ownership and chooses the mod's license.

## Releases

FEMS will use Semantic Versioning (`MAJOR.MINOR.PATCH`) for intentional application releases. No release has been published. See [CHANGELOG.md](CHANGELOG.md) for the release policy; nothing is published automatically.

## License and credits

The FEMS project is licensed under the [MIT License](LICENSE), with copyright attributed to The Heavy. This license does not automatically apply to community mods, third-party dependencies, or third-party assets. Contributors must have the right to submit content. See [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) and [CONTRIBUTING.md](CONTRIBUTING.md#licensing-and-contributions).

False Echo and its game content remain the property of their respective owners. FEMS is not an official product of the game developer.
