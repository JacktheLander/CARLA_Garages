import json

import unreal


CONTENT_ROOT = "/Game/SanJose"
TEXTURE_ROOT = "/Game/SanJose/Textures"
LEVEL_PATH = "/Game/SanJose/SanJoseLevel"
OUTPUT_FILE = r"D:\Unreal\Projects\SanJoseUE4_426_Copy\validate_ue4_texture_links.json"


def main():
    texture_paths = {
        path.split(".")[0]
        for path in unreal.EditorAssetLibrary.list_assets(TEXTURE_ROOT, recursive=True, include_folder=False)
    }
    material_records = []
    linked_materials = 0

    for path in unreal.EditorAssetLibrary.list_assets(CONTENT_ROOT, recursive=True, include_folder=False):
        asset = unreal.load_asset(path)
        if not isinstance(asset, unreal.Material):
            continue

        used = []
        for material_property in (
            unreal.MaterialProperty.MP_BASE_COLOR,
            unreal.MaterialProperty.MP_NORMAL,
            unreal.MaterialProperty.MP_ROUGHNESS,
            unreal.MaterialProperty.MP_METALLIC,
            unreal.MaterialProperty.MP_OPACITY,
            unreal.MaterialProperty.MP_EMISSIVE_COLOR,
        ):
            node = unreal.MaterialEditingLibrary.get_material_property_input_node(asset, material_property)
            if not node:
                continue
            try:
                texture = node.get_editor_property("texture")
            except Exception:
                texture = None
            if texture:
                used.append(texture.get_path_name())

        uses_new_textures = any(path_name.split(".")[0] in texture_paths for path_name in used)
        if uses_new_textures:
            linked_materials += 1

        material_records.append(
            {
                "material": asset.get_path_name(),
                "used_textures": used,
                "uses_new_textures": uses_new_textures,
            }
        )

    level_loaded = bool(unreal.EditorLoadingAndSavingUtils.load_map(LEVEL_PATH))

    result = {
        "texture_asset_count": len(texture_paths),
        "material_count": len(material_records),
        "materials_using_new_textures": linked_materials,
        "level_loaded": level_loaded,
        "materials": material_records,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)

    unreal.log(
        "VALIDATION texture_asset_count={} material_count={} linked_materials={} level_loaded={}".format(
            result["texture_asset_count"],
            result["material_count"],
            result["materials_using_new_textures"],
            result["level_loaded"],
        )
    )


main()
