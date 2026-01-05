import io
import math
from enum import Enum, auto, StrEnum
from pathlib import Path
from typing import Callable

import PySide6
from PIL import Image
from PySide6.QtCore import Qt, QRectF, QPoint, Signal, QObject, QSize, QRect, QIODevice, QFile
from PySide6.QtGui import QImage, QPixmap, QPainter, QTransform
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QGraphicsPixmapItem, QFileDialog, QGraphicsScene, QLayout, QGraphicsView

from widgets import EditableDoubleLabel


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

class Scene(Enum):
    MEGAMIX_SONG_SELECT = auto()
    MEGAMIX_RESULT = auto()
    FUTURE_TONE_SONG_SELECT = auto()
    FUTURE_TONE_RESULT = auto()

####################################################
def round_up(number, decimal_places):
    factor = 10 ** decimal_places
    return math.ceil(number * factor) / factor

def get_transparent_edge_pixels(image):

    if not image.hasAlphaChannel():
        edges = {
            "Top": 0,
            "Bottom": 0,
            "Left": 0,
            "Right": 0
        }
        return edges

    width = image.width()
    height = image.height()

    top = 0
    bottom = 0
    left = 0
    right = 0

    for y in range(height):
        row_has_opaque = False
        for x in range(width):
            if image.pixelColor(x, y).alpha() != 0:
                row_has_opaque = True
                break
        if row_has_opaque:
            break
        top += 1

    for y in range(height - 1, -1, -1):
        row_has_opaque = False
        for x in range(width):
            if image.pixelColor(x, y).alpha() != 0:
                row_has_opaque = True
                break
        if row_has_opaque:
            break
        bottom += 1

    for x in range(width):
        col_has_opaque = False
        for y in range(height):
            if image.pixelColor(x, y).alpha() != 0:
                col_has_opaque = True
                break
        if col_has_opaque:
            break
        left += 1

    for x in range(width - 1, -1, -1):
        col_has_opaque = False
        for y in range(height):
            if image.pixelColor(x, y).alpha() != 0:
                col_has_opaque = True
                break
        if col_has_opaque:
            break
        right += 1

    edges = {
    "Top": top,
    "Bottom": bottom,
    "Left": left,
    "Right": right
    }
    return edges

def get_real_image_area(image:QImage) -> QRect:
    t_edges = get_transparent_edge_pixels(image)
    image_rect = image.rect()
    adjusted_rect = image_rect.adjusted(t_edges["Left"],t_edges["Top"],-t_edges["Right"],-t_edges["Bottom"])
    return adjusted_rect

######################################################
class QScalingGraphicsScene(QGraphicsView):
    def __init__(self):
        super().__init__()
    def resizeEvent(self,event):
        self.fitInView(self.scene().sceneRect())


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
            })
        ]
        self.flipped_h = False
        self.flipped_v = False
        self.is_visible = True
        self.initial_calc = True
        self.last_value = {}
        self.edit_controls = self.create_edit_controls()

        self.update_sprite()

        self.edit_controls[SpriteSetting.ZOOM.value].setValue(self.edit_controls[SpriteSetting.ZOOM.value].spinbox.maximum())

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

    def required_size(self) -> QSize:
        return self.sprite_size.size().toSize()

    def update_all_ranges(self,rect):
        for setting in self.edit_controls:
            self.edit_controls[setting].set_range(self.calculate_range(setting,rect))
    def load_new_image(self,image_location,fallback=False):
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
            self.location = image_location
            self.sprite_image = qimage

        self.t_edges = get_transparent_edge_pixels(self.sprite_image)
        self.rect = get_real_image_area(self.sprite_image)
        self.x = 0
        self.y = 0


        self.initial_calc = True
        self.last_value = {}
        self.update_all_ranges(self.rect)

        self.update_sprite()
        self.set_initial_values()
        return ["Updated"]

    def update_sprite(self,hq_output=False):
        zoom = self.edit_controls[SpriteSetting.ZOOM.value].value
        zoom_inverse = 1/zoom
        horizontal_offset = self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].value
        vertical_offset = self.edit_controls[SpriteSetting.VERTICAL_OFFSET.value].value
        rotation = self.edit_controls[SpriteSetting.ROTATION.value].value
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
        self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].setValue(self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].range[0])
        self.edit_controls[SpriteSetting.VERTICAL_OFFSET.value].setValue(self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].range[0])
        self.edit_controls[SpriteSetting.ROTATION.value].setValue(0)

        if self.sprite_image.size().width() / self.sprite_image.size().height() == 1:
            self.edit_controls[SpriteSetting.ZOOM.value].setValue(self.edit_controls[SpriteSetting.ZOOM.value].range[0])
        else:
            self.edit_controls[SpriteSetting.ZOOM.value].setValue(self.edit_controls[SpriteSetting.ZOOM.value].range[1])

    def update_pixmap(self):
        self.setPixmap(QPixmap(self.apply_fix(self.grab_scene_portion(self.sprite_scene,self.sprite_size).toImage())))
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

    def set_initial_values(self):
        hor_range = self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].range
        hor_center = (hor_range[1] + hor_range[0]) / 2

        ver_range = self.edit_controls[SpriteSetting.VERTICAL_OFFSET.value].range
        ver_center = (ver_range[1]+ver_range[0])/2

        self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].setValue(hor_center)
        self.edit_controls[SpriteSetting.VERTICAL_OFFSET.value].setValue(ver_center)
        self.edit_controls[SpriteSetting.ZOOM.value].setValue(self.edit_controls[SpriteSetting.ZOOM.value].range[1])
        self.edit_controls[SpriteSetting.ROTATION.value].setValue(0)

