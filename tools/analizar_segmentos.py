from pathlib import Path
import struct
from collections import Counter

ROM_PATH = Path("rom/JetForceGemini.z64")

# Límites razonables para evitar falsos positivos
RAM_MIN = 0x80000000
RAM_MAX = 0x80800000

ROM_SIZE = 0x02000000


def u32(data, off):
    return struct.unpack_from(">I", data, off)[0]


def is_ram(addr):
    return RAM_MIN <= addr < RAM_MAX


def is_rom(off):
    return 0 <= off < len(data)


def hex8(x):
    return f"0x{x:08X}"


def add_candidate(results, kind, rom_off, values, score, reason):
    results.append({
        "kind": kind,
        "rom": rom_off,
        "values": values,
        "score": score,
        "reason": reason,
    })


print("=" * 78)
print("JET FORCE GEMINI - ANALIZADOR DE SEGMENTOS ROM -> RAM")
print("=" * 78)

if not ROM_PATH.exists():
    print(f"ERROR: no existe {ROM_PATH}")
    raise SystemExit(1)

data = ROM_PATH.read_bytes()
size = len(data)

print(f"ROM: {hex8(size)} ({size / 1024 / 1024:.2f} MiB)")

if size != ROM_SIZE:
    print(f"AVISO: se esperaba una ROM de {hex8(ROM_SIZE)} bytes.")

entrypoint = u32(data, 0x08)

print(f"Entrypoint header: {hex8(entrypoint)}")
print()

results = []

# ---------------------------------------------------------------------------
# 1. Buscar tablas de pares ROM/RAM
# ---------------------------------------------------------------------------

print("[1] TABLAS ROM -> RAM")
print("-" * 78)

# Buscamos secuencias del tipo:
#
# ROM offset
# RAM address
#
# y también:
#
# ROM start
# ROM end
# RAM start
#
# usando palabras big-endian.

for off in range(0, size - 16, 4):

    a = u32(data, off)
    b = u32(data, off + 4)
    c = u32(data, off + 8)
    d = u32(data, off + 12)

    # Caso A:
    # ROM offset + RAM address
    if a < size and is_ram(b):
        score = 1
        reason = "ROM offset + RAM address"

        # Si el siguiente valor también parece un tamaño/rango válido
        if c < size:
            score += 1
            reason += " + siguiente valor ROM"

        add_candidate(
            results,
            "ROM_RAM",
            off,
            (a, b, c, d),
            score,
            reason
        )

    # Caso B:
    # ROM start, ROM end, RAM start, RAM end
    if (
        a < size and
        b < size and
        a < b and
        is_ram(c)
    ):
        score = 4

        if is_ram(d) and c < d:
            score += 2

        add_candidate(
            results,
            "SEGMENTO",
            off,
            (a, b, c, d),
            score,
            "ROM start/end + RAM start/end"
        )


# ---------------------------------------------------------------------------
# 2. Buscar estructuras de segmento de 16 bytes
# ---------------------------------------------------------------------------

print("[2] CANDIDATOS A ESTRUCTURAS DE SEGMENTOS")
print("-" * 78)

segment_candidates = []

for off in range(0, size - 16, 4):

    r0 = u32(data, off)
    r1 = u32(data, off + 4)
    r2 = u32(data, off + 8)
    r3 = u32(data, off + 12)

    # Formato típico:
    #
    # ROM_START
    # ROM_END
    # RAM_START
    # RAM_END
    #
    if (
        r0 < size and
        r1 < size and
        r0 < r1 and
        is_ram(r2) and
        is_ram(r3) and
        r2 < r3
    ):
        size_rom = r1 - r0
        size_ram = r3 - r2

        # No aceptar tamaños absurdos
        if 0 < size_rom <= 0x02000000 and 0 < size_ram <= 0x10000000:

            score = 5

            # Si el tamaño ROM y RAM coincide, muy interesante.
            if size_rom == size_ram:
                score += 4

            segment_candidates.append(
                (
                    score,
                    off,
                    r0,
                    r1,
                    r2,
                    r3,
                    size_rom,
                    size_ram
                )
            )


