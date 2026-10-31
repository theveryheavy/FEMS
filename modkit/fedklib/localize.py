"""Localisation round-trip: game JSON tables <-> translator-friendly CSV."""
import csv
import json
from pathlib import Path

from .content import LANGS, CONTENT_MAP

# Build 26300950 adds Chinese tables. Older profiles simply have no ZH files,
# and table_paths skips languages whose source table is absent.
LOCALIZATION_LANGS = LANGS + ["ZH"]

GROUP_PREFIXES = [
    ("Endless", "data/localization/Endless {L}.json"),
    ("Frontline News", "data/localization/Frontline News {L}.json"),
    ("Localization", "data/localization/Localization {L}.json"),
    ("War Diary", "data/localization/War Diary {L}.json"),
]


def table_paths(project):
    """[(group_name, lang, path)] for every translatable table."""
    out = []
    for name, pattern in GROUP_PREFIXES:
        for lang in LOCALIZATION_LANGS:
            rel = pattern.format(L=lang)
            p = Path(project.root) / "content" / rel
            if p.exists():
                out.append((name, lang, p))
    return out


def export_csv(project, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, lang, path in table_paths(project):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data and isinstance(data[0], list) and len(data[0]) > 1 and name == "Localization":
            pass
        rows = data
        dest = out / f"{name} - {lang}.csv"
        with open(dest, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["key", "text"])
            for row in rows:
                if isinstance(row, list) and len(row) >= 2:
                    w.writerow([row[0], row[1]])
        written.append(dest)
    # rules table is a plain matrix, export as-is
    rules = Path(project.root) / "content" / "data/localization/FE Rules and Missions - Rules.json"
    if rules.exists():
        dest = out / "FE Rules and Missions - Rules.csv"
        rows = json.loads(rules.read_text(encoding="utf-8"))
        with open(dest, "w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerows(rows)
        written.append(dest)
    return written


def import_csv(project, in_dir):
    src = Path(in_dir)
    changed = []
    for name, lang, path in table_paths(project):
        csv_path = src / f"{name} - {lang}.csv"
        if not csv_path.exists():
            continue
        with open(csv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows:
            continue
        table = json.loads(path.read_text(encoding="utf-8"))
        index = {row[0]: i for i, row in enumerate(table) if isinstance(row, list) and row}
        for row in rows[1:]:
            if len(row) < 2:
                continue
            key, text = row[0], row[1]
            if key in index:
                table[index[key]][1] = text
            else:
                table.append([key, text])
        path.write_text(json.dumps(table, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        changed.append(path)
    return changed


def stats(project):
    out = []
    for name, lang, path in table_paths(project):
        data = json.loads(path.read_text(encoding="utf-8"))
        empty = sum(1 for r in data if isinstance(r, list) and len(r) > 1 and not str(r[1]).strip())
        out.append({"group": name, "lang": lang, "keys": len(data), "empty": empty, "file": str(path)})
    return out
