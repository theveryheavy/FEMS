"""Save game editing (JSON payload + SHA-1 checksum)."""
import hashlib
import json
import os
from pathlib import Path

DEFAULT_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "False_Echo" / "save"


def load_save(path):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    payload = json.loads(doc["payload"])
    return doc, payload


def checksum(payload_str):
    return hashlib.sha1(payload_str.encode("utf-8")).hexdigest()


def save_save(path, payload, version=1.0):
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    doc = {"checksum": checksum(text), "version": version,
           "format": "false_echo_save", "payload": text}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    return doc


def find_saves(folder=None):
    folder = Path(folder) if folder else DEFAULT_DIR
    if not folder.exists():
        return []
    return sorted(p for p in folder.glob("*.json"))
