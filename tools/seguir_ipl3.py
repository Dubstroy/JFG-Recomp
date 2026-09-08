from pathlib import Path
import struct
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_BIG_ENDIAN


ROM_PATH = Path("rom/JetForceGemini.z64")

ROM_BOOT_START = 0x40
ROM_BOOT_END = 0x1000

RAM_BOOT_START = 0x80000400

MAX_INSTRUCTIONS = 5000


def u32(data, off):
    return struct.unpack_from(">I", data, off)[0]


def rom_to_ram(rom_off):
    return RAM_BOOT_START + (rom_off - ROM_BOOT_START)


def ram_to_rom(ram_addr):
    return ROM_BOOT_START + (ram_addr - RAM_BOOT_START)


data = ROM_PATH.read_bytes()

boot = data[ROM_BOOT_START:ROM_BOOT_END]

md = Cs(
    CS_ARCH_MIPS,
    CS_MODE_MIPS32 + CS_MODE_BIG_ENDIAN
)

md.detail = True


# ----------------------------------------------------------------------
# Crear mapa de instrucciones del IPL3
# ----------------------------------------------------------------------

instructions = {}

for insn in md.disasm(boot, RAM_BOOT_START):

    instructions[insn.address] = insn


print("=" * 78)
print("JET FORCE GEMINI - CONTROL FLOW IPL3")
print("=" * 78)

print(f"ROM boot : 0x{ROM_BOOT_START:08X}-0x{ROM_BOOT_END:08X}")
print(f"RAM boot : 0x{RAM_BOOT_START:08X}-0x{RAM_BOOT_START + len(boot):08X}")
print(f"Entry    : 0x{RAM_BOOT_START:08X}")
print()

print(f"Instrucciones decodificadas: {len(instructions)}")
print()


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def parse_imm(op_str):

    # Busca el último número hexadecimal/decimal de la instrucción.
    # No pretende ser un parser completo de MIPS.

    parts = op_str.replace(",", " ").split()

    for p in reversed(parts):

        p = p.strip()

        try:
            if p.startswith("0x"):
                return int(p, 16)

            if p.startswith("-0x"):
                return -int(p[1:], 16)

        except:
            pass

    return None


def target_of(insn):

    mnem = insn.mnemonic.lower()
    op = insn.op_str

    # J / JAL
    if mnem in ("j", "jal"):

        try:
            return int(op, 16)
        except:
            return None

    # Branches: Capstone normalmente muestra la dirección destino
    if mnem.startswith("b"):

        parts = op.replace(",", " ").split()

        if parts:

            candidate = parts[-1]

            try:
                return int(candidate, 16)
            except:
                pass

    return None


def is_unconditional_jump(mnem):

    return mnem in (
        "j",
        "jr",
    )


def is_branch(mnem):

    return mnem.startswith("b")


# ----------------------------------------------------------------------
# Seguimiento CFG
# ----------------------------------------------------------------------

visited = set()
queue = [RAM_BOOT_START]

edges = []

external_targets = set()

jal_targets = set()

branch_targets = set()

indirect_jumps = []