for item in sorted(segment_candidates, reverse=True)[:100]:

    (
        score,
        off,
        rom_start,
        rom_end,
        ram_start,
        ram_end,
        rom_len,
        ram_len
    ) = item

    print(
        f"ROM tabla {hex8(off)} | "
        f"ROM {hex8(rom_start)}-{hex8(rom_end)} "
        f"({hex(rom_len)}) | "
        f"RAM {hex8(ram_start)}-{hex8(ram_end)} "
        f"({hex(ram_len)}) | "
        f"score={score}"
    )

print(f"\nCandidatos encontrados: {len(segment_candidates)}")
print()


# ---------------------------------------------------------------------------
# 3. Buscar secuencias de 3 o más pares ROM/RAM
# ---------------------------------------------------------------------------

print("[3] SECUENCIAS DE TABLAS ROM/RAM")
print("-" * 78)

sequences = []

for off in range(0, size - 24, 4):

    pairs = 0

    for i in range(0, 24, 8):
        rom_value = u32(data, off + i)
        ram_value = u32(data, off + i + 4)

        if rom_value < size and is_ram(ram_value):
            pairs += 1

    if pairs >= 3:
        sequences.append((pairs, off))


for pairs, off in sorted(sequences, reverse=True)[:100]:

    print(
        f"ROM {hex8(off)} | "
        f"{pairs}/3 pares ROM/RAM"
    )

print(f"\nSecuencias encontradas: {len(sequences)}")
print()


# ---------------------------------------------------------------------------
# 4. Buscar tablas DMA típicas
# ---------------------------------------------------------------------------

print("[4] POSIBLES TABLAS DMA")
print("-" * 78)

dma_candidates = []

for off in range(0, size - 16, 4):

    a = u32(data, off)
    b = u32(data, off + 4)
    c = u32(data, off + 8)
    d = u32(data, off + 12)

    # Una entrada DMA típica puede contener:
    #
    # ROM start
    # ROM end
    # RAM destination
    # tamaño / flags
    #
    if (
        a < size and
        b <= size and
        a < b and
        is_ram(c)
    ):
        score = 3

        dma_size = b - a

        if dma_size > 0 and dma_size < 0x02000000:
            score += 1

        if d == dma_size:
            score += 3

        dma_candidates.append(
            (
                score,
                off,
                a,
                b,
                c,
                d
            )
        )


for item in sorted(dma_candidates, reverse=True)[:100]:

    score, off, a, b, c, d = item

    print(
        f"ROM tabla {hex8(off)} | "
        f"ROM {hex8(a)}-{hex8(b)} | "
        f"RAM {hex8(c)} | "
        f"valor4={hex8(d)} | "
        f"score={score}"
    )

print(f"\nCandidatos DMA: {len(dma_candidates)}")
print()


# ---------------------------------------------------------------------------
# 5. Buscar punteros RAM agrupados
# ---------------------------------------------------------------------------

print("[5] ZONAS CON MUCHOS PUNTEROS RAM")
print("-" * 78)

# Dividimos la ROM en bloques de 0x1000 y contamos cuántas palabras
# parecen direcciones RAM.

block_size = 0x1000
ram_blocks = []

for base in range(0, size, block_size):

    count = 0

    end = min(base + block_size, size)

    for off in range(base, end - 3, 4):

        value = u32(data, off)

        if is_ram(value):
            count += 1

    if count >= 8:
        ram_blocks.append((count, base))


for count, base in sorted(ram_blocks, reverse=True)[:100]:

    print(
        f"ROM {hex8(base)}-{hex8(min(base + block_size, size))} | "
        f"{count} punteros RAM"
    )

print(f"\nBloques con concentración de punteros: {len(ram_blocks)}")
print()


# ---------------------------------------------------------------------------
# 6. Buscar direcciones de entrada plausibles
# ---------------------------------------------------------------------------

