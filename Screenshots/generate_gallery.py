from pathlib import Path


ROOT = Path(__file__).resolve().parent
README = ROOT / "README.md"

START = "<!-- IMAGE_GALLERY_START -->"
END = "<!-- IMAGE_GALLERY_END -->"

COLUMNS = 3
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def escape_cell(text):
    return text.replace("|", r"\|")


def build_gallery():
    lines = []

    for module_dir in sorted([p for p in ROOT.iterdir() if p.is_dir()]):
        images = sorted(
            [p for p in module_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
        )

        if not images:
            continue

        lines.append(f"### {module_dir.name}")
        lines.append("")
        lines.append("| " + " | ".join(["Screenshot"] * COLUMNS) + " |")
        lines.append("| " + " | ".join(["---"] * COLUMNS) + " |")

        for i in range(0, len(images), COLUMNS):
            row = images[i:i + COLUMNS]
            padded_row = row + [None] * (COLUMNS - len(row))

            image_cells = [
                f"![{escape_cell(img.name)}]({img.relative_to(ROOT).as_posix()})" if img else ""
                for img in padded_row
            ]
            caption_cells = [f"`{escape_cell(img.name)}`" if img else "" for img in padded_row]

            lines.append("| " + " | ".join(image_cells) + " |")
            lines.append("| " + " | ".join(caption_cells) + " |")

        lines.append("")

    return "\n".join(lines).strip() or "_No screenshot images found._"


def update_readme():
    text = README.read_text(encoding="utf-8")

    if START not in text or END not in text:
        text = f"# Screenshots\n\n{START}\n\n{END}\n"

    before = text.split(START)[0]
    after = text.split(END)[1]

    gallery = build_gallery()

    updated = (
        before
        + START
        + "\n\n"
        + gallery
        + "\n\n"
        + END
        + after
    )

    README.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    update_readme()
    print("README gallery updated.")
