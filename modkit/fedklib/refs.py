"""Fast RIP-relative LEA reference finder.

GML string constants in a YYC build are materialised by `lea reg, [rip+disp]`
instructions. Scanning for the handful of LEA encodings is ~1000x faster than
disassembling the whole .text section.
"""
import struct

_MODRM_RIP = (0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0x3D)


def find_lea_refs(pe, targets):
    """targets: iterable of VAs. Returns {target_va: [instruction_vas]}."""
    wanted = set(targets)
    out = {}
    text = [s for s in pe.sections if s[0] == ".text"][0]
    start_va, raw, size = text[1], text[3], text[2]
    blob = bytes(pe.data[raw:raw + size])
    i = 0
    while True:
        i = blob.find(b"\x48\x8d", i)
        if i < 0:
            break
        if i + 6 < len(blob):
            modrm = blob[i + 2]
            if modrm in _MODRM_RIP:
                disp = struct.unpack_from("<i", blob, i + 3)[0]
                insn_va = start_va + i
                tgt = insn_va + 7 + disp
                if tgt in wanted:
                    out.setdefault(tgt, []).append(insn_va)
        i += 1
    return out
