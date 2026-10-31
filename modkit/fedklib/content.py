"""Content blobs: the game's actual data (days, dialogues, missions, localisation).

They are base64(zlib(json)) strings compiled into False Echo.exe as GML string
constants. Each blob is referenced by exactly one `lea rdx, [rip+disp]` in the
binary, which is what makes safe in-place patching (and relocation) possible.
"""
import base64
import json
import zlib

LANGS = ["CS", "DE", "EN", "ES", "FR", "ITA", "KO", "PL", "RU"]

# STRG index -> logical file name (verified by decoding every blob)
CONTENT_MAP = {
    2598: "data/characters.json",
    2599: "data/d01_missions.json",
    2600: "data/d02_missions.json",
    2601: "data/d03_missions.json",
    2602: "data/d99_missions.json",
    2603: "data/d99_rules.json",
    2604: "data/day01.json",
    2605: "data/day01_dialogues.json",
    2606: "data/day02.json",
    2607: "data/day02_dialogues.json",
    2608: "data/day03.json",
    2609: "data/day03_dialogues.json",
    2610: "data/day99_dialogues.json",
    2612: "data/intro.json",
    2622: "data/localization/FE Rules and Missions - Rules.json",
}
GROUPS = {
    2613: ("data/localization/Endless {L}.json", LANGS),
    2623: ("data/localization/Frontline News {L}.json", LANGS),
    2632: ("data/localization/Localization {L}.json", LANGS),
    2641: ("data/localization/War Diary {L}.json", LANGS),
}
for start, (pattern, langs) in GROUPS.items():
    for i, lang in enumerate(langs):
        CONTENT_MAP[start + i] = pattern.format(L=lang)

BY_NAME = {v: k for k, v in CONTENT_MAP.items()}


def decode(b64):
    """base64+zlib -> parsed JSON. Returns (obj, had_trailing_nul)."""
    raw = zlib.decompress(base64.b64decode(b64 + "=" * (-len(b64) % 4)))
    nul = raw.endswith(b"\x00")
    return json.loads(raw.rstrip(b"\x00").decode("utf-8")), nul


def encode(obj, nul=True):
    """JSON -> base64+zlib (compact, UTF-8 preserved)."""
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    raw = text.encode("utf-8") + (b"\x00" if nul else b"")
    return base64.b64encode(zlib.compress(raw, 9)).decode("ascii")


def _csize(text):
    return len(zlib.compress(text.encode("utf-8"), 9))


def fit(obj, target_b64_len, nul=True):
    """Encode so the base64 text is *exactly* target_b64_len chars.

    Trailing spaces are legal JSON whitespace and are tolerated by the game's
    parser (verified in-game), so they are used as padding.
    """
    base = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ("\x00" if nul else "")
    q = target_b64_len // 4
    lo, hi = (q - 1) * 3 + 1, q * 3

    def size(pad):
        # padding goes before the NUL terminator
        s = base[:-1] + " " * pad + base[-1] if nul else base + " " * pad
        return _csize(s)

    if size(0) > hi:
        return None
    if size(0) >= lo:
        best = 0
    else:
        a, b = 0, 400000
        if size(b) < lo:
            return None
        while a < b:
            m = (a + b) // 2
            if size(m) < lo:
                a = m + 1
            else:
                b = m
        best = a
    for pad in range(max(0, best - 64), best + 512):
        n = size(pad)
        if lo <= n <= hi:
            s = (base[:-1] + " " * pad + base[-1]) if nul else (base + " " * pad)
            out = base64.b64encode(zlib.compress(s.encode("utf-8"), 9)).decode("ascii")
            if len(out) == target_b64_len:
                return out
        if n > hi:
            break
    return None
