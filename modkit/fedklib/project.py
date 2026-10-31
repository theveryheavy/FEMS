"""Project layout, extraction and packing."""
import hashlib
import json
import os
import shutil
from pathlib import Path

from . import content as C
from .pe import PE
from .refs import find_lea_refs


class Project:
    def __init__(self, root, game_dir):
        self.root = Path(root)
        self.game = Path(game_dir)

    # ---------- paths ----------
    @property
    def content_dir(self):
        return self.root / "content"

    @property
    def index_path(self):
        return self.root / "content_index.json"

    def load_index(self):
        with open(self.index_path, encoding="utf-8") as f:
            return json.load(f)

    # ---------- extract ----------
    def extract_content(self, strings_json, content_map=None):
        """strings_json: dump/strings.json produced by the UTMT dump script."""
        with open(strings_json, encoding="utf-8") as f:
            strings = {s["id"]: s["text"] for s in json.load(f) if s.get("text")}
        pe = PE(self.game / "False Echo.exe")
        content_map = content_map or C.CONTENT_MAP

        targets = {}
        for idx in content_map:
            b64 = strings.get(idx)
            if not b64:
                continue
            hit = pe.find_blob(b64)
            if not hit:
                continue
            off, va = hit
            targets[va] = (idx, off, len(b64))

        refs = find_lea_refs(pe, targets.keys())
        index = {}
        for va, (idx, off, length) in targets.items():
            b64 = strings[idx]
            obj, nul = C.decode(b64)
            name = content_map[idx]
            dest = self.content_dir / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "w", encoding="utf-8", newline="\n") as f:
                json.dump(obj, f, ensure_ascii=False, indent=2)
                f.write("\n")
            index[name] = {
                "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
                "strg_index": idx,
                "file_offset": off,
                "va": va,
                "b64_len": length,
                "refs": refs.get(va, []),
                "nul": nul,
            }
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)
        return index

    # ---------- pack ----------
    def pack_content(self, out_exe, only=None):
        index = self.load_index()
        pe = PE(self.game / "False Echo.exe")
        relocate = []

        for name, meta in sorted(index.items()):
            if only and name not in only:
                continue
            src = self.content_dir / name
            if not src.exists():
                continue
            if hashlib.sha256(src.read_bytes()).hexdigest() == meta.get("sha256"):
                continue  # unchanged
            with open(src, encoding="utf-8") as f:
                obj = json.load(f)
            b64 = C.fit(obj, meta["b64_len"], meta.get("nul", True))
            if b64:
                pe.patch_bytes(meta["file_offset"], b64.encode())
            else:
                data = C.encode(obj, meta.get("nul", True)).encode() + b"\0"
                relocate.append((name, meta, data))

        if relocate:
            # one new section, all grown blobs inside it
            buf = bytearray()
            placements = []
            for name, meta, data in relocate:
                while len(buf) % 16:
                    buf.append(0)
                placements.append((name, meta, len(buf)))
                buf.extend(data)
            while len(buf) % 16:
                buf.append(0)
            sec_va = pe.add_section(bytes(buf))
            for name, meta, offset in placements:
                new_va = sec_va + offset
                for ref in meta["refs"]:
                    pe.retarget_rip_ref(ref, new_va)

        pe.save(out_exe)
        return out_exe
