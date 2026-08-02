import io
import math
import os
import sys

from concurrent.futures import ThreadPoolExecutor
from enum import Enum, auto
from pathlib import Path


import PIL.ImageShow

import kkdlib

import yaml
from PIL import Image
from PySide6.QtCore import Qt, QSize, Signal, QRectF, QStandardPaths, QUrl, QPoint, QCoreApplication
from PySide6.QtGui import QPixmap, QPalette, QColor, QImage, QPainter, QGuiApplication, QDesktopServices, QAction, QImageReader
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox, QSizePolicy, QSpacerItem, QMenu

import SceneComposer
from SceneComposer import SpriteGroup, TextureType
from ui_SongFarcCreator import Ui_SongFarcCreatorWindow
from widgets import QSmarterMenu


from FarcCreator import FarcCreator
from SceneComposer import SpriteSetting, QSpriteSlave, SpriteType, QScalingGraphicsScene, PvBackLayout
from ThirdParty.auto_creat_mod_spr_db import Manager,add_farc_to_Manager,read_farc
from ui_SpriteHelper import Ui_MainWindow
from ui_ThumbnailIDField import Ui_ThumbnailIDField
from ui_ThumbnailTextureCreator import Ui_ThumbnailTextureCreator
from ui_ThumbnailWidget import Ui_ThumbnailWidget
from widgets import Stylesheet


class OutputTarget(Enum):
    CLIPBOARD = auto()
    IMAGE_VIEWER = auto()
    IMAGE = auto()

class Configurable:
    def __init__(self):
        self.script_directory = Path.cwd()
        self.version = "1.2.1 (preview)"

        QCoreApplication.setApplicationName("MMSH")
        self.saved_files_location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
        self.remembered_ids_file_location = os.path.join(self.saved_files_location, "remembered_ids.yaml")
        self.remembered_song_pack_names_file_location = os.path.join(self.saved_files_location, "remembered_names.yaml")


        if os.path.exists(self.saved_files_location):
            pass
        else:
            os.makedirs(self.saved_files_location,exist_ok=True)

        print(f"MMSH saved files are stored in: {self.saved_files_location}")


        formats = QImageReader.supportedImageFormats()
        Qimage_supported = sorted(fmt.data().decode() for fmt in formats)
        self.readable_extensions = " ".join(sorted([f"*.{ext}" for ext in Qimage_supported]))

        self.allowed_file_types = f"Image Files ({self.readable_extensions})"
        self.last_used_directory = self.script_directory

def show_message_box(title,contents):
    message_box = QMessageBox()
    message_box.setModal(True)
    message_box.setWindowTitle(title)
    message_box.setText(contents)
    message_box.exec()

class ThumbnailIDFieldWidget(QWidget):
    additionalRequested = Signal(QWidget)
    removeRequested = Signal(QWidget)
    thumb_count_request = Signal()

    def __init__(self,parent=None,variant=False, inferred_id:str=None):

        super(ThumbnailIDFieldWidget, self).__init__(parent)
        self.variant = variant


        self.value = None
        self.ui = Ui_ThumbnailIDField()
        self.ui.setupUi(self,variant)

        self.toggle_ex = QAction()
        self.toggle_ex.setCheckable(True)
        self.toggle_ex.setText("Set as _EX sprite")
        self.toggle_ex.toggled.connect(self.toggle_ex_action)

        self.config_dropdown = QMenu(self.ui.config_button)
        self.config_dropdown.addAction(self.toggle_ex)

        is_ex = False

        if inferred_id:
            if type(inferred_id) is str:
                if inferred_id.endswith("_EX"):
                    inferred_id = inferred_id.removesuffix("_EX")
                    is_ex = True
            self.ui.song_id_spinbox.setValue(float(inferred_id))

        else:
            self.ui.song_id_spinbox.setValue(0)

        self.ui.song_id_spinbox.editingFinished.connect(self.thumb_count_request.emit)
        self.ui.config_button.clicked.connect(self.config_button_callback)

        if variant:
            self.ui.id_line_button.clicked.connect(lambda: self.additionalRequested.emit(self))
        else:
            self.ui.id_line_button.clicked.connect(lambda: self.removeRequested.emit(self))

        if is_ex:
            self.toggle_ex.setChecked(True)


    def config_button_callback(self):
        self.config_dropdown.popup(self.ui.config_button.mapToGlobal(QPoint(0, self.ui.config_button.height())))

    def toggle_ex_action(self):
        if self.toggle_ex.isChecked():

            self.ui.song_id_spinbox.setSuffix("_EX")
            self.ui.song_id_spinbox.editingFinished.emit()

        else:

            self.ui.song_id_spinbox.setSuffix("")
            self.ui.song_id_spinbox.editingFinished.emit()



class ThumbnailWidget(QWidget):
    removeRequested = Signal(QWidget)
    thumb_count_request = Signal()

    def __init__(self, parent=None, image_path=None, inferred_id=None):

        super(ThumbnailWidget, self).__init__(parent)

        self.ui = Ui_ThumbnailWidget()
        self.ui.setupUi(self)
        self.ui.remove_thumbnail_button.clicked.connect(self.remove_thumb)
        self.id_field_list = []
        self.image_path = image_path

        id_count = 0
        if inferred_id:
            for i_id in inferred_id:
                if id_count == 0:
                    self.add_id_field(False, i_id=i_id)
                else:
                    self.add_id_field(True , i_id=i_id)
                id_count = id_count + 1
        else:
            self.add_id_field(False)
    def add_id_field(self, can_be_removed=False, i_id=None):
        if can_be_removed:
            id_field = ThumbnailIDFieldWidget(variant=False ,inferred_id = i_id)
        else:
            id_field = ThumbnailIDFieldWidget(variant=True ,inferred_id = i_id)

        id_field.removeRequested.connect(self.remove_id_field)
        id_field.additionalRequested.connect(self.add_id_field)
        id_field.thumb_count_request.connect(lambda: self.thumb_count_request.emit())
        self.id_field_list.append(id_field)
        self.ui.thumbnail_id_formLayout.addRow(id_field)
        self.thumb_count_request.emit()

    def remove_id_field(self,widget):
        self.ui.thumbnail_id_formLayout.removeRow(widget)
        self.id_field_list.remove(widget)
        self.thumb_count_request.emit()

    def remove_thumb(self):

        self.removeRequested.emit(self)


