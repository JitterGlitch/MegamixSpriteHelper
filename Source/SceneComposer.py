import io
import math
from enum import Enum, auto, StrEnum
from pathlib import Path
from typing import Callable

import PIL
import PySide6
import hashlib
from PIL import Image
from PySide6.QtCore import Qt, QRectF, QPoint, Signal, QObject, QSize, QRect, QIODevice, QFile, QThread, QFileSystemWatcher, QTimer
from PySide6.QtGui import QImage, QPixmap, QPainter, QTransform, QColor, QPen
from PySide6.QtWidgets import QGraphicsPixmapItem, QFileDialog, QGraphicsScene, QLayout, QGraphicsView, QWidget, QSpacerItem, QSizePolicy, QScrollArea, QCheckBox, QRadioButton, QLabel

from widgets import EditableDoubleLabel, QSmarterMenu


class State(Enum):
    FALLBACK = auto()
    IMAGE_TOO_SMALL = auto()
    UPDATED = auto()

class SpriteType(StrEnum):
    JACKET = "Jacket"
    BACKGROUND = "Background"
    THUMBNAIL = "Thumbnail"
    LOGO = "Logo"

class SpriteSetting(StrEnum):
    HORIZONTAL_OFFSET = "Horizontal Offset"
    VERTICAL_OFFSET = "Vertical Offset"
    ROTATION = "Rotation"
    ZOOM = "Zoom"
    BRIGHTNESS = "Brightness"
class PvBackLayout(Enum):
    MMSongSelect = "Megamix Song Select"
    MMResult = "Megamix Result"
    FTResult = "Future Tone Result"
####################################################
def round_up(number, decimal_places):
    factor = 10 ** decimal_places
    return math.ceil(number * factor) / factor

def qimage_to_pil(img: QImage):
    ptr = img.constBits()
    if hasattr(ptr, 'asstring'):
        data = ptr.asstring(img.byteCount())
    else:
        data = bytes(ptr)
    pil_img = Image.frombuffer('RGBA', (img.width(), img.height()), data, 'raw', 'BGRA', 0, 1)
    return pil_img

def get_transparent_edge_pixels(image):

    pil_img = qimage_to_pil(image)

    if pil_img.mode != 'RGBA':
        pil_img = pil_img.convert('RGBA')

    alpha = pil_img.getchannel('A')

    bbox = alpha.getbbox()

    if bbox is None:
        edges = {
            "Top": 0,
            "Bottom": 0,
            "Left": 0,
            "Right": 0
        }
        return edges

    left, upper, right, lower = bbox
    width, height = pil_img.size

    edges = {
        "Top": upper,
        "Bottom": height - lower,
        "Left": left,
        "Right": width - right
    }
    return edges

def get_real_image_area(image:QImage) -> QRect:
    t_edges = get_transparent_edge_pixels(image)
    image_rect = image.rect()
    adjusted_rect = image_rect.adjusted(t_edges["Left"],t_edges["Top"],-t_edges["Right"],-t_edges["Bottom"])
    return adjusted_rect

def compute_file_hash(file_path):
    hash_func = hashlib.new('md5')
    if not file_path.startswith(":"):
        if Path(file_path).exists():
            with open(file_path, 'rb') as file:
                while chunk := file.read(8192):
                    hash_func.update(chunk)
            return hash_func.hexdigest()

    return None

