from pathlib import Path
import struct

ROM_PATH = Path("rom/JetForceGemini.z64")

TARGET = 0x000A32E4
BEFORE = 0x80
AFTER = 0x100

RAM_MIN = 0x80000000
RAM_MAX = 0x80800000


def u32(data, off):
    return struct.unpack_from(">I", data, off)[0]


def is_ram(x):
    return RAM_MIN <= x < RAM_MAX


data = ROM_PATH.read_bytes()

start = TARGET - BEFORE
end = TARGET + AFTER

print("=" * 78)
print("INSPECCION DE POSIBLE TABLA ROM/RAM")
print("=" * 78)
print(f"Zona: 0x{start:08X} - 0x{end:08X}")
print(f"Objetivo: 0x{TARGET:08X}")
print()

print("[1] PALABRAS DE 32 BITS")
print("-" * 78)

for off in range(start, end, 4):

    value = u32(data, off)

    tags = []

    if value < len(data):
        tags.append("ROM")

    if is_ram(value):
        tags.append("RAM")

    if value % 4 == 0:
        tags.append("ALIGN4")

    tag_text = ",".join(tags)

    print(
        f"ROM 0x{off:08X} : "
        f"0x{value:08X}"
        + (f" [{tag_text}]" if tag_text else "")
    )


print()
print("[2] BYTES + ASCII")
print("-" * 78)

for off in range(start, end, 16):

    chunk = data[off:off + 16]

    hex_part = " ".join(f"{b:02X}" for b in chunk)

    ascii_part = "".join(
        chr(b) if 32 <= b <= 126 else "."
        for b in chunk
    )

    print(
        f"0x{off:08X}: "
        f"{hex_part:<47} "
        f"|{ascii_part}|"
    )


print()
print("[3] INTERPRETACION DE POSIBLES PARES")
print("-" * 78)

for off in range(start, end - 8, 4):

    a = u32(data, off)
    b = u32(data, off + 4)

    if a < len(data) and is_ram(b):

        print(
            f"ROM 0x{off:08X}: "
            f"ROM={a:#010x} -> RAM={b:#010x}"
        )


print()
print("[4] POSIBLES ENTRADAS DE 16 BYTES")
print("-" * 78)

for off in range(start, end - 16, 4):

    a = u32(data, off)
    b = u32(data, off + 4)
    c = u32(data, off + 8)
    d = u32(data, off + 12)

    if (
        a < len(data)
        and b <= len(data)
        and a < b
        and is_ram(c)
    ):
        print(
            f"ROM tabla 0x{off:08X} | "
            f"ROM {a:#010x}-{b:#010x} | "
            f"RAM {c:#010x} | "
            f"valor4={d:#010x}"
        )


print()
print("=" * 78)
print("FIN")
print("=" * 78)