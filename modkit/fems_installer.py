"""Steam-aware installer for the exact False Echo Demo build FEMS supports."""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


HERE = (Path(sys.executable).resolve().parent if getattr(sys, "frozen", False)
        else Path(__file__).resolve().parent)
GAME_EXE = "False Echo.exe"
MANIFEST_NAME = "fems_supported_build.json"


def fail(message, code=1):
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(code)


def read_steam_install():
    try:
        import winreg
    except ImportError:
        fail("the installer runs on Windows only")
    steam_root = None
    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        for view in (getattr(winreg, "KEY_WOW64_32KEY", 0), getattr(winreg, "KEY_WOW64_64KEY", 0)):
            try:
                with winreg.OpenKey(hive, r"Software\Valve\Steam", 0, winreg.KEY_READ | view) as key:
                    steam_root, _ = winreg.QueryValueEx(key, "SteamPath")
                    break
            except OSError:
                continue
        if steam_root:
            break
    if not steam_root:
        candidates = [os.environ.get("ProgramFiles(x86)", ""), os.environ.get("ProgramFiles", "")]
        steam_root = next((str(Path(x) / "Steam") for x in candidates if x and (Path(x) / "Steam" / "steam.exe").exists()), None)
    if not steam_root:
        fail("Steam installation was not found. Install Steam, then run this installer again.")
    root = Path(steam_root).expanduser().resolve()
    if not (root / "steam.exe").is_file():
        fail(f"Steam registry path is invalid: {root}")
    return root


def steam_libraries(steam_root):
    paths = [steam_root]
    vdf = steam_root / "steamapps" / "libraryfolders.vdf"
    if vdf.is_file():
        text = vdf.read_text(encoding="utf-8", errors="replace")
        for raw in re.findall(r'"path"\s*"((?:\\.|[^"])*)"', text):
            decoded = raw.replace("\\\\", "\\").replace('\\"', '"')
            p = Path(decoded).expanduser()
            if p.is_absolute() and p not in paths:
                paths.append(p)
    return paths


def find_game(steam_root, libraries, app_id, explicit=None):
    discovered = []
    for library in libraries:
        appmanifest = library / "steamapps" / f"appmanifest_{app_id}.acf"
        if not appmanifest.is_file():
            continue
        text = appmanifest.read_text(encoding="utf-8", errors="replace")
        appid = re.search(r'"appid"\s*"(\d+)"', text)
        install = re.search(r'"installdir"\s*"([^"]+)"', text)
        build = re.search(r'"buildid"\s*"(\d+)"', text)
        if not appid or appid.group(1) != app_id or not install:
            continue
        target = library / "steamapps" / "common" / install.group(1)
        if target.is_dir():
            discovered.append((target.resolve(), build.group(1) if build else None))
    if explicit:
        target = Path(explicit).expanduser().resolve()
        match = next(((p, b) for p, b in discovered if p == target), None)
        if match:
            return match
        fail(f"the supplied path is not registered as Steam App {app_id}: {target}")
    if discovered:
        return discovered[0]
    fail(f"Steam App {app_id} ({'False Echo Demo'}) is not installed in a discovered Steam library.")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_build(game, manifest):
    expected = manifest["files"]
    mismatches = []
    for filename, wanted in expected.items():
        path = game / filename
        if not path.is_file():
            mismatches.append(f"missing {filename}")
            continue
        actual = sha256(path)
        if actual.lower() != wanted.lower():
            mismatches.append(f"{filename}: got SHA-256 {actual}")
    if mismatches:
        fail(
            "this game build is not supported. FEMS supports only the exact "
            f"{manifest['game']} reference build (GameMaker file version {manifest['product_version']}).\n"
            "The version string alone is not sufficient to identify the build.\n  "
            + "\n  ".join(mismatches)
            + "\nNo game files were changed."
        , 2)


def fingerprints(game, manifest):
    return {name: sha256(Path(game) / name) for name in manifest["files"]}


def current_install_kind(game, manifest):
    """Return base/installed for a known build; reject every other binary state."""
    actual = fingerprints(game, manifest)
    base = {name: value.lower() for name, value in manifest["files"].items()}
    if {name: value.lower() for name, value in actual.items()} == base:
        return "base"
    record_path = HERE / "fems_installed_build.json"
    if record_path.is_file():
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
            expected = record.get("files", {})
            if record.get("steam_build_id") == str(manifest.get("steam_build_id")) and all(
                actual.get(name, "").lower() == digest.lower()
                for name, digest in expected.items()
            ) and set(expected) == set(manifest["files"]):
                return "fems"
        except (OSError, ValueError, AttributeError):
            pass
    fail(
        "the installed executable/data files match neither the supported base build nor "
        "the last FEMS build recorded on this computer. Restore the original files through "
        "Steam or the FEMS backup before applying mods. No files were changed.",
        2,
    )


def is_game_running():
    running = subprocess.run(
        ["tasklist", "/FI", f"IMAGENAME eq {GAME_EXE}"],
        capture_output=True, text=True, check=False,
    )
    return GAME_EXE.lower() in (running.stdout or "").lower()