######################################################
class QScalingGraphicsScene(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.zoomed_in = False
        self.center_on = None
        self.size = 2.15
        self.forced_size = None
    def resizeEvent(self,event):
        self.lock_in()

    def wheelEvent(self, event, /):
        event.ignore()

    def get_available_geometry(self):
        first = self.parentWidget()
        p = first
        while p:
            if isinstance(p, QScrollArea):
                return p.viewport().contentsRect()
            p = p.parentWidget()
        return first.contentsRect()
    def set_forced_size(self,size:QSize):
        self.forced_size = size

    def lock_in(self):
        if self.forced_size:
            self.setMinimumSize(self.forced_size)
            self.setMaximumSize(self.forced_size)
        else:
            min_width = self.get_available_geometry().width() / 16

            self.setMaximumSize(QSize(min_width * 16 / self.size, min_width * 9 / self.size))
            self.setMinimumSize(QSize(min_width * 16 / self.size, min_width * 9 / self.size))

        if not self.zoomed_in:
            self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        else:
            self.fitInView(0, 0, self.scene().width() / 2, self.scene().height() / 2, Qt.AspectRatioMode.KeepAspectRatio)
            self.centerOn(self.center_on)

def qresource_to_bytes(location):
    file = QFile(location)
    if not file.exists():
        raise FileNotFoundError(f"Resource {location} not found")

    if file.open(QIODevice.ReadOnly):
        data = file.readAll()
        file.close()

        image_data = bytes(data)
        return io.BytesIO(image_data)
    else:
        raise IOError(f"Cannot open resource {location}")

class PathWatcher(QThread):
    ImageLocationUpdate = Signal(str)
    def __init__(self,C_Sprites):
        super().__init__()
        self.C_Sprites = C_Sprites

        self.timer = QTimer()
        self.timer.timeout.connect(self.manual_file_update_check)
        self.timer.start(1000)

    def manual_file_update_check(self):
        for sprite in self.C_Sprites.list:
            if sprite.location is str:
                new_image_hash = compute_file_hash(sprite.location)
                if new_image_hash is None:
                    continue
                if not new_image_hash == sprite.hash:
                    print("Manual Image check detected change in " + sprite.type)
                    sprite.hash = new_image_hash
                    sprite.load_new_image(sprite.location, fallback=True,reset_values=False)
            else:
                continue

class QSpriteBase(QGraphicsPixmapItem, QObject):
    SpriteUpdated = Signal()
    def __init__(self,
                 sprite:str,
                 sprite_type:SpriteType,
                 size:PySide6.QtCore.QRectF,
                 scale:float=None,
                 offset:QPoint=QPoint(0,0)):
        QObject.__init__(self)
        QGraphicsPixmapItem.__init__(self)
        #Set default image and fallback dummy.
        self.dummy_location = sprite
        self.location = sprite
        self.sprite_size = size
        self.hash = compute_file_hash(sprite)
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.offset=offset
        if scale:
            self.setScale(scale)

        self.controls_enabled = True
        self.sprite_image = QImage(self.location)
        self.t_edges = get_transparent_edge_pixels(self.sprite_image)
        self.rect = get_real_image_area(self.sprite_image)
        self.x = 0
        self.y = 0

        self.sprite_slaves_list = []


        #Create a scene that will crop image to max size
        self.sprite = QGraphicsPixmapItem()
        self.sprite.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.sprite.setPixmap(QPixmap(self.sprite_image))
        self.sprite_scene = QGraphicsScene()
        self.sprite_scene.setSceneRect(self.sprite_size)
        self.sprite_scene.addItem(self.sprite)

        self.type = sprite_type


        self.sprite_settings = [
            (SpriteSetting.HORIZONTAL_OFFSET, {
                'initial_value': 0,
                'decimals': 0,
                'rough_step': 1,
                'precise_step': 1
            }),
            (SpriteSetting.VERTICAL_OFFSET, {
                'initial_value': 0,
                'decimals': 0,
                'rough_step': 1,
                'precise_step': 1
            }),
            (SpriteSetting.ROTATION, {
                'initial_value': 0,
                'decimals': 0,
                'rough_step': 1,
                'precise_step': 1
            }),
            (SpriteSetting.ZOOM, {
                'initial_value': 1,
                'decimals': 3,
                'rough_step': 0.001,
                'precise_step': 0.001
            }),
            (SpriteSetting.BRIGHTNESS, {
                'initial_value': 100,
                'decimals': 0,
                'rough_step': 1,
                'precise_step': 1
            }),
        ]
        self.flipped_h = False
        self.flipped_v = False
        self.is_visible = True
        self.initial_calc = True
        self.last_value = {}
        self.edit_controls = self.create_edit_controls()

        self.update_sprite()

        self.edit_controls[SpriteSetting.ZOOM.value].setValue(self.edit_controls[SpriteSetting.ZOOM.value].spinbox.maximum())
        self.edit_controls[SpriteSetting.BRIGHTNESS.value].setValue(self.edit_controls[SpriteSetting.BRIGHTNESS.value].spinbox.maximum())

        if self.type == SpriteType.THUMBNAIL:
            print(self.t_edges)
            print(self.rect)

    def create_edit_controls(self) -> dict[Callable[[], str], EditableDoubleLabel]:
        editable_values = {}
        for setting in self.sprite_settings:
            parameters = setting[1]
            edit = EditableDoubleLabel(sprite=self,
                                       setting=setting[0],
                                       range=self.calculate_range(setting[0],self.rect),
                                       **parameters)
            edit.editingFinished.connect(self.update_sprite)
            editable_values[setting[0].value] = edit
        return editable_values

    def add_edit_controls_to(self,layout:QLayout):
        for control in self.edit_controls:
            layout.addWidget(self.edit_controls[control])

        verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(verticalSpacer)

    def grab_scene_portion(self,scene:QGraphicsScene, source_rect:QRectF) -> QPixmap:
        pixmap = QPixmap(source_rect.size().toSize())
        pixmap.fill("transparent")

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        scene.render(painter, QRectF(pixmap.rect()), source_rect)
        painter.end()

        return pixmap

    def calculate_range(self,sprite_setting,rect):
        match sprite_setting:
            case SpriteSetting.HORIZONTAL_OFFSET:
                area_over_req_size = rect.width() - self.required_size().width()

                if area_over_req_size > 0:
                    return -area_over_req_size-self.x+self.offset.x(), -self.x-self.offset.x()

                else:
                    return -self.offset.x(),-self.offset.x()

            case SpriteSetting.VERTICAL_OFFSET:
                area_over_req_size = rect.height() - self.required_size().height()

                if area_over_req_size > 0:
                    return -area_over_req_size-self.y-self.offset.y(), -self.y-self.offset.y()

                else:
                    return -self.offset.y(),-self.offset.y()

            case SpriteSetting.ZOOM:
                if self.required_size() == QSize(0,0):
                    return 0.10,1.00
                if self.sprite_image.width() == 0:
                    return 1.00,1.00
                if self.sprite_image.height() == 0:
                    return 1.00,1.00

                width_factor = self.required_size().width() / (self.sprite_image.width()-self.t_edges["Left"]-self.t_edges["Right"])
                height_factor = self.required_size().height() / (self.sprite_image.height()-self.t_edges["Left"]-self.t_edges["Right"])

                image_w = (self.sprite_image.size() * width_factor)
                image_h = (self.sprite_image.size() * height_factor)

                image_w_pass = False
                image_h_pass = False

                if image_w.width() >= self.required_size().width() and image_w.height() >= self.required_size().height():
                    image_w_pass = True
                if image_h.width() >= self.required_size().width() and image_h.height() >= self.required_size().height():
                    image_h_pass = True

                if image_w_pass and image_h_pass:
                    image_w_area = image_w.width() * image_w.height()
                    image_h_area = image_h.width() * image_h.height()

                    if image_w_area >= image_h_area:
                        return round_up(width_factor,3), 1.00
                    else:
                        return round_up(height_factor,3), 1.00
                elif image_w_pass:
                    return round_up(width_factor,3), 1.00
                else:
                    return round_up(height_factor,3),1.00

            case SpriteSetting.ROTATION:
                return -360,0
            case SpriteSetting.BRIGHTNESS:
                return 50,100

    def required_size(self) -> QSize:
        return self.sprite_size.size().toSize()

    def update_all_ranges(self,rect):
        for setting in self.edit_controls:
            self.edit_controls[setting].set_range(self.calculate_range(setting,rect))
    def load_new_image(self,image_location,fallback=False,reset_values=True):
        qimage =QImage(image_location)
        required_size = self.required_size()

        rw = required_size.width()
        rh = required_size.height()
        w = qimage.width()
        h = qimage.height()
        trans_edges = get_transparent_edge_pixels(qimage)

        if w-trans_edges["Left"] == 0: #Check if image is fully transparent
            iw = 0
            ih = 0
        else:
            iw = w-trans_edges["Left"]-trans_edges["Right"]
            ih = h-trans_edges["Top"]-trans_edges["Bottom"]

        if (iw, ih ) < (rw, rh):
            if fallback:
                print(f"Image for {self.type.value} is no longer meeting minimum required size. Falling back to dummy image.")
                print(f"Real Image size is {iw}x{ih}")
                self.location = self.dummy_location
                self.sprite_image = QImage(self.location)
                return ["Fallback" , iw,ih,rw,rh]
            else:
                print(f"Chosen image for {self.type.value} is too small. It's size is {iw,ih}")
                print(f"Required size for the sprite is {rw,rh}")
                return ["Image too small",iw,ih,rw,rh]
        else:
            self.update_location(image_location)
            self.sprite_image = qimage
            self.hash = compute_file_hash(image_location)

        self.t_edges = get_transparent_edge_pixels(self.sprite_image)
        self.rect = get_real_image_area(self.sprite_image)
        self.x = 0
        self.y = 0


        self.initial_calc = True
        self.last_value = {}
        self.update_all_ranges(self.rect)

        self.update_sprite()
        if reset_values:
            self.set_initial_values()

        if self.type == SpriteType.THUMBNAIL:
            print(self.t_edges)
            print(self.rect)
        return ["Updated"]
    def bind_watcher(self,watcher:PathWatcher):
        self.watcher = watcher
    def update_location(self,image_location):
        print("Updating location")
        self.location = image_location
        self.watcher.ImageLocationUpdate.emit(self.location)
    def update_sprite(self,hq_output=False):
        zoom = self.edit_controls[SpriteSetting.ZOOM.value].value
        zoom_inverse = 1/zoom
        horizontal_offset = self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].value
        vertical_offset = self.edit_controls[SpriteSetting.VERTICAL_OFFSET.value].value
        rotation = self.edit_controls[SpriteSetting.ROTATION.value].value
        brightness = self.edit_controls[SpriteSetting.BRIGHTNESS.value].value
        image_size = self.sprite_image

        result = QImage(self.sprite_size.size().toSize(), QImage.Format.Format_ARGB32)
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)
        painter.setRenderHints(QPainter.RenderHint.LosslessImageRendering,)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.VerticalSubpixelPositioning)

        t_ns = QTransform()
        t_ns.translate(horizontal_offset, vertical_offset)
        t_ns.translate((image_size.width() / 2), (image_size.height() / 2))
        t_ns.rotate(rotation)
        t_ns.translate(-(image_size.width() / 2), -(image_size.height() / 2))

        t_s = QTransform()
        t_s.translate(horizontal_offset, vertical_offset)
        t_s.translate((image_size.width() / 2), (image_size.height() / 2))
        t_s.rotate(rotation)
        t_s.translate(-(image_size.width() / 2), -(image_size.height() / 2))
        t_s.scale(zoom, zoom)


        if hq_output:
            if isinstance(self.location, str):
                if self.location.startswith(":"):
                    self.location = qresource_to_bytes(self.location)
            with Image.open(self.location) as image:
                width = int(image_size.width() * zoom)
                height = int(image_size.height() * zoom)
                drawn_image = image.resize((width,height),Image.Resampling.LANCZOS).toqimage()

            painter.setTransform(t_ns,combine=False)
            if self.is_visible:
                painter.drawPixmap(0 + self.offset.x(), 0 + self.offset.y(), QPixmap(drawn_image))
        else:
            painter.setTransform(t_s, combine=False)
            drawn_image = QPixmap(self.sprite_image)
            if self.is_visible:
                painter.drawPixmap(0 + self.offset.x()*zoom_inverse, 0 + self.offset.y()*zoom_inverse, QPixmap(drawn_image))


        transformed_rect = t_s.mapRect(self.rect)

        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
        painter.setOpacity((100-brightness)/100)
        painter.fillRect(0 + self.offset.x(), 0 + self.offset.y(), image_size.width(), image_size.height(),
                         QColor(0, 0, 0))

        painter.end()

        self.x = int(transformed_rect.x()) - horizontal_offset
        self.y = int(transformed_rect.y()) - vertical_offset

        self.sprite.setPixmap(QPixmap(self._apply_flips(result)))
        self.update_pixmap()

        recalculate_offsets = False

        if self.initial_calc:
            for setting in self.edit_controls:
                self.last_value[setting] = self.edit_controls[setting].value

            self.update_all_ranges(transformed_rect)
            self.initial_calc = False
        else:
            for setting in self.last_value:
                if self.edit_controls[setting].value != self.last_value[setting]:
                    if setting in ["Horizontal Offset" , "Vertical Offset"]:
                        continue
                    else:
                        recalculate_offsets = True
                        break

        if recalculate_offsets:
            self.update_all_ranges(transformed_rect)
            for setting in self.edit_controls:
                self.last_value[setting] = self.edit_controls[setting].value

        self.SpriteUpdated.emit()
    def set_initial_values(self):
        for setting in self.edit_controls:
            self.edit_controls[setting].setValue(self.edit_controls[setting].range[1])
        self.update_sprite()
    def _apply_flips(self,image:QImage):
        if self.flipped_h:
            image.flip(Qt.Orientation.Horizontal)
        if self.flipped_v:
            image.flip(Qt.Orientation.Vertical)
        return image
    def toggle_flip(self,flip_type):
        match flip_type:
            case Qt.Orientation.Vertical:
                self.flipped_v = not self.flipped_v
            case Qt.Orientation.Horizontal:
                self.flipped_h = not self.flipped_h

        self.update_sprite()
    def toggle_visibility(self,state):
        self.is_visible = state
        self.update_sprite()
        for setting in self.edit_controls:
            self.edit_controls[setting].setEnabled(state)
        self.controls_enabled = state
        self.SpriteUpdated.emit()

    def update_pixmap(self):
        self.setPixmap(self.grab_scene_portion(self.sprite_scene, self.sprite_size))

    def mousePressEvent(self, event, /):
        self.save_image()

        super().mousePressEvent(event)

    def save_image(self):
        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Save Image",
            "image.png",
            "PNG Files (*.png)"
        )
        if filename:
            self.pixmap().save(filename, "PNG",100)
            print(f"Image saved to: {filename}")
