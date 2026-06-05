from pathlib import Path


ROOT = Path(__file__).resolve().parent
README = ROOT / "README.md"

START = "<!-- IMAGE_GALLERY_START -->"
END = "<!-- IMAGE_GALLERY_END -->"

COLUMNS = 3
IMAGE_WIDTH = 220
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def build_gallery():
    sections = []

    for module_dir in sorted([p for p in ROOT.iterdir() if p.is_dir()]):
        images = sorted(
            [p for p in module_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
        )

        if not images:
            continue

        sections.append(f"### {module_dir.name}\n")
        sections.append("<table>\n")

        for i in range(0, len(images), COLUMNS):
            row = images[i:i + COLUMNS]
            sections.append("  <tr>\n")

            for img in row:
                rel_path = img.relative_to(ROOT).as_posix()
                sections.append(
                    '    <td align="center">\n'
                    f'      <img src="{rel_path}" width="{IMAGE_WIDTH}"><br>\n'
                    f"      <sub>{img.name}</sub>\n"
                    "    </td>\n"
                )

            sections.append("  </tr>\n")

        sections.append("</table>\n\n")

    return "\n".join(sections).strip() or "_No screenshot images found._"


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