class QSpriteSlave(QGraphicsPixmapItem):

    def __init__(self, tracked: QSpriteBase, position: QPoint,scale:float=None,rotation:int=None):
        super().__init__()
        self.tracked = tracked
        tracked.SpriteUpdated.connect(self.update_sprite)
        self.rotation = rotation
        self.scale = scale
        self.setPos(position)
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

        self.update_sprite()
    def update_sprite(self):
        if self.scale:
            self.setPixmap(self.tracked.pixmap())
            self.setScale(self.scale)
        else:
            self.setPixmap(self.tracked.pixmap())

        if self.rotation:
            image = self.pixmap().toImage()
            image = image.transformed(QTransform().rotate(self.rotation))
            self.setPixmap(QPixmap(image))
class QLayer(QGraphicsPixmapItem):
    def __init__(self,
                 sprite: str,
                 size: PySide6.QtCore.QRectF = QRectF(0,0,1920,1080),
                 scale:float=1):
        super().__init__()
        self.sprite_size = size
        self.setPixmap(QPixmap(sprite))
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.setScale(scale)

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

class QMMSongSelectScene(QGraphicsScene):
    def __init__(self,jacket:QJacket, logo:QLogo, background:QSpriteBase, thumbnail:QThumbnail):
        super().__init__()

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
        self.top_layer = QLayer(u":icon/Images/MM UI - Song Select/Top Layer - New Classics.png")
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
        self.addItem(self.top_layer)

    def toggle_new_classics(self,state):
        if state:
            self.top_layer.setPixmap(QPixmap(u":icon/Images/MM UI - Song Select/Top Layer - New Classics.png"))
        else:
            self.top_layer.setPixmap(QPixmap(u":icon/Images/MM UI - Song Select/Top Layer.png"))
class QFTSongSelectScene(QGraphicsScene):
    def __init__(self,jacket:QJacket, logo:QLogo, background:QSpriteBase):
        super().__init__()
        #####
        self.jacket = QSpriteSlave(jacket, QPoint(1331, 205), rotation=-5 ,scale=0.97)
        self.logo = QSpriteSlave(logo, QPoint(803, 515), scale=0.9)
        self.background = QSpriteSlave(background,QPoint(0,0), scale=1.50)

        ######
        self.backdrop = QLayer(u":icon/Images/FT UI - Song Select/Base.png")
        self.middle_layer = QLayer(u":icon/Images/FT UI - Song Select/Middle Layer.png")
        self.top_layer = QLayer(u":icon/Images/FT UI - Song Select/Top Layer - New Classics.png")
        ######
        self.setSceneRect(0, 0, 1920, 1080)
        self.setBackgroundBrush(Qt.GlobalColor.black)

        self.addItem(self.backdrop)
        self.addItem(self.background)
        self.addItem(self.middle_layer)
        self.addItem(self.jacket)
        self.addItem(self.logo)
        self.addItem(self.top_layer)

    def toggle_new_classics(self, state):
        if state:
            self.top_layer.setPixmap(QPixmap(u":icon/Images/FT UI - Song Select/Top Layer - New Classics.png"))
        else:
            self.top_layer.setPixmap(QPixmap(u":icon/Images/FT UI - Song Select/Top Layer.png"))
