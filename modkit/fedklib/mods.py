"""Portable, data-only False Echo mod packages (.femod)."""
import hashlib
import json
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath


FORMAT_VERSION = 1
ALLOWED_ROOTS = {"content", "assets"}
MANIFEST_NAME = "mod.json"
PREVIEW_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def _slug(value):
    slug = re.sub(r"[^a-z0-9._-]+", "-", value.strip().lower()).strip("-.")
    if not slug:
        raise SystemExit("mod name must contain letters or numbers")
    return slug


def _safe_relative(value):
    """Accept only content/assets paths, in either POSIX or Windows ZIP form."""
    if not isinstance(value, str) or "\\" in value:
        raise ValueError(f"invalid mod file path: {value!r}")
    p = PurePosixPath(value)
    if (p.is_absolute() or not p.parts or
            any(part in ("", ".", "..") or ":" in part or part.endswith((".", " ")) for part in p.parts)):
        raise ValueError(f"unsafe mod file path: {value!r}")
    if p.parts[0] not in ALLOWED_ROOTS:
        raise ValueError(f"mod file must be under content/ or assets/: {value}")
    return p


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _safe_preview(value):
    if not isinstance(value, str) or "\\" in value:
        raise ValueError(f"invalid mod preview path: {value!r}")
    p = PurePosixPath(value)
    if p.is_absolute() or len(p.parts) < 2 or p.parts[0] != "media" or any(x in ("", ".", "..") for x in p.parts):
        raise ValueError(f"preview image must be under media/: {value!r}")
    if p.suffix.lower() not in PREVIEW_SUFFIXES:
        raise ValueError("preview image must be PNG, JPEG, or WebP")
    return p


def create(project, name, author="", version="1.0.0"):
    slug = _slug(name)
    root = Path(project.root) / "mods" / slug
    if root.exists():
        raise SystemExit(f"mod folder already exists: {root}")
    root.mkdir(parents=True)
    doc = {
        "format": "femod",
        "format_version": FORMAT_VERSION,
        "id": slug,
        "name": name,
        "version": version,
        "author": author,
        "description": "",
        "homepage": "",
        "image": "media/cover.png",
        "files": [],
    }
    (root / MANIFEST_NAME).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "README.md").write_text(
        "# " + name + "\n\n"
        "Put edited files under `content/` or `assets/`, keeping the same paths as in `project/`.\n"
        "For example, `content/data/day01_dialogues.json` replaces that content file.\n\n"
        "Add optional `homepage` and `image` metadata to mod.json. Put a PNG, JPEG, or WebP cover at `media/cover.png`.\n\n"
        "Build it with `python fedk.py mod build --name " + slug + "`.\n",
        encoding="utf-8",
    )
    return root


def build(project, name, out=None):
    slug = _slug(name)
    root = Path(project.root) / "mods" / slug
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.is_file():
        raise SystemExit(f"missing mod manifest: {manifest_path}")
    doc = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = []
    for area in sorted(ALLOWED_ROOTS):
        for path in sorted((root / area).rglob("*")) if (root / area).exists() else []:
            if path.is_file():
                rel = path.relative_to(root).as_posix()
                _safe_relative(rel)
                data = path.read_bytes()
                files.append({"path": rel, "sha256": _sha256(data)})
    if not files:
        raise SystemExit("mod has no files; add at least one file under content/ or assets/")
    doc.update({"format": "femod", "format_version": FORMAT_VERSION, "id": slug, "files": files})
    image_rel = doc.get("image")
    image_path = None
    image_data = None
    if image_rel:
        image_path = _safe_preview(image_rel)
        candidate = root.joinpath(*image_path.parts)
        if candidate.is_file():
            image_data = candidate.read_bytes()
            doc["image_sha256"] = _sha256(image_data)
        else:
            doc.pop("image", None)
            doc.pop("image_sha256", None)
    target = Path(out) if out else Path(project.root) / "build" / f"{slug}.femod"
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr(MANIFEST_NAME, json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
        for entry in files:
            zf.write(root / Path(*PurePosixPath(entry["path"]).parts), entry["path"])
        if image_rel and image_data is not None:
            zf.writestr(image_rel, image_data)
    return target, len(files)


def inspect(package):
    with zipfile.ZipFile(package, "r") as zf:
        names = zf.namelist()
        if names.count(MANIFEST_NAME) != 1:
            raise ValueError("package must contain exactly one root mod.json")
        doc = json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))
        if not isinstance(doc, dict) or not isinstance(doc.get("id"), str):
            raise ValueError("invalid mod manifest")
        if _slug(doc["id"]) != doc["id"]:
            raise ValueError("mod ID must be a normalized lowercase slug")
        if doc.get("format") != "femod" or doc.get("format_version") != FORMAT_VERSION:
            raise ValueError("unsupported mod package format/version")
        declared = doc.get("files")
        if not isinstance(declared, list) or not declared:
            raise ValueError("mod manifest has no files")
        seen = set()
        casefolded = set()
        checked = []
        for entry in declared:
            if not isinstance(entry, dict):
                raise ValueError("invalid file entry in manifest")
            rel = _safe_relative(entry.get("path"))
            key = rel.as_posix()
            if key in seen:
                raise ValueError(f"duplicate file in manifest: {key}")
            if key.casefold() in casefolded:
                raise ValueError(f"case-insensitive path collision in manifest: {key}")
            seen.add(key)
            casefolded.add(key.casefold())
            if names.count(key) != 1:
                raise ValueError(f"package entry missing or duplicated: {key}")
            data = zf.read(key)
            if _sha256(data) != entry.get("sha256"):
                raise ValueError(f"checksum mismatch: {key}")
            checked.append((key, data))
        extras = set()
        if doc.get("image"):
            image_path = _safe_preview(doc["image"]).as_posix()
            if names.count(image_path) != 1:
                raise ValueError(f"preview image missing or duplicated: {image_path}")
            image_data = zf.read(image_path)
            if _sha256(image_data) != doc.get("image_sha256"):
                raise ValueError(f"preview image checksum mismatch: {image_path}")
            extras.add(image_path)
        # No unlisted payloads: the manifest fully describes the package.
        payload_names = {n for n in names if n != MANIFEST_NAME and not n.endswith("/")}
        if payload_names != seen | extras:
            raise ValueError("package contains files not declared in mod.json")
        return doc, checked


def read_preview(package):
    doc, _ = inspect(package)
    if not doc.get("image"):
        return None
    with zipfile.ZipFile(package, "r") as zf:
        return zf.read(_safe_preview(doc["image"]).as_posix())


def apply(project, package):
    doc, payload = inspect(package)
    root = Path(project.root)
    # Validate every destination before writing any file.
    destinations = []
    for rel, data in payload:
        dest = root.joinpath(*PurePosixPath(rel).parts)
        if not dest.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"destination escapes project: {rel}")
        destinations.append((rel, dest, data))
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = root / "backup" / f"mod-{doc['id']}-{stamp}"
    existing = [(rel, dest) for rel, dest, _ in destinations if dest.exists()]
    for rel, dest in existing:
        saved = backup.joinpath(*PurePosixPath(rel).parts)
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest, saved)
    for _, dest, data in destinations:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return doc, [rel for rel, _, _ in destinations], backup if existing else None
