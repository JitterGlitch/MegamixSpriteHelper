import io
import math
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from enum import Enum, auto
from pathlib import Path
from time import sleep

import PIL.ImageShow

import kkdlib

import yaml
from PIL import Image
from PySide6.QtCore import Qt, QFileSystemWatcher, QSize, Signal, QRectF, QStandardPaths, QUrl, QFile, QIODevice, QByteArray, QRect
from PySide6.QtGui import QPixmap, QPalette, QColor, QImage, QPainter, QGuiApplication, QDesktopServices, QImageWriter, QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox, QSizePolicy, QMenu, QMenuBar

from Source.ui_SongFarcCreator import Ui_SongFarcCreatorWindow
from widgets import QSmarterMenu

try:
    from wand.image import Image as WImage
except ImportError:
    import sys

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)


    message_box = QMessageBox()
    message_box.setModal(True)
    message_box.setTextFormat(Qt.TextFormat.RichText)
    message_box.setWindowTitle("ImageMagick is not installed")
    message_box.setText("Please install ImageMagick with 'Install development headers and libraries for C and C++ checked. \n"
                        "<a href='https://docs.wand-py.org/en/latest/guide/install.html#install-imagemagick-on-windows'>More Info</a>")
    message_box.setIcon(QMessageBox.Icon.Critical)
    message_box.exec()

    sys.exit(1)


from FarcCreator import FarcCreator
from SceneComposer import QControllableSprites, QPreviewScenes, SpriteSetting, QSpriteSlave, SpriteType, QScalingGraphicsScene, PvBackLayout
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
        self.version = 1.2

        extensions = Image.registered_extensions()
        self.readable_extensions = [ext for ext, fmt in extensions.items() if fmt in Image.OPEN]
        formats_string = " ".join(sorted([f"*{ext}" for ext in self.readable_extensions]))

        self.allowed_file_types = f"Image Files ({formats_string})"
        self.last_used_directory = self.script_directory



class ThumbnailIDFieldWidget(QWidget):
    additionalRequested = Signal(QWidget)
    removeRequested = Signal(QWidget)
    thumb_count_request = Signal()

    def __init__(self,parent=None,variant=False, inferred_id=None):

        super(ThumbnailIDFieldWidget, self).__init__(parent)
        self.variant = variant    #False cannot be removed, spawns with button to add more id fields
                                                #True can be removed, spawns with button to remove itself.

        self.value = None #This should contain Song ID , needs to check if it's under ID limit.
        self.ui = Ui_ThumbnailIDField()
        self.ui.setupUi(self,variant)
        if inferred_id:
            self.ui.song_id_spinbox.setValue(float(inferred_id))
        self.ui.song_id_spinbox.editingFinished.connect(self.thumb_count_request.emit)

        if variant:
            self.ui.id_line_button.clicked.connect(lambda: self.additionalRequested.emit(self))
        else:
            self.ui.id_line_button.clicked.connect(lambda: self.removeRequested.emit(self))




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
        self.ui.formLayout.addRow(id_field)
        self.thumb_count_request.emit()

    def remove_id_field(self,widget):
        self.ui.formLayout.removeRow(widget)
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