class QThumbnail(QSpriteBase):
    def __init__(self,
                 sprite: str,
                 size: PySide6.QtCore.QRectF,
                 mask: str):

        self.sprite_mask = QImage(mask)
        super().__init__(sprite,SpriteType.THUMBNAIL,size,offset=QPoint(28,1))

    def required_size(self) -> QSize:
        return QSize(100,61)

    def apply_mask_to_pixmap(self, pixmap:QPixmap) -> QPixmap:
        result_pixmap = QPixmap(self.sprite.pixmap().size())
        result_pixmap.fill("transparent")  # This prevents ghost images from showing up

        painter = QPainter(result_pixmap)
        painter.setRenderHint(QPainter.RenderHint.LosslessImageRendering)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.VerticalSubpixelPositioning)

        painter.drawPixmap(0, 0, pixmap)

        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)

        painter.drawImage(0, 0, self.sprite_mask)
        painter.end()

        return result_pixmap

    def update_pixmap(self):
        self.pixmap_no_mask = self.grab_scene_portion(self.sprite_scene, self.sprite_size)
        self.setPixmap(self.apply_mask_to_pixmap(self.pixmap_no_mask))
class QJacket(QSpriteBase):
    def __init__(self,sprite: str,
                 size: PySide6.QtCore.QRectF):
        super().__init__(sprite,SpriteType.JACKET,size)

    def apply_fix(self,image:QImage) -> QImage:
        w = image.width()
        h = image.height()
        image_s = image

        image_fix = QImage(QSize(502,502), QImage.Format.Format_ARGB32)
        image_fix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image_fix)
        painter.setOpacity(50 / 255)
        painter.drawImage(0,0,image_s.scaled(w+2, h+2))
        painter.setOpacity(255)
        painter.drawImage(1,1,image)
        painter.end()

        return image_fix

    def required_size(self) -> QSize:
        return QSize(500,500)

    def set_initial_values(self):
        self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].setValue(self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].range[1])
        self.edit_controls[SpriteSetting.VERTICAL_OFFSET.value].setValue(self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].range[1])
        self.edit_controls[SpriteSetting.ROTATION.value].setValue(0)

        if self.sprite_image.size().width() / self.sprite_image.size().height() == 1:
            self.edit_controls[SpriteSetting.ZOOM.value].setValue(self.edit_controls[SpriteSetting.ZOOM.value].range[0])
        else:
            self.edit_controls[SpriteSetting.ZOOM.value].setValue(self.edit_controls[SpriteSetting.ZOOM.value].range[1])

    def update_pixmap(self):
        print(self.sprite_size)
        self.image_without_fix = (self.grab_scene_portion(self.sprite_scene,QRectF(0.000000, 0.000000, 500.000000, 500.000000)).toImage())
        print(self.image_without_fix.size())
        self.setPixmap(QPixmap(self.apply_fix(self.image_without_fix)))
class QBackground(QSpriteBase):
    def __init__(self,sprite,size):
        super().__init__(sprite,SpriteType.BACKGROUND,size)

    def required_size(self) -> QSize:
        return QSize(1280,720)
