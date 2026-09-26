import yaml
import zipfile
from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from SceneComposer import SceneComposerObjects


def save_project(SC:SceneComposerObjects, output_path:Path):

        group_data = {}
        image_path_set = set()

        for sprite_group in SC.sprite_groups:
            sprite_data = {}
            sprite_group_object = SC.enum_to_obj(sprite_group.value)

            for sprite in sprite_group_object.list:

                sprite_info = sprite.save_data()

                sprite_data.update({
                    f"{sprite.sprite_type}": sprite_info
                })

                group_data.update({f"Sprite {sprite_group.value}": sprite_data})

                if sprite_info is None:
                    continue

                image_path = sprite_info["Location"]
                if image_path is not None:
                    image_path_set.add(image_path)

        with zipfile.ZipFile(output_path.with_suffix(".mmsh"), 'w', zipfile.ZIP_DEFLATED) as zf:
            manifest = yaml.dump(group_data, default_flow_style=False, allow_unicode=True)
            zf.writestr('manifest.yaml', manifest)

            for img_path in image_path_set:
                img_path = Path(img_path)
                archive_name = f"Images/{img_path.name}"
                zf.write(img_path, arcname=archive_name)