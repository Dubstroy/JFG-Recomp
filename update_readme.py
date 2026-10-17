import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROGRESS_FILE = ROOT / "progress.json"
README_FILE = ROOT / "README.md"

START_MARKER = "<!-- PROGRESS:START -->"
END_MARKER = "<!-- PROGRESS:END -->"


def render_progress(data):
    project = data["project"]
    rows = [
        "| Área | Estado | Detalle |",
        "|---|---|---|",
    ]
    for milestone in data["milestones"]:
        details = milestone["details"].replace("|", "\\|")
        rows.append(
            f"| {milestone['name']} | **{milestone['status']}** | {details} |"
        )

    return (
        "## 📊 Estado del Proyecto\n\n"
        f"**Estado general:** 🟡 `{project['status']}`\n\n"
        + "\n".join(rows)
        + f"\n\n**Última actualización:** `{project['last_update']}`\n"
    )


def main():
    if not PROGRESS_FILE.exists():
        print(f"ERROR: {PROGRESS_FILE} not found")
        return 1

    if not README_FILE.exists():
        print(f"ERROR: {README_FILE} not found")
        return 1

    with PROGRESS_FILE.open("r", encoding="utf-8") as progress_file:
        data = json.load(progress_file)

    with README_FILE.open("r", encoding="utf-8") as readme_file:
        readme = readme_file.read()

    if START_MARKER not in readme or END_MARKER not in readme:
        print("ERROR: progress markers not found")
        return 1

    start = readme.index(START_MARKER)
    end = readme.index(END_MARKER)
    if start >= end:
        print("ERROR: progress markers are in the wrong order")
        return 1

    content_start = start + len(START_MARKER)
    new_readme = (
        readme[:content_start]
        + "\n\n"
        + render_progress(data)
        + "\n"
        + readme[end:]
    )

    with README_FILE.open("w", encoding="utf-8", newline="\n") as readme_file:
        readme_file.write(new_readme)

    print("README.md updated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
