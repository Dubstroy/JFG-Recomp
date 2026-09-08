import struct
import re
from pathlib import Path

ROM_PATH = Path("rom/JetForceGemini.z64")

RAM_START = 0x80000000
RAM_END   = 0x80800000

def u32(data, off):
    return struct.unpack_from(">I", data, off)[0]

def u16(data, off):
    return struct.unpack_from(">H", data, off)[0]

def is_ram(addr):
    return RAM_START <= addr < RAM_END

def is_rom_offset(value, rom_size):
    return 0 <= value < rom_size

def printable_string(data):
    return all(32 <= b <= 126 or b in (9,) for b in data)

print("=" * 70)
print("JET FORCE GEMINI - ANALISIS ROM")
print("=" * 70)

if not ROM_PATH.exists():
    print(f"ERROR: No existe {ROM_PATH}")
    raise SystemExit(1)

data = ROM_PATH.read_bytes()
size = len(data)

print(f"\nROM size : 0x{size:08X} ({size:,} bytes / {size / 1024 / 1024:.2f} MiB)")

# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

print("\n[1] N64 HEADER")
print("-" * 70)

magic = data[0:4]
print(f"Magic       : {magic.hex(' ').upper()}")

if magic == b"\x80\x37\x12\x40":
    print("Formato     : N64 .z64 BIG-ENDIAN")
elif magic == b"\x37\x80\x40\x12":
    print("Formato     : N64 .v64 BYTE-SWAPPED")
elif magic == b"\x40\x12\x37\x80":
    print("Formato     : N64 .n64 LITTLE-ENDIAN")
else:
    print("Formato     : desconocido")

clock = u32(data, 4)
entry = u32(data, 8)
release = u32(data, 0x0C)
crc1 = u32(data, 0x10)
crc2 = u32(data, 0x14)

name = data[0x20:0x34].rstrip(b"\x00 ").decode("ascii", errors="replace")

print(f"Clock       : 0x{clock:08X}")
print(f"Entrypoint  : 0x{entry:08X}")
print(f"Release     : 0x{release:08X}")
print(f"CRC1        : 0x{crc1:08X}")
print(f"CRC2        : 0x{crc2:08X}")
print(f"Name        : {name}")

# ------------------------------------------------------------
# BOOT
# ------------------------------------------------------------

print("\n[2] IPL3 / BOOT")
print("-" * 70)

boot_start = 0x40
boot_end = min(0x1000, size)

print(f"ROM         : 0x{boot_start:08X} - 0x{boot_end - 1:08X}")
print(f"RAM         : 0x80000400 - 0x{0x80000400 + (boot_end - boot_start) - 1:08X}")
print(f"Size        : {boot_end - boot_start:,} bytes")

# ------------------------------------------------------------
# FIRMAS DE COMPRESION
# ------------------------------------------------------------

print("\n[3] FIRMAS DE COMPRESION / CONTENEDORES")
print("-" * 70)

signatures = {
    b"MIO0": "MIO0",
    b"Yay0": "YAY0",
    b"YAY0": "YAY0",
    b"gzip": "GZIP",
    b"\x1f\x8b": "GZIP",
    b"RNC\x01": "RNC",
    b"RNC\x02": "RNC",
}

found_signatures = []

for sig, name_sig in signatures.items():
    pos = 0
    while True:
        pos = data.find(sig, pos)
        if pos == -1:
            break

        found_signatures.append((pos, name_sig))
        print(f"{name_sig:8} ROM 0x{pos:08X}")
        pos += 1

if not found_signatures:
    print("No se encontraron firmas conocidas.")

# ------------------------------------------------------------
# PUNTEROS RAM
# ------------------------------------------------------------

print("\n[4] PUNTEROS QUE PARECEN DIRECCIONES RAM")
print("-" * 70)

ram_hits = []

for off in range(0, size - 3, 4):
    value = u32(data, off)

    if is_ram(value):
        ram_hits.append((off, value))

for off, value in ram_hits[:300]:
    print(f"ROM 0x{off:08X} -> RAM 0x{value:08X}")

print(f"\nTotal candidatos RAM: {len(ram_hits):,}")

