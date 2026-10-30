# FEMS documentation

FEMS is an early-stage project. This index describes the guides the project needs and distinguishes current repository guidance from application documentation that cannot be accurate until an application is released.

## Installation

**Not available yet:** There is no published FEMS application or supported installation method. Check [GitHub Releases](https://github.com/theveryheavy/FEMS/releases) for future packages. A source checkout is not currently an installable product.

## Getting started

**Not available yet:** There is no released app to configure or run. When one is available, this guide should cover prerequisites, installation, first launch, and how to verify the installation.

## User guide

**Planned:** Document the implemented workflows for managing, discovering, and accessing mods. Do not rely on these features until they are released and documented against the actual application.

## Modding guide

**Planned:** Document the supported game mod format, tools, packaging rules, compatibility expectations, and safe installation practices after those are established by the application.

## Mod developer guide

**Planned:** Explain how to create, test, version, package, license, and publish an independent mod. No FEMS-specific mod SDK or package format is defined yet.

## Mod submission and catalog

The catalog is planned as a static, community-maintained registry. There is no operational catalog yet, and an issue submission does not make a mod discoverable automatically.

### Submit a new mod

1. Create, test, and publish your mod in a repository or other stable location that you control.
2. Prepare the metadata below and decide which license applies to the mod and its assets.
3. Open a [Mod Submission issue](https://github.com/theveryheavy/FEMS/issues/new?template=mod-submission.yml), choose a new submission, and provide the metadata, compatibility details, and screenshots or icon where available.
4. Maintainers validate that the links and metadata are usable, review compatibility and licensing information, and may ask you to clarify or change the submission.
5. Approved entries can be added to the official static FEMS mod catalog when it is implemented. Until then, approval does not mean users can discover or install the mod through FEMS.
6. FEMS users will be able to discover and access approved entries through the catalog once that feature is released. The developer's published project remains the source of the mod.

### Expected mod metadata

Each catalog entry is expected to contain:

| Field | Expected value |
|---|---|
| Unique mod ID | Stable, unique identifier, preferably lowercase with hyphens (for example, `example-mod`). |
| Name and description | Display name and concise explanation of what the mod changes. |
| Author | Individual or organization responsible for the mod. |
| Repository URL | Public source or project page controlled by the developer. |
| Download URL | Direct or release-page link, if downloads are published separately. |
| Version | Current mod version, preferably SemVer if appropriate. |
| License | SPDX identifier or clear license name and a link to its text. |
| Supported game versions | Explicit False Echo versions, or a clear statement if not yet verified. |
| Supported FEMS versions | Explicit FEMS versions, or a clear statement that compatibility is not yet verified. |
| Categories and tags | Short, useful discovery labels. |
| Dependencies | Required or optional mods/tools and their versions, or `None`. |
| Screenshots and icon | Links to representative screenshots and an icon, if available, with usage rights confirmed. |

This is a documentation contract, not an implemented schema or API. Maintainers may refine it when the static catalog is introduced.

### Update or remove a mod

Use the same [Mod Submission issue form](https://github.com/theveryheavy/FEMS/issues/new?template=mod-submission.yml), select **Update an existing mod** or **Remove a mod**, and include its stable mod ID and catalog link if available. For an update, provide changed metadata and compatibility information. For removal, explain the request and whether the mod is withdrawn, moved, or no longer maintained. The catalog is not operational yet, so current removal requests can only be recorded for maintainers.

### Report a broken or malicious mod

Do not install or run a mod you believe is malicious. Report its mod ID, repository/download URL, observed behavior, and relevant version to the maintainers through a GitHub issue without publishing exploit details, private data, or harmful files. For vulnerabilities in FEMS itself, follow [SECURITY.md](../SECURITY.md) and report privately. Maintainers may temporarily remove or flag catalog entries while investigating once a catalog exists.

### Licensing and compatibility

Each mod author chooses and states the mod's license. A mod may use a license different from FEMS's MIT license. Third-party dependencies and assets keep their own licenses and attribution terms. Catalog inclusion does not transfer copyright, authorize redistribution, or imply endorsement. Authors are responsible for having permission to submit metadata and media, and should state supported game/FEMS versions and known limitations accurately.

## FAQ

**Can I install FEMS now?** No. There is no published application release yet.

**Can I submit a mod?** Yes, through the GitHub issue form. The request can be reviewed and recorded, but the catalog is not available and approval does not yet make it discoverable in an app.

**Does MIT apply to every mod?** No. MIT applies to the main FEMS project source code only. Mods and third-party material retain their own licenses.

**Where can I ask a question?** Use [GitHub Discussions](https://github.com/theveryheavy/FEMS/discussions) when enabled; see [SUPPORT.md](../SUPPORT.md) for the current route.

## Development and contribution instructions

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the contribution process and licensing expectations. The repository does not yet contain application code, dependency setup, build commands, or automated tests. Future development documentation should record those commands alongside the implementation rather than inventing them in advance.

## Documentation site

No website or deployment workflow is configured. When the documentation grows, [MkDocs with Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) is a lightweight static-site option. It can build from Markdown and be hosted on GitHub Pages; configure Pages and a deployment workflow only when there is a maintained docs site to publish.

Future FEMS web documentation should use dark backgrounds, minimal typography, industrial and retro-terminal influences, and restrained colors inspired by False Echo. Avoid implying official affiliation or using game assets without permission.
