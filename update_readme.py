import json
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent
PROGRESS_FILE = ROOT / "progress.json"
README_FILE = ROOT / "README.md"

START_MARKER = "<!-- PROGRESS:START -->"
END_MARKER = "<!-- PROGRESS:END -->"


def make_progress_bar(value, width=20):
    value = max(0.0, min(100.0, value))
    filled = round((value / 100) * width)
    return "█" * filled + "░" * (width - filled)


def main():
    if not PROGRESS_FILE.exists():
        print(f"ERROR: {PROGRESS_FILE} not found")
        return 1

    if not README_FILE.exists():
        print(f"ERROR: {README_FILE} not found")
        return 1

    with PROGRESS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    with README_FILE.open("r", encoding="utf-8") as f:
        readme = f.read()

    if START_MARKER not in readme:
        print("ERROR: PROGRESS:START marker not found")
        return 1

    if END_MARKER not in readme:
        print("ERROR: PROGRESS:END marker not found")
        return 1

    start_marker_pos = readme.index(START_MARKER)
    end_marker_pos = readme.index(END_MARKER)

    if start_marker_pos >= end_marker_pos:
        print("ERROR: Progress markers are in the wrong order")
        return 1

    project = data["project"]
    decomp = data["decompilation"]
    functions = data["functions"]
    jump_tables = data["jump_tables"]
    relocations = data["relocations"]
    components = data["components"]

    status = project["status"]

    decomp_progress = float(decomp["progress"])

    functions_total = int(functions["total"])
    functions_analyzed = int(functions["analyzed"])
    functions_successful = int(functions["successful"])
    functions_errors = int(functions["errors"])

    jump_detected = int(jump_tables["detected"])
    jump_resolved = int(jump_tables["resolved"])

    reloc_total = int(relocations["total"])
    reloc_resolved = int(relocations["resolved"])

    function_progress = (
        functions_analyzed / functions_total * 100
        if functions_total
        else 0
    )

    successful_progress = (
        functions_successful / functions_total * 100
        if functions_total
        else 0
    )

    jump_progress = (
        jump_resolved / jump_detected * 100
        if jump_detected
        else 0
    )

    reloc_progress = (
        reloc_resolved / reloc_total * 100
        if reloc_total
        else 0
    )

    today = date.today().isoformat()

    progress_section = (
        "## 📊 Progreso del Proyecto\n\n"
        f"**Estado:** 🟡 `{status}`\n\n"
        "| Área | Progreso |\n"
        "|---|---:|\n"
        f"| Decompilación | **{decomp_progress:.2f}%** |\n"
        f"| Análisis de funciones | **{function_progress:.2f}%** |\n"
        f"| Funciones exitosas | **{successful_progress:.2f}%** |\n"
        f"| Jump Tables | **{jump_progress:.2f}%** |\n"
        f"| Relocations | **{reloc_progress:.2f}%** |\n\n"
        "### Progreso visual\n\n"
        "```text\n"
        f"Decompilación        [{make_progress_bar(decomp_progress)}] {decomp_progress:.2f}%\n"
        f"Funciones analizadas [{make_progress_bar(function_progress)}] {function_progress:.2f}%\n"
        f"Funciones exitosas   [{make_progress_bar(successful_progress)}] {successful_progress:.2f}%\n"
        f"Jump Tables          [{make_progress_bar(jump_progress)}] {jump_progress:.2f}%\n"
        f"Relocations          [{make_progress_bar(reloc_progress)}] {reloc_progress:.2f}%\n"
        "```\n\n"
        "### Funciones\n\n"
        f"- **Total:** {functions_total:,}\n"
        f"- **Analizadas:** {functions_analyzed:,}\n"
        f"- **Exitosas:** {functions_successful:,}\n"
        f"- **Errores:** {functions_errors:,}\n\n"
        "### Jump Tables\n\n"
        f"- **Detectadas:** {jump_detected:,}\n"
        f"- **Resueltas:** {jump_resolved:,}\n\n"
        "### Relocations\n\n"
        f"- **Total:** {reloc_total:,}\n"
        f"- **Resueltas:** {reloc_resolved:,}\n\n"
        "### Componentes\n\n"
        "| Componente | Progreso |\n"
        "|---|---:|\n"
        f"| ELF Analysis | **{float(components['elf_analysis']):.2f}%** |\n"
        f"| MIPS Analysis | **{float(components['mips_analysis']):.2f}%** |\n"
        f"| C Generation | **{float(components['c_generation']):.2f}%** |\n"
        f"| Native Build | **{float(components['native_build']):.2f}%** |\n"
        f"| Runtime | **{float(components['runtime']):.2f}%** |\n\n"
        f"**Última actualización:** `{today}`\n"
    )

    start = start_marker_pos + len(START_MARKER)

    new_readme = (
        readme[:start]
        + "\n\n"
        + progress_section
        + "\n"
        + readme[end_marker_pos:]
    )

    with README_FILE.open("w", encoding="utf-8", newline="\n") as f:
        f.write(new_readme)

    print("README.md updated successfully.")
    print(f"Status: {status}")
    print(f"Decompilation: {decomp_progress:.2f}%")
    print(f"Functions: {functions_analyzed}/{functions_total}")
    print(f"Successful: {functions_successful}/{functions_total}")
    print(f"Jump Tables: {jump_resolved}/{jump_detected}")
    print(f"Relocations: {reloc_resolved}/{reloc_total}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())