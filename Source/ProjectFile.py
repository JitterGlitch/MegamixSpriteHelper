import yaml
import zipfile
from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from SceneComposer import SceneComposerObjects, SpriteSetting
from main import Configurable


def save_project(SC:SceneComposerObjects, output_path:Path,config:Configurable):

        main_data = {}
        group_data = {}
        image_path_set = set()

        save_file_version = 1

        main_data.update({
            "MMSH Version": config.version_long,
            "Save File Version": save_file_version
        })
        for sprite_group in SC.sprite_groups:
            sprite_data = {}
            sprite_group_object = SC.enum_to_obj(sprite_group.value)

            for sprite in sprite_group_object.list:
                sprite_info = sprite.save_data()

                sprite_data.update({
                    f"{sprite.sprite_type}": sprite_info
                })

                group_data.update({f"{sprite_group.value}": sprite_data})

                if sprite_info is None:
                    continue

                image_path = sprite_info["Location"]
                if image_path is not None:
                    image_path_set.add(image_path)

        main_data.update({
            "Sprites":group_data
        })



        with zipfile.ZipFile(output_path.with_suffix(".mmsh"), 'w', zipfile.ZIP_DEFLATED) as zf:
            manifest = yaml.dump(main_data, default_flow_style=False, allow_unicode=True)
            zf.writestr('manifest.yaml', manifest)

            for img_path in image_path_set:
                img_path = Path(img_path)
                archive_name = f"Images/{img_path.name}"
                zf.write(img_path, arcname=archive_name)

def get_list_of_missing_files(SC:SceneComposerObjects,manifest) -> set[Path]:
    missing_list = set()

    for sprite_group in manifest:
        for sprite_type in manifest[sprite_group]:
            sprite_object = SC.type_to_sprite(sprite_group, sprite_type)
            sprite_info = manifest[sprite_group][sprite_type]

            if sprite_info is None:
                continue

            if not Path(sprite_info["Location"]).exists():
                missing_list.add(Path(sprite_info["Location"]))

    return missing_list

def load_project(SC:SceneComposerObjects,project_path,unpack_path:Path):


    with zipfile.ZipFile(project_path, 'r') as zf:
        manifest = yaml.unsafe_load(zf.read('manifest.yaml'))
        archive_name = Path(zf.filename).name.removesuffix(".mmsh")

        missing_image_list = get_list_of_missing_files(SC,manifest)
        missing_image_dict = {}
        for image in missing_image_list:

            image_name = image.name
            missing_image_dict.update({str(image):f"{unpack_path}/Project File Images/{archive_name}/Images/{image_name}"})
            zf.extract(f"Images/{image_name}",unpack_path.joinpath(f"Project File Images/{archive_name}"))



        for sprite_group in manifest:
            for sprite_type in manifest[sprite_group]:
                sprite_object = SC.type_to_sprite(sprite_group,sprite_type)
                sprite_info = manifest[sprite_group][sprite_type]

                if sprite_info is None:
                    continue

                if Path(sprite_info["Location"]) not in missing_image_list:
                    sprite_object.load_new_image(str(sprite_info["Location"]))
                else:
                    sprite_object.load_new_image(missing_image_dict[str(sprite_info["Location"])])
                sprite_object.edit_controls[SpriteSetting.ZOOM.value].setValue(sprite_info["Edit Controls"]["Zoom"])
                sprite_object.edit_controls[SpriteSetting.ROTATION.value].setValue(sprite_info["Edit Controls"]["Rotation"])

                for sprite_control in sprite_info["Edit Controls"]:
                    sprite_object.edit_controls[sprite_control].setValue(sprite_info["Edit Controls"][sprite_control])

                if sprite_info.get("Sprite Specific") is not None:
                    for entry in sprite_info["Sprite Specific"]:
                        match entry:
                            case "Drop Shadow":
                                sprite_object.drop_shadow.toggle_visibility(True)
                                for sprite_control in sprite_info["Sprite Specific"]["Drop Shadow"]["Edit Controls"]:
                                    sprite_object.drop_shadow.edit_controls[sprite_control].setValue(sprite_info["Sprite Specific"]["Drop Shadow"]["Edit Controls"][sprite_control])
                            case _:
                                print(f"Sprite Specific: {entry} is not implemented!")
                sprite_object.redraw_and_check_status()