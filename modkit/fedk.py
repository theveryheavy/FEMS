#!/usr/bin/env python3
"""FEMS (False Echo Modding Suite) command line interface.

  python fedk.py info
  python fedk.py extract
  python fedk.py pack [--with-assets]
  python fedk.py --game <Steam game folder> install
  python fedk.py play
  python fedk.py localize export|import|stats
  python fedk.py campaign new --day 09 --index 4
  python fedk.py save list|show|set|unlock
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from fedklib import content as C
from fedklib import saves as S
from fedklib import datawin as D
from fedklib import localize as L
from fedklib import campaign as CP
from fedklib import mods as M
from fedklib.project import Project

GAME_DEFAULT = HERE.parent


def default_project_root():
    manifest = HERE / "fems_supported_build.json"
    if manifest.is_file():
        try:
            rel = json.loads(manifest.read_text(encoding="utf-8")).get("project")
            if rel:
                return (HERE / rel).resolve()
        except (OSError, ValueError):
            pass
    return HERE / "project"


def game_dir(args):
    if getattr(args, "game", None):
        return Path(args.game).resolve()
    base = default_project_root() / "game"
    return base if (base / "data.win").is_file() else GAME_DEFAULT


def proj(args):
    root = Path(args.project).resolve() if getattr(args, "project", None) else default_project_root()
    game = Path(args.game).resolve() if getattr(args, "game", None) else root / "game"
    if not (game / "data.win").is_file():
        game = GAME_DEFAULT
    return Project(root, game)


def human(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{u}"
        n /= 1024
    return f"{n:.1f}TB"


def cmd_info(args):
    g = game_dir(args)
    from fedklib import __version__
    print(f"FEMS     : False Echo Modding Suite {__version__}")
    manifest = HERE / "fems_supported_build.json"
    if manifest.is_file():
        info = json.loads(manifest.read_text(encoding="utf-8"))
        print(f"supported: {info['game']} {info['product_version']} (Steam build {info.get('steam_build_id', 'unknown')})")
    print(f"game dir : {g}")
    for f in ("data.win", "False Echo.exe"):
        p = g / f
        print(f"  {f:<16} {human(p.stat().st_size) if p.exists() else 'MISSING'}")
    print("\nengine   : GameMaker Studio 2 2024.14 (YYC - native C++)")
    print("content  : base64+zlib JSON compiled into False Echo.exe")
    print("assets   : sprites/textures/fonts/shaders/rooms in data.win")
    saves = S.find_saves()
    print(f"saves    : {len(saves)} file(s) in {S.DEFAULT_DIR}")
    idx = proj(args).index_path
    if idx.exists():
        print(f"project  : {len(json.load(open(idx)))} content file(s) -> {idx.parent}")
    else:
        print("project  : not extracted (run: fedk extract)")


def cmd_extract(args):
    g = game_dir(args)
    p = proj(args)
    dump = p.root / "dump"
    dump.mkdir(parents=True, exist_ok=True)
    print("[1/3] dumping data.win assets via UndertaleModTool ...")
    D.run_script(g / "data.win", D.scripts_dir() / "dump_data.csx", env={"FEDUMP_OUT": dump})
    print("[2/3] extracting content blobs from False Echo.exe ...")
    supported = HERE / "fems_supported_build.json"
    content_map = json.loads(supported.read_text(encoding="utf-8")).get("content_map") if supported.is_file() else None
    idx = p.extract_content(dump / "strings.json", content_map=content_map)
    baseline = p.root / "baseline" / "content"
    if baseline.exists():
        shutil.rmtree(baseline)
    baseline.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(p.content_dir, baseline)
    for sub in ("sprites", "textures", "fonts", "shaders", "textures.json", "sprites.json",
                "fonts.json", "shaders.json", "objects.json", "rooms.json", "sounds.json",
                "strings.json", "meta.json"):
        src, dst = dump / sub, p.root / "assets" / sub
        if not src.exists():
            continue
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    print(f"[3/3] {len(idx)} content files + assets in {p.root}")


def cmd_pack(args):
    g = game_dir(args)
    p = proj(args)
    build = p.root / "build"
    build.mkdir(parents=True, exist_ok=True)
    print("[1/2] patching False Echo.exe ...")
    out_exe = build / "False Echo.exe"
    p.pack_content(out_exe)
    print(f"      -> {out_exe.name} ({human(out_exe.stat().st_size)})")
    print("[2/2] data.win ...")
    if args.with_assets:
        from fedklib import assets as A
        out = A.pack_assets(p, g, build)
        if out is None:
            shutil.copy2(g / "data.win", build / "data.win")
    else:
        shutil.copy2(g / "data.win", build / "data.win")
    print("done. install with: install_fems.cmd")


def cmd_install(args):
    if not args.game:
        sys.exit("specify the Steam game folder with --game, or run install_fems.cmd for Steam discovery and build checks")
    g = Path(args.game).resolve()
    p = proj(args)
    build = p.root / "build"
    if not (build / "False Echo.exe").exists():
        sys.exit("nothing to install - run 'fedk pack' first")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = p.root / "backup" / stamp
    backup.mkdir(parents=True, exist_ok=True)
    for f in ("False Echo.exe", "data.win"):
        if (g / f).exists():
            shutil.copy2(g / f, backup / f)
        if (build / f).exists():
            shutil.copy2(build / f, g / f)
    print(f"installed into {g}\nbackup: {backup}")


def cmd_play(args):
    g = game_dir(args)
    env = dict(os.environ, SteamAppId="5072320", SteamGameId="5072320")
    print("launching (Steam must be running) ...")
    subprocess.Popen([str(g / "False Echo.exe")], cwd=str(g), env=env)


def cmd_localize(args):
    p = proj(args)
    if args.action == "export":
        out = Path(args.out) if args.out else p.root / "localize"
        files = L.export_csv(p, out)
        print(f"exported {len(files)} CSV file(s) to {out}")
    elif args.action == "import":
        files = L.import_csv(p, Path(args.dir))
        print(f"imported {len(files)} table(s); run 'fedk pack' to rebuild")
    else:
        for s in L.stats(p):
            print(f"{s['group']:<15} {s['lang']:<4} keys={s['keys']:<5} empty={s['empty']}")


def cmd_campaign(args):
    p = proj(args)
    if args.action == "new":
        out = CP.new_campaign(p, name=args.name or f"day{args.day}")
        print("campaign scaffolded in", out)
        print("edit the JSON, then: fedk campaign apply --name ... --replace-day 03")
    elif args.action == "apply":
        files = CP.apply_campaign(p, name=args.name or f"day{args.day}", replace_day=args.replace_day)
        for f in files:
            print("wrote", f)
        print("\nnext: fedk pack --with-assets && install_fems.cmd")
    else:
        problems, missing = CP.validate(p)
        for pr in problems:
            print("ERROR", pr)
        print(f"missing localisation keys: {len(missing)}")
        for k in missing[:40]:
            print("  ", k)


def cmd_save(args):
    if args.action == "list":
        for f in S.find_saves(args.dir):
            try:
                doc, payload = S.load_save(f)
                print(f"{f.name:<32} day={payload.get('current_day')} "
                      f"unlocked={payload.get('highest_unlocked_day')} task={payload.get('current_task')}")
            except KeyError:
                continue  # settings.json etc. are not save slots
            except Exception as e:
                print(f"{f.name:<32} <unreadable: {e}>")
        return
    base = Path(args.dir) if args.dir else S.DEFAULT_DIR
    path = base / "savegame_slot_0.json"
    doc, payload = S.load_save(path)
    if args.action == "show":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.action == "set":
        node = payload
        parts = args.path.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = json.loads(args.value)
        S.save_save(path, payload, doc.get("version", 1.0))
        print("updated", path)
    elif args.action == "unlock":
        payload["highest_unlocked_day"] = float(args.day)
        S.save_save(path, payload, doc.get("version", 1.0))
        print("highest_unlocked_day =", args.day)


def cmd_mod(args):
    p = proj(args)
    if args.action == "create":
        out = M.create(p, args.name, args.author, args.version)
        print("created mod workspace:", out)
        print("copy edited files from project/ into its content/ or assets/ folders")
    elif args.action == "build":
        out, count = M.build(p, args.name, args.out)
        print(f"built {out} ({count} file(s))")
    elif args.action == "apply":
        if not args.file:
            sys.exit("mod apply requires --file PACKAGE.femod")
        doc, files, backup = M.apply(p, args.file)
        print(f"applied {doc.get('name', doc['id'])} {doc.get('version', '')}: {len(files)} file(s)")
        for name in files:
            print("  ", name)
        if backup:
            print("backup:", backup)
        print("next: fedk pack [--with-assets]")
    else:
        if not args.file:
            sys.exit("mod inspect requires --file PACKAGE.femod")
        doc, files = M.inspect(args.file)
        print(f"{doc.get('name', doc['id'])} [{doc['id']}] v{doc.get('version', '?')}")
        print(f"author: {doc.get('author') or '(unspecified)'}")
        print(f"description: {doc.get('description') or '(none)'}")
        print(f"files: {len(files)}")
        for name, _ in files:
            print("  ", name)


def main():
    ap = argparse.ArgumentParser(prog="fedk", description="FEMS — False Echo Modding Suite")
    ap.add_argument("--game", help="game folder (default: parent of modkit/)")
    ap.add_argument("--project", help="project folder (default: modkit/project)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("info").set_defaults(func=cmd_info)
    sub.add_parser("extract", help="extract assets + content").set_defaults(func=cmd_extract)

    k = sub.add_parser("pack", help="build patched exe/data.win")
    k.add_argument("--with-assets", action="store_true", help="also apply texture/sprite/shader edits")
    k.set_defaults(func=cmd_pack)

    sub.add_parser("install").set_defaults(func=cmd_install)
    sub.add_parser("play").set_defaults(func=cmd_play)

    lo = sub.add_parser("localize", help="localisation export/import/stats")
    lo.add_argument("action", choices=["export", "import", "stats"])
    lo.add_argument("--out")
    lo.add_argument("--dir")
    lo.set_defaults(func=cmd_localize)

    ca = sub.add_parser("campaign", help="custom campaign helpers")
    ca.add_argument("action", choices=["new", "apply", "validate"])
    ca.add_argument("--name", default="day09")
    ca.add_argument("--day", default="09")
    ca.add_argument("--replace-day", default="03")
    ca.add_argument("--index", default="4")
    ca.add_argument("--lang", default="EN")
    ca.set_defaults(func=cmd_campaign)

    sv = sub.add_parser("save", help="save game editing")
    sv.add_argument("action", choices=["list", "show", "set", "unlock"])
    sv.add_argument("--dir")
    sv.add_argument("--path")
    sv.add_argument("--value")
    sv.add_argument("--day", default="3")
    sv.set_defaults(func=cmd_save)

    md = sub.add_parser("mod", help="create, package, inspect, and apply data-only mods")
    md.add_argument("action", choices=["create", "build", "apply", "inspect"])
    md.add_argument("--name", default="my-mod", help="mod workspace name (create/build)")
    md.add_argument("--author", default="")
    md.add_argument("--version", default="1.0.0")
    md.add_argument("--out", help="output .femod path (build)")
    md.add_argument("--file", help=".femod package path (apply/inspect)")
    md.set_defaults(func=cmd_mod)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