if len(ram_hits) > 300:
    print(f"(Mostrando solamente los primeros 300)")

# ------------------------------------------------------------
# PUNTEROS ROM
# ------------------------------------------------------------

print("\n[5] VALORES QUE PARECEN OFFSETS ROM")
print("-" * 70)

rom_hits = []

for off in range(0, size - 3, 4):
    value = u32(data, off)

    if value < size and value >= 0x1000:
        rom_hits.append((off, value))

for off, value in rom_hits[:300]:
    print(f"ROM 0x{off:08X} contiene offset 0x{value:08X}")

print(f"\nTotal candidatos ROM: {len(rom_hits):,}")

# ------------------------------------------------------------
# POSIBLES PARES ROM -> RAM
# ------------------------------------------------------------

print("\n[6] POSIBLES PARES ROM -> RAM")
print("-" * 70)

pairs = []

for off in range(0, size - 7, 4):
    a = u32(data, off)
    b = u32(data, off + 4)

    if is_rom_offset(a, size) and is_ram(b):
        pairs.append((off, a, b))

    elif is_ram(a) and is_rom_offset(b, size):
        pairs.append((off, a, b))

for off, a, b in pairs[:250]:
    print(
        f"ROM 0x{off:08X}: "
        f"0x{a:08X} -> 0x{b:08X}"
    )

print(f"\nTotal pares candidatos: {len(pairs):,}")

# ------------------------------------------------------------
# STRINGS ASCII
# ------------------------------------------------------------

print("\n[7] STRINGS ASCII IMPORTANTES")
print("-" * 70)

strings = []

i = 0

while i < size:
    if 32 <= data[i] <= 126:
        start = i

        while i < size and 32 <= data[i] <= 126:
            i += 1

        length = i - start

        if length >= 8:
            text = data[start:i].decode("ascii", errors="replace")
            strings.append((start, text))

    i += 1

# Primero strings que parezcan especialmente interesantes
keywords = (
    "DMA",
    "MIO",
    "YAY",
    "BOOT",
    "DEBUG",
    "ERROR",
    "GAME",
    "JET",
    "GEMINI",
    "ROM",
    "RAM",
    "LOAD",
    "SAVE",
    "FILE",
    "VERSION",
    "Rare",
    "Nintendo",
)

interesting = []

for off, text in strings:
    if any(k.lower() in text.lower() for k in keywords):
        interesting.append((off, text))

for off, text in interesting[:300]:
    print(f"ROM 0x{off:08X}: {text}")

print(f"\nStrings totales >=8 chars: {len(strings):,}")
print(f"Strings interesantes: {len(interesting):,}")

# ------------------------------------------------------------
# CANDIDATOS A TABLAS
# ------------------------------------------------------------

print("\n[8] ZONAS CON MUCHOS PUNTEROS RAM")
print("-" * 70)

# Agrupamos candidatos RAM cercanos.
clusters = []

if ram_hits:
    start = ram_hits[0][0]
    last = ram_hits[0][0]
    count = 1

    for off, value in ram_hits[1:]:
        if off - last <= 0x40:
            count += 1
        else:
            if count >= 3:
                clusters.append((start, last, count))

            start = off
            count = 1

        last = off

    if count >= 3:
        clusters.append((start, last, count))

for start, end, count in clusters[:150]:
    print(
        f"ROM 0x{start:08X}-0x{end+4:08X} "
        f"({count} punteros RAM)"
    )

print(f"\nClusters encontrados: {len(clusters):,}")

# ------------------------------------------------------------
# ANALISIS DE PALABRAS MIPS
# ------------------------------------------------------------

print("\n[9] CANDIDATOS A CODIGO MIPS")
print("-" * 70)

