"""Custom campaign scaffolding.

The engine reads a *fixed* set of content blobs (day01-03, d99, intro, ...).
A brand-new day therefore cannot simply be added as a file: it has to occupy
an existing slot. This module scaffolds a campaign in `project/campaigns/<name>`
and can apply it over a chosen day slot.
"""
import json
import shutil
from pathlib import Path

DAY_TEMPLATE = {
    "day": "dayXX",
    "day_index": "3",
    "step_1": {
        "UID": "dayxx_ev_01",
        "triggers": [{"type": "on_message_received", "event_id": "ng_begin"}],
        "actions": [
            {"type": "mono_nonskip", "text_key": "dayxx_intro_01", "auto_ms": 4000.0}
        ],
    },
}

DIALOGUE_TEMPLATE = {
    "groups": {
        "dayxx_group_01": [
            {"side": "left", "loc": "dayxx_dia_01", "npc": "xo"},
            {"side": "right", "loc": "dayxx_dia_02"},
        ]
    }
}

MISSION_TEMPLATE = {
    "m_dayxx_01": {
        "character": "sailor_01",
        "verification_direction": "inbound",
        "ver_sender_key": "txt_verm_sender_inb_01",
        "msgDateTrue": True,
        "time_sec": 0.0,
        "decoded_message": "dayxx_text_01",
    }
}

LOCALISATION_SEED = [
    ["dayxx_intro_01", "New orders have arrived."],
    ["dayxx_dia_01", "Officer on deck."],
    ["dayxx_dia_02", "As you were."],
    ["dayxx_text_01", "CONVOY SIGHTED. HOLD POSITION."],
]


def _sub(obj, token, value):
    return json.loads(json.dumps(obj).replace(token, value))


def campaigns_dir(project):
    return Path(project.root) / "campaigns"


def new_campaign(project, name="day09"):
    out = campaigns_dir(project) / name
    if out.exists():
        raise SystemExit(f"{out} already exists")
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.json").write_text(
        json.dumps(_sub(DAY_TEMPLATE, "dayxx", name), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / f"{name}_dialogues.json").write_text(
        json.dumps(_sub(DIALOGUE_TEMPLATE, "dayxx", name), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "missions.json").write_text(
        json.dumps(_sub(MISSION_TEMPLATE, "dayxx", name), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "rules.json").write_text(
        json.dumps({"version": 1.0}, indent=2) + "\n", encoding="utf-8")
    loc = [[k.replace("dayxx", name), v] for k, v in LOCALISATION_SEED]
    (out / "localisation EN.json").write_text(
        json.dumps(loc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "README.txt").write_text(
        "Edit the JSON files here, then run:\n"
        f"  python fedk.py campaign apply --name {name} --replace-day 03\n"
        "which copies them over the day-03 slot and merges the localisation keys.\n",
        encoding="utf-8")
    return out


def apply_campaign(project, name="day09", replace_day="03"):
    src = campaigns_dir(project) / name
    if not src.exists():
        raise SystemExit(f"campaign not found: {src}")
    data = Path(project.root) / "content" / "data"
    dd = replace_day.zfill(2)
    mapping = {
        f"{name}.json": f"day{dd}.json",
        f"{name}_dialogues.json": f"day{dd}_dialogues.json",
        "missions.json": f"d{dd}_missions.json",
        "rules.json": f"d{dd}_rules.json",
    }
    written = []
    for source, target in mapping.items():
        s, t = src / source, data / target
        if not s.exists():
            continue
        if not t.exists():
            print(f"  ! slot {target} does not exist in this build - skipped")
            continue
        shutil.copy2(s, t)
        written.append(t)
    loc_src = src / "localisation EN.json"
    loc_dst = data / "localization" / "Localization EN.json"
    if loc_src.exists() and loc_dst.exists():
        table = json.loads(loc_dst.read_text(encoding="utf-8"))
        have = {r[0] for r in table if isinstance(r, list) and r}
        for key, text in json.loads(loc_src.read_text(encoding="utf-8")):
            if key not in have:
                table.append([key, text])
        loc_dst.write_text(json.dumps(table, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(loc_dst)
    return written


def validate(project):
    problems = []
    content = Path(project.root) / "content"
    loc_keys = set()
    for p in (content / "data" / "localization").glob("*.json"):
        try:
            table = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            problems.append(f"{p.name}: invalid JSON ({e})")
            continue
        if isinstance(table, list) and table and isinstance(table[0], list):
            loc_keys |= {r[0] for r in table if isinstance(r, list) and r}
    used = set()

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ("text_key", "loc", "decoded_message", "ver_sender_key",
                         "ver_receiver_key", "message"):
                    if isinstance(v, str) and v and not v.endswith(".png"):
                        used.add(v)
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for p in (content / "data").glob("*.json"):
        try:
            walk(json.loads(p.read_text(encoding="utf-8")))
        except Exception as e:
            problems.append(f"{p.name}: invalid JSON ({e})")
    missing = sorted(k for k in used if k and k not in loc_keys and not k.startswith("spr_"))
    return problems, missing
