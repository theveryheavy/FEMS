"""Restart-aware mod library and clean-overlay staging for the FEMS UI."""
import json
import shutil
from pathlib import Path, PurePosixPath

from . import mods as M


ASSET_ITEMS = (
    "sprites", "textures", "fonts", "shaders", "textures.json", "sprites.json",
    "fonts.json", "shaders.json", "objects.json", "rooms.json", "sounds.json",
    "strings.json", "meta.json",
)
STATE_NAME = "fems_mod_state.json"


def library_dir(profile):
    path = Path(profile) / ".fems" / "library"
    path.mkdir(parents=True, exist_ok=True)
    return path


def state_path(profile):
    return Path(profile) / STATE_NAME


def load_state(profile):
    path = state_path(profile)
    if not path.is_file():
        return {"version": 1, "requested": [], "applied": []}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"version": 1, "requested": [], "applied": []}
    return {
        "version": 1,
        "requested": list(dict.fromkeys(state.get("requested", []))),
        "applied": list(dict.fromkeys(state.get("applied", []))),
    }


def save_state(profile, state):
    path = state_path(profile)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_package(profile, package):
    source = Path(package)
    doc, _ = M.inspect(source)
    folder = library_dir(profile)
    stem = f"{doc['id']}--{doc.get('version', '1.0.0')}"
    target = folder / f"{stem}.femod"
    serial = 2
    while target.exists():
        try:
            current, _ = M.inspect(target)
            if current.get("id") == doc.get("id") and current.get("version") == doc.get("version"):
                raise FileExistsError(f"{doc['name']} {doc.get('version', '')} is already in the library")
        except ValueError:
            pass
        target = folder / f"{stem}-{serial}.femod"
        serial += 1
    shutil.copy2(source, target)
    return target


def package_list(profile):
    result = []
    folder = library_dir(profile)
    for path in sorted(folder.glob("*.femod"), key=lambda p: p.name.casefold()):
        try:
            doc, payload = M.inspect(path)
            result.append({"path": path, "doc": doc, "files": len(payload), "error": None})
        except Exception as exc:
            result.append({"path": path, "doc": {"id": path.stem, "name": path.stem}, "files": 0, "error": str(exc)})
    return result


def set_requested(profile, filenames):
    packages = [item for item in package_list(profile) if not item["error"]]
    available = {item["path"].name: item["doc"].get("id") for item in packages}
    wanted = list(dict.fromkeys(filenames))
    unknown = sorted(set(wanted).difference(available))
    if unknown:
        raise ValueError("unknown or invalid mod package(s): " + ", ".join(unknown))
    ids = [available[name] for name in wanted]
    if len(ids) != len(set(ids)):
        raise ValueError("only one version of each mod can be enabled at a time")
    state = load_state(profile)
    state["requested"] = wanted
    save_state(profile, state)
    return state


def _copy_tree_replace(source, destination):
    source = Path(source)
    destination = Path(destination)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def restore_baseline(profile):
    root = Path(profile)
    baseline_content = root / "baseline" / "content"
    dump = root / "dump"
    if not baseline_content.is_dir():
        raise FileNotFoundError(f"mod content baseline is missing: {baseline_content}")
    _copy_tree_replace(baseline_content, root / "content")
    assets = root / "assets"
    if assets.exists():
        shutil.rmtree(assets)
    assets.mkdir(parents=True)
    for item in ASSET_ITEMS:
        source = dump / item
        if not source.exists():
            continue
        dest = assets / item
        if source.is_dir():
            shutil.copytree(source, dest)
        else:
            shutil.copy2(source, dest)


def stage_requested(profile):
    """Rebuild the editable project from pristine extraction plus selected mods."""
    root = Path(profile).resolve()
    state = load_state(root)
    packages = {item["path"].name: item for item in package_list(root) if not item["error"]}
    missing = [name for name in state["requested"] if name not in packages]
    if missing:
        raise ValueError("selected mod package is missing or invalid: " + ", ".join(missing))
    overlays = []
    for filename in state["requested"]:
        doc, payload = M.inspect(packages[filename]["path"])
        overlays.append((doc, payload))

    restore_baseline(root)
    applied_files = []
    for doc, payload in overlays:
        for rel, data in payload:
            posix = PurePosixPath(rel)
            dest = root.joinpath(*posix.parts)
            if not dest.resolve().is_relative_to(root):
                raise ValueError(f"mod destination escapes profile: {rel}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            applied_files.append(rel)
    return {"mods": len(overlays), "files": applied_files, "state": state}


def mark_applied(profile):
    state = load_state(profile)
    state["applied"] = list(state["requested"])
    save_state(profile, state)
    return state