class ThumbnailWindow(QWidget):
    resized = Signal()
    NameDeleteRequest = Signal()
    def __init__(self):
        super(ThumbnailWindow, self).__init__()
        self.main_box = Ui_ThumbnailTextureCreator()
        self.main_box.setupUi(self)
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
                id_field.setStyleSheet("")
                id_seen.append(id_field.ui.song_id_spinbox.value())
                if  id_field.ui.song_id_spinbox.value() == 0:
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

        duplicates = list(filter(lambda a: a != 0, duplicates))

        for thumbnail_widget in self.thumbnail_widgets:
            for id_field in thumbnail_widget.id_field_list:
                if id_field.ui.song_id_spinbox.value() in duplicates:
                    id_field.setPalette(self.id_conflict_palette)
                    id_field.parent().parent().parent().parent().setStyleSheet(Stylesheet.SCROLL_AREA_CONFLICT.value)
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
            print(image_name)
            if image_name.isdigit() and len(image_name) >= 3:
                id_list = [image_name]
                inferred_id_list.append([image_path,id_list])
            else:
                inferred_id_list.append((image_path,[]))
        return inferred_id_list

    def space_out_thumbnails(self):
        width = self.main_box.verticalLayout.geometry().width()
        widget_width = 365
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
        if Path('remembered_ids.yaml').exists():
            with io.open('remembered_ids.yaml', 'r', encoding='utf8') as infile:
                saved_data = yaml.safe_load(infile)
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
                thumbnail_texture.save(str(config.script_directory) + "/Thumbnail Texture.png","png")
                compression = self.main_box.farc_compression_combobox.currentEnum()

                FarcCreator.create_thumbnail_farc(thumbnail_positions,thumbnail_texture.transpose(Image.FLIP_TOP_BOTTOM),chosen_dir,mod_name,compression)

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
                        ids.append(int(id_field.ui.song_id_spinbox.value()))
                    remember_data.append([image,ids])

                if Path('remembered_ids.yaml').exists():
                    with io.open('remembered_ids.yaml', 'r' , encoding='utf8') as infile:
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

                    with io.open('remembered_ids.yaml', 'w', encoding='utf8') as outfile:
                        yaml.dump(new_data, outfile, default_flow_style=False, allow_unicode=True)

                    self.known_ids = self.read_saved_ids()

                else:
                   with io.open('remembered_ids.yaml', 'w', encoding='utf8') as outfile:
                       yaml.dump(remember_data, outfile, default_flow_style=False, allow_unicode=True)

                self.known_ids = self.read_saved_ids()

    def next_power_of_two(self,n):
        if n <= 0:
            return 1
        p = 1
        while p < n:
            p *= 2
        return p

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
            tex_height = self.next_power_of_two(total_height)
            area = (tex_width, tex_height)
        return area

    def save_pack_name(self):

        if Path('remembered_names.yaml').exists():
            with io.open('remembered_names.yaml', 'r' , encoding='utf8') as infile:
                remember_data = yaml.safe_load(infile)
                if self.main_box.mod_name_lineedit.combo_box.currentText() not in remember_data:
                    remember_data.append(self.main_box.mod_name_lineedit.combo_box.currentText())

                    with io.open('remembered_names.yaml', 'w', encoding='utf8') as outfile:
                        yaml.dump(remember_data, outfile, default_flow_style=False, allow_unicode=True)


        else:
            remember_data = []
            for i in range(self.main_box.mod_name_lineedit.combo_box.count()):
                remember_data.append(self.main_box.mod_name_lineedit.combo_box.itemText(i))

            if self.main_box.mod_name_lineedit.combo_box.currentText() != "":
                remember_data.append(self.main_box.mod_name_lineedit.combo_box.currentText())

            with io.open('remembered_names.yaml', 'w', encoding='utf8') as outfile:
                yaml.dump(remember_data, outfile, default_flow_style=False, allow_unicode=True)

        for i in range(self.main_box.mod_name_lineedit.combo_box.count()):
            self.main_box.mod_name_lineedit.combo_box.removeItem(i)
        self.main_box.mod_name_lineedit.combo_box.addItems(remember_data)

    def fill_combobox_suggestions(self):
        if Path('remembered_names.yaml').exists():
            with io.open('remembered_names.yaml', 'r' , encoding='utf8') as infile:
                remember_data = yaml.safe_load(infile)
                self.main_box.mod_name_lineedit.combo_box.addItems(remember_data)

    def delete_selected_name(self):
        name = self.main_box.mod_name_lineedit.combo_box.currentText()
        if name == "":
            return

        edited_file = False

        if Path('remembered_names.yaml').exists():
            with io.open('remembered_names.yaml', 'r', encoding='utf8') as infile:
                remember_data = yaml.safe_load(infile)

                if name in remember_data:
                    remember_data.remove(name)
                    edited_file = True

            if edited_file:
                with io.open('remembered_names.yaml', 'w', encoding='utf8') as outfile:
                    yaml.dump(remember_data, outfile, default_flow_style=False, allow_unicode=True)



        self.main_box.mod_name_lineedit.combo_box.removeItem(self.main_box.mod_name_lineedit.combo_box.currentIndex())
        self.main_box.mod_name_lineedit.combo_box.setCurrentText("")
        self.main_box.mod_name_lineedit.label_set_placeholder_text()


