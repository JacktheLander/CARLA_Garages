from pathlib import Path

folder = Path(".")

for file in folder.iterdir():
    if not file.is_file():
        continue

    # Only target PNG files
    if file.suffix.lower() != ".png":
        continue

    stem = file.stem

    # Only rename if it ends with "_A"
    if not stem.endswith("_A"):
        continue

    new_stem = stem[:-2]  # remove "_A"
    new_file = file.with_name(new_stem + file.suffix)

    if new_file.exists():
        print(f"SKIPPED: {file.name} -> {new_file.name} already exists")
        continue

    file.rename(new_file)
    print(f"RENAMED: {file.name} -> {new_file.name}")
