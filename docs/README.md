# FEMS documentation

FEMS includes a Windows-oriented developer toolkit. It can inspect, extract, package, and apply modifications for the exact game build recorded in [`modkit/fems_supported_build.json`](../modkit/fems_supported_build.json). The game, extracted data, and generated project profiles are not part of this repository.

## Installation and getting started

Install Python 3.10 or later on Windows, install the Python dependency, and point the CLI to a locally installed, supported game:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python modkit\fedk.py --game "C:\path\to\False Echo Demo" info
python modkit\fedk.py --game "C:\path\to\False Echo Demo" extract
```

The first asset extraction downloads the UndertaleModTool CLI to the ignored `modkit/tools/utmt/` directory. FEMS creates an editable profile under `modkit/project/`; it is local working data and should not be committed. See the [modding guide](../modkit/docs/MODDING_GUIDE.md).

## User guide

The current source provides the `fedk` CLI and, on Windows, a companion F8 overlay for selecting packages. The overlay is launched with `modkit/fems_play.cmd`; it is not a native in-game menu. To see the available CLI commands, run `python modkit\fedk.py --help`. The repository does not include a standalone application build.

## Modding guide

See [Modding guide](../modkit/docs/MODDING_GUIDE.md), [Content format](../modkit/docs/CONTENT_FORMAT.md), and [Architecture](../modkit/docs/ARCHITECTURE.md). The supported capabilities and known limitations are recorded in those guides. In particular, arbitrary game logic changes, audio, fonts, rooms, and objects are not supported by the current automated packer.

## Mod developer guide

Create a workspace with `python modkit\fedk.py --game "<game folder>" mod create --name my-mod`, edit only the files needed in the generated project, and build with `python modkit\fedk.py --game "<game folder>" mod build --name my-mod`. Read the [portable mod package guide](../modkit/docs/MOD_PACKAGES.md) for the `.femod` format, supported paths, integrity checks, application, and compatibility limits. Mods are independently authored and may use their own licenses.

## Mod submission and catalog

FEMS does not yet contain a hosted catalog, registry, or API. The initial proposed discovery system is a static, community-maintained registry reviewed through GitHub.

### Submit a new mod

1. Create, test, and publish the mod at a stable repository or project page you control.
2. Prepare the metadata below and identify the licenses for the mod and its assets.
3. Open a [Mod Submission issue](https://github.com/theveryheavy/FEMS/issues/new?template=mod-submission.yml) and provide the metadata, compatibility information, and screenshots or icon where available.
4. Maintainers validate links and metadata, review the submission, and may request clarification. An issue is a request for review, not an automatic catalog listing.
5. Approved entries may be added to a static catalog once it exists. Until then, approval does not make the mod discoverable or installable through FEMS.
6. Users will be able to discover and access approved entries through FEMS only after a catalog feature is implemented. Mod authors remain responsible for their own releases and downloads.

### Expected metadata

| Field | Expected value |
|---|---|
| Unique mod ID | Stable identifier, preferably lowercase with hyphens, such as `example-mod`. |
| Name and description | Display name and concise explanation of the mod. |
| Author | Individual or organization responsible for the mod. |
| Repository URL | Public source or project page controlled by the developer. |
| Download URL | Direct or release-page link, if applicable. |
| Version | Current mod version; SemVer is recommended where appropriate. |
| License | SPDX identifier or license name and a link to its text. |
| Supported game versions | Explicit False Echo versions, or say if not verified. |
| Supported FEMS versions | Explicit FEMS versions, or say if not verified. |
| Categories and tags | Short, useful discovery labels. |
| Dependencies | Required or optional mods/tools and versions, or `None`. |
| Screenshots and icon | Links to representative media, if available and authorized for submission. |

This is a documentation contract, not an implemented schema or API.

### Update, remove, or report a mod

Use the same [Mod Submission issue form](https://github.com/theveryheavy/FEMS/issues/new?template=mod-submission.yml) and identify the stable mod ID. For an update, include changed metadata and compatibility information. For removal, say whether the mod is withdrawn, moved, or no longer maintained. To report a broken or potentially malicious mod, do not install or run it; include its ID, link, and observed issue without sharing private data or harmful files. For vulnerabilities in FEMS itself, use the private reporting route in [SECURITY.md](../SECURITY.md).

Mod authors choose their own licenses. FEMS's MIT license does not apply to independent mods or third-party assets, and catalog inclusion does not transfer copyright, authorize redistribution, or imply endorsement. Submit only metadata and media you have the right to share.

## FAQ

**Is FEMS an official False Echo product?** No. It is an unofficial community project.

**Does this repository include the game or extracted assets?** No. It includes the toolkit source and technical guides only. A compatible game installation is required for operations on game files.

**Can I use a different game build?** The installer checks the exact fingerprints in the supported build manifest and rejects unrecognized builds. Do not bypass these checks; update support requires a reviewed profile for the new build.

**Can I install mods from an FEMS catalog?** Not yet. The catalog is planned, not implemented.

**Does MIT apply to every mod or dependency?** No. FEMS source uses MIT; mods, dependencies, and third-party assets retain their own licenses.

## Development and contribution instructions

See [CONTRIBUTING.md](../CONTRIBUTING.md) for setup, checks, and contribution guidance. The repository CI checks Python syntax and command-line help without needing game files or downloads.

## Documentation website

There is no website or deployment workflow. If a standalone site is needed later, [MkDocs with Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) is a lightweight Markdown-based option that can be hosted on GitHub Pages after maintainers intentionally configure it. Future FEMS web documentation should use dark backgrounds, minimal typography, industrial and retro-terminal influences, and restrained colors inspired by False Echo. Do not imply official affiliation or use game assets without permission.
