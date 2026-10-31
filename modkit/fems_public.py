"""Supported public FEMS entry point; intentionally exposes no extract command."""
import json
import sys
from pathlib import Path

HERE = (Path(sys.executable).resolve().parent if getattr(sys, "frozen", False)
        else Path(__file__).resolve().parent)
if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(HERE))


def _profile():
    manifest = json.loads((HERE / "fems_supported_build.json").read_text(encoding="utf-8"))
    return (HERE / manifest["project"]).resolve()


def _help():
    print("FEMS - False Echo Modding Suite")
    print("Usage: FEMS.exe <command>")
    print("  install       Check Steam and install the selected content mods")
    print("  play          Apply queued mods, start the game, and launch the F8 overlay")
    print("  mods          List installed mod packages")
    print("  version       Show the FEMS version")
    print("  help          Show this help")


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    command = args.pop(0).casefold() if args else "help"
    if command in ("help", "--help", "-h"):
        _help()
        return 0
    if command in ("version", "--version"):
        from fedklib import __version__
        print(f"[INFO] FEMS {__version__}")
        return 0
    if command == "mods":
        from fedklib.manager import package_list
        items = package_list(_profile())
        if not items:
            print("[INFO] No mod packages are installed.")
        for item in items:
            if item["error"]:
                print(f"[ERROR] {item['path'].name}: {item['error']}")
            else:
                doc = item["doc"]
                print(f"[OK] {doc.get('name', doc.get('id'))} {doc.get('version', '')} - {doc.get('description', '')}")
        return 0
    if command == "install":
        from fedklib import manager
        profile = _profile()
        staged = manager.stage_requested(profile)
        if any(str(path).startswith("assets/") for path in staged["files"]):
            print("[ERROR] This standalone FEMS release supports content mods only; asset mods require the developer toolkit.", file=sys.stderr)
            return 2
        from fems_installer import main as installer_main
        installer_main(args, content_only=True)
        manager.mark_applied(profile)
        print("[OK] Selected mods are installed.")
        return 0
    if command == "play":
        from fems_launcher import main as launcher_main
        launcher_main(content_only=True)
        return 0
    print(f"[ERROR] Unknown command: {command}", file=sys.stderr)
    _help()
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