###################################################################################################
def show_message_box(title,contents):
    message_box = QMessageBox()
    message_box.setModal(True)
    message_box.setWindowTitle(title)
    message_box.setText(contents)
    message_box.exec()

class MainWindow(QMainWindow):



    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_box = Ui_MainWindow()
        self.main_box.setupUi(self)
        self.setWindowTitle("Megamix Sprite Helper" + " " + str(config.version))

        # Prepare new window
        self.thumbnail_creator = ThumbnailWindow()
        self.song_farc_creator = SongFarcCreatorWindow()

        self.menu = self.main_box.menu

        self.file_menu = self.menu.addMenu("File")
        self.open_project = self.file_menu.addAction("Open Project...", self.close)
        self.save_project = self.file_menu.addAction("Save Project", self.close)

        self.export_menu = self.menu.addMenu("Export")
        self.export_menu.addAction("Create Song Sprite Farc", lambda: self.song_farc_creator.show())
        self.export_menu.addAction("Create Thumbnail Farc", lambda: self.thumbnail_creator.show())
        self.export_menu.addAction("Generate Sprite Database", self.generate_spr_db_button_callback)
        self.export_menu.addSection("Textures")
        self.export_menu.addAction("Export Thumbnail Texture", self.song_farc_creator.export_thumbnail_button_callback)
        self.export_logo = self.export_menu.addAction("Export Logo Texture", self.song_farc_creator.export_logo_button_callback)
        self.export_menu.addAction("Export Jacket/Background Texture", self.song_farc_creator.export_background_jacket_button_callback)


        self.config_scenes_menu = QSmarterMenu("Configure Scenes",self)
        self.display_scenes_menu = QSmarterMenu("Display Scenes", self)
        self.menu.addMenu(self.config_scenes_menu)
        self.menu.addMenu(self.display_scenes_menu)

        self.share_menu = QSmarterMenu("Share",self)
        self.menu.addMenu(self.share_menu)
        self.share_menu.addAction("Copy preview to clipboard",lambda: self.generate_preview(OutputTarget.CLIPBOARD)).setShortcut("Ctrl+C")
        self.share_menu.addAction("Open preview in external program",lambda: self.generate_preview(OutputTarget.IMAGE_VIEWER)).setShortcut("Ctrl+O")

        #Start watching for file updates of loaded files
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.watcher_file_modified_action)

        #self.main_box.farc_export_button.clicked.connect(self.export_background_jacket_logo_farc_button_callback)
        self.main_box.flip_horizontal_button.clicked.connect(lambda: self.flip_current_sprite(Qt.Orientation.Horizontal))
        self.main_box.flip_vertical_button.clicked.connect(lambda: self.flip_current_sprite(Qt.Orientation.Vertical))

        self.main_box.current_sprite_combobox.currentIndexChanged.connect(lambda: self.current_sprite_tab_switcher(self.main_box.current_sprite_combobox.currentIndex()))

        self.display_scenes()

        self.song_farc_creator.init_preview(self.P_Scenes.PV_Back_Creator_Window)

        #Make sure that tab matches options shown on start
        self.current_sprite_tab_switcher(self.main_box.current_sprite_combobox.currentIndex())




    def resizeEvent(self,event):
        self.space_out_scenes()

    def current_sprite_tab_switcher(self,tab):
        self.main_box.sprite_controls.setCurrentIndex(tab)

        self.main_box.load_image_button.clicked.disconnect()

        sprite = self.main_box.current_sprite_combobox.currentText()
        self.main_box.load_image_button.clicked.connect(lambda:self.load_new_sprite_image(sprite))
        self.main_box.load_image_button.setText(f"Load {sprite} Image")

        match sprite:
            case "Background":
                self.main_box.load_image_button.setEnabled(self.C_Sprites.background.controls_enabled)
                self.main_box.flip_vertical_button.setEnabled(self.C_Sprites.background.controls_enabled)
                self.main_box.flip_horizontal_button.setEnabled(self.C_Sprites.background.controls_enabled)
            case "Jacket":
                self.main_box.load_image_button.setEnabled(self.C_Sprites.jacket.controls_enabled)
                self.main_box.flip_vertical_button.setEnabled(self.C_Sprites.jacket.controls_enabled)
                self.main_box.flip_horizontal_button.setEnabled(self.C_Sprites.jacket.controls_enabled)
            case "Logo":
                self.main_box.load_image_button.setEnabled(self.C_Sprites.logo.controls_enabled)
                self.main_box.flip_vertical_button.setEnabled(self.C_Sprites.logo.controls_enabled)
                self.main_box.flip_horizontal_button.setEnabled(self.C_Sprites.logo.controls_enabled)
            case "Thumbnail":
                self.main_box.load_image_button.setEnabled(self.C_Sprites.thumbnail.controls_enabled)
                self.main_box.flip_vertical_button.setEnabled(self.C_Sprites.thumbnail.controls_enabled)
                self.main_box.flip_horizontal_button.setEnabled(self.C_Sprites.thumbnail.controls_enabled)

    def flip_current_sprite(self,flip_type):
        current_sprite = self.main_box.current_sprite_combobox.currentText()
        match current_sprite:
            case "Background":
                self.C_Sprites.background.toggle_flip(flip_type)
            case "Jacket":
                self.C_Sprites.jacket.toggle_flip(flip_type)
            case "Logo":
                self.C_Sprites.logo.toggle_flip(flip_type)
            case "Thumbnail":
                self.C_Sprites.thumbnail.toggle_flip(flip_type)

    def display_scenes(self):
        self.C_Sprites = QControllableSprites()
        self.P_Scenes = QPreviewScenes(self.C_Sprites)

        self.populate_display_scene_menu()

        self.C_Sprites.thumbnail.add_edit_controls_to(self.main_box.verticalLayout_12)
        self.C_Sprites.logo.add_edit_controls_to(self.main_box.verticalLayout_11)
        self.C_Sprites.jacket.add_edit_controls_to(self.main_box.verticalLayout_10)
        self.C_Sprites.background.add_edit_controls_to(self.main_box.verticalLayout_8)
        self.selected_scenes_views = []


        self.display_selected_scenes()

    def populate_display_scene_menu(self):
        self.mm_song_select_toggle = self.display_scenes_menu.addAction("MegaMix Song Select")
        self.mm_result_toggle = self.display_scenes_menu.addAction("MegaMix Results")
        self.mm_practise_toggle = self.display_scenes_menu.addAction("MegaMix Practice Mode")
        self.ft_song_select_toggle = self.display_scenes_menu.addAction("Future Tone Song Select")
        self.ft_result_toggle = self.display_scenes_menu.addAction("Future Tone Results")
        self.pv_back_toggle = self.display_scenes_menu.addAction("PV Back")

        self.scene_toggle_list = []
        self.scene_toggle_list.append((self.mm_song_select_toggle, self.P_Scenes.MM_SongSelect))
        self.scene_toggle_list.append((self.ft_song_select_toggle, self.P_Scenes.FT_SongSelect))
        self.scene_toggle_list.append((self.mm_result_toggle,self.P_Scenes.MM_Result))
        self.scene_toggle_list.append((self.ft_result_toggle,self.P_Scenes.FT_Result))
        self.scene_toggle_list.append((self.mm_practise_toggle, self.P_Scenes.MM_PractiseMode))
        self.scene_toggle_list.append((self.pv_back_toggle,self.P_Scenes.PV_Back))

        self.new_classics_toggle = QAction("Show New Classics UI")
        self.new_classics_toggle.setCheckable(True)
        self.new_classics_toggle.setChecked(True)

        self.has_logo_toggle = QAction("Show Logo")
        self.has_logo_toggle.setCheckable(True)
        self.has_logo_toggle.setChecked(True)
        self.has_logo_toggle.toggled.connect(self.has_logo_toggle_callback)

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
            if toggle[0].isChecked() == True:
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
            # scene_view.setBackgroundBrush(self.palette().color(QPalette.ColorRole.Window))
            scene_view.setBackgroundBrush(Qt.black)
            scene_view.setScene(scene)
            self.selected_scenes_views.append(scene_view)

            self.main_box.image_grid.addWidget(scene_view)

        self.populate_configure_scene_menu()
        self.space_out_scenes()
    def populate_configure_scene_menu(self):
        self.config_scenes_menu.clear()
        self.config_scenes_menu.addSection("Apply to all scenes")
        new_classic_toggleable_scene_present = any(item in self.P_Scenes.new_classics_scenes for item in self.selected_scenes)

        if len(self.selected_scenes) > 0:
            self.config_scenes_menu.addAction(self.has_logo_toggle)

        if new_classic_toggleable_scene_present:
            self.config_scenes_menu.addAction(self.new_classics_toggle)
            for scene in self.P_Scenes.new_classics_scenes:
                self.new_classics_toggle.toggled.connect(scene.toggle_new_classics)


        self.config_scenes_menu.addSection("Per Scene toggles")
        for scene in self.selected_scenes:
            self.config_scenes_menu.addMenu(scene.scene_config_menu)

    def space_out_scenes(self):
        if len(self.selected_scenes_views) > 1:
            size = 2.15
        else:
            size = 1.06

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
        #Update sprites if the zoom was changed
        if self.C_Sprites.jacket.edit_controls[SpriteSetting.ZOOM.value].value != 1.0:
            self.C_Sprites.jacket.update_sprite(hq_output=True)
        if self.C_Sprites.background.edit_controls[SpriteSetting.ZOOM.value].value != 1.0:
            self.C_Sprites.background.update_sprite(hq_output=True)
        if self.C_Sprites.thumbnail.edit_controls[SpriteSetting.ZOOM.value].value != 1.0:
            self.C_Sprites.thumbnail.update_sprite(hq_output=True)
        if self.C_Sprites.logo.edit_controls[SpriteSetting.ZOOM.value].value != 1.0:
            self.C_Sprites.logo.update_sprite(hq_output=True)

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

    def watcher_file_modified_action(self,path):
        sleep(2)
        keep_watching_path = False

        for sprite in self.C_Sprites.list:
            if path == sprite.location:
                print(f"{sprite.type.value} image was changed")
                if sprite.load_new_image(path,fallback=True) == "Updated":
                     keep_watching_path = True

        if keep_watching_path:
            self.watcher.removePath(path)
            self.watcher.addPath(path)
        else:
            self.watcher.removePath(path)

    def has_logo_toggle_callback(self):
        if self.has_logo_toggle.isChecked():
            state = True
        else:
            state = False

        for sprite_slave in self.C_Sprites.logo.sprite_slaves_list:
            sprite_slave: QSpriteSlave
            if sprite_slave.tracked.type == SpriteType.LOGO and sprite_slave.zoomed_in == True:
                sprite_slave.toggle_zoom_in(True)

        self.C_Sprites.logo.toggle_visibility(state)
        self.export_logo.setEnabled(state)
        self.song_farc_creator.main_box.logo_checkbox.setEnabled(state)
        self.song_farc_creator.main_box.logo_checkbox.setChecked(state)
        if self.main_box.current_sprite_combobox.currentText() == "Logo":
            self.main_box.load_image_button.setEnabled(state)
            self.main_box.flip_vertical_button.setEnabled(state)
            self.main_box.flip_horizontal_button.setEnabled(state)



    def load_new_sprite_image(self,sprite):
        sprite_object = None
        match sprite:
            case "Background":
                sprite_object = self.C_Sprites.background
            case "Jacket":
                sprite_object = self.C_Sprites.jacket
            case "Thumbnail":
                sprite_object = self.C_Sprites.thumbnail
            case "Logo":
                sprite_object = self.C_Sprites.logo

        image_location = QFileDialog.getOpenFileName(self,
                                                 f"Open {sprite_object.type.value} image",
                                                 str(config.last_used_directory),
                                                 config.allowed_file_types)[0]
        if image_location == "":
            print("User didn't select image")
        else:
            config.last_used_directory = Path(image_location).parent
            ret= sprite_object.load_new_image(image_location)
            match ret[0]:
                case "Updated":
                    self.watcher.addPath(image_location)
                case "Image too small":
                    iw = ret[1]
                    ih = ret[2]
                    rw = ret[3]
                    rh = ret[4]

                    show_message_box(f"{sprite} image is too small.",
                                     f"Required image size for {sprite} is {rw}x{rh}.\n"
                                     f"Loaded image is {iw}x{ih}, ignoring transparent area.")


    def export_qimage_with_mask(self,qimage:QImage, mask:bytes, output_path:str):
        # TODO - This reeks of AI-Genned code. Delete unnecessary checks

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            if not qimage.save(temp_path):
                raise ValueError("Failed to save QImage to temporary file")

            with WImage(filename=temp_path) as img:
                with WImage(blob=mask) as mask_img:
                    if img.size != mask_img.size:
                        mask_img.resize(img.width, img.height)

                    img.composite(mask_img, operator='copy_alpha')

                    img.background_color = "rgb(255, 255, 255)"
                    img.compression = 'zip'
                    img.colorspace = 'srgb'

                    img.metadata['MegaMix Sprite Helper version'] = str(config.version)

                    img.save(filename=output_path)

        except Exception as e:
            print(f"Error during image processing: {str(e)}")
            raise
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def generate_spr_db_button_callback(self,path=None):
        spr_path = path
        if spr_path is False:
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
            print(f"Generated mod_spr_db in {spr_path}")