class QLogo(QSpriteBase):
    def __init__(self,sprite,size):
        super().__init__(sprite,SpriteType.LOGO,size)
    def required_size(self) -> QSize:
        return QSize(1,1)





    def calculate_range(self,sprite_setting:SpriteSetting,rect):

        match sprite_setting:
            case SpriteSetting.HORIZONTAL_OFFSET:
                space = self.sprite_size.size().width() - rect.width()
                #need to split this value based on area available on different sides

                if space > 0:
                    return (-self.x-self.offset.x(),
                            -self.x-self.offset.x()+space)

                else:
                    return (-self.offset.x()+(space/2),
                            -self.offset.x()-(space/2))

            case SpriteSetting.VERTICAL_OFFSET:
                space =  self.sprite_size.size().height() - rect.height()

                if space > 0:
                    return (-self.y-self.offset.y(),
                            -self.y-self.offset.y()+space)

                else:
                    return (-self.offset.y()+(space/2),
                            -self.offset.y()-(space/2))

            case SpriteSetting.ZOOM:

                width_factor = self.sprite_size.size().width() / self.sprite_image.width()
                height_factor = self.sprite_size.size().height() / self.sprite_image.height()

                #TODO Round it up to number of decimals specified in sprite settings
                if width_factor > 1:
                    width_factor = 1
                if height_factor > 1:
                    height_factor = 1

                if width_factor > height_factor:
                    return 0.01,round_up(width_factor,3)
                elif width_factor < height_factor:
                    return 0.01,round_up(height_factor,3)
                else:
                    return 0.01,round_up(height_factor,3)
            case SpriteSetting.ROTATION:
                return -360,0
            case SpriteSetting.BRIGHTNESS:
                return 50, 100

    def set_initial_values(self):
        hor_range = self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].range
        hor_center = (hor_range[1] + hor_range[0]) / 2

        ver_range = self.edit_controls[SpriteSetting.VERTICAL_OFFSET.value].range
        ver_center = (ver_range[1]+ver_range[0])/2

        self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].setValue(hor_center)
        self.edit_controls[SpriteSetting.VERTICAL_OFFSET.value].setValue(ver_center)
        self.edit_controls[SpriteSetting.ZOOM.value].setValue(self.edit_controls[SpriteSetting.ZOOM.value].range[1])
        self.edit_controls[SpriteSetting.ROTATION.value].setValue(0)
        self.edit_controls[SpriteSetting.BRIGHTNESS.value].setValue(100)

class QSpriteSlave(QGraphicsPixmapItem):

    def __init__(self, tracked: QSpriteBase, position: QPoint,scale:float=None,rotation:int=None,brightness:int=None):
        super().__init__()
        self.tracked = tracked
        self.tracked.SpriteUpdated.connect(self.update_sprite)
        self.tracked.sprite_slaves_list.append(self)
        self.rotation = rotation
        self.scale = scale
        self.brightness = brightness
        self.setPos(position)
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.zoomed_in = False
        self._hovered = False
        if not self.tracked.type == SpriteType.BACKGROUND:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setAcceptHoverEvents(True)




        self.update_sprite()


    def hoverEnterEvent(self, event):
        self._hovered = True
        self.update_sprite()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._hovered = False
        self.update_sprite()
        super().hoverLeaveEvent(event)

    def update_sprite(self):
        self.setPixmap(self.tracked.pixmap())
        if self.scale:
            self.setScale(self.scale)

        result = self.tracked.pixmap()
        painter = QPainter(result)

        if self.brightness:
            painter.save()
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
            painter.setOpacity((100 - self.brightness) / 100)
            painter.fillRect(0 , 0, self.tracked.sprite_image.width()+300, self.tracked.sprite_image.height()+300,
                             QColor(0, 0, 0))
            painter.restore()

        if self._hovered:
            painter.save()
            pen = QPen(QColor("yellow"), 10, Qt.SolidLine)
            painter.setPen(pen)
            rect = self.boundingRect()
            painter.drawRect(rect.adjusted(3, 3, -3, -3))
            painter.drawRect(rect)
            painter.restore()

        self.setPixmap(result)
        painter.end()

        if self.rotation:
            image = self.pixmap().toImage()
            transform = QTransform().rotate(self.rotation)
            image = image.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(QPixmap(image))
    def toggle_zoom_in(self,state):
        if not self.tracked.type == SpriteType.BACKGROUND:
            if not state:
                view: QScalingGraphicsScene
                for view in self.scene().views():
                    view.center_on = self
                    view.zoomed_in = True
                    self.zoomed_in = True
                    view.lock_in()
            else:
                for view in self.scene().views():
                    view.center_on = None
                    view.zoomed_in = False
                    self.zoomed_in = False
                    view.lock_in()
    def mousePressEvent(self,event):
        self.toggle_zoom_in(self.zoomed_in)
class QLayer(QGraphicsPixmapItem):
    def __init__(self,
                 sprite: str,
                 size: PySide6.QtCore.QRectF = QRectF(0,0,1920,1080),
                 scale:float=1,
                 brightness:int=None,
                 opacity:int=None):
        super().__init__()
        self.sprite = QPixmap(sprite)
        self.sprite_size = size
        self.setPixmap(QPixmap(sprite))
        self.brightness = brightness
        self.opacity = opacity

        self.update_sprite()

        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.setScale(scale)
    def update_sprite(self):
        result = QImage(self.sprite_size.size().toSize(), QImage.Format.Format_ARGB32)
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)

        if self.opacity:
            painter.setOpacity(self.opacity / 100)

        painter.drawPixmap(QPoint(0, 0), self.sprite)

        if self.brightness:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
            painter.setOpacity((100 - self.brightness) / 100)
            painter.fillRect(0, 0, self.pixmap().width(), self.pixmap().height(), QColor(0, 0, 0))

        painter.end()
        self.setPixmap(QPixmap(result))

class QControllableSprites:
    def __init__(self):
        self.thumbnail = QThumbnail(u":icon/Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png",
                                      QRectF(0, 0, 128, 64),
                                      u":icon/Images/Dummy/Thumbnail-Maskv3.png")

        self.logo = QLogo(u":icon/Images/Dummy/SONG_LOGO_DUMMY.png",
                            QRectF(0, 0, 870, 330))
        self.jacket = QJacket(u":icon/Images/Dummy/SONG_JK_DUMMY.png",
                                QRectF(0, 0, 502, 502))
        self.background = QSpriteBase(u":icon/Images/Dummy/SONG_BG_DUMMY.png",
                                        SpriteType.BACKGROUND,
                                        QRectF(0, 0, 1280, 720))

        self.list = [self.thumbnail,self.logo,self.jacket,self.background]
        self.sprite_updater = PathWatcher(self)

        for sprite in self.list:
            sprite.bind_watcher(self.sprite_updater)

