from pathlib import Path

# Change this to your texture folder, or leave "." for the current folder
folder = Path(".")

rename_rules = {
    "_BC": "_A",   # Base Color / Albedo
    "_N": "_N",    # Normal
    "_R": "_R",    # Roughness
    "_M": "_M",    # Metallic
}

valid_exts = {".png", ".jpg", ".jpeg", ".tga", ".bmp", ".tif", ".tiff"}

for file in folder.iterdir():
    if not file.is_file() or file.suffix.lower() not in valid_exts:
        continue

    stem = file.stem

    # Only rename Unreal texture files starting with T_
    if not stem.startswith("T_"):
        continue

    new_stem = "M_" + stem[2:]

    for old_suffix, new_suffix in rename_rules.items():
        if new_stem.endswith(old_suffix):
            new_stem = new_stem[: -len(old_suffix)] + new_suffix
            break

    new_file = file.with_name(new_stem + file.suffix)

    if new_file.exists():
        print(f"SKIPPED: {file.name} -> {new_file.name} already exists")
        continue

    file.rename(new_file)
    print(f"RENAMED: {file.name} -> {new_file.name}")