class SongFarcCreatorWindow(QWidget):
    def resizeEvent(self, event, /):
        self.scene_view.lock_in()
    def __init__(self):
        super(SongFarcCreatorWindow, self).__init__()
        self.main_box = Ui_SongFarcCreatorWindow()
        self.main_box.setupUi(self)

        self.main_box.export_farc_pushbutton.pressed.connect(self.export_background_jacket_logo_farc_button_callback)

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
        # scene_view.setBackgroundBrush(self.palette().color(QPalette.ColorRole.Window))
        self.scene_view.setBackgroundBrush(Qt.black)

        self.scene_view.setScene(scene)
        scene.layout_choose_layout = self.main_box.pv_back_layout_choose_layout
        scene.options_layout = self.main_box.pv_back_scene_option_layout
        scene.toggle_layout(PvBackLayout.MMSongSelect)
        scene.add_layouts_to_window()

        self.main_box.horizontalLayout.addWidget(self.scene_view)
    def export_background_jacket_logo_farc_button_callback(self):
        output_location = QFileDialog.getExistingDirectory(self, "Choose folder to save farc file to", str(config.last_used_directory))

        if output_location == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(output_location)

            bg_jk = Image.fromqimage(self.create_background_jacket_texture()).transpose(Image.Transpose.FLIP_TOP_BOTTOM)

            song_id = pad_number(int(self.main_box.farc_song_id_spinbox.value()))
            compression = self.main_box.compression_comboBox.currentEnum()
            print(compression)

            if self.main_box.logo_checkbox:
                logo = Image.fromqimage(self.create_logo_texture()).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            else:
                logo = None

            if self.main_box.pv_back_sprite_checkbox:
                pv_back_texture = Image.fromqimage(self.create_pv_back_texture()).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            else:
                pv_back_texture = None

            FarcCreator.create_jk_bg_logo_farc(song_id, bg_jk, logo, output_location,compression,pv_back_texture=pv_back_texture)


    def create_background_jacket_texture(self):
        main_window.C_Sprites.background.update_sprite(hq_output=True)
        main_window.C_Sprites.jacket.update_sprite(hq_output=True)

        background_jacket_texture = QImage(QSize(2048, 1024),QImage.Format.Format_ARGB32)
        background_jacket_texture.fill(Qt.GlobalColor.transparent)
        painter = QPainter(background_jacket_texture)
        painter.setRenderHint(QPainter.RenderHint.LosslessImageRendering)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.VerticalSubpixelPositioning)

        painter.drawPixmap(1,1,main_window.C_Sprites.background.pixmap().scaled(1282,722))
        painter.drawPixmap(2,2,main_window.C_Sprites.background.pixmap())
        painter.drawPixmap(1286, 2,main_window.C_Sprites.jacket.pixmap())
        painter.end()

        return background_jacket_texture
    def create_logo_texture(self):
        main_window.C_Sprites.logo.update_sprite(hq_output=True)

        logo = main_window.C_Sprites.logo.pixmap()
        logo_texture = QImage(QSize(1024, 512), QImage.Format.Format_ARGB32)
        logo_texture.fill(Qt.GlobalColor.transparent)
        painter = QPainter(logo_texture)
        painter.setRenderHint(QPainter.RenderHint.LosslessImageRendering)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.VerticalSubpixelPositioning)
        painter.drawPixmap(2,2,logo)
        painter.end()
        return logo_texture
    def create_thumbnail_texture(self) -> QImage:
        main_window.C_Sprites.thumbnail.update_sprite(hq_output=True)

        thumbnail = QPixmap(main_window.C_Sprites.thumbnail.pixmap_no_mask)
        thumbnail_texture = QImage(QSize(128, 64), QImage.Format.Format_RGBA8888)
        thumbnail_texture.fill(Qt.GlobalColor.transparent)
        painter = QPainter(thumbnail_texture)
        painter.setRenderHint(QPainter.RenderHint.LosslessImageRendering)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.VerticalSubpixelPositioning)
        painter.drawPixmap(0, 0, thumbnail)
        painter.end()
        return thumbnail_texture
    def create_pv_back_texture(self):
        main_window.C_Sprites.background.update_sprite(hq_output=True)
        main_window.C_Sprites.jacket.update_sprite(hq_output=True)
        main_window.C_Sprites.logo.update_sprite(hq_output=True)



        pv_back_texture = QImage(QSize(2048, 1024), QImage.Format.Format_ARGB32)
        pv_back_texture.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pv_back_texture)
        painter.setRenderHint(QPainter.RenderHint.LosslessImageRendering)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.VerticalSubpixelPositioning)

        self.scene_view.scene().render(painter, target=QRectF(1, 1, 1282, 722))
        self.scene_view.scene().render(painter, target=QRectF(2, 2, 1280, 720))

        painter.end()

        return pv_back_texture
    def export_background_jacket_button_callback(self):
        save_location = QFileDialog.getSaveFileName(self, "Save File",str(config.last_used_directory)+"/Background Texture.png","Images (*.png)")[0]

        if save_location == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(save_location).parent
            background_jacket_texture = self.create_background_jacket_texture()
            background_jacket_texture.save(save_location,"png")
    def export_thumbnail_button_callback(self):
        save_location = QFileDialog.getSaveFileName(self, "Save File", str(config.last_used_directory) + "/Thumbnail Texture.png", "Images (*.png)")[0]
        if save_location == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(save_location)
            thumbnail_texture = self.create_thumbnail_texture()
            file = QFile(":icon/Images/Dummy/Thumbnail-Maskv3.png")
            if not file.open(QIODevice.OpenModeFlag.ReadOnly):
                raise FileNotFoundError(f"Resource not found")

            data = file.readAll()
            file.close()
            mask = bytes(data)

            self.export_qimage_with_mask(thumbnail_texture,mask,save_location)
    def export_logo_button_callback(self):
        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Save Image",
            str(config.last_used_directory) + "/Logo Texture.png",
            "PNG Files (*.png)"
        )
        if filename == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(filename).parent
            logo_texture = self.create_logo_texture()
            logo_texture.save(filename, "png")


if __name__ == "__main__":
    config = Configurable()
    FarcCreator = FarcCreator()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = MainWindow()
    main_window.show()
    kkdlib.txp.init_wgpu()
    app.exec()