class QMMResultScene(QGraphicsScene):
    def __init__(self,jacket:QJacket, logo:QLogo, background:QSpriteBase):
        super().__init__()

        #####
        self.jacket = QSpriteSlave(jacket, QPoint(108, 387), rotation=7, scale=0.9)
        self.logo = QSpriteSlave(logo, QPoint(67, 784), scale=0.7)
        self.background = QSpriteSlave(background,QPoint(0,0), scale=1.50)
        ######
        self.backdrop = QLayer(u":icon/Images/Dummy/SONG_BG_DUMMY.png",scale=1.5)
        self.middle_layer = QLayer(u":icon/Images/MM UI - Results Screen/Middle Layer.png")
        self.top_layer = QLayer(u":icon/Images/MM UI - Results Screen/Top Layer - New Classics.png")
        ######
        self.setSceneRect(0, 0, 1920, 1080)
        self.setBackgroundBrush(Qt.GlobalColor.black)

        self.addItem(self.backdrop)
        self.addItem(self.background)
        self.addItem(self.middle_layer)
        self.addItem(self.jacket)
        self.addItem(self.logo)
        self.addItem(self.top_layer)

    def toggle_new_classics(self, state):
        if state:
            self.top_layer.setPixmap(QPixmap(u":icon/Images/MM UI - Results Screen/Top Layer - New Classics.png"))
        else:
            self.top_layer.setPixmap(QPixmap(u":icon/Images/MM UI - Results Screen/Top Layer.png"))
class QFTResultScene(QGraphicsScene):
    def __init__(self,jacket:QJacket, logo:QLogo):
        super().__init__()

        #####
        self.jacket = QSpriteSlave(jacket, QPoint(164, 303), rotation=-5)
        self.logo = QSpriteSlave(logo, QPoint(134, 663), scale=0.75)
        ######
        self.backdrop = QLayer(u":icon/Images/FT UI - Results Screen/Base.png")
        self.middle_layer = QLayer(u":icon/Images/FT UI - Results Screen/Middle Layer.png")
        self.top_layer = QLayer(u":icon/Images/FT UI - Results Screen/Top Layer - New Classics.png")
        ######
        self.setSceneRect(0, 0, 1920, 1080)
        self.setBackgroundBrush(Qt.GlobalColor.black)

        self.addItem(self.backdrop)
        self.addItem(self.middle_layer)
        self.addItem(self.jacket)
        self.addItem(self.logo)
        self.addItem(self.top_layer)

    def toggle_new_classics(self, state):
        if state:
            self.top_layer.setPixmap(QPixmap(u":icon/Images/FT UI - Results Screen/Top Layer - New Classics.png"))
        else:
            self.top_layer.setPixmap(QPixmap(u":icon/Images/FT UI - Results Screen/Top Layer.png"))

class QPreviewScenes:
    def __init__(self,C_Sprites:QControllableSprites):
        self.MM_SongSelect = QMMSongSelectScene(C_Sprites.jacket,
                                                C_Sprites.logo,
                                                C_Sprites.background,
                                                C_Sprites.thumbnail)

        self.FT_SongSelect = QFTSongSelectScene(C_Sprites.jacket,
                                                C_Sprites.logo,
                                                C_Sprites.background)

        self.MM_Result = QMMResultScene(C_Sprites.jacket,
                                        C_Sprites.logo,
                                        C_Sprites.background)

        self.FT_Result = QFTResultScene(C_Sprites.jacket,
                                        C_Sprites.logo)