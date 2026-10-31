# Contributing to FEMS

Thank you for considering a contribution. FEMS welcomes documentation improvements, thoughtful proposals, and community mod submissions from people with all levels of experience. The application source code is not currently included in this repository.

## Before you start

- Read and follow the [Code of Conduct](CODE_OF_CONDUCT.md).
- Search [existing issues](https://github.com/theveryheavy/FEMS/issues) before opening a duplicate.
- For broad proposals, open an issue first so the community can discuss the direction before implementation.
- Keep contributions focused and follow the existing Markdown conventions.
- Do not add False Echo executables, game data, extracted game content/assets, local save files, user-specific install state, or unrelated binaries.

## Submit or update a mod

Mods are published in this repository through pull requests, not by opening a mod submission issue:

1. Create a directory under `mods/` named with the mod's stable, unique ID.
2. Add the required `mod.json` metadata and a `README.md`; include only content you have the right to contribute.
3. Open a pull request against `main`. For updates, edit the existing mod directory rather than creating a duplicate.
4. Describe compatibility, license, dependencies, source/download links, and any relevant changes in the pull request.
5. Address maintainer review. A merged entry is a catalog listing; it does not mean FEMS hosts, verifies, or redistributes the mod.

See [mods/README.md](mods/README.md) for exact metadata and review expectations. Use the mod issue form only for questions, broken listings, or safety reports.

## Report bugs and propose features

Use the [Bug Report](https://github.com/theveryheavy/FEMS/issues/new?template=bug-report.yml) form for reproducible defects and the [Feature Request](https://github.com/theveryheavy/FEMS/issues/new?template=feature-request.yml) form for proposals. Include enough context to understand the problem, environment, and expected outcome. Do not put credentials, private user data, or undisclosed security vulnerabilities in public issues.

## Pull requests

1. Fork the repository and create a branch for your change.
2. Make a focused change and update relevant documentation.
3. Run relevant checks. If a check cannot be run, say so in the pull request rather than claiming it passed.
4. Open a pull request against `main` and complete the pull request template.
5. Respond to review feedback and keep the change easy to review.

Maintainers may request changes, additional tests, or revisions to keep the project maintainable. A pull request is not accepted until reviewed and merged by a maintainer.

## Licensing and contributions

The FEMS project is licensed under MIT. By submitting a project contribution, you confirm that you have the right to contribute it and that you are not knowingly submitting content that violates another person's rights.

Mods submitted under `mods/` keep their own licenses; do not apply the FEMS MIT license to them. Third-party dependencies and assets also retain their own licenses and attribution terms. Identify owners and licenses, preserve required notices, and obtain permission where needed. Do not submit another person's work as your own.
