from pathlib import Path
from capstone import *
import struct

ROM_PATH = Path(r"rom\JetForceGemini.z64")

BOOT_START = 0x40
BOOT_END = 0x1000
RAM_BASE = 0x80000400

rom = ROM_PATH.read_bytes()
boot = rom[BOOT_START:BOOT_END]

md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_BIG_ENDIAN)
md.detail = True


def u32(data, off):
    return struct.unpack(">I", data[off:off+4])[0]


def rom_to_ram(rom_off):
    return RAM_BASE + (rom_off - BOOT_START)


def ram_to_rom(ram):
    return BOOT_START + (ram - RAM_BASE)


def is_ram(v):
    return (
        0x80000000 <= v <= 0x807FFFFF or
        0xA0000000 <= v <= 0xA07FFFFF
    )


def is_rom(v):
    return 0 <= v < len(rom)


def print_ins(ins):
    ro = ram_to_rom(ins.address)
    print(
        f"ROM 0x{ro:04X} | "
        f"RAM 0x{ins.address:08X} | "
        f"{ins.mnemonic:8} {ins.op_str}"
    )


print("=" * 72)
print("JET FORCE GEMINI - ANALISIS PROFUNDO DEL BOOT")
print("=" * 72)

print(f"ROM size:       {len(rom):,} bytes")
print(f"Boot:           0x{BOOT_START:04X}-0x{BOOT_END-1:04X}")
print(f"Boot size:      {len(boot)} bytes")
print(f"RAM base:       0x{RAM_BASE:08X}")

# ============================================================
# DESENSAMBLAR CADA OFFSET, NO SOLO LINEALMENTE
# ============================================================

print()
print("[1] INSTRUCCIONES MIPS DETECTADAS")
print()

all_instructions = {}

for off in range(0, len(boot) - 3, 4):
    code = boot[off:off+4]
    ram = rom_to_ram(BOOT_START + off)

    ins = list(md.disasm(code, ram))

    if ins:
        i = ins[0]
        all_instructions[off] = i

print(f"Instrucciones individuales reconocidas: {len(all_instructions)}")

# ============================================================
# AGRUPAR INSTRUCCIONES CONTIGUAS
# ============================================================

print()
print("[2] REGIONES DE CODIGO")

regions = []

offsets = sorted(all_instructions)

if offsets:
    start = offsets[0]
    prev = offsets[0]

    for off in offsets[1:]:
        if off == prev + 4:
            prev = off
        else:
            regions.append((start, prev + 4))
            start = off
            prev = off

    regions.append((start, prev + 4))

# Fusionar huecos <= 16 bytes
merged = []

for start, end in regions:
    if not merged:
        merged.append([start, end])
    else:
        if start - merged[-1][1] <= 16:
            merged[-1][1] = end
        else:
            merged.append([start, end])

for n, (start, end) in enumerate(merged, 1):
    print(
        f"Region {n:02}: "
        f"ROM 0x{BOOT_START+start:04X}-0x{BOOT_START+end-1:04X} | "
        f"RAM 0x{rom_to_ram(BOOT_START+start):08X}-"
        f"0x{rom_to_ram(BOOT_START+end-4):08X} | "
        f"{end-start} bytes"
    )

# ============================================================
# CONTROL FLOW
# ============================================================

print()
print("[3] CONTROL FLOW")
print()

control_mnemonics = {
    "j", "jal", "jr", "jalr",
    "beq", "bne",
    "blez", "bgtz",
    "bltz", "bgez",
    "bltzal", "bgezal"
}

for off, ins in all_instructions.items():
    if ins.mnemonic in control_mnemonics:
        print_ins(ins)

# ============================================================
# J / JAL: CALCULAR DESTINO
# ============================================================

print()
print("[4] DESTINOS DE J / JAL")
print()

for off, ins in all_instructions.items():

    if ins.mnemonic not in ("j", "jal"):
        continue

    try:
        target = int(ins.op_str, 16)
    except ValueError:
        continue

    print(
        f"{ins.mnemonic.upper():4} "
        f"RAM 0x{ins.address:08X} -> "
        f"0x{target:08X}"
    )

# ============================================================
# LUI
# ============================================================

print()
print("[5] LUI - POSIBLES CONSTRUCCIONES DE DIRECCIONES")
print()

items = sorted(all_instructions.items())

for index, (off, ins) in enumerate(items):

    if ins.mnemonic != "lui":
        continue

    print_ins(ins)

    if index + 1 < len(items):
        next_ins = items[index + 1][1]
        print(
            f"             siguiente: "
            f"{next_ins.mnemonic} {next_ins.op_str}"
        )

# ============================================================
# CONSTANTES 32 BIT
# ============================================================

print()
print("[6] CONSTANTES QUE PARECEN DIRECCIONES")
print()

for off in range(0, len(boot) - 3, 4):

    value = u32(boot, off)

    if is_ram(value):
        print(
            f"ROM 0x{BOOT_START+off:04X}: "
            f"0x{value:08X}  <-- RAM"
        )

    elif 0x04000000 <= value <= 0x04FFFFFF:
        print(
            f"ROM 0x{BOOT_START+off:04X}: "
            f"0x{value:08X}  <-- N64 HARDWARE"
        )

# ============================================================
# POSIBLES OFFSETS DEL ROM
# ============================================================

print()
print("[7] POSIBLES REFERENCIAS AL ROM")
print()

rom_refs = []

for off in range(0, len(boot) - 3, 4):

    value = u32(boot, off)

    if 0 < value < len(rom) and value % 4 == 0:
        rom_refs.append((off, value))

for off, value in rom_refs:

    print(
        f"ROM 0x{BOOT_START+off:04X}: "
        f"0x{value:08X}"
    )

# ============================================================
# PALABRAS CRITICAS DEL BOOT
# ============================================================

print()
print("[8] WORDS DEL BOOT")
print()

for off in range(0, len(boot), 4):

    value = u32(boot, off)

    # Solo mostrar words interesantes
    interesting = (
        is_ram(value) or
        0x04000000 <= value <= 0x04FFFFFF or
        (0 < value < len(rom) and value % 4 == 0)
    )

    if interesting:
        print(
            f"ROM 0x{BOOT_START+off:04X} | "
            f"RAM 0x{rom_to_ram(BOOT_START+off):08X} | "
            f"0x{value:08X}"
        )

# ============================================================
# PRIMERAS REGIONES DE CODIGO COMPLETAS
# ============================================================

print()
print("[9] DETALLE DE REGIONES DE CODIGO")
print()

for n, (start, end) in enumerate(merged, 1):

    size = end - start

    if size < 12:
        continue

    print()
    print(
        f"--- REGION {n:02} "
        f"ROM 0x{BOOT_START+start:04X}-0x{BOOT_START+end-1:04X} "
        f"({size} bytes) ---"
    )

    for off in range(start, end, 4):

        ins = all_instructions.get(off)

        if ins:
            print_ins(ins)

# ============================================================
# RESUMEN
# ============================================================

print()
print("=" * 72)
print("RESUMEN")
print("=" * 72)

print(f"ROM:                    {len(rom):,} bytes")
print(f"Boot:                   {len(boot)} bytes")
print(f"Instrucciones MIPS:     {len(all_instructions)}")
print(f"Regiones detectadas:    {len(merged)}")
print(f"Referencias ROM:        {len(rom_refs)}")

print()
print("IMPORTANTE:")
print("Las regiones son heuristicas.")
print("No deben utilizarse aun como segmentos definitivos del ELF.")
print("=" * 72)