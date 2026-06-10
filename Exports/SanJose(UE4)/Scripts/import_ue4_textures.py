import os

import unreal


SOURCE_DIR = r"D:\Unreal\Projects\SanJoseUE4_426_Copy\TextureExports_UE5"
DESTINATION_PATH = "/Game/SanJose/Textures"
LOG_FILE = r"D:\Unreal\Projects\SanJoseUE4_426_Copy\import_ue4_textures.log"


def log(message):
    unreal.log(message)
    with open(LOG_FILE, "a", encoding="utf-8") as handle:
        handle.write(message + "\n")


def import_textures():
    with open(LOG_FILE, "w", encoding="utf-8") as handle:
        handle.write("")

    filenames = sorted(
        os.path.join(SOURCE_DIR, name)
        for name in os.listdir(SOURCE_DIR)
        if name.lower().endswith((".png", ".tga", ".jpg", ".jpeg", ".bmp", ".exr"))
    )

    tasks = []
    for filename in filenames:
        task = unreal.AssetImportTask()
        task.filename = filename
        task.destination_path = DESTINATION_PATH
        task.automated = True
        task.replace_existing = True
        task.save = True
        tasks.append(task)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)

    imported = []
    failed = []
    for filename in filenames:
        stem = os.path.splitext(os.path.basename(filename))[0]
        asset_path = "{}/{}.{}".format(DESTINATION_PATH, stem, stem)
        texture = unreal.load_asset(asset_path)
        if texture is None:
            failed.append(stem)
            log("IMPORT_FAILED {}".format(filename))
            continue

        if stem.endswith("_N") or stem.endswith("_Normal"):
            texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
            texture.set_editor_property("srgb", False)
        elif stem.endswith("_R") or stem.endswith("_M") or stem.endswith("_ORM"):
            texture.set_editor_property("srgb", False)

        unreal.EditorAssetLibrary.save_loaded_asset(texture)
        imported.append(stem)
        log("IMPORTED {}".format(asset_path))

    log("SUMMARY requested={} imported={} failed={}".format(len(filenames), len(imported), len(failed)))
    if failed:
        log("FAILED_NAMES {}".format(",".join(failed)))


import_textures()