def pad_number(number):
    if number >= 100:
        return str(number)
    elif number >= 10:
        return "0"+ str(number)
    else:
        return "00" + str(number)


def next_power_of_two(n):
    if n <= 0:
        return 1
    p = 1
    while p < n:
        p *= 2
    return p


class ThumbnailWindow(QWidget):
    resized = Signal()
    NameDeleteRequest = Signal()
    def __init__(self):
        super(ThumbnailWindow, self).__init__()
        self.main_box = Ui_ThumbnailTextureCreator()
        self.main_box.setupUi(self)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.main_box.load_folder_button.clicked.connect(self.scan_folder_for_thumbnails)
        self.main_box.export_farc_button.clicked.connect(self.create_thumbnail_farc)
        self.main_box.load_image_button.clicked.connect(self.select_file_for_thumbnails)
        self.main_box.load_image_button.clicked.connect(self.update_thumbnail_count_labels)
        self.main_box.delete_all_thumbs_button.clicked.connect(self.delete_all_thumbs)
        self.main_box.mod_name_lineedit.delete_button.clicked.connect(self.delete_selected_name)
        self.thumbnail_widgets = []
        self.resized.connect(self.space_out_thumbnails)
        self.main_box.export_farc_button.setDisabled(True)

        self.id_conflict_palette = QPalette()
        self.id_conflict_palette.setColor(QPalette.ColorRole.Text, QColor(255, 0, 0))

        self.placeholder_palette = QPalette()
        self.placeholder_palette.setColor(QPalette.ColorRole.Text, QColor(170, 170, 170))

        self.auto_filled_palette = QPalette()
        self.auto_filled_palette.setColor(QPalette.ColorRole.Text, QColor(170, 170, 170))

        self.normal_palette = QPalette()
        self.normal_palette.setColor(QPalette.ColorRole.Text, QColor(255,255,255))

        self.known_ids = self.read_saved_ids()

        self.fill_combobox_suggestions()

    def resizeEvent(self,event):
        super().resizeEvent(event)

        self.resized.emit()

    def update_thumbnail_count_labels(self):
        loaded_thumbs = len(self.thumbnail_widgets)
        left_to_fillout = 0

        id_seen = []

        #Gather list of id's, Apply colors
        for thumbnail_widget in self.thumbnail_widgets:
            thumbnail_widget.setStyleSheet("")

            for id_field in thumbnail_widget.id_field_list:

                thumb_id = str(int(id_field.ui.song_id_spinbox.value())) + str(id_field.ui.song_id_spinbox.suffix())
                id_field.setStyleSheet("")
                id_seen.append(thumb_id)
                if  thumb_id in ("0","0_EX"):
                    thumbnail_widget.setStyleSheet(Stylesheet.SCROLL_AREA_UNFILLED.value)
                    id_field.setStyleSheet(Stylesheet.ID_FIELD_PLACEHOLDER.value)
                    left_to_fillout = left_to_fillout + 1

        # Look for conflicts
        duplicates = []
        seen = set()
        #keep only duplicates found
        for i in id_seen:
            if i in seen:
                duplicates.append(i)
            else:
                seen.add(i)

        duplicates = list(filter(lambda a: a not in ("0","0_EX"), duplicates))

        for thumbnail_widget in self.thumbnail_widgets:
            for id_field in thumbnail_widget.id_field_list:
                thumb_id = str(int(id_field.ui.song_id_spinbox.value())) + str(id_field.ui.song_id_spinbox.suffix())
                if thumb_id in duplicates:
                    id_field.setPalette(self.id_conflict_palette)
                    thumbnail_widget.setStyleSheet(Stylesheet.SCROLL_AREA_CONFLICT.value)
                    id_field.setStyleSheet(Stylesheet.ID_FIELD_CONFLICT.value)
                    left_to_fillout = left_to_fillout + 1

        self.main_box.thumbnails_to_fillout_label.setText(f"ID's left to fill out: {left_to_fillout}")
        self.main_box.thumbnails_loaded_label.setText(f"Unique Thumbnails loaded: {loaded_thumbs}")

        if left_to_fillout > 0:
            self.main_box.export_farc_button.setDisabled(True)
            self.main_box.export_farc_button.setToolTip("Please fill out all id fields before exporting FARC file.")
        elif loaded_thumbs == 0:
            self.main_box.export_farc_button.setDisabled(True)
            self.main_box.export_farc_button.setToolTip("")
        else:
            self.main_box.export_farc_button.setDisabled(False)
            self.main_box.export_farc_button.setToolTip("")

    def add_thumbnail(self,image_path,inferred_id):
        if self.thumbnail_widgets:
            for thumbnail in self.thumbnail_widgets:
                if image_path == thumbnail.image_path:
                    return

        thumbnail_widget = ThumbnailWidget(image_path=image_path, inferred_id=inferred_id)


        thumbnail_widget.removeRequested.connect(self.remove_thumbnail_widget)
        thumbnail_widget.thumb_count_request.connect(self.update_thumbnail_count_labels)

        pixmap = QPixmap(image_path)
        thumbnail_widget.ui.thumbnail_image.setPixmap(pixmap)
        thumbnail_widget.ui.thumbnail_image.setScaledContents(True)

        self.main_box.gridLayout.addWidget(thumbnail_widget, 0, 0)
        self.thumbnail_widgets.append(thumbnail_widget)
        return thumbnail_widget

    def infer_thumbnail_id(self,image_path):
        inferred_id_list = []

        for entry in main_window.thumbnail_creator.known_ids:
            if str(image_path) == entry[0]:
                inferred_id_list.append((image_path,entry[1]))
                break

        if not inferred_id_list:
            image_name = Path(image_path).stem
            image_name = image_name.removeprefix("pv_")
            is_ex = False
            print(image_name)

            if image_name.endswith("_EX"):
                image_name = image_name.removesuffix("_EX")
                is_ex = True
                print("Removing suffix")
                print(image_name)

            if image_name.isdigit() and len(image_name) >= 3:
                print(image_name)
                if is_ex:
                    id_list = [str(image_name)+"_EX"]
                else:
                    id_list = [str(image_name)]
                inferred_id_list.append([image_path,id_list])
            else:
                inferred_id_list.append((image_path,[]))
        return inferred_id_list

    def space_out_thumbnails(self):
        width = self.main_box.verticalLayout.geometry().width()
        widget_width = 395
        columns = (width // widget_width) - 1
        x = 0
        y = 0
        for thumbnail in self.thumbnail_widgets:
            self.main_box.gridLayout.removeWidget(thumbnail)

            self.main_box.gridLayout.addWidget(thumbnail,y,x)
            if x == columns:
                y = y + 1
                x = 0
            else:
                x = x + 1
    def read_saved_ids(self):
        if os.path.exists(config.remembered_ids_file_location):
            with io.open(config.remembered_ids_file_location, 'r', encoding='utf8') as infile:
                saved_data = yaml.safe_load(infile)
                print(f"Loaded saved ids from: {config.remembered_ids_file_location}")
                return saved_data
        else:
            return []


    def remove_thumbnail_widget(self, widget):
        self.main_box.gridLayout.removeWidget(widget)
        self.thumbnail_widgets.remove(widget)
        widget.deleteLater()

        self.space_out_thumbnails()
        self.update_thumbnail_count_labels()

    def delete_all_thumbs(self):
        if len(self.thumbnail_widgets) == 0:
            return
        for widget in self.thumbnail_widgets:
            self.main_box.gridLayout.removeWidget(widget)
            widget.deleteLater()

        self.thumbnail_widgets = []

        self.space_out_thumbnails()
        self.update_thumbnail_count_labels()

    def select_file_for_thumbnails(self):
        selected_files = QFileDialog.getOpenFileNames(self,"Choose images to load",str(config.last_used_directory),config.allowed_file_types)[0]

        if not selected_files:
            print("No files were selected")
        else:
            print(Path(selected_files[0]).parent)
            config.last_used_directory = Path(selected_files[0]).parent

            with ThreadPoolExecutor() as executor:  # This was a waste of time to add...
                futures = []

                for file in selected_files:
                    if Path(file).suffix in config.readable_extensions:
                        try:
                            with Image.open(file) as open_image:
                                if open_image.size == (128, 64):
                                    print(f"found thumbnail at: {file}")
                                    futures.append(executor.submit(self.infer_thumbnail_id, file))
                        except:
                            print("Skipping invalid file")
                            continue

            results = [future.result() for future in futures]
            for widget in results:
                self.add_thumbnail(widget[0][0], widget[0][1])

            self.space_out_thumbnails()
            self.update_thumbnail_count_labels()

            if not results:
                show_message_box("No valid Thumbnail files found","No valid Thumbnail files found\n"
                                                                  "Valid thumbnail image must be 128x64.\n"
                                                                  "No other images will get loaded.")


    def scan_folder_for_thumbnails(self):
        selected_folder = QFileDialog.getExistingDirectory(self, "Choose folder containing thumbnails", str(config.last_used_directory))

        if selected_folder == "":
            print("Folder wasn't selected")
        else:
            print(selected_folder)
            config.last_used_directory = Path(selected_folder)

            with ThreadPoolExecutor() as executor:  # This was a waste of time to add...
                futures = []

                if True:
                    for file in Path(selected_folder).rglob('*'):
                        if file.is_dir():
                            continue
                        if Path(file).suffix in config.readable_extensions:
                            try:
                                with Image.open(file) as open_image:
                                    if open_image.size == (128, 64):
                                        print(f"found thumbnail at: {file}")
                                        futures.append(executor.submit(self.infer_thumbnail_id, file))
                            except PIL.UnidentifiedImageError:
                                print("Skipping invalid file")
                                continue

            results = [future.result() for future in futures]
            for widget in results:
                self.add_thumbnail(widget[0][0],widget[0][1])


            self.space_out_thumbnails()
            self.update_thumbnail_count_labels()

            if not results:
                show_message_box("No valid Thumbnail files found","No valid Thumbnail files found\nValid thumbnail image must be 128x64.\nNo other images will get loaded.")

    def create_thumbnail_farc(self):
        mod_name = self.main_box.mod_name_lineedit.get_filtered_text()
        if mod_name == "":
            show_message_box("Error", "You need to specify mod name!")
        else:
            all_thumb_data = []
            for thumb_widget in self.thumbnail_widgets:
                thumb_data = []
                image_path = thumb_widget.image_path
                ids = []

                for id_list in thumb_widget.id_field_list:
                    ids.append(int(id_list.ui.song_id_spinbox.value()))

                thumb_data.append(ids)
                thumb_data.append(image_path)
                all_thumb_data.append(thumb_data)

            thumb_unique_count = 0
            for _ in all_thumb_data:
                thumb_unique_count = thumb_unique_count + 1

            texture_size = self.calculate_texture_grid(thumb_unique_count)

            if texture_size == (0,0):
                return

            thumbnail_texture = Image.new('RGBA', texture_size)
            x=0
            y=0
            thumb = 0
            thumbnail_positions = []

            for thumb_data in all_thumb_data:
            #[id,id...],image
                thumb= thumb + 1
                thumbnail_texture.alpha_composite(Image.open(thumb_data[1]).convert("RGBA"),(x,y))

                for thumb_id in thumb_data[0]:
                    thumbnail_positions.append([pad_number(thumb_id), (x, y)])

                if thumb == 7:
                    x = 0
                    y = y + 64
                    thumb = 0
                else:
                    x = x + 128

            thumbnail_positions.sort(key=lambda x: int(x[0]))
            for data in thumbnail_positions:
                print(data)

            chosen_dir = QFileDialog.getExistingDirectory(self, "Choose folder to save farc file to", str(config.last_used_directory))

            if chosen_dir == "":
                print("Folder wasn't chosen")
            else:
                config.last_used_directory = Path(chosen_dir)
                self.save_pack_name()
                thumbnail_texture.save(str(config.saved_files_location) + "/Thumbnail Texture.png","png")
                compression = self.main_box.farc_compression_combobox.currentEnum()

                FarcCreator.create_thumbnail_farc(thumbnail_positions,thumbnail_texture.transpose(Image.Transpose.FLIP_TOP_BOTTOM),chosen_dir,mod_name,compression)

                msgBox = QMessageBox()
                msgBox.setWindowTitle(" ")
                msgBox.setText("Thumbnail farc created successfully.")
                msgBox.setIcon(QMessageBox.Icon.Question)
                msgBox.setInformativeText("Do you want to generate sprite database?")
                msgBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                msgBox.setDefaultButton(QMessageBox.StandardButton.Yes)
                ret = msgBox.exec()
                match ret:
                    case QMessageBox.StandardButton.Yes:
                        main_window.generate_spr_db_button_callback(path=chosen_dir)
                    case QMessageBox.StandardButton.No:
                        print("No")

                #Remember ID's used for images
                remember_data = []
                for thumb_widget in self.thumbnail_widgets:
                    image = str(thumb_widget.image_path)
                    ids = []
                    for id_field in thumb_widget.id_field_list:
                        ids.append(str(int(id_field.ui.song_id_spinbox.value())) + str(id_field.ui.song_id_spinbox.suffix()))
                    remember_data.append([image,ids])

                if os.path.exists(config.remembered_ids_file_location):
                    with io.open(config.remembered_ids_file_location, 'r' , encoding='utf8') as infile:
                        saved_data = yaml.safe_load(infile)

                        saved_paths =  {entry[0] for entry in saved_data}
                        current_paths = {entry[0] for entry in remember_data}

                        common_paths = saved_paths & current_paths
                        untouched_saved_paths = saved_paths - common_paths

                        new_data = []

                        #Write new data for common paths and new ones
                        #Append unchanged data
                        #dump YAML

                        for entry in remember_data:
                            new_data.append(entry)

                        for entry in saved_data:
                            if entry[0] in untouched_saved_paths:
                                new_data.append(entry)

                    with io.open(config.remembered_ids_file_location, 'w', encoding='utf8') as outfile:
                        yaml.dump(new_data, outfile, default_flow_style=False, allow_unicode=True)

                    self.known_ids = self.read_saved_ids()

                else:
                   with io.open(config.remembered_ids_file_location, 'w', encoding='utf8') as outfile:
                       yaml.dump(remember_data, outfile, default_flow_style=False, allow_unicode=True)

                self.known_ids = self.read_saved_ids()

    def calculate_texture_grid(self, thumb_amount):
        if thumb_amount <= 0:
            return 0, 0

        if thumb_amount < 8:
            tex_width = 128 * thumb_amount
            tex_height = 64
            return tex_width,tex_height
        else:
            tex_width = 1024

            rows = math.ceil(thumb_amount / 7)

            total_height = rows * 66  # Height of a thumbnail plus 2 pixels of a gap
            tex_height = next_power_of_two(total_height)
            area = (tex_width, tex_height)
        return area

    def save_pack_name(self):

        if os.path.exists(config.remembered_song_pack_names_file_location):
            with io.open(config.remembered_song_pack_names_file_location, 'r' , encoding='utf8') as infile:
                remember_data = yaml.safe_load(infile)
                if self.main_box.mod_name_lineedit.combo_box.currentText() not in remember_data:
                    remember_data.append(self.main_box.mod_name_lineedit.combo_box.currentText())

                    with io.open(config.remembered_song_pack_names_file_location, 'w', encoding='utf8') as outfile:
                        yaml.dump(remember_data, outfile, default_flow_style=False, allow_unicode=True)


        else:
            remember_data = []
            for i in range(self.main_box.mod_name_lineedit.combo_box.count()):
                remember_data.append(self.main_box.mod_name_lineedit.combo_box.itemText(i))

            if self.main_box.mod_name_lineedit.combo_box.currentText() != "":
                remember_data.append(self.main_box.mod_name_lineedit.combo_box.currentText())

            with io.open(config.remembered_song_pack_names_file_location, 'w', encoding='utf8') as outfile:
                yaml.dump(remember_data, outfile, default_flow_style=False, allow_unicode=True)

        for i in range(self.main_box.mod_name_lineedit.combo_box.count()):
            self.main_box.mod_name_lineedit.combo_box.removeItem(i)
        self.main_box.mod_name_lineedit.combo_box.addItems(remember_data)
        self.main_box.mod_name_lineedit.combo_box.setCurrentText("")


    def fill_combobox_suggestions(self):
        if os.path.exists(config.remembered_song_pack_names_file_location):
            with io.open(config.remembered_song_pack_names_file_location, 'r' , encoding='utf8') as infile:
                remember_data = yaml.safe_load(infile)
                self.main_box.mod_name_lineedit.combo_box.addItems(remember_data)
                print(f"Loaded Song Pack names from: {config.remembered_song_pack_names_file_location}")
        self.main_box.mod_name_lineedit.combo_box.setCurrentText("")


    def delete_selected_name(self):
        name = self.main_box.mod_name_lineedit.combo_box.currentText()
        if name == "":
            return

        edited_file = False

        if os.path.exists(config.remembered_song_pack_names_file_location):
            with io.open(config.remembered_song_pack_names_file_location, 'r', encoding='utf8') as infile:
                remember_data = yaml.safe_load(infile)

                if name in remember_data:
                    remember_data.remove(name)
                    edited_file = True

            if edited_file:
                with io.open(config.remembered_song_pack_names_file_location, 'w', encoding='utf8') as outfile:
                    yaml.dump(remember_data, outfile, default_flow_style=False, allow_unicode=True)



        self.main_box.mod_name_lineedit.combo_box.removeItem(self.main_box.mod_name_lineedit.combo_box.currentIndex())
        self.main_box.mod_name_lineedit.combo_box.setCurrentText("")

###################################################################################################
def export_texture_button_callback(texture:TextureType):
    match texture:
        case TextureType.JACKET_BACKGROUND:
            texture_image = main_window.SC.create_background_jacket_texture(main_window.main_box.sprite_group_combobox.currentEnum())
        case TextureType.LOGO:
            texture_image,_ = main_window.SC.create_logo_texture([(main_window.main_box.sprite_group_combobox.currentEnum(),"")])
        case TextureType.THUMBNAIL:
            texture_image = main_window.SC.create_thumbnail_texture(main_window.main_box.sprite_group_combobox.currentEnum())
        case TextureType.PV_BACK:
            texture_image = main_window.SC.create_pv_back_texture(main_window.main_box.sprite_group_combobox.currentEnum())

    filename, _ = QFileDialog.getSaveFileName(
        None,
        "Save " + texture,
        str(config.last_used_directory) + f"/{texture}.png",
        "PNG Files (*.png)"
    )
    if filename == "":
        print("Directory wasn't chosen")
    else:
        config.last_used_directory = Path(filename).parent
        texture_image.save(filename, "png")

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_box = Ui_MainWindow()
        self.main_box.setupUi(self)
        self.SC = SceneComposer.SceneComposerObjects()
        self._prev_enum = None

        self.setWindowTitle("Megamix Sprite Helper" + " " + str(config.version))

        # Prepare new window
        self.thumbnail_creator = ThumbnailWindow()
        self.song_farc_creator = SongFarcCreatorWindow(self.SC)

        self.menu = self.main_box.menu

        self.export_menu = self.menu.addMenu("Export")
        self.export_menu.addAction("Create Song Sprite Farc", lambda: self.song_farc_creator.show())
        self.export_menu.addAction("Create Thumbnail Farc", lambda: self.thumbnail_creator.show())
        self.export_menu.addAction("Generate Sprite Database", lambda: self.generate_spr_db_button_callback())

        self.export_menu.addSection("Textures")

        self.export_menu.addAction(f"Export {TextureType.JACKET_BACKGROUND}", lambda: export_texture_button_callback(TextureType.JACKET_BACKGROUND))
        self.export_menu.addAction(f"Export {TextureType.LOGO}", lambda: export_texture_button_callback(TextureType.LOGO))
        self.export_menu.addAction(f"Export {TextureType.THUMBNAIL}", lambda: export_texture_button_callback(TextureType.THUMBNAIL))
        self.export_menu.addAction(f"Export {TextureType.PV_BACK}", lambda: export_texture_button_callback(TextureType.PV_BACK))


        self.config_scenes_menu = QSmarterMenu("Configure Scenes",self)
        self.display_scenes_menu = QSmarterMenu("Display Scenes", self)
        self.menu.addMenu(self.config_scenes_menu)
        self.menu.addMenu(self.display_scenes_menu)

        self.share_menu = QSmarterMenu("Share",self)
        self.menu.addMenu(self.share_menu)
        self.share_menu.addAction("Copy preview to clipboard",lambda: self.generate_preview(OutputTarget.CLIPBOARD)).setShortcut("Ctrl+C")
        self.share_menu.addAction("Open preview in external program",lambda: self.generate_preview(OutputTarget.IMAGE_VIEWER)).setShortcut("Ctrl+O")

        self.main_box.flip_horizontal_button.clicked.connect(lambda: self.flip_current_sprite(Qt.Orientation.Horizontal))
        self.main_box.flip_vertical_button.clicked.connect(lambda: self.flip_current_sprite(Qt.Orientation.Vertical))
        self.main_box.current_sprite_combobox.currentIndexChanged.connect(lambda: self.current_sprite_tab_switcher(self.main_box.current_sprite_combobox.currentIndex()))
        self.main_box.sprite_group_combobox.currentEnumChanged.connect(self.sprite_group_changed)

        self.display_scenes()

        self.song_farc_creator.init_preview(self.SC.P_Scenes.PV_Back_Creator_Window)

        #Make sure that tab matches options shown on start
        self.current_sprite_tab_switcher(self.main_box.current_sprite_combobox.currentIndex())

        self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).logo.VisibilityToggled.connect(self.disable_shared_controls)
        self._prev_enum = self.main_box.sprite_group_combobox.currentEnum()




    def sprite_group_changed(self):
        current_enum = self.main_box.sprite_group_combobox.currentEnum()
        current_sprite_object = self.SC.enum_to_obj(current_enum)

        non_active_sprite_object_list = list(self.SC.sprite_groups.values())
        non_active_sprite_object_list.remove(current_sprite_object)

        self.SC.P_Scenes.switch_sprite_group(current_sprite_object)

        self.SC.enum_to_obj(self._prev_enum).logo.VisibilityToggled.disconnect(self.disable_shared_controls)
        self.SC.enum_to_obj(current_enum).logo.VisibilityToggled.connect(self.disable_shared_controls)
        self._prev_enum = current_enum

        for sprite in current_sprite_object.list:
            for slave in sprite.sprite_slaves_list:
                slave.tracked.SpriteUpdated.connect(slave.update_sprite)

        current_sprite_object.update_sprites()

        for sprite in current_sprite_object.list:
            sprite.hide_edit_controls(False)

        for sprite_object in non_active_sprite_object_list:
            for sprite in sprite_object.list:
                sprite.hide_edit_controls(True)

        self.disable_shared_controls()

    def resizeEvent(self,event):
        self.space_out_scenes()

    def current_sprite_tab_switcher(self,tab):
        self.main_box.sprite_controls.setCurrentIndex(tab)

        self.main_box.load_image_button.clicked.disconnect()

        sprite = self.main_box.current_sprite_combobox.currentText()
        self.main_box.load_image_button.clicked.connect(lambda:self.load_new_sprite_image(sprite))
        self.main_box.load_image_button.setText(f"Load {sprite} Image")

        match sprite:
            case SpriteType.BACKGROUND:
                self.main_box.load_image_button.setEnabled(self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).background.controls_enabled)
                self.main_box.flip_vertical_button.setEnabled(self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).background.controls_enabled)
                self.main_box.flip_horizontal_button.setEnabled(self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).background.controls_enabled)
            case SpriteType.JACKET:
                self.main_box.load_image_button.setEnabled(self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).jacket.controls_enabled)
                self.main_box.flip_vertical_button.setEnabled(self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).jacket.controls_enabled)
                self.main_box.flip_horizontal_button.setEnabled(self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).jacket.controls_enabled)
            case SpriteType.LOGO:
                self.main_box.load_image_button.setEnabled(self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).logo.controls_enabled)
                self.main_box.flip_vertical_button.setEnabled(self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).logo.controls_enabled)
                self.main_box.flip_horizontal_button.setEnabled(self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).logo.controls_enabled)
            case SpriteType.THUMBNAIL:
                self.main_box.load_image_button.setEnabled(self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).thumbnail.controls_enabled)
                self.main_box.flip_vertical_button.setEnabled(self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).thumbnail.controls_enabled)
                self.main_box.flip_horizontal_button.setEnabled(self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).thumbnail.controls_enabled)

    def flip_current_sprite(self,flip_type):
        current_sprite = self.main_box.current_sprite_combobox.currentText()
        match current_sprite:
            case SpriteType.BACKGROUND:
                self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).background.toggle_flip(flip_type)
            case SpriteType.JACKET:
                self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).jacket.toggle_flip(flip_type)
            case SpriteType.LOGO:
                self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).logo.toggle_flip(flip_type)
            case SpriteType.THUMBNAIL:
                self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).thumbnail.toggle_flip(flip_type)

    def display_scenes(self):
        self.populate_display_scene_menu()

        self.mm_practice_toggle.setChecked(False)
        self.pv_back_toggle.setChecked(False)

        current_enum = self.main_box.sprite_group_combobox.currentEnum()
        current_sprite_object = self.SC.enum_to_obj(current_enum)

        sprite_object_list = list(self.SC.sprite_groups.values())

        for sprite_object in sprite_object_list:
            sprite_object.thumbnail.add_edit_controls_to(self.main_box.thumbnail_control_layout)
            sprite_object.logo.add_edit_controls_to(self.main_box.logo_control_layout)
            sprite_object.jacket.add_edit_controls_to(self.main_box.jacket_control_layout)
            sprite_object.background.add_edit_controls_to(self.main_box.background_control_layout)

        sprite_object_list.remove(current_sprite_object)

        for sprite_object in sprite_object_list:
            for sprite in sprite_object.list:
                sprite.hide_edit_controls(True)

        sprite_control_layout = [self.main_box.thumbnail_control_layout,
                                 self.main_box.logo_control_layout,
                                 self.main_box.jacket_control_layout,
                                 self.main_box.background_control_layout]

        verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        for layout in sprite_control_layout:
            layout.addItem(verticalSpacer)

        self.selected_scenes_views = []


        self.display_selected_scenes()

    def populate_display_scene_menu(self):
        self.mm_song_select_toggle = self.display_scenes_menu.addAction("MegaMix Song Select")
        self.mm_result_toggle = self.display_scenes_menu.addAction("MegaMix Results")
        self.mm_practice_toggle = self.display_scenes_menu.addAction("MegaMix Practice Mode")
        self.ft_song_select_toggle = self.display_scenes_menu.addAction("Future Tone Song Select")
        self.ft_result_toggle = self.display_scenes_menu.addAction("Future Tone Results")
        self.pv_back_toggle = self.display_scenes_menu.addAction("PV Back")

        self.scene_toggle_list = []
        self.scene_toggle_list.append((self.mm_song_select_toggle, self.SC.P_Scenes.MM_SongSelect))
        self.scene_toggle_list.append((self.ft_song_select_toggle, self.SC.P_Scenes.FT_SongSelect))
        self.scene_toggle_list.append((self.mm_result_toggle,self.SC.P_Scenes.MM_Result))
        self.scene_toggle_list.append((self.ft_result_toggle,self.SC.P_Scenes.FT_Result))
        self.scene_toggle_list.append((self.mm_practice_toggle, self.SC.P_Scenes.MM_PracticeMode))
        self.scene_toggle_list.append((self.pv_back_toggle,self.SC.P_Scenes.PV_Back))

        self.new_classics_toggle = QAction("Show New Classics UI")
        self.new_classics_toggle.setCheckable(True)
        self.new_classics_toggle.setChecked(True)

        for toggle in self.scene_toggle_list:
            toggle[0].setCheckable(True)
            toggle[0].setChecked(True)
            toggle[0].triggered.connect(self.display_selected_scenes)
    def display_selected_scenes(self):
        self.selected_scenes = []

        for scene_view in self.selected_scenes_views:
            scene_view.destroy()
            scene_view.deleteLater()
            self.main_box.image_grid.removeWidget(scene_view)

        self.selected_scenes_views.clear()



        for toggle in self.scene_toggle_list:
            if toggle[0].isChecked():
                self.selected_scenes.append(toggle[1])


        for scene in self.selected_scenes:
            scene_view = QScalingGraphicsScene()
            scene_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scene_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
            sizePolicy2.setHorizontalStretch(1)
            sizePolicy2.setVerticalStretch(1)
            scene_view.setSizePolicy(sizePolicy2)
            scene_view.setMinimumSize(QSize(512, 288))
            scene_view.setMaximumSize(QSize(512, 288))
            scene_view.setBaseSize(QSize(512, 288))
            scene_view.setRenderHint(QPainter.Antialiasing, True)
            scene_view.setRenderHint(QPainter.SmoothPixmapTransform, True)
            scene_view.setBackgroundBrush(Qt.black)
            scene_view.setScene(scene)
            self.selected_scenes_views.append(scene_view)

            self.main_box.image_grid.addWidget(scene_view)

        self.populate_configure_scene_menu()
        self.space_out_scenes()
    def populate_configure_scene_menu(self):
        self.config_scenes_menu.clear()
        self.config_scenes_menu.addSection("Apply to all scenes")
        new_classic_toggleable_scene_present = any(item in self.SC.P_Scenes.new_classics_scenes for item in self.selected_scenes)

        if new_classic_toggleable_scene_present:
            self.config_scenes_menu.addAction(self.new_classics_toggle)
            for scene in self.SC.P_Scenes.new_classics_scenes:
                self.new_classics_toggle.toggled.connect(scene.toggle_new_classics)


        self.config_scenes_menu.addSection("Per Scene toggles")
        for scene in self.selected_scenes:
            self.config_scenes_menu.addMenu(scene.scene_config_menu)

    def space_out_scenes(self):
        if len(self.selected_scenes_views) > 1:
            size = 2
        else:
            size = 1

        columns = 1
        x = 0
        y = 0
        for scene in self.selected_scenes_views:
            self.main_box.image_grid.removeWidget(scene)
            scene.size = size
            scene.lock_in()
            self.main_box.image_grid.addWidget(scene,y,x)
            if x == columns:
                y = y + 1
                x = 0
            else:
                x = x + 1

    def generate_preview(self,target:OutputTarget):
        self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).jacket.update_sprite(hq_output=True)
        self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).background.update_sprite(hq_output=True)
        self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).thumbnail.update_sprite(hq_output=True)
        self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).logo.update_sprite(hq_output=True)

        if len(self.selected_scenes) == 0:
            return
        if len(self.selected_scenes) > 1:
            width = 3840
            height = math.ceil((len(self.selected_scenes)/2))*1080
        else:
            width = 1920
            height = 1080

        preview = QImage(QSize(width,height),QImage.Format.Format_ARGB32)
        painter = QPainter(preview)

        x = 0
        y = 0
        w = 0
        h = 0
        for scene in self.selected_scenes:
            print(QRectF(x,y,scene.width(), scene.height()))
            scene.render(painter,target=QRectF(w,h,1920, 1080))

            if x == 1:
                w = 0
                h = h+1080

                y = y + 1
                x = 0
            else:
                w = w + 1920
                x = x + 1

        painter.end()

        match target:
            case OutputTarget.CLIPBOARD:
                clipboard = QGuiApplication.clipboard()
                clipboard.setImage(preview)

            case OutputTarget.IMAGE_VIEWER:
                temp_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.TempLocation)
                temp_file = os.path.join(temp_dir, "qt_image.png")

                if preview.save(temp_file, "PNG"):
                    url = QUrl.fromLocalFile(temp_file)
                    QDesktopServices.openUrl(url)


    def disable_shared_controls(self):
        state = self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).logo.is_visible

        if self.main_box.current_sprite_combobox.currentText() == SpriteType.LOGO:
            self.main_box.load_image_button.setEnabled(state)
            self.main_box.flip_vertical_button.setEnabled(state)
            self.main_box.flip_horizontal_button.setEnabled(state)



    def load_new_sprite_image(self,sprite):
        sprite_object = None
        match sprite:
            case SpriteType.BACKGROUND:
                sprite_object = self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).background
            case SpriteType.JACKET:
                sprite_object = self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).jacket
            case SpriteType.THUMBNAIL:
                sprite_object = self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).thumbnail
            case SpriteType.LOGO:
                sprite_object = self.SC.enum_to_obj(self.main_box.sprite_group_combobox.currentEnum()).logo

        image_location = QFileDialog.getOpenFileName(self,
                                                 f"Open {sprite_object.sprite_type.value} image",
                                                 str(config.last_used_directory),
                                                 config.allowed_file_types)[0]
        if image_location == "":
            print("User didn't select image")
        else:
            config.last_used_directory = Path(image_location).parent
            ret= sprite_object.load_new_image(image_location)
            match ret[0]:
                case "Updated":
                    pass
                case "Image too small":
                    iw = ret[1]
                    ih = ret[2]
                    rw = ret[3]
                    rh = ret[4]

                    show_message_box(f"{sprite} image is too small.",
                                     f"Required image size for {sprite} is {rw}x{rh}.\n"
                                     f"Loaded image is {iw}x{ih}, ignoring transparent area.")

    def generate_spr_db_button_callback(self,path=None):
        spr_path = path
        if spr_path is None:
            spr_path = QFileDialog.getExistingDirectory(self,"Choose 2d folder to generate spr_db for",str(config.last_used_directory))

        if spr_path == "":
            print("Folder wasn't chosen")
        else:
            spr_db = Manager()
            farc_list = []
            new_thumb_farc_count = 0
            config.last_used_directory = Path(spr_path)
            for spr in Path(spr_path).iterdir():
                _temp_file = Path(spr)
                if _temp_file.suffix.upper() == ".FARC":
                    farc_list.append(_temp_file)
            if len(farc_list) > 0:
                has_old_tmb_farc = False
                has_new_tmb_farc = False
                for farc_file in farc_list:
                    if farc_file.name == "spr_sel_pvtmb.farc":
                        has_old_tmb_farc = True
                    elif farc_file.name[:14] == "spr_sel_pvtmb_":
                        new_thumb_farc_count = new_thumb_farc_count +1
                        has_new_tmb_farc = True
                if has_new_tmb_farc:
                    if has_old_tmb_farc:
                        farc_list.remove(Path(spr_path + "/spr_sel_pvtmb.farc"))
                        show_message_box("Warning", "You have included both new and old thumbnail farcs in your mod! Generating spr_db was skipped."
                                                    "\n"
                                                    "\nPlease remove 'spr_sel_pvtmb.farc' from your mod to generate sprite database.")
                        print("Found Both old and new thumbnail farc formats. Skipping database generation.")
                        return
                    else:
                        print("Only separate thumbnail farc files found.")
                    if new_thumb_farc_count > 1:
                        show_message_box("Warning", "You have included multiple new thumbnail farcs in your mod! Generating spr_db was skipped."
                                                    "\n"
                                                    "\nPlease include only 1 thumbnail farc in your mod to generate sprite database.")
                        print("Multiple new thumbnail farc's found. Skipping database generation.")
                        return

                for farc_file in farc_list:
                    farc_reader = read_farc(farc_file)
                    add_farc_to_Manager(farc_reader, spr_db)
            spr_db.write_db(f'{spr_path}/mod_spr_db.bin')
            print(spr_db.sprinfo_list)
            print(f"Generated mod_spr_db in {spr_path}")