while queue and len(visited) < MAX_INSTRUCTIONS:

    addr = queue.pop()

    if addr in visited:
        continue

    insn = instructions.get(addr)

    if insn is None:
        continue

    visited.add(addr)

    mnem = insn.mnemonic.lower()

    next_addr = addr + 4

    target = target_of(insn)

    # --------------------------------------------------------------
    # JAL
    # --------------------------------------------------------------

    if mnem == "jal":

        if target is not None:

            jal_targets.add(target)

            if target in instructions:
                queue.append(target)
            else:
                external_targets.add(target)

            edges.append(
                (addr, "JAL", target)
            )

        # Delay slot + continuación
        queue.append(next_addr)
        continue

    # --------------------------------------------------------------
    # J
    # --------------------------------------------------------------

    if mnem == "j":

        if target is not None:

            if target in instructions:
                queue.append(target)
            else:
                external_targets.add(target)

            edges.append(
                (addr, "J", target)
            )

        # El delay slot se ejecuta antes del salto
        queue.append(next_addr)

        # No seguir secuencialmente después del delay slot
        continue

    # --------------------------------------------------------------
    # JR
    # --------------------------------------------------------------

    if mnem == "jr":

        indirect_jumps.append(
            (addr, insn.mnemonic, insn.op_str)
        )

        # El delay slot se ejecuta, pero destino desconocido
        queue.append(next_addr)
        continue

    # --------------------------------------------------------------
    # Branch
    # --------------------------------------------------------------

    if is_branch(mnem):

        if target is not None:

            branch_targets.add(target)

            if target in instructions:
                queue.append(target)
            else:
                external_targets.add(target)

            edges.append(
                (addr, "BRANCH", target)
            )

        # delay slot + camino fall-through
        queue.append(next_addr)
        continue

    # --------------------------------------------------------------
    # Instrucción normal
    # --------------------------------------------------------------

    queue.append(next_addr)


# ----------------------------------------------------------------------
# Mostrar instrucciones alcanzables
# ----------------------------------------------------------------------

print("[1] INSTRUCCIONES ALCANZABLES DESDE ENTRYPOINT")
print("-" * 78)

for addr in sorted(visited):

    insn = instructions[addr]

    rom = ram_to_rom(addr)

    print(
        f"ROM 0x{rom:08X} | "
        f"RAM 0x{addr:08X} | "
        f"{insn.mnemonic:<8} {insn.op_str}"
    )


print()
print(f"Total alcanzables: {len(visited)}")
print()


# ----------------------------------------------------------------------
# JAL
# ----------------------------------------------------------------------

print("[2] DESTINOS JAL")
print("-" * 78)

for target in sorted(jal_targets):

    if target in instructions:

        print(
            f"JAL interno: 0x{target:08X} "
            f"(ROM 0x{ram_to_rom(target):08X})"
        )

    else:

        print(
            f"JAL EXTERNO: 0x{target:08X}"
        )


print()
print(f"Total JAL: {len(jal_targets)}")
print()


# ----------------------------------------------------------------------
# Branches
# ----------------------------------------------------------------------

print("[3] DESTINOS DE BRANCH")
print("-" * 78)

for target in sorted(branch_targets):

    if target in instructions:

        print(
            f"Branch interno: 0x{target:08X} "
            f"(ROM 0x{ram_to_rom(target):08X})"
        )

    else:

        print(
            f"Branch externo: 0x{target:08X}"
        )


print()
print(f"Total branches: {len(branch_targets)}")
print()


# ----------------------------------------------------------------------
# Destinos externos
# ----------------------------------------------------------------------

print("[4] DESTINOS FUERA DEL IPL3")
print("-" * 78)

for target in sorted(external_targets):

    print(
        f"0x{target:08X}"
    )


print()
print(f"Total destinos externos: {len(external_targets)}")
print()


# ----------------------------------------------------------------------
# JR
# ----------------------------------------------------------------------

print("[5] JR / SALTOS INDIRECTOS")
print("-" * 78)

for addr, mnemonic, op in indirect_jumps:

    print(
        f"RAM 0x{addr:08X} | "
        f"{mnemonic} {op}"
    )


print()
print(f"Total JR: {len(indirect_jumps)}")
print()


# ----------------------------------------------------------------------
# Últimas instrucciones alcanzables
# ----------------------------------------------------------------------

print("[6] ULTIMAS INSTRUCCIONES ALCANZABLES")
print("-" * 78)

for addr in sorted(visited)[-40:]:

    insn = instructions[addr]

    print(
        f"RAM 0x{addr:08X} | "
        f"{insn.mnemonic:<8} {insn.op_str}"
    )


print()
print("=" * 78)
print("FIN")
print("=" * 78)