"""Asset (data.win) modding: texture pages, sprite frames, shader sources."""
import json
import shutil
from pathlib import Path

from PIL import Image

from . import datawin as D

SHADER_FILES = {
    "vertex_glsl_es.txt": "vertex_glsl_es",
    "fragment_glsl_es.txt": "fragment_glsl_es",
    "vertex_glsl.txt": "vertex_glsl",
    "fragment_glsl.txt": "fragment_glsl",
    "vertex_hlsl9.txt": "vertex_hlsl9",
    "fragment_hlsl9.txt": "fragment_hlsl9",
}


def _same(a, b):
    try:
        return a.read_bytes() == b.read_bytes()
    except FileNotFoundError:
        return False


def collect_plan(project):
    root = Path(project.root)
    assets = root / "assets"
    dump = root / "dump"
    plan = {"textures": [], "shaders": []}

    textures = json.loads((assets / "textures.json").read_text(encoding="utf-8"))
    by_index = {t["id"]: t for t in textures}
    pages = {t["name"]: t["id"] for t in textures}

    # 1. whole-page edits
    dirty = {}
    for t in textures:
        name = t["name"]
        a = assets / "textures" / f"{name}.png"
        b = dump / "textures" / f"{name}.png"
        if a.exists() and _same(a, b) is False:
            dirty[name] = a

    # 2. individual sprite frames composited back onto their pages
    sprites = json.loads((assets / "sprites.json").read_text(encoding="utf-8"))
    for spr in sprites:
        for fr in spr.get("frames", []):
            src = assets / "sprites" / spr["name"] / f"{fr['i']}.png"
            orig = dump / "sprites" / spr["name"] / f"{fr['i']}.png"
            if not src.exists() or _same(src, orig):
                continue
            if fr.get("page") is None:
                continue
            name = fr["page"]
            page_path = dirty.get(name, assets / "textures" / f"{name}.png")
            base = Image.open(page_path).convert("RGBA")
            frame = Image.open(src).convert("RGBA")
            if frame.size != (fr["w"], fr["h"]):
                raise SystemExit(
                    f"sprite {spr['name']}#{fr['i']} is {frame.size[0]}x{frame.size[1]} "
                    f"but the frame slot is {fr['w']}x{fr['h']}; resizing sprites is not supported yet")
            base.alpha_composite(frame, (fr["x"], fr["y"]))
            out = root / "build" / "pages" / f"{name}.png"
            out.parent.mkdir(parents=True, exist_ok=True)
            base.save(out)
            dirty[name] = out

    for name, path in dirty.items():
        plan["textures"].append({"index": pages[name], "png": str(path)})

    # 3. shader sources
    for sh in json.loads((assets / "shaders.json").read_text(encoding="utf-8")):
        name = sh["name"]
        entry = {"name": name}
        changed = False
        for fname, field in SHADER_FILES.items():
            a = assets / "shaders" / name / fname
            b = dump / "shaders" / name / fname
            if a.exists() and _same(a, b) is False:
                entry[field] = str(a)
                changed = True
        if changed:
            plan["shaders"].append(entry)
    return plan


def pack_assets(project, game_dir, build_dir):
    plan = collect_plan(project)
    if not plan["textures"] and not plan["shaders"]:
        print("      no asset changes")
        return None
    plan_path = Path(project.root) / "build" / "asset_plan.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    out = Path(build_dir) / "data.win"
    print(f"      textures={len(plan['textures'])} shaders={len(plan['shaders'])}")
    D.run_script(Path(game_dir) / "data.win",
                 D.scripts_dir() / "apply_patch.csx",
                 out=out, env={"FEDK_PATCH": plan_path})
    return out
