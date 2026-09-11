import json
from pathlib import Path
from datetime import date


ROOT = Path(__file__).resolve().parent
PROGRESS_FILE = ROOT / "progress.json"
STATS_FILE = ROOT / "N64Recomp" / "progress_stats.json"

def percentage(current, total):
    if total <= 0:
        return 0.0
    return round((current / total) * 100, 2)


def load_progress():
    with PROGRESS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_recomp_stats():
    if not STATS_FILE.exists():
        print(f"WARNING: {STATS_FILE} not found")
        return None

    with STATS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(data):
    with PROGRESS_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.write("\n")


def update_calculated_values(data):
    functions = data["functions"]
    jump_tables = data["jump_tables"]
    relocations = data["relocations"]

    functions["analysis_progress"] = percentage(
        functions["analyzed"],
        functions["total"]
    )

    functions["success_progress"] = percentage(
        functions["successful"],
        functions["total"]
    )

    jump_tables["progress"] = percentage(
        jump_tables["resolved"],
        jump_tables["detected"]
    )

    relocations["progress"] = percentage(
        relocations["resolved"],
        relocations["total"]
    )

    return data


def print_report(data):
    functions = data["functions"]
    jump_tables = data["jump_tables"]
    relocations = data["relocations"]
    components = data["components"]

    print()
    print("=" * 60)
    print("JET FORCE GEMINI - RECOMP PROGRESS")
    print("=" * 60)

    print()
    print(
        f"Decompilation              "
        f"{data['decompilation']['progress']:6.2f}%"
    )

    print(
        f"Function analysis          "
        f"{functions['analysis_progress']:6.2f}% "
        f"({functions['analyzed']}/{functions['total']})"
    )

    print(
        f"Successful functions       "
        f"{functions['success_progress']:6.2f}% "
        f"({functions['successful']}/{functions['total']})"
    )

    print(
        f"Jump tables                "
        f"{jump_tables['progress']:6.2f}% "
        f"({jump_tables['resolved']}/{jump_tables['detected']})"
    )

    print(
        f"Relocations                "
        f"{relocations['progress']:6.2f}% "
        f"({relocations['resolved']}/{relocations['total']})"
    )

    print()
    print("Components")
    print("-" * 60)

    for name, value in components.items():
        label = name.replace("_", " ").title()
        print(f"{label:<28} {value:6.2f}%")

    print()
    print(f"Status: {data['project']['status']}")
    print("=" * 60)
    print()


def main():
    if not PROGRESS_FILE.exists():
        print(f"ERROR: {PROGRESS_FILE} not found")
        return 1

    data = load_progress()
    stats = load_recomp_stats()

    if stats is not None:
            data["functions"]["total"] = stats["functions_total"]
            data["functions"]["analyzed"] = stats["functions_analyzed"]
            data["functions"]["successful"] = stats["functions_successful"]
            data["functions"]["errors"] = stats["functions_failed"]

            data["jump_tables"]["detected"] = stats["jump_tables_detected"]
            data["jump_tables"]["resolved"] = stats["jump_tables_resolved"]

    data["project"]["last_update"] = str(date.today())

    data = update_calculated_values(data)
    save_progress(data)
    print_report(data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())