class SongFarcCreatorWindow(QWidget):
    def resizeEvent(self, event, /):
        self.scene_view.lock_in()
    def __init__(self,SC_obj):
        super(SongFarcCreatorWindow, self).__init__()
        self.main_box = Ui_SongFarcCreatorWindow()
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.SC = SC_obj
        self.main_box.setupUi(self,SC_obj=self.SC,sprite_group_enum=SceneComposer.SpriteGroup)

        self.main_box.export_farc_pushbutton.pressed.connect(self.export_background_jacket_logo_farc_button_callback)

        self.main_box.ex_sprites_checkbox.toggled.connect(self.ex_sprite_checkbox_callback)
        self.main_box.pv_back_sprite_checkbox.toggled.connect(self.pv_back_sprite_checkbox_callback)
        self.main_box.pv_back_sprite_group_widget.SpriteGroupChanged.connect(self.switch_pv_back_scene_sprite_group)

    def ex_sprite_checkbox_callback(self):
        self.main_box.ex_sprite_group_widget.setEnabled(self.main_box.ex_sprites_checkbox.isChecked())
    def pv_back_sprite_checkbox_callback(self):
        self.main_box.pv_back_sprite_group_widget.setEnabled(self.main_box.pv_back_sprite_checkbox.isChecked())
        self.main_box.pv_back_tab.setEnabled(self.main_box.pv_back_sprite_checkbox.isChecked())
        self.main_box.tab_view.setTabVisible(1,self.main_box.pv_back_sprite_checkbox.isChecked())
    def init_preview(self,scene):
        self.scene_view = QScalingGraphicsScene()
        self.scene_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scene_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(1)
        self.scene_view.setSizePolicy(sizePolicy2)
        self.scene_view.setMinimumSize(QSize(512, 288))
        self.scene_view.setMaximumSize(QSize(512, 288))
        self.scene_view.setBaseSize(QSize(512, 288))
        self.scene_view.setRenderHint(QPainter.Antialiasing, True)
        self.scene_view.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.scene_view.setBackgroundBrush(Qt.black)
        self.scene_view.set_forced_size(QSize(512,288))

        self.scene_view.setScene(scene)
        scene.layout_choose_layout = self.main_box.pv_back_layout_choose_layout
        scene.options_layout = self.main_box.pv_back_scene_option_layout
        scene.toggle_layout(PvBackLayout.MMSongSelect)
        scene.add_layouts_to_window()

        self.main_box.pv_back_preview_layout.addWidget(self.scene_view)
    def export_background_jacket_logo_farc_button_callback(self):


        logo = None
        pv_back_texture = None
        ex_bg_jk = None

        song_id = pad_number(int(self.main_box.farc_song_id_spinbox.value()))
        compression = self.main_box.compression_comboBox.currentEnum()

        default_sprite_group = self.main_box.default_sprite_group_widget.get_selected_sprite_group()
        ex_sprite_group = self.main_box.ex_sprite_group_widget.get_selected_sprite_group()
        pv_back_sprite_group = self.main_box.pv_back_sprite_group_widget.get_selected_sprite_group()

        ex_sprites_checked = self.main_box.ex_sprites_checkbox.isChecked()
        base_logo_visible = main_window.SC.enum_to_obj(self.main_box.default_sprite_group_widget.get_selected_sprite_group()).logo.is_visible
        ex_logo_visible = main_window.SC.enum_to_obj(self.main_box.ex_sprite_group_widget.get_selected_sprite_group()).logo.is_visible
        pv_back_checked = self.main_box.pv_back_sprite_checkbox.isChecked()

        placeholders_used = []
        if main_window.SC.enum_to_obj(default_sprite_group).background.location.startswith(":"):
            placeholders_used.append(f"{default_sprite_group.value}: {main_window.SC.enum_to_obj(default_sprite_group).background.sprite_type.name}\n")
        if main_window.SC.enum_to_obj(default_sprite_group).jacket.location.startswith(":"):
            placeholders_used.append(f"{default_sprite_group.value}: {main_window.SC.enum_to_obj(default_sprite_group).jacket.sprite_type.name}\n")

        if base_logo_visible:
            if main_window.SC.enum_to_obj(default_sprite_group).logo.location.startswith(":"):
                placeholders_used.append(f"{default_sprite_group.value}: {main_window.SC.enum_to_obj(default_sprite_group).logo.sprite_type.name}\n")

        if ex_sprites_checked:
            if main_window.SC.enum_to_obj(ex_sprite_group).background.location.startswith(":"):
                placeholders_used.append(f"{ex_sprite_group.value}: {main_window.SC.enum_to_obj(ex_sprite_group).background.sprite_type.name}\n")
            if main_window.SC.enum_to_obj(ex_sprite_group).jacket.location.startswith(":"):
                placeholders_used.append(f"{ex_sprite_group.value}: {main_window.SC.enum_to_obj(ex_sprite_group).jacket.sprite_type.name}\n")

            if ex_logo_visible:
                if main_window.SC.enum_to_obj(ex_sprite_group).logo.location.startswith(":"):
                    placeholders_used.append(f"{ex_sprite_group.value}: {main_window.SC.enum_to_obj(ex_sprite_group).logo.sprite_type.name}\n")

        if pv_back_checked:
            for sprite in main_window.SC.enum_to_obj(pv_back_sprite_group).list:
                if sprite.sprite_type in (SpriteType.LOGO, SpriteType.BACKGROUND, SpriteType.JACKET):
                    if sprite.location.startswith(":"):
                        placeholders_used.append(f"{pv_back_sprite_group.value}: {sprite.sprite_type.name}\n")

        placeholders_used = list(set(placeholders_used))
        placeholders_used.sort()

        if placeholders_used:
            placeholder_str = "".join(placeholders_used)
            show_message_box("Placeholders used","Following sprites are using placeholder sprites:\n\n" + placeholder_str+"\nIf that's not intended then verify if you selected correct sprite groups.")



        output_location = QFileDialog.getExistingDirectory(self, "Choose folder to save farc file to", str(config.last_used_directory))

        if output_location == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(output_location)

            bg_jk = Image.fromqimage(main_window.SC.create_background_jacket_texture(default_sprite_group)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            logo_list = []

            if base_logo_visible:
                logo_list.append((default_sprite_group,""))

            if ex_sprites_checked:
                ex_bg_jk = Image.fromqimage(main_window.SC.create_background_jacket_texture(ex_sprite_group)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                if ex_logo_visible:
                    logo_list.append((ex_sprite_group, "_EX"))

            logo_texture, logo_info = main_window.SC.create_logo_texture(logo_list)
            if logo_texture is not None:
                logo_texture = Image.fromqimage(logo_texture).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                logos = (logo_texture,logo_info)
            else:
                logos = []

            if pv_back_checked:
                pv_back_texture = Image.fromqimage(main_window.SC.create_pv_back_texture(pv_back_sprite_group)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)

            print(f"Logos = {logos}")
            FarcCreator.create_jk_bg_logo_farc(song_id, bg_jk, logos, output_location,compression,pv_back_texture=pv_back_texture,ex_bg_jk_texture=ex_bg_jk)

            if self.main_box.generate_spr_db_after_export_checkbox.isChecked():
                main_window.generate_spr_db_button_callback(path=output_location)

    def switch_pv_back_scene_sprite_group(self):
        self.scene_view.scene().switch_sprite_group(main_window.SC.enum_to_obj(self.main_box.pv_back_sprite_group_widget.get_selected_sprite_group()))
        main_window.SC.enum_to_obj(self.main_box.pv_back_sprite_group_widget.get_selected_sprite_group()).update_sprites()


if __name__ == "__main__":
    config = Configurable()
    FarcCreator = FarcCreator()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = MainWindow()
    main_window.show()
    app.exec()