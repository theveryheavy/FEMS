"""Content-only patcher for the public FEMS build; performs no extraction."""
import hashlib
import json
from pathlib import Path

from . import content as C
from .public_pe import PatchPE


def pack_content(project_root, base_exe, out_exe):
    root = Path(project_root)
    index = json.loads((root / "content_index.json").read_text(encoding="utf-8"))
    pe = PatchPE(base_exe)
    relocate = []
    for name, meta in sorted(index.items()):
        source = root / "content" / name
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() == meta.get("sha256"):
            continue
        obj = json.loads(source.read_text(encoding="utf-8"))
        encoded = C.fit(obj, meta["b64_len"], meta.get("nul", True))
        if encoded:
            pe.patch_bytes(meta["file_offset"], encoded.encode("ascii"))
        else:
            payload = C.encode(obj, meta.get("nul", True)).encode("ascii") + b"\0"
            relocate.append((name, meta, payload))

    if relocate:
        section_data = bytearray()
        placements = []
        for name, meta, payload in relocate:
            while len(section_data) % 16:
                section_data.append(0)
            placements.append((name, meta, len(section_data)))
            section_data.extend(payload)
        while len(section_data) % 16:
            section_data.append(0)
        section_va = pe.add_section(bytes(section_data))
        for _name, meta, offset in placements:
            target_va = section_va + offset
            for reference_va in meta["refs"]:
                pe.retarget_rip_ref(reference_va, target_va)
    out = Path(out_exe)
    out.parent.mkdir(parents=True, exist_ok=True)
    pe.save(out)
    return out
