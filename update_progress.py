import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROGRESS_FILE = ROOT / "progress.json"


def main():
    if not PROGRESS_FILE.exists():
        print(f"ERROR: {PROGRESS_FILE} not found")
        return 1

    with PROGRESS_FILE.open("r", encoding="utf-8") as progress_file:
        data = json.load(progress_file)

    if "project" not in data or "milestones" not in data:
        print("ERROR: progress.json must define project and milestones")
        return 1

    data["project"]["last_update"] = date.today().isoformat()

    with PROGRESS_FILE.open("w", encoding="utf-8", newline="\n") as progress_file:
        json.dump(data, progress_file, indent=4, ensure_ascii=False)
        progress_file.write("\n")

    print(f"Updated progress data for {data['project']['status']}")
    for milestone in data["milestones"]:
        print(f"- {milestone['name']}: {milestone['status']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