class QMMSongSelectScene(QGraphicsScene):
    def __init__(self,jacket:QJacket, logo:QLogo, background:QSpriteBase, thumbnail:QThumbnail):
        super().__init__()
        self.name = "MegaMix Song Select"

        #####
        self.jacket = QSpriteSlave(jacket, QPoint(1284, 130), rotation=7)
        self.logo = QSpriteSlave(logo, QPoint(825, 537), scale=0.8)
        self.background = QSpriteSlave(background,QPoint(0,0), scale=1.50)
        self.thumbnail_1 = QSpriteSlave(thumbnail, QPoint(-98, -24), scale=1.25)
        self.thumbnail_2 = QSpriteSlave(thumbnail, QPoint(-66, 90), scale=1.25)
        self.thumbnail_3 = QSpriteSlave(thumbnail, QPoint(-34, 204), scale=1.25)
        self.thumbnail_selected = QSpriteSlave(thumbnail, QPoint(-8, 332), scale=1.578125)
        self.thumbnail_4 = QSpriteSlave(thumbnail, QPoint(44, 476), scale=1.25)
        self.thumbnail_5 = QSpriteSlave(thumbnail, QPoint(108, 704), scale=1.25)
        self.thumbnail_6 = QSpriteSlave(thumbnail, QPoint(140, 818), scale=1.25)
        self.thumbnail_7 = QSpriteSlave(thumbnail, QPoint(168, 948), scale=1.25)
        ######
        self.backdrop = QLayer(u":icon/Images/MM UI - Song Select/Backdrop.png")
        self.song_selector = QLayer(u":icon/Images/MM UI - Song Select/Song Selector.png")
        self.middle_layer = QLayer(u":icon/Images/MM UI - Song Select/Middle Layer.png")
        self.top_layer_nc = QLayer(u":icon/Images/MM UI - Song Select/Top Layer - New Classics.png")
        self.top_layer = QLayer(u":icon/Images/MM UI - Song Select/Top Layer.png")
        ######
        self.setSceneRect(0, 0, 1920, 1080)
        self.setBackgroundBrush(Qt.GlobalColor.black)

        self.addItem(self.backdrop)
        self.addItem(self.background)
        self.addItem(self.jacket)
        self.addItem(self.middle_layer)
        self.addItem(self.logo)
        self.addItem(self.song_selector)
        self.addItem(self.thumbnail_1)
        self.addItem(self.thumbnail_2)
        self.addItem(self.thumbnail_3)
        self.addItem(self.thumbnail_selected)
        self.addItem(self.thumbnail_4)
        self.addItem(self.thumbnail_5)
        self.addItem(self.thumbnail_6)
        self.addItem(self.thumbnail_7)
        self.addItem(self.top_layer_nc)
        self.addItem(self.top_layer)

        self.top_layer.setVisible(False)

        self.scene_config_menu = QSmarterMenu(self.name)
        self.show_ui_toggle = self.scene_config_menu.addAction("Show UI")
        self.show_ui_toggle.setCheckable(True)
        self.show_ui_toggle.setChecked(True)
        self.show_ui_toggle.toggled.connect(self.toggle_ui)

    def toggle_new_classics(self,state:bool):
        self.top_layer.setVisible(not state)
        self.top_layer_nc.setVisible(state)

    def toggle_ui(self,state:bool):
        self.top_layer.setVisible(state)
        self.song_selector.setVisible(state)
        self.thumbnail_1.setVisible(state)
        self.thumbnail_2.setVisible(state)
        self.thumbnail_3.setVisible(state)
        self.thumbnail_4.setVisible(state)
        self.thumbnail_5.setVisible(state)
        self.thumbnail_6.setVisible(state)
        self.thumbnail_7.setVisible(state)
        self.thumbnail_selected.setVisible(state)

class QMMResultScene(QGraphicsScene):
    def __init__(self,jacket:QJacket, logo:QLogo, background:QSpriteBase):
        super().__init__()
        self.name = "MegaMix Results"

        #####
        self.jacket = QSpriteSlave(jacket, QPoint(108, 387), rotation=7, scale=0.9)
        self.logo = QSpriteSlave(logo, QPoint(67, 784), scale=0.7)
        self.background = QSpriteSlave(background,QPoint(0,0), scale=1.50)
        ######
        self.backdrop = QLayer(u":icon/Images/Dummy/SONG_BG_DUMMY.png",scale=1.5)
        self.middle_layer_jacket_shadow = QLayer(u":icon/Images/MM UI - Results Screen/Middle Layer - Jacket Shadow.png")
        self.middle_layer_song_credit = QLayer(u":icon/Images/MM UI - Results Screen/Middle Layer - Song Credit.png")
        self.top_layer_nc = QLayer(u":icon/Images/MM UI - Results Screen/Top Layer - New Classics.png")
        self.top_layer = QLayer(u":icon/Images/MM UI - Results Screen/Top Layer.png")
        ######
        self.setSceneRect(0, 0, 1920, 1080)
        self.setBackgroundBrush(Qt.GlobalColor.black)

        self.addItem(self.backdrop)
        self.addItem(self.background)
        self.addItem(self.middle_layer_jacket_shadow)
        self.addItem(self.middle_layer_song_credit)
        self.addItem(self.jacket)
        self.addItem(self.logo)
        self.addItem(self.top_layer_nc)
        self.addItem(self.top_layer)

        self.top_layer.setVisible(False)

        self.scene_config_menu = QSmarterMenu(self.name)
        self.show_ui_toggle = self.scene_config_menu.addAction("Show UI")
        self.show_ui_toggle.setCheckable(True)
        self.show_ui_toggle.setChecked(True)
        self.show_ui_toggle.toggled.connect(self.toggle_ui)

    def toggle_new_classics(self, state):
        self.top_layer.setVisible(not state)
        self.top_layer_nc.setVisible(state)

    def toggle_ui(self,state:bool):
        self.middle_layer_song_credit.setVisible(state)
        self.top_layer.setVisible(state)
class QMMPractiseModeScene(QGraphicsScene):
    def __init__(self,jacket:QJacket, logo:QLogo, background:QSpriteBase):
        super().__init__()
        self.name = "MegaMix Practise Mode"
        brightness = 40
        ######
        self.jacket = QSpriteSlave(jacket, QPoint(1294, 147), rotation=7, brightness=brightness)
        self.logo = QSpriteSlave(logo, QPoint(739, 508), brightness=brightness)
        self.background = QSpriteSlave(background, QPoint(0, 0), scale=1.50, brightness=brightness)
        #####
        #TODO - Finish UI
        #TODO - Add methods to toggle elements of UI
        # Rendering should have options to choose what is visible

        self.grid = QLayer(u":icon/Images/MM UI - Practise Mode/Grid.png",opacity=25)
        self.jacket_shadow = QLayer(u":icon/Images/MM UI - Practise Mode/Jacket Shadow.png")
        self.top_layer = QLayer(u":icon/Images/MM UI - Practise Mode/UI.png")
        #####
        self.setSceneRect(0,0,1920,1080)
        self.setBackgroundBrush(Qt.GlobalColor.black)

        self.addItem(self.background)
        self.addItem(self.jacket)
        self.addItem(self.jacket_shadow)
        self.addItem(self.logo)
        self.addItem(self.grid)
        self.addItem(self.top_layer)

        self.scene_config_menu = QSmarterMenu(self.name)
        self.show_ui_toggle = self.scene_config_menu.addAction("Show UI")
        self.show_ui_toggle.setCheckable(True)
        self.show_ui_toggle.setChecked(True)
        self.show_ui_toggle.toggled.connect(self.toggle_ui)

        self.show_grid_toggle = self.scene_config_menu.addAction("Show grid")
        self.show_grid_toggle.setCheckable(True)
        self.show_grid_toggle.setChecked(True)
        self.show_grid_toggle.toggled.connect(self.toggle_grid)

    def toggle_ui(self,state:bool):
        self.top_layer.setVisible(state)
    def toggle_grid(self,state:bool):
        self.grid.setVisible(state)