def find_pristine_source(game, manifest, install_kind):
    """Find the exact supported source executable without shipping a game copy."""
    if install_kind == "base":
        source = Path(game)
        check_build(source, manifest)
        return source
    expected = {name: value.lower() for name, value in manifest["files"].items()}
    backups = HERE / "backups"
    if backups.is_dir():
        for folder in sorted((p for p in backups.iterdir() if p.is_dir()), reverse=True):
            if all((folder / name).is_file() for name in expected):
                found = fingerprints(folder, manifest)
                if {name: value.lower() for name, value in found.items()} == expected:
                    return folder
    fail("the original supported game files were not found in the FEMS backups. "
         "Restore the game through Steam before reinstalling FEMS.", 2)


def install(game, manifest, content_only=False):
    if not (game / GAME_EXE).is_file() or not (game / "data.win").is_file():
        fail(f"not a False Echo game folder (expected {GAME_EXE} and data.win): {game}")
    # Do all compatibility checks before creating a build or touching the game.
    install_kind = current_install_kind(game, manifest)
    project_root = (HERE / manifest["project"]).resolve()
    if not project_root.is_dir():
        fail(f"the FEMS profile for this build is missing: {project_root}")
    if not (project_root / "content_index.json").is_file() or not (project_root / "baseline" / "content").is_dir():
        fail(f"the FEMS content profile is incomplete: {project_root}")
    base_game = find_pristine_source(game, manifest, install_kind)
    if is_game_running():
        fail("False Echo is running. Close the game and run the installer again.")

    build = project_root / "build"
    build.mkdir(parents=True, exist_ok=True)
    print("[INFO] Building the modded game files...")
    if content_only:
        from fedklib.public_packer import pack_content
        pack_content(project_root, base_game / GAME_EXE, build / GAME_EXE)
        shutil.copy2(base_game / "data.win", build / "data.win")
    else:
        fedk = HERE / "fedk.py"
        cmd = [sys.executable, str(fedk), "--project", str(project_root), "--game", str(base_game), "pack", "--with-assets"]
        result = subprocess.run(cmd, cwd=HERE.parent, check=False)
        if result.returncode:
            fail(f"fedk pack failed with exit code {result.returncode}; game files were not changed.")
    for name in (GAME_EXE, "data.win"):
        if not (build / name).is_file():
            fail(f"build did not produce {name}; game files were not changed.")
    # Re-check to guard against Steam updating the files while the build runs.
    if current_install_kind(game, manifest) != install_kind:
        fail("the Steam game files changed while FEMS was building. No files were installed.")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = HERE / "backups" / stamp
    backup.mkdir(parents=True, exist_ok=False)
    for name in (GAME_EXE, "data.win"):
        shutil.copy2(game / name, backup / name)
    record = {
        "suite_version": manifest["suite_version"],
        "steam_app_id": manifest["steam_app_id"],
        "steam_build_id": str(manifest["steam_build_id"]),
        "product_version": manifest["product_version"],
        "files": fingerprints(build, manifest),
    }
    record_path = HERE / "fems_installed_build.json"
    record_temp = record_path.with_suffix(".tmp")
    try:
        for name in (GAME_EXE, "data.win"):
            shutil.copy2(build / name, game / name)
        record_temp.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        os.replace(record_temp, record_path)
    except OSError as exc:
        # Restore both originals if a file copy fails partway through.
        for name in (GAME_EXE, "data.win"):
            saved = backup / name
            if saved.is_file():
                shutil.copy2(saved, game / name)
        record_temp.unlink(missing_ok=True)
        hint = " Run install_fems.cmd as administrator if this Steam library requires elevation." if getattr(exc, "winerror", None) == 5 else ""
        fail(f"install failed and the previous game files were restored: {exc}.{hint}")
    print(f"[OK] Installed FEMS {manifest['suite_version']} into {game}")
    print(f"[INFO] Previous files backed up to {backup}")


def main(argv=None, *, content_only=False):
    ap = argparse.ArgumentParser(description="Install FEMS into the supported Steam game build")
    ap.add_argument("--game-dir", help="explicit Steam game folder; still subject to Steam and build checks")
    args = ap.parse_args(argv)
    if sys.version_info < (3, 10):
        fail("Python 3.10 or newer is required.")
    missing = [] if content_only else [name for name in ("PIL", "tkinter") if importlib.util.find_spec(name) is None]
    if missing:
        fail("missing Python module(s): " + ", ".join(missing) + ". Install Python 3.10+ with Tcl/Tk, then run: python -m pip install pillow")
    manifest_path = HERE / MANIFEST_NAME
    if not manifest_path.is_file():
        fail(f"supported-build manifest is missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    steam_root = read_steam_install()
    libraries = steam_libraries(steam_root)
    game, build_id = find_game(steam_root, libraries, manifest["steam_app_id"], args.game_dir)
    print(f"[INFO] Steam: {steam_root}")
    print(f"[INFO] Game:  {game}")
    if build_id:
        print(f"[INFO] Steam build ID: {build_id}")
        expected_build = manifest.get("steam_build_id")
        if expected_build and build_id != str(expected_build):
            fail(f"Steam build {build_id} is unsupported; FEMS supports only build {expected_build}.")
    install(game, manifest, content_only=content_only)


if __name__ == "__main__":
    main()
