import json
import re

import unreal


CONTENT_ROOT = "/Game/SanJose"
TEXTURE_ROOT = "/Game/SanJose/Textures"
LOG_FILE = r"D:\Unreal\Projects\SanJoseUE4_426_Copy\relink_ue4_material_textures.log"
SUMMARY_FILE = r"D:\Unreal\Projects\SanJoseUE4_426_Copy\relink_ue4_material_textures.json"

NAME_OVERRIDES = {
    "Tiles": "Tile",
    "Glass": "Glass",
    "CarGlass_A": "Glass",
}


def log(message):
    unreal.log(message)
    with open(LOG_FILE, "a", encoding="utf-8") as handle:
        handle.write(message + "\n")


def load_texture(stem):
    return unreal.load_asset("{}/{}.{}".format(TEXTURE_ROOT, stem, stem))


def material_base_name(material_name):
    if material_name.startswith("M_"):
        name = material_name[2:]
    else:
        name = material_name

    name = re.sub(r"_(BaseColor|Normal|Opacity|EmissiveColor|Roughness|Metallic)_\d+$", "", name)
    name = re.sub(r"_\d+$", "", name)
    return NAME_OVERRIDES.get(name, name)


def connect_texture(material, texture, material_property, sampler_type, output_name, x, y):
    node = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionTextureSample, x, y
    )
    node.set_editor_property("texture", texture)
    node.set_editor_property("sampler_type", sampler_type)
    unreal.MaterialEditingLibrary.connect_material_property(node, output_name, material_property)


def relink_material(material):
    base = material_base_name(material.get_name())
    prefix = "T_{}".format(base)

    base_color = load_texture(prefix + "_BC")
    normal = load_texture(prefix + "_N")
    roughness = load_texture(prefix + "_R")

    connected = []
    if base_color:
        connect_texture(
            material,
            base_color,
            unreal.MaterialProperty.MP_BASE_COLOR,
            unreal.MaterialSamplerType.SAMPLERTYPE_COLOR,
            "RGB",
            -500,
            -120,
        )
        connected.append(base_color.get_name())

    if normal:
        connect_texture(
            material,
            normal,
            unreal.MaterialProperty.MP_NORMAL,
            unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL,
            "RGB",
            -500,
            120,
        )
        connected.append(normal.get_name())

    if roughness:
        connect_texture(
            material,
            roughness,
            unreal.MaterialProperty.MP_ROUGHNESS,
            unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE,
            "R",
            -500,
            360,
        )
        connected.append(roughness.get_name())

    if connected:
        unreal.MaterialEditingLibrary.layout_material_expressions(material)
        unreal.MaterialEditingLibrary.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        log("RELINKED {} base={} textures={}".format(material.get_path_name(), base, ",".join(connected)))
    else:
        log("NO_MATCH {} base={}".format(material.get_path_name(), base))

    return {"material": material.get_path_name(), "base": base, "textures": connected}


def main():
    with open(LOG_FILE, "w", encoding="utf-8") as handle:
        handle.write("")

    records = []
    for path in unreal.EditorAssetLibrary.list_assets(CONTENT_ROOT, recursive=True, include_folder=False):
        asset = unreal.load_asset(path)
        if isinstance(asset, unreal.Material):
            records.append(relink_material(asset))

    with open(SUMMARY_FILE, "w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2)

    linked = [record for record in records if record["textures"]]
    log("SUMMARY materials={} linked={}".format(len(records), len(linked)))


main()