class QFTSongSelectScene(QGraphicsScene):
    def __init__(self,jacket:QJacket, logo:QLogo, background:QSpriteBase):
        super().__init__()
        self.name = "Future Tone Song Select"
        #####
        self.jacket = QSpriteSlave(jacket, QPoint(1331, 205), rotation=-5 ,scale=0.97)
        self.logo = QSpriteSlave(logo, QPoint(803, 515), scale=0.9)
        self.background = QSpriteSlave(background,QPoint(0,0), scale=1.50)

        ######
        self.backdrop = QLayer(u":icon/Images/FT UI - Song Select/Base.png")
        self.middle_layer = QLayer(u":icon/Images/FT UI - Song Select/Middle Layer.png")
        self.top_layer_nc = QLayer(u":icon/Images/FT UI - Song Select/Top Layer - New Classics.png")
        self.top_layer = QLayer(u":icon/Images/FT UI - Song Select/Top Layer.png")
        ######
        self.setSceneRect(0, 0, 1920, 1080)
        self.setBackgroundBrush(Qt.GlobalColor.black)

        self.addItem(self.backdrop)
        self.addItem(self.background)
        self.addItem(self.middle_layer)
        self.addItem(self.jacket)
        self.addItem(self.logo)
        self.addItem(self.top_layer_nc)
        self.addItem(self.top_layer)

        self.top_layer.setVisible(False)

        self.scene_config_menu = QSmarterMenu(self.name)
        self.show_ui_toggle = self.scene_config_menu.addAction("Show UI")
        self.show_ui_toggle.setCheckable(True)
        self.show_ui_toggle.setChecked(True)
        self.show_ui_toggle.toggled.connect(self.toggle_ui)

    def toggle_new_classics(self, state):
        self.top_layer.setVisible(not state)
        self.top_layer_nc.setVisible(state)
    def toggle_ui(self,state:bool):
        self.top_layer.setVisible(state)
class QFTResultScene(QGraphicsScene):
    def __init__(self,jacket:QJacket, logo:QLogo):
        super().__init__()
        self.name = "Future Tone Results"

        #####
        self.jacket = QSpriteSlave(jacket, QPoint(164, 303), rotation=-5)
        self.logo = QSpriteSlave(logo, QPoint(134, 663), scale=0.75)
        ######
        self.backdrop = QLayer(u":icon/Images/FT UI - Results Screen/Base.png")
        self.middle_layer_jacket_shadow = QLayer(u":icon/Images/FT UI - Results Screen/Middle Layer - Jacket Shadow.png")
        self.middle_layer_song_credit = QLayer(u":icon/Images/FT UI - Results Screen/Middle Layer - Song Credit.png")
        self.top_layer_nc = QLayer(u":icon/Images/FT UI - Results Screen/Top Layer - New Classics.png")
        self.top_layer = QLayer(u":icon/Images/FT UI - Results Screen/Top Layer.png")

        ######
        self.setSceneRect(0, 0, 1920, 1080)
        self.setBackgroundBrush(Qt.GlobalColor.black)

        self.addItem(self.backdrop)
        self.addItem(self.middle_layer_song_credit)
        self.addItem(self.middle_layer_jacket_shadow)
        self.addItem(self.jacket)
        self.addItem(self.logo)
        self.addItem(self.top_layer_nc)
        self.addItem(self.top_layer)

        self.top_layer.setVisible(False)

        self.scene_config_menu = QSmarterMenu(self.name)
        self.show_ui_toggle = self.scene_config_menu.addAction("Show UI")
        self.show_ui_toggle.setCheckable(True)
        self.show_ui_toggle.setChecked(True)
        self.show_ui_toggle.toggled.connect(self.toggle_ui)

    def toggle_new_classics(self, state):
        self.top_layer.setVisible(not state)
        self.top_layer_nc.setVisible(state)
    def toggle_ui(self,state:bool):
        self.top_layer.setVisible(state)
        self.middle_layer_song_credit.setVisible(state)

