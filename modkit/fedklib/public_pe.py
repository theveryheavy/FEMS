"""Restricted PE writer for the public, content-only FEMS distribution.

This deliberately contains patch operations only. It has no string scanning,
blob discovery, disassembly, or extraction helpers.
"""
import struct


class PatchPE:
    def __init__(self, path):
        self.path = str(path)
        self.data = bytearray(open(self.path, "rb").read())
        self._reload()

    def _reload(self):
        data = self.data
        if data[:2] != b"MZ" or len(data) < 0x40:
            raise ValueError("not a valid PE file")
        pe_off = struct.unpack_from("<I", data, 0x3C)[0]
        if pe_off + 24 > len(data) or data[pe_off:pe_off + 4] != b"PE\0\0":
            raise ValueError("not a valid PE file")
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

    def va2off(self, va):
        for _name, sva, size, raw, vsize in self.sections:
            if sva <= va < sva + max(size, vsize):
                return raw + (va - sva)
        return None

    def patch_bytes(self, off, payload):
        self.data[off:off + len(payload)] = payload

    def save(self, path):
        with open(path, "wb") as stream:
            stream.write(self.data)

    def add_section(self, payload, name=b".fems", characteristics=0x40000040):
        data = self.data
        e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
        nsec = struct.unpack_from("<H", data, e_lfanew + 6)[0]
        opt_size = struct.unpack_from("<H", data, e_lfanew + 20)[0]
        opt = e_lfanew + 24
        sec_table = opt + opt_size
        if sec_table + (nsec + 1) * 40 > min(section[3] for section in self.sections):
            raise RuntimeError("no room for another section header")
        file_align = struct.unpack_from("<I", data, opt + 36)[0]
        sect_align = struct.unpack_from("<I", data, opt + 32)[0]
        last = max(self.sections, key=lambda section: section[1])
        last_end_va = last[1] + max(last[4], last[2])
        new_va = (last_end_va + sect_align - 1) // sect_align * sect_align
        raw_ptr = (len(data) + file_align - 1) // file_align * file_align
        data.extend(b"\0" * (raw_ptr - len(data)))
        data.extend(payload)
        raw_size = (len(payload) + file_align - 1) // file_align * file_align
        data.extend(b"\0" * (raw_ptr + raw_size - len(data)))
        header = bytearray(40)
        header[:len(name)] = name
        struct.pack_into("<I", header, 8, (len(payload) + sect_align - 1) // sect_align * sect_align)
        struct.pack_into("<I", header, 12, new_va - self.base)
        struct.pack_into("<I", header, 16, raw_size)
        struct.pack_into("<I", header, 20, raw_ptr)
        struct.pack_into("<I", header, 36, characteristics)
        data[sec_table + nsec * 40:sec_table + (nsec + 1) * 40] = header
        struct.pack_into("<H", data, e_lfanew + 6, nsec + 1)
        struct.pack_into("<I", data, opt + 56, new_va - self.base + ((len(payload) + sect_align - 1) // sect_align * sect_align))
        self._reload()
        return new_va

    def retarget_rip_ref(self, insn_va, new_target_va):
        off = self.va2off(insn_va)
        if off is None or off + 7 > len(self.data) or self.data[off:off + 2] != b"\x48\x8d":
            raise ValueError("expected RIP-relative LEA")
        if self.data[off + 2] not in {0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0x3D}:
            raise ValueError("LEA is not RIP-relative")
        displacement = new_target_va - (insn_va + 7)
        if not (-2**31 <= displacement < 2**31):
            raise ValueError("target is out of relative-address range")
        struct.pack_into("<i", self.data, off + 3, displacement)
        return True
