# FEMS - False Echo Modding Suite

[![CI](https://github.com/theveryheavy/FEMS/actions/workflows/ci.yml/badge.svg)](https://github.com/theveryheavy/FEMS/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/theveryheavy/FEMS)](https://github.com/theveryheavy/FEMS/graphs/contributors)

FEMS is an open-source toolkit for creating, packaging, managing, and applying community modifications for False Echo. It currently provides a Windows-oriented developer CLI and a companion mod-selection overlay.

FEMS is an unofficial community project, not an official product of the game developer. This repository contains FEMS source and documentation, not the game itself.

## What works today

- Inspect a supported local game build and extract its editable content.
- Edit and export/import localization tables, scaffold campaigns, and edit saves.
- Create, inspect, build, and apply `.femod` packages.
- Patch supported content and selected sprite, texture, and shader resources.
- Install changes to a matching Steam game build with fingerprint checks and backups.
- Queue content mods and launch the game with the F8 companion overlay.

The current build manifest supports only the exact False Echo Demo Steam build identified in [`modkit/fems_supported_build.json`](modkit/fems_supported_build.json). Asset editing requires the optional UndertaleModTool CLI, which FEMS downloads when needed. Font, audio, room, object, and general executable-logic editing are not implemented. See the [toolkit documentation](docs/README.md) for precise limitations.

## Installation and first run

The current source tools are for Windows and require Python 3.10 or later. A game installation is not included; use a copy installed through Steam. The installer refuses game files that do not match the supported-build fingerprints.

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python modkit\fedk.py --game "C:\path\to\False Echo Demo" info
python modkit\fedk.py --game "C:\path\to\False Echo Demo" extract
```

Extraction creates a local working profile under `modkit/project/`; that profile and extracted game resources are intentionally excluded from Git. UndertaleModTool is downloaded on first use and is also excluded.

To create and build a mod, follow the [mod package guide](modkit/docs/MOD_PACKAGES.md). Review the generated changes and keep backups before installing modifications. Use `install_fems.cmd` from the `modkit` directory for the supported Steam installation, and `fems_play.cmd` to launch it with the companion overlay.

The default FEMS source entry point is `python modkit\fedk.py --help`. There is no published standalone installer or release package; no release has been created by this repository setup.

## Documentation

- [Documentation index](docs/README.md)
- [Modding guide](modkit/docs/MODDING_GUIDE.md)
- [Portable mod package guide](modkit/docs/MOD_PACKAGES.md)
- [Content format reference](modkit/docs/CONTENT_FORMAT.md)
- [Technical architecture](modkit/docs/ARCHITECTURE.md)
- [Contributing](CONTRIBUTING.md)
- [Mod submission and catalog process](docs/README.md#mod-submission-and-catalog)
- [Support](SUPPORT.md) | [Security](SECURITY.md)

## Mod discovery and submissions

FEMS does not yet include a hosted catalog or API. Mod authors can request review for a future static community catalog through the [Mod Submission issue form](https://github.com/theveryheavy/FEMS/issues/new?template=mod-submission.yml). Include the metadata, compatibility, license, dependencies, and media described in the [submission guide](docs/README.md#mod-submission-and-catalog). Submissions are reviewed; they are not automatically published or hosted.

Mod creators retain control of their mods and may choose their own licenses. Catalog submission does not transfer ownership or authorize FEMS to relicense or redistribute a mod.

## Contributing

Contributions are welcome from first-time contributors and experienced developers. Start with [CONTRIBUTING.md](CONTRIBUTING.md), review the [Code of Conduct](CODE_OF_CONDUCT.md), and use the [issue tracker](https://github.com/theveryheavy/FEMS/issues) for bugs and proposals. General questions belong in [GitHub Discussions](https://github.com/theveryheavy/FEMS/discussions) once enabled; until then, see [Support](SUPPORT.md).

## License

FEMS source code is licensed under the [MIT License](LICENSE). This does not automatically apply to community mods, third-party dependencies, or third-party assets: each retains its own license and attribution requirements. Contributors must have the right to submit content. See [CONTRIBUTING.md](CONTRIBUTING.md#licensing-and-contributions) and [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

No False Echo executable, game data, extracted game content, bundled game assets, or third-party tool binaries are included. Users are responsible for having a lawful game copy and for respecting the game's and third-party material's applicable terms.

## Credits

FEMS is a community project for False Echo players and mod authors. It uses [Pillow](https://github.com/python-pillow/Pillow) for image handling and [UndertaleModTool](https://github.com/UnderminersTeam/UndertaleModTool) for supported GameMaker asset operations; see [third-party notices](THIRD-PARTY-NOTICES.md). False Echo and related names and assets remain the property of their respective owners.