print("[6] DIRECCIONES RAM QUE PARECEN ENTRYPOINTS")
print("-" * 78)

entry_candidates = []

for off in range(0, size - 4, 4):

    value = u32(data, off)

    if not is_ram(value):
        continue

    # Las entradas de código suelen estar alineadas.
    if value % 4 != 0:
        continue

    # No nos interesan las zonas extremadamente bajas de RAM.
    if value < 0x80000400:
        continue

    # Revisamos las palabras siguientes.
    score = 0

    for j in range(1, 5):

        nxt = u32(data, off + j * 4)

        # Valores que parecen instrucciones MIPS razonables:
        opcode = nxt >> 26

        if opcode in (
            0x00,  # SPECIAL
            0x02,  # J
            0x03,  # JAL
            0x04,  # BEQ
            0x05,  # BNE
            0x09,  # ADDIU
            0x0F,  # LUI
            0x23,  # LW
            0x2B,  # SW
        ):
            score += 1

    if score >= 2:

        entry_candidates.append(
            (
                score,
                off,
                value
            )
        )


for score, off, value in sorted(entry_candidates, reverse=True)[:100]:

    print(
        f"ROM {hex8(off)} | "
        f"RAM {hex8(value)} | "
        f"score={score}"
    )

print(f"\nCandidatos entrypoint: {len(entry_candidates)}")
print()


# ---------------------------------------------------------------------------
# 7. Buscar tablas con offsets ROM consecutivos
# ---------------------------------------------------------------------------

print("[7] TABLAS DE OFFSETS ROM CONSECUTIVOS")
print("-" * 78)

offset_tables = []

for off in range(0, size - 32, 4):

    vals = [
        u32(data, off + i * 4)
        for i in range(8)
    ]

    valid = sum(v < size for v in vals)

    increasing = 0

    for i in range(7):

        if vals[i] < vals[i + 1]:
            increasing += 1

    if valid >= 6 and increasing >= 5:

        offset_tables.append(
            (
                valid,
                increasing,
                off,
                vals
            )
        )


for valid, increasing, off, vals in sorted(
    offset_tables,
    key=lambda x: (x[0], x[1]),
    reverse=True
)[:100]:

    texto = " ".join(hex8(v) for v in vals)

    print(
        f"ROM {hex8(off)} | "
        f"valid={valid}/8 | "
        f"increasing={increasing}/7 | "
        f"{texto}"
    )

print(f"\nTablas de offsets candidatas: {len(offset_tables)}")
print()


# ---------------------------------------------------------------------------
# 8. Resumen de los mejores candidatos
# ---------------------------------------------------------------------------

print("=" * 78)
print("RESUMEN - CANDIDATOS MAS INTERESANTES")
print("=" * 78)

print("\n[SEGMENTOS]")
for item in sorted(segment_candidates, reverse=True)[:20]:

    (
        score,
        off,
        rom_start,
        rom_end,
        ram_start,
        ram_end,
        rom_len,
        ram_len
    ) = item

    print(
        f"score={score} | "
        f"tabla={hex8(off)} | "
        f"ROM={hex8(rom_start)}-{hex8(rom_end)} | "
        f"RAM={hex8(ram_start)}-{hex8(ram_end)}"
    )


print("\n[DMA]")
for item in sorted(dma_candidates, reverse=True)[:20]:

    score, off, a, b, c, d = item

    print(
        f"score={score} | "
        f"tabla={hex8(off)} | "
        f"ROM={hex8(a)}-{hex8(b)} | "
        f"RAM={hex8(c)}"
    )


print("\n[ENTRYPOINTS]")
for score, off, value in sorted(entry_candidates, reverse=True)[:20]:

    print(
        f"score={score} | "
        f"ROM={hex8(off)} | "
        f"RAM={hex8(value)}"
    )


print("\n" + "=" * 78)
print("ANALISIS TERMINADO")
print("=" * 78)