class QPVBackScene(QGraphicsScene):
    def __init__(self,mm_song_select:QMMSongSelectScene,mm_result:QMMResultScene,ft_result:QFTResultScene,logo=None,jacket=None,background=None):
        super().__init__()
        self.name = "Pv Back Scene"

        self.mm_song_select_scene = mm_song_select
        self.ft_result_scene = ft_result
        self.mm_result_scene = mm_result

        self.layout_choose_layout = None
        self.options_layout = None


        self.background = QSpriteSlave(background,position=QPoint(0,0),scale=1.50,brightness=40)

        ## MM Song Select ##
        self.mm_song_select_jacket = QSpriteSlave(jacket,position=mm_song_select.jacket.pos().toPoint(), rotation=mm_song_select.jacket.rotation,brightness=40)
        self.mm_song_select_logo = QSpriteSlave(logo,position=mm_song_select.logo.pos().toPoint(),scale=mm_song_select.logo.scale,brightness=40)
        self.mm_song_select_backdrop = QLayer(u":icon/Images/MM UI - Song Select/Backdrop.png")
        self.mm_song_select_middle_layer = QLayer(u":icon/Images/MM UI - Song Select/Middle Layer.png")
        ## MM Result ##
        self.mm_result_jacket = QSpriteSlave(jacket, mm_result.jacket.pos().toPoint(), scale=mm_result.jacket.scale, rotation=mm_result.jacket.rotation,brightness=40)
        self.mm_result_logo = QSpriteSlave(logo, mm_result.logo.pos().toPoint(), scale=mm_result.logo.scale,brightness=40)
        self.mm_result_backdrop = QLayer(u":icon/Images/Dummy/SONG_BG_DUMMY.png", scale=1.5)
        self.mm_result_middle_layer_jacket_shadow = QLayer(u":icon/Images/MM UI - Results Screen/Middle Layer - Jacket Shadow.png")
        ## FT Result ##
        self.ft_result_jacket = QSpriteSlave(jacket, ft_result.jacket.pos().toPoint(), rotation=ft_result.jacket.rotation,brightness=40)
        self.ft_result_logo = QSpriteSlave(logo, ft_result.logo.pos().toPoint(), scale=ft_result.logo.scale,brightness=40)
        self.ft_result_backdrop = QLayer(u":icon/Images/FT UI - Results Screen/Base.png",brightness=40)
        self.ft_result_middle_layer_jacket_shadow = QLayer(u":icon/Images/FT UI - Results Screen/Middle Layer - Jacket Shadow.png")
        ## MM Practise Mode ##
        self.grid = QLayer(u":icon/Images/MM UI - Practise Mode/Grid.png", opacity=25)

        self.centered_layout_state = False
        self.grid_visible_state = True
        self.grid_lower_opacity_state = False
        self.logo_visibility_state = True
        self.logo_size_state = False
        self.ft_result_show_background_state = False

        self.setSceneRect(0, 0, 1920, 1080)
        self.setBackgroundBrush(Qt.GlobalColor.black)

        self.addItem(self.mm_song_select_backdrop)
        self.addItem(self.mm_result_backdrop)
        self.addItem(self.ft_result_backdrop)

        self.addItem(self.background)

        self.addItem(self.mm_song_select_jacket)
        self.addItem(self.mm_song_select_middle_layer)
        self.addItem(self.mm_song_select_logo)

        self.addItem(self.mm_result_middle_layer_jacket_shadow)
        self.addItem(self.mm_result_jacket)
        self.addItem(self.mm_result_logo)

        self.addItem(self.ft_result_middle_layer_jacket_shadow)
        self.addItem(self.ft_result_jacket)
        self.addItem(self.ft_result_logo)

        self.addItem(self.grid)

        self.hide_all()
        self.scene_config_menu = QSmarterMenu(self.name)
        self.toggle_layout(PvBackLayout.MMSongSelect)
    def hide_all(self):
        self.mm_song_select_backdrop.setVisible(False)
        self.mm_song_select_jacket.setVisible(False)
        self.mm_song_select_logo.setVisible(False)
        self.mm_song_select_middle_layer.setVisible(False)
        self.background.setVisible(False)
        self.mm_result_backdrop.setVisible(False)
        self.mm_result_jacket.setVisible(False)
        self.mm_result_logo.setVisible(False)
        self.mm_result_middle_layer_jacket_shadow.setVisible(False)
        self.ft_result_middle_layer_jacket_shadow.setVisible(False)
        self.ft_result_backdrop.setVisible(False)
        self.ft_result_jacket.setVisible(False)
        self.ft_result_logo.setVisible(False)

    def toggle_logo_visibility(self):
        self.logo_visibility_state = not self.logo_visibility_state
        self.toggle_layout(self.current_layout)

    def toggle_layout(self,layout):
        self.hide_all()
        self.current_layout = layout
        match layout:
            case PvBackLayout.MMSongSelect:

                self.mm_song_select_backdrop.setVisible(True)
                self.mm_song_select_jacket.setVisible(True)
                self.mm_song_select_middle_layer.setVisible(True)
                self.background.setVisible(True)
                if self.logo_visibility_state:
                    self.mm_song_select_logo.setVisible(True)

            case PvBackLayout.MMResult:
                self.mm_result_backdrop.setVisible(True)
                self.mm_result_jacket.setVisible(True)
                self.mm_result_middle_layer_jacket_shadow.setVisible(True)
                self.background.setVisible(True)
                if self.logo_visibility_state:
                    self.mm_result_logo.setVisible(True)

            case PvBackLayout.FTResult:
                self.ft_result_middle_layer_jacket_shadow.setVisible(True)
                self.ft_result_backdrop.setVisible(not self.ft_result_show_background_state)
                self.ft_result_jacket.setVisible(True)
                self.background.setVisible(self.ft_result_show_background_state)
                if self.logo_visibility_state:
                    self.ft_result_logo.setVisible(True)

        self.build_menu_options()
    def toggle_grid(self,state):
        self.grid.setVisible(state)
        self.grid_visible_state = not self.grid_visible_state
        self.build_menu_options()
    def toggle_centered_layout(self,state):
        if state:
            self.mm_song_select_jacket.setPos(QPoint(self.mm_song_select_scene.jacket.pos().toPoint().x()-361,self.mm_song_select_scene.jacket.pos().toPoint().y()+57))
            self.mm_song_select_middle_layer.setPos(QPoint(self.mm_song_select_scene.middle_layer.pos().toPoint().x()-361,self.mm_song_select_scene.middle_layer.pos().toPoint().y()+57))

            self.mm_song_select_logo.setPos(QPoint(367, 548))


        else:
            self.mm_song_select_jacket.setPos(self.mm_song_select_scene.jacket.pos().toPoint())
            if self.logo_size_state:
                self.toggle_logo_size(True)
                self.mm_song_select_logo.setPos(QPoint(805, 517))
                self.logo_size_state = not self.logo_size_state

            else:
                self.mm_song_select_logo.setPos(self.mm_song_select_scene.logo.pos().toPoint())

            self.mm_song_select_middle_layer.setPos(self.mm_song_select_scene.middle_layer.pos().toPoint())
            self.mm_song_select_logo.scale = self.mm_song_select_scene.logo.scale

        self.centered_layout_state = not self.centered_layout_state
        print(self.mm_song_select_logo.pos())
    def toggle_logo_size(self,state):
        if state:
            x_offset = 40
            y_offset = 40
            self.mm_song_select_logo.scale = 1
            self.ft_result_logo.scale = 1
            self.mm_result_logo.scale = 1

            if self.centered_layout_state:
                self.mm_song_select_logo.setPos(QPoint(367, 548))
            else:
                self.mm_song_select_logo.setPos(QPoint(int(self.mm_song_select_scene.logo.x() - (x_offset/2)),int(self.mm_song_select_scene.logo.y() - (y_offset/2))))

            self.ft_result_logo.setPos(QPoint(int(self.ft_result_scene.logo.x() - x_offset), int(self.ft_result_scene.logo.y() - y_offset)))

            self.mm_result_logo.setPos(QPoint(int(self.mm_result_scene.logo.x() - x_offset), int(self.mm_result_scene.logo.y() - y_offset)))


        else:
            self.mm_song_select_logo.scale = self.mm_song_select_scene.logo.scale
            self.mm_result_logo.scale = self.mm_result_scene.logo.scale
            self.ft_result_logo.scale = self.ft_result_scene.logo.scale

            if self.centered_layout_state:
                self.mm_song_select_logo.setPos(QPoint(367, 548))
            else:
                self.mm_song_select_logo.setPos(QPoint(int(self.mm_song_select_scene.logo.x()), int(self.mm_song_select_scene.logo.y())))

            self.ft_result_logo.setPos(QPoint(int(self.ft_result_scene.logo.x()), int(self.ft_result_scene.logo.y())))

            self.mm_result_logo.setPos(QPoint(int(self.mm_result_scene.logo.x()), int(self.mm_result_scene.logo.y())))


        self.mm_song_select_logo.update_sprite()
        self.ft_result_logo.update_sprite()
        self.mm_result_logo.update_sprite()

        self.logo_size_state = not self.logo_size_state
        print(self.mm_song_select_logo.pos())

    def toggle_ft_result_background(self,state):
        self.ft_result_backdrop.setVisible(not state)
        self.background.setVisible(state)
        self.ft_result_show_background_state = not self.ft_result_show_background_state
    def change_grid_opacity(self,state:bool):
        if state:
            self.grid.opacity = 5

        else:
            self.grid.opacity = 25
        self.grid_lower_opacity_state = not self.grid_lower_opacity_state
        self.grid.update_sprite()

    def build_menu_options(self):
        self.scene_config_menu.clear()
        if self.options_layout:
            self.clear_layout(self.options_layout)

            label = QLabel("Scene Options")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.options_layout.addWidget(label)

        match self.current_layout:
            case PvBackLayout.MMSongSelect:
                self.scene_config_menu.addAction("Change to MM Result Layout").triggered.connect(lambda: self.toggle_layout(PvBackLayout.MMResult))
                self.scene_config_menu.addAction("Change to FT Result Layout").triggered.connect(lambda: self.toggle_layout(PvBackLayout.FTResult))
                self.centered_layout_toggle = self.scene_config_menu.addAction("Use centered layout")
                self.centered_layout_toggle.setCheckable(True)
                self.centered_layout_toggle.toggled.connect(lambda: self.toggle_centered_layout(self.centered_layout_toggle.isChecked()))
                self.scene_config_menu.addAction(self.centered_layout_toggle)

                if self.options_layout:
                    self.centered_layout_checkbox = QCheckBox("Use centered layout")
                    self.centered_layout_checkbox.setChecked(self.centered_layout_state)
                    self.centered_layout_checkbox.toggled.connect(lambda: self.toggle_centered_layout(self.centered_layout_checkbox.isChecked()))
                    self.options_layout.addWidget(self.centered_layout_checkbox)

            case PvBackLayout.MMResult:
                self.scene_config_menu.addAction("Change to MM Song Select Layout").triggered.connect(lambda: self.toggle_layout(PvBackLayout.MMSongSelect))
                self.scene_config_menu.addAction("Change to FT Result Layout").triggered.connect(lambda: self.toggle_layout(PvBackLayout.FTResult))
            case PvBackLayout.FTResult:
                self.scene_config_menu.addAction("Change to MM Song Select Layout").triggered.connect(lambda: self.toggle_layout(PvBackLayout.MMSongSelect))
                self.scene_config_menu.addAction("Change to MM Result Layout").triggered.connect(lambda: self.toggle_layout(PvBackLayout.MMResult))

                self.ft_result_backdrop_visible_toggle = self.scene_config_menu.addAction("Show Background")
                self.ft_result_backdrop_visible_toggle.setCheckable(True)
                self.ft_result_backdrop_visible_toggle.setChecked(self.ft_result_show_background_state)
                self.ft_result_backdrop_visible_toggle.toggled.connect(lambda: self.toggle_ft_result_background(self.ft_result_backdrop_visible_toggle.isChecked()))

                if self.options_layout:
                    self.ft_result_backdrop_visible_checkbox = QCheckBox("Show Background")
                    self.ft_result_backdrop_visible_checkbox.setChecked(self.ft_result_show_background_state)
                    self.ft_result_backdrop_visible_checkbox.toggled.connect(lambda: self.toggle_ft_result_background(self.ft_result_backdrop_visible_checkbox.isChecked()))
                    self.options_layout.addWidget(self.ft_result_backdrop_visible_checkbox)

        self.grid_toggle = self.scene_config_menu.addAction("Show Grid")
        self.grid_toggle.setCheckable(True)
        self.grid_toggle.setChecked(self.grid_visible_state)
        self.grid_toggle.toggled.connect(lambda: self.toggle_grid(self.grid_toggle.isChecked()))

        if self.options_layout:
            self.grid_checkbox = QCheckBox("Show Grid")
            self.grid_checkbox.setChecked(self.grid_visible_state)
            self.grid_checkbox.toggled.connect(lambda: self.toggle_grid(self.grid_checkbox.isChecked()))
            self.options_layout.addWidget(self.grid_checkbox)

        if self.grid_visible_state:

            self.grid_opacity_toggle = self.scene_config_menu.addAction("Lower grid opacity")
            self.grid_opacity_toggle.setCheckable(True)
            self.grid_opacity_toggle.setChecked(self.grid_lower_opacity_state)
            self.grid_opacity_toggle.toggled.connect(lambda: self.change_grid_opacity(self.grid_opacity_toggle.isChecked()))

        if self.options_layout:
            self.grid_opacity_checkbox = QCheckBox("Lower grid opacity")
            self.grid_opacity_checkbox.setChecked(self.grid_lower_opacity_state)
            self.grid_opacity_checkbox.setEnabled(self.grid_visible_state)
            self.grid_opacity_checkbox.toggled.connect(lambda: self.change_grid_opacity(self.grid_opacity_checkbox.isChecked()))
            self.options_layout.addWidget(self.grid_opacity_checkbox)

        self.logo_size_toggle = self.scene_config_menu.addAction("Use bigger logo")
        self.logo_size_toggle.setCheckable(True)
        self.logo_size_toggle.setChecked(self.logo_size_state)
        self.logo_size_toggle.toggled.connect(lambda: self.toggle_logo_size(self.logo_size_toggle.isChecked()))

        if self.options_layout:
            self.logo_size_checkbox = QCheckBox("Use bigger logo")
            self.logo_size_checkbox.setChecked(self.logo_size_state)
            self.logo_size_checkbox.toggled.connect(lambda: self.toggle_logo_size(self.logo_size_checkbox.isChecked()))
            self.options_layout.addWidget(self.logo_size_checkbox)

    def add_layouts_to_window(self):
        self.mm_song_select_radio = QRadioButton()
        self.mm_song_select_radio.setText(PvBackLayout.MMSongSelect.value)
        self.layout_choose_layout.addWidget(self.mm_song_select_radio)

        self.mm_result_radio = QRadioButton()
        self.mm_result_radio.setText(PvBackLayout.MMResult.value)
        self.layout_choose_layout.addWidget(self.mm_result_radio)

        self.ft_result_radio = QRadioButton()
        self.ft_result_radio.setText(PvBackLayout.FTResult.value)
        self.layout_choose_layout.addWidget(self.ft_result_radio)

        self.mm_song_select_radio.toggled.connect(lambda :self.toggle_layout(PvBackLayout.MMSongSelect))
        self.mm_result_radio.toggled.connect(lambda :self.toggle_layout(PvBackLayout.MMResult))
        self.ft_result_radio.toggled.connect(lambda :self.toggle_layout(PvBackLayout.FTResult))

        self.mm_song_select_radio.setChecked(True)

    def clear_layout(self,layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                    widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout:
                    self.clear_layout(sub_layout)

class QPreviewScenes:
    def __init__(self,C_Sprites:QControllableSprites):
        self.MM_SongSelect = QMMSongSelectScene(C_Sprites.jacket,
                                                C_Sprites.logo,
                                                C_Sprites.background,
                                                C_Sprites.thumbnail)

        self.MM_Result = QMMResultScene(C_Sprites.jacket,
                                        C_Sprites.logo,
                                        C_Sprites.background)

        self.MM_PractiseMode = QMMPractiseModeScene(C_Sprites.jacket,
                                                    C_Sprites.logo,
                                                    C_Sprites.background)

        self.FT_SongSelect = QFTSongSelectScene(C_Sprites.jacket,
                                                C_Sprites.logo,
                                                C_Sprites.background)


        self.FT_Result = QFTResultScene(C_Sprites.jacket,
                                        C_Sprites.logo)
        self.PV_Back = QPVBackScene(self.MM_SongSelect,
                                    self.MM_Result,
                                    self.FT_Result,
                                    jacket=C_Sprites.jacket,
                                    logo=C_Sprites.logo,
                                    background=C_Sprites.background)
        self.PV_Back_Creator_Window = QPVBackScene(self.MM_SongSelect,
                                    self.MM_Result,
                                    self.FT_Result,
                                    jacket=C_Sprites.jacket,
                                    logo=C_Sprites.logo,
                                    background=C_Sprites.background)

        self.new_classics_scenes = [self.MM_SongSelect,self.MM_Result,self.FT_SongSelect,self.FT_Result]

class SceneComposerObjects:
    def __init__(self):
        self.C_Sprites = QControllableSprites()
        self.P_Scenes = QPreviewScenes(self.C_Sprites)