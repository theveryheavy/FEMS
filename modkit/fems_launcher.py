"""Apply queued mod selection and launch the supported Steam game plus overlay."""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = (Path(sys.executable).resolve().parent if getattr(sys, "frozen", False)
        else Path(__file__).resolve().parent)
sys.path.insert(0, str(HERE))

from fedklib import manager
from fems_installer import (
    find_game, install, is_game_running, read_steam_install, steam_libraries,
    current_install_kind,
)


def steam_is_running():
    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq steam.exe"],
        capture_output=True, text=True, check=False,
    )
    return "steam.exe" in (result.stdout or "").lower()


def main(*, content_only=False):
    manifest_path = HERE / "fems_supported_build.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    profile = (HERE / manifest["project"]).resolve()
    steam = read_steam_install()
    game, build_id = find_game(steam, steam_libraries(steam), manifest["steam_app_id"])
    expected = str(manifest.get("steam_build_id", ""))
    if expected and build_id != expected:
        raise SystemExit(f"Steam build {build_id or 'unknown'} is unsupported; FEMS requires {expected}.")
    if not steam_is_running():
        raise SystemExit("Start Steam, then run fems_play.cmd again.")
    if is_game_running():
        raise SystemExit("False Echo is already running. Close it before starting FEMS.")

    install_kind = current_install_kind(game, manifest)
    state = manager.load_state(profile)
    if install_kind == "base" and not state["requested"] and state["applied"]:
        # Steam's file verification may have restored the supported base files.
        manager.mark_applied(profile)
        state = manager.load_state(profile)
    pending = state["requested"] != state["applied"] or (install_kind == "base" and bool(state["requested"]))
    if pending:
        if is_game_running():
            raise SystemExit("Close False Echo first. Relaunch with fems_play.cmd to apply queued mods and restart the game.")
        summary = manager.stage_requested(profile)
        if content_only and any(str(path).startswith("assets/") for path in summary["files"]):
            raise SystemExit("This standalone FEMS release supports content mods only; asset mods require the developer toolkit.")
        print(f"[INFO] Preparing {summary['mods']} mod(s), {len(summary['files'])} content file(s)...")
        install(game, manifest, content_only=content_only)
        manager.mark_applied(profile)
        print("[OK] Mod selection applied.")
    overlay = HERE / ("FEMS-Overlay.exe" if getattr(sys, "frozen", False) else "fems_overlay.py")
    try:
        command = [str(overlay)] if getattr(sys, "frozen", False) else [sys.executable, str(overlay)]
        subprocess.Popen(
            command,
            cwd=HERE,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except OSError as exc:
        print(f"[WARN] Could not start overlay: {exc}")
    env = dict(os.environ, SteamAppId=manifest["steam_app_id"], SteamGameId=manifest["steam_app_id"])
    print("[INFO] Launching False Echo...")
    subprocess.Popen([str(game / "False Echo.exe")], cwd=str(game), env=env)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