# Opcodes MIPS comunes.
# No significa que todo lo detectado sea código.
mips_opcodes = {
    0x00: "SPECIAL",
    0x01: "REGIMM",
    0x02: "J",
    0x03: "JAL",
    0x04: "BEQ",
    0x05: "BNE",
    0x06: "BLEZ",
    0x07: "BGTZ",
    0x08: "ADDI",
    0x09: "ADDIU",
    0x0A: "SLTI",
    0x0B: "SLTIU",
    0x0C: "ANDI",
    0x0D: "ORI",
    0x0E: "XORI",
    0x0F: "LUI",
    0x20: "LB",
    0x21: "LH",
    0x23: "LW",
    0x24: "LBU",
    0x25: "LHU",
    0x28: "SB",
    0x29: "SH",
    0x2B: "SW",
}

mips_hits = []

# No analizamos IPL3 otra vez.
analysis_start = 0x1000

for off in range(analysis_start, size - 3, 4):
    word = u32(data, off)
    opcode = word >> 26

    if opcode in mips_opcodes:
        mips_hits.append((off, word, mips_opcodes[opcode]))

for off, word, op in mips_hits[:500]:
    print(f"ROM 0x{off:08X}: {word:08X}  {op}")

print(f"\nTotal palabras con opcode MIPS común: {len(mips_hits):,}")

# ------------------------------------------------------------
# J / JAL Y TARGETS
# ------------------------------------------------------------

print("\n[10] J / JAL Y DESTINOS")
print("-" * 70)

jumps = []

for off in range(analysis_start, size - 3, 4):
    word = u32(data, off)
    opcode = word >> 26

    if opcode in (0x02, 0x03):
        target = (word & 0x03FFFFFF) << 2

        jumps.append((off, opcode, target))

for off, opcode, target in jumps[:500]:
    name_jump = "JAL" if opcode == 0x03 else "J"

    print(
        f"ROM 0x{off:08X}: "
        f"{name_jump} target field 0x{target:08X}"
    )

print(f"\nTotal J/JAL candidatos: {len(jumps):,}")

# ------------------------------------------------------------
# LUI -> DIRECCION RAM
# ------------------------------------------------------------

print("\n[11] LUI + SIGUIENTE INSTRUCCION")
print("-" * 70)

lui_hits = []

for off in range(analysis_start, size - 7, 4):
    word1 = u32(data, off)
    word2 = u32(data, off + 4)

    opcode1 = word1 >> 26

    if opcode1 == 0x0F:
        rt = (word1 >> 16) & 0x1F
        imm = word1 & 0xFFFF

        # Significado aproximado
        upper = imm << 16

        if is_ram(upper):
            lui_hits.append((off, word1, word2, upper, rt))

for off, w1, w2, upper, rt in lui_hits[:300]:
    print(
        f"ROM 0x{off:08X}: "
        f"LUI rt={rt} -> 0x{upper:08X} | "
        f"next=0x{w2:08X}"
    )

print(f"\nTotal LUI RAM candidatos: {len(lui_hits):,}")

# ------------------------------------------------------------
# DISTRIBUCION DE DATOS
# ------------------------------------------------------------

print("\n[12] DISTRIBUCION GENERAL")
print("-" * 70)

# Cantidad de ceros por bloques de 1 MB
block_size = 0x100000

for start in range(0, size, block_size):
    end = min(start + block_size, size)
    block = data[start:end]

    zero_count = block.count(0)
    printable = sum(1 for b in block if 32 <= b <= 126)

    print(
        f"ROM 0x{start:08X}-0x{end-1:08X} | "
        f"zeros={zero_count:7d} | "
        f"ASCII={printable:7d}"
    )

# ------------------------------------------------------------
# RESUMEN
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("RESUMEN")
print("=" * 70)

print(f"ROM size             : 0x{size:08X}")
print(f"Entrypoint header    : 0x{entry:08X}")
print(f"RAM pointer hits     : {len(ram_hits):,}")
print(f"ROM offset hits      : {len(rom_hits):,}")
print(f"ROM/RAM pairs        : {len(pairs):,}")
print(f"Compression signatures: {len(found_signatures):,}")
print(f"Strings >=8 chars    : {len(strings):,}")
print(f"MIPS opcode hits     : {len(mips_hits):,}")
print(f"J/JAL candidates     : {len(jumps):,}")
print(f"LUI RAM candidates   : {len(lui_hits):,}")

print("\nANALISIS TERMINADO")
print("No asumir que los candidatos MIPS son codigo real.")