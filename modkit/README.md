# FEMS toolkit

This directory contains the Python CLI, library, Windows installer/launcher, and F8 companion overlay source. Start with the repository [README](../README.md) for setup and safety notes.

## Requirements

- Windows for the installer, launcher, and overlay.
- Python 3.10 or later.
- Dependencies from the repository root: `python -m pip install -r requirements.txt`.
- A locally installed False Echo Demo build matching [`fems_supported_build.json`](fems_supported_build.json) for game-dependent commands.

The game is not included. The first `extract` operation downloads the UndertaleModTool CLI into `tools/utmt/`; that binary is local, is not part of this source distribution, and remains subject to its own license.

## Common commands

Run commands from the repository root:

```powershell
python modkit\fedk.py --game "C:\path\to\False Echo Demo" info
python modkit\fedk.py --game "C:\path\to\False Echo Demo" extract
python modkit\fedk.py --game "C:\path\to\False Echo Demo" mod create --name my-mod
python modkit\fedk.py --game "C:\path\to\False Echo Demo" mod build --name my-mod
```

For all commands and options, run `python modkit\fedk.py --help`. Consult the [modding guide](docs/MODDING_GUIDE.md), [package guide](docs/MOD_PACKAGES.md), [content format](docs/CONTENT_FORMAT.md), and [architecture notes](docs/ARCHITECTURE.md).

Extraction and builds write local data to `project/`, `dump/`, and `build/`; those paths are ignored by Git because they may contain game-derived material. Do not force-add them or redistribute game files.

The source toolkit currently reports version `0.9.0`. This is the code's internal version; this repository setup does not publish a release or standalone binary.
