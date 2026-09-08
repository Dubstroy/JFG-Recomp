from pathlib import Path
import struct
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_BIG_ENDIAN

ROM_PATH = Path("rom/JetForceGemini.z64")

ROM_START = 0x40
ROM_END   = 0x1000
RAM_START = 0x80000400

data = ROM_PATH.read_bytes()
boot = data[ROM_START:ROM_END]

md = Cs(
    CS_ARCH_MIPS,
    CS_MODE_MIPS32 | CS_MODE_BIG_ENDIAN
)

print("=" * 100)
print("JET FORCE GEMINI - DESENSAMBLADO COMPLETO IPL3")
print("=" * 100)
print(f"ROM: 0x{ROM_START:04X}-0x{ROM_END:04X}")
print(f"RAM: 0x{RAM_START:08X}-0x{RAM_START + len(boot):08X}")
print()

count = 0

for off in range(0, len(boot), 4):
    rom = ROM_START + off
    ram = RAM_START + off

    word = struct.unpack_from(">I", boot, off)[0]
    raw = boot[off:off+4]

    insns = list(md.disasm(raw, ram))

    if insns:
        insn = insns[0]

        print(
            f"ROM 0x{rom:04X} | "
            f"RAM 0x{ram:08X} | "
            f"{word:08X} | "
            f"{insn.mnemonic:<10} {insn.op_str}"
        )

        count += 1

    else:
        print(
            f"ROM 0x{rom:04X} | "
            f"RAM 0x{ram:08X} | "
            f"{word:08X} | "
            f"????"
        )

print()
print("=" * 100)
print(f"Palabras analizadas : {len(boot) // 4}")
print(f"Instrucciones MIPS  : {count}")
print("=" * 100)