# Contributing to FEMS

Thank you for considering a contribution. FEMS welcomes bug reports, thoughtful feature proposals, documentation improvements, code contributions, and mod catalog requests from people with all levels of experience.

## Before you start

- Read and follow the [Code of Conduct](CODE_OF_CONDUCT.md).
- Search [existing issues](https://github.com/theveryheavy/FEMS/issues) before opening a duplicate.
- For broad proposals, open an issue first so the community can discuss the direction before implementation.
- Keep contributions focused and follow the existing Python and Markdown conventions.
- Do not add game executables, `data.win`, extracted game content/assets, local save files, user-specific install state, generated mod packages, or downloaded third-party binaries. The `.gitignore` covers common generated paths; check staged files before submitting.

## Development setup

The toolkit targets Windows and Python 3.10 or later. From the repository root, install the image dependency and run the CLI smoke checks:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m compileall -q modkit
python modkit\fedk.py --help
python modkit\fems_public.py help
```

These checks do not require a game installation. Game-dependent operations also require a locally installed game build that matches `modkit/fems_supported_build.json`; extraction may download UndertaleModTool into an ignored directory. Do not claim game integration was tested unless it was tested against that supported build.

## Report bugs and propose features

Use the [Bug Report](https://github.com/theveryheavy/FEMS/issues/new?template=bug-report.yml) form for reproducible defects and the [Feature Request](https://github.com/theveryheavy/FEMS/issues/new?template=feature-request.yml) form for proposals. Include enough context to understand the problem, environment, and expected outcome. Do not put credentials, private user data, or undisclosed security vulnerabilities in public issues.

## Pull requests

1. Fork the repository and create a branch for your change.
2. Make a focused change and update relevant documentation.
3. Run the checks above and any relevant game-dependent checks. If a check cannot be run, say so in the pull request rather than claiming it passed.
4. Open a pull request against `main` and complete the pull request template.
5. Respond to review feedback and keep the change easy to review.

Maintainers may request changes, additional tests, or revisions to keep the project maintainable. A pull request is not accepted until reviewed and merged by a maintainer.

## Mod catalog contributions

Submit new mods and requests to update or remove an entry using the [Mod Submission issue form](https://github.com/theveryheavy/FEMS/issues/new?template=mod-submission.yml). Follow the [mod submission guide](docs/README.md#mod-submission-and-catalog). A submission requests review; it does not guarantee inclusion, transfer ownership, or authorize FEMS to host or relicense the mod.

## Licensing and contributions

The main FEMS project source code is licensed under MIT. By submitting a contribution, you confirm that you have the right to contribute it and that you are not knowingly submitting content that violates another person's rights. Your contribution to FEMS is offered under the project's MIT License unless you clearly identify material with a different license and the maintainers approve its inclusion.

This project license does not apply automatically to independently licensed mods, third-party code, artwork, screenshots, icons, or other assets. Identify their owners and licenses, preserve required notices, and obtain permission where needed. Do not submit another person's work as your own.
