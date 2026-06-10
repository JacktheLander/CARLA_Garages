import json
import os
import traceback

import unreal


MISSING_NAMES_FILE = r"D:\Unreal\Projects\SanJoseUE4_426_Copy\missing_texture_names.txt"
OUTPUT_ROOT = r"D:\Unreal\Projects\SanJoseUE4_426_Copy\TextureExports_UE5"
LOG_FILE = r"D:\Unreal\Projects\SanJoseUE4_426_Copy\export_ue5_textures.log"


def log(message):
    unreal.log(message)
    with open(LOG_FILE, "a", encoding="utf-8") as handle:
        handle.write(message + "\n")


def load_missing_names():
    with open(MISSING_NAMES_FILE, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle.readlines() if line.strip()]


def try_export(texture, filename):
    task = unreal.AssetExportTask()
    task.object = texture
    task.filename = filename
    task.automated = True
    task.prompt = False
    task.replace_identical = True
    task.write_empty_files = False
    try:
        return bool(unreal.Exporter.run_asset_export_task(task))
    except Exception:
        log("EXPORT_EXCEPTION {} {}".format(filename, traceback.format_exc()))
        return False


def main():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as handle:
        handle.write("")

    names = load_missing_names()
    successes = []
    failures = []

    for name in names:
        asset_path = "/Game/ParkingGarage/Textures/{}.{}".format(name, name)
        texture = unreal.load_asset(asset_path)
        if texture is None:
            failures.append({"name": name, "reason": "missing_asset", "asset_path": asset_path})
            log("MISSING_ASSET {}".format(asset_path))
            continue

        exported = False
        outputs = []
        for extension in (".png", ".tga"):
            filename = os.path.join(OUTPUT_ROOT, name + extension)
            if try_export(texture, filename) and os.path.exists(filename) and os.path.getsize(filename) > 0:
                exported = True
                outputs.append(filename)
                log("EXPORTED {} -> {}".format(asset_path, filename))
                break

        if exported:
            successes.append({"name": name, "outputs": outputs})
        else:
            failures.append({"name": name, "reason": "export_failed", "asset_path": asset_path})
            log("EXPORT_FAILED {}".format(asset_path))

    summary = {
        "requested": len(names),
        "successes": successes,
        "failures": failures,
    }
    summary_path = os.path.join(OUTPUT_ROOT, "export_summary.json")
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    log("SUMMARY requested={} successes={} failures={}".format(len(names), len(successes), len(failures)))


main()
