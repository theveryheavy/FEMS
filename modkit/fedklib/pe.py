"""Minimal dependency-free PE32+ (x64) reader/writer for False Echo modding.

Covers: section map, VA<->offset, locating base64 blobs, RIP-relative reference
discovery (GML string constants are only referenced that way), in-place patching,
and appending a new section + retargeting references when content grows.
"""
import struct


class PE:
    def __init__(self, path):
        self.path = str(path)
        self.data = bytearray(open(self.path, "rb").read())
        self._reload()

    def _reload(self):
        data = self.data
        if data[:2] != b"MZ" or len(data) < 0x40:
            raise ValueError("not a valid PE file (missing DOS header)")
        pe_off = struct.unpack_from("<I", data, 0x3C)[0]
        if pe_off + 24 > len(data) or data[pe_off:pe_off + 4] != b"PE\0\0":
            raise ValueError("not a valid PE file (missing PE signature)")
        coff = pe_off + 4
        nsec = struct.unpack_from("<H", data, coff + 2)[0]
        opt_size = struct.unpack_from("<H", data, coff + 16)[0]
        opt = coff + 20
        if opt + opt_size > len(data) or struct.unpack_from("<H", data, opt)[0] != 0x20B:
            raise ValueError("expected a PE32+ executable")
        self.base = struct.unpack_from("<Q", data, opt + 24)[0]
        self.sections = []
        sec_table = opt + opt_size
        for i in range(nsec):
            off = sec_table + i * 40
            if off + 40 > len(data):
                raise ValueError("truncated PE section table")
            name = bytes(data[off:off + 8]).rstrip(b"\0").decode(errors="replace")
            vsize, rva, raw_size, raw_ptr = struct.unpack_from("<IIII", data, off + 8)
            self.sections.append((name, self.base + rva, raw_size, raw_ptr, vsize))

    def off2va(self, off):
        for name, va, size, raw, vsize in self.sections:
            if raw <= off < raw + size:
                return va + (off - raw)
        return None

    def va2off(self, va):
        for name, sva, size, raw, vsize in self.sections:
            if sva <= va < sva + max(size, vsize):
                return raw + (va - sva)
        return None

    def sec_of(self, va):
        for name, sva, size, raw, vsize in self.sections:
            if sva <= va < sva + max(size, vsize):
                return name
        return None

    def read_cstr(self, va, maxlen=200):
        off = self.va2off(va)
        if off is None:
            return None
        return bytes(self.data[off:off + maxlen]).split(b"\0")[0]

    def find_blob(self, b64):
        needle = b64[:64].encode()
        i = bytes(self.data).find(needle)
        while i >= 0:
            if bytes(self.data[i:i + len(b64)]) == b64.encode():
                return i, self.off2va(i)
            i = bytes(self.data).find(needle, i + 1)
        return None

    def rip_refs(self):
        text = next((s for s in self.sections if s[0] == ".text"), None)
        if text is None:
            raise ValueError("PE has no .text section")
        blob = bytes(self.data[text[3]:text[3] + text[2]])
        targets = {}
        modrm_rip = {0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0x3D}
        pos = 0
        while True:
            pos = blob.find(b"\x48\x8d", pos)
            if pos < 0:
                break
            if pos + 7 <= len(blob) and blob[pos + 2] in modrm_rip:
                disp = struct.unpack_from("<i", blob, pos + 3)[0]
                va = text[1] + pos
                targets.setdefault(va + 7 + disp, []).append(va)
            pos += 1
        return targets

    def patch_bytes(self, off, payload):
        self.data[off:off + len(payload)] = payload

    def save(self, path):
        with open(path, "wb") as f:
            f.write(self.data)

    def add_section(self, payload, name=b".fedk", characteristics=0x40000040):
        data = self.data
        e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
        nsec = struct.unpack_from("<H", data, e_lfanew + 6)[0]
        opt_size = struct.unpack_from("<H", data, e_lfanew + 20)[0]
        opt = e_lfanew + 24
        sec_table = opt + opt_size
        if sec_table + (nsec + 1) * 40 > min(s[3] for s in self.sections):
            raise RuntimeError("no room for another section header")
        file_align = struct.unpack_from("<I", data, opt + 36)[0]
        sect_align = struct.unpack_from("<I", data, opt + 32)[0]
        size_of_headers = struct.unpack_from("<I", data, opt + 60)[0]

        last = max(self.sections, key=lambda s: s[1])
        last_end_va = last[1] + max(last[4], last[2])
        new_va = (last_end_va + sect_align - 1) // sect_align * sect_align
        raw_ptr = (len(data) + file_align - 1) // file_align * file_align
        if len(data) < raw_ptr:
            data.extend(b"\0" * (raw_ptr - len(data)))
        data.extend(payload)
        raw_size = (len(payload) + file_align - 1) // file_align * file_align
        if len(data) < raw_ptr + raw_size:
            data.extend(b"\0" * (raw_ptr + raw_size - len(data)))

        hdr = bytearray(40)
        hdr[0:len(name)] = name
        struct.pack_into("<I", hdr, 8, (len(payload) + sect_align - 1) // sect_align * sect_align)
        struct.pack_into("<I", hdr, 12, new_va - self.base)
        struct.pack_into("<I", hdr, 16, raw_size)
        struct.pack_into("<I", hdr, 20, raw_ptr)
        struct.pack_into("<I", hdr, 36, characteristics)
        data[sec_table + nsec * 40: sec_table + (nsec + 1) * 40] = hdr

        struct.pack_into("<H", data, e_lfanew + 6, nsec + 1)
        struct.pack_into("<I", data, opt + 56, new_va - self.base + ((len(payload) + sect_align - 1) // sect_align * sect_align))
        # SizeOfHeaders must stay as-is: it describes the PE headers, not the file offset
        self._reload()
        return new_va

    def retarget_rip_ref(self, insn_va, new_target_va):
        off = self.va2off(insn_va)
        if off is None:
            raise ValueError("bad instruction address")
        if off + 7 > len(self.data) or self.data[off:off + 2] != b"\x48\x8d":
            raise ValueError("expected RIP-relative LEA at %#x" % insn_va)
        modrm = self.data[off + 2]
        if modrm not in {0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0x3D}:
            raise ValueError("LEA is not RIP-relative at %#x" % insn_va)
        new_disp = new_target_va - (insn_va + 7)
        if not (-2**31 <= new_disp < 2**31):
            raise ValueError("target out of rel32 range")
        struct.pack_into("<i", self.data, off + 3, new_disp)
        return True
