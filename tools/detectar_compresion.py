import gzip
import struct
from pathlib import Path

ROM_PATH = Path("rom/JetForceGemini.z64")

def u32(data, off):
    return struct.unpack_from(">I", data, off)[0]

def find_all(data, pattern):
    pos = 0
    while True:
        pos = data.find(pattern, pos)
        if pos == -1:
            break
        yield pos
        pos += 1

print("=" * 70)
print("JET FORCE GEMINI - DETECTOR DE COMPRESION")
print("=" * 70)

if not ROM_PATH.exists():
    print(f"ERROR: No existe {ROM_PATH}")
    raise SystemExit(1)

data = ROM_PATH.read_bytes()
size = len(data)

print(f"ROM: 0x{size:08X} ({size / 1024 / 1024:.2f} MiB)")

# ============================================================
# MIO0
# ============================================================

print("\n[1] MIO0")
print("-" * 70)

mio0_count = 0

for off in find_all(data, b"MIO0"):
    mio0_count += 1

    if off + 16 > size:
        continue

    decompressed_size = u32(data, off + 4)
    comp_offset = u32(data, off + 8)
    raw_offset = u32(data, off + 12)

    print(
        f"Encontrado ROM 0x{off:08X} | "
        f"descomprimido=0x{decompressed_size:X} | "
        f"comp_off=0x{comp_offset:X} | "
        f"raw_off=0x{raw_offset:X}"
    )

print(f"Total firmas MIO0: {mio0_count}")

# ============================================================
# YAY0
# ============================================================

print("\n[2] YAY0")
print("-" * 70)

yay0_count = 0

for off in find_all(data, b"Yay0"):

    yay0_count += 1

    if off + 16 > size:
        continue

    decompressed_size = u32(data, off + 4)
    link_offset = u32(data, off + 8)
    byte_offset = u32(data, off + 12)

    print(
        f"Encontrado ROM 0x{off:08X} | "
        f"descomprimido=0x{decompressed_size:X} | "
        f"link_off=0x{link_offset:X} | "
        f"byte_off=0x{byte_offset:X}"
    )

print(f"Total firmas YAY0: {yay0_count}")

# ============================================================
# GZIP
# ============================================================

print("\n[3] GZIP VALIDADO")
print("-" * 70)

gzip_candidates = 0
gzip_valid = 0

for off in find_all(data, b"\x1f\x8b"):

    gzip_candidates += 1

    # GZIP necesita al menos 10 bytes de header
    if off + 10 > size:
        continue

    # Compression method = 8 (DEFLATE)
    if data[off + 2] != 8:
        continue

    # Intentamos realmente descomprimir.
    try:
        decompressed = gzip.decompress(data[off:])

        if len(decompressed) > 0:
            gzip_valid += 1

            print(
                f"GZIP VALIDO ROM 0x{off:08X} | "
                f"descomprimido={len(decompressed):,} bytes "
                f"(0x{len(decompressed):X})"
            )

    except Exception:
        pass

print(f"Candidatos GZIP: {gzip_candidates}")
print(f"GZIP realmente validos: {gzip_valid}")

# ============================================================
# ZIP
# ============================================================

print("\n[4] ZIP")
print("-" * 70)

zip_count = 0

for off in find_all(data, b"PK\x03\x04"):
    zip_count += 1
    print(f"Firma ZIP ROM 0x{off:08X}")

print(f"Total firmas ZIP: {zip_count}")

# ============================================================
# RNC
# ============================================================

print("\n[5] RNC")
print("-" * 70)

rnc_count = 0

for off in find_all(data, b"RNC\x01"):
    rnc_count += 1
    print(f"RNC método 1 ROM 0x{off:08X}")

for off in find_all(data, b"RNC\x02"):
    rnc_count += 1
    print(f"RNC método 2 ROM 0x{off:08X}")

print(f"Total firmas RNC: {rnc_count}")

# ============================================================
# RESUMEN
# ============================================================

print("\n" + "=" * 70)
print("RESUMEN")
print("=" * 70)

print(f"MIO0 firmas          : {mio0_count}")
print(f"YAY0 firmas          : {yay0_count}")
print(f"GZIP candidatos      : {gzip_candidates}")
print(f"GZIP validos         : {gzip_valid}")
print(f"ZIP firmas           : {zip_count}")
print(f"RNC firmas           : {rnc_count}")

if mio0_count == 0 and yay0_count == 0 and gzip_valid == 0 and zip_count == 0 and rnc_count == 0:
    print("\nNo se detecto compresion conocida.")

print("\nANALISIS TERMINADO")