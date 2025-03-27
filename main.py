import sys
from pathlib import Path

from PIL import Image, ImageOps
from PIL.Image import Resampling
from copykitten import copy_image
from customtkinter import CTkButton, CTkImage, CTkLabel, CTk, CTkFrame, CTkToplevel
from easygui import msgbox
from filedialpy import openFile



class Configurable():
    def __init__(self):
        self.script_directory = Path.cwd()

class App(CTk):
    def __init__(self):
        super().__init__()
        self.title("Megamix Sprite Helper")
        self.geometry(self.set_window_size())
        self.resizable(False,False)
        self.image_size = (self.width * 0.83, self.height * 0.5)

        CTkFrame(self,fg_color="transparent").grid(row=0,column=2,padx=55,pady=10, sticky="nsw")
        self.check_for_files()
        #Set default images for images used
        SceneComposer.scaled_background = ImageOps.scale(Image.open((config.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png')), (1.5)).convert('RGBA')
        SceneComposer.jacket = Image.open((config.script_directory / 'Images/Dummy/SONG_JK_DUMMY.png')).convert('RGBA')
        SceneComposer.logo = Image.open((config.script_directory / 'Images/Dummy/SONG_LOGO_DUMMY.png')).convert('RGBA')
        SceneComposer.thumbnail = Image.open((config.script_directory / 'Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png')).convert('RGBA')

        self.draw_image_grid()

        load_background_button = CTkButton(self, text="Load Background", command=self.load_background_button_callback)
        load_background_button.grid(row=0, column=2, padx=10, pady=10, sticky="wn")

        load_thumbnail_button = CTkButton(self, text="Load Thumbnail", command=self.load_thumbnail_button_callback)
        load_thumbnail_button.grid(row=0, column=2, padx=10, pady=50, sticky="ne")

        load_logo_button = CTkButton(self, text="Load Logo", command=self.load_logo_button_callback)
        load_logo_button.grid(row=0, column=2, padx=10, pady=50, sticky="wn")

        load_jacket_button = CTkButton(self, text="Load Jacket",command=self.load_jacket_button_callback)
        load_jacket_button.grid(row=0, column=2, padx=10, pady=10, sticky="ne")

        self.copy_to_clipboard_button = CTkButton(self, text="Copy to clipboard",command=self.copy_to_clipboard_button_callback)
        self.copy_to_clipboard_button.grid(row=0, column=2, padx=10, pady=90, sticky="wn")

    def draw_image_grid(self):
        self.mm_song_selector_preview = CTkLabel(self, image=self.get_scene("mm_song_selector"), text="")
        self.ft_song_selector_preview = CTkLabel(self, image=self.get_scene("ft_song_selector"), text="")
        self.mm_result_preview = CTkLabel(self, image=self.get_scene("mm_result"), text="")
        self.ft_result_preview = CTkLabel(self, image=self.get_scene("ft_result"), text="")

        self.mm_song_selector_preview.grid(row=0, column=0, padx=0, pady=0, sticky="wn")
        self.ft_song_selector_preview.grid(row=0, column=1, padx=0, pady=0, sticky="ne")
        self.mm_result_preview.grid(row=1, column=0, padx=0, pady=0, sticky="wn")
        self.ft_result_preview.grid(row=1, column=1, padx=0, pady=0, sticky="wn")

    def check_for_files(self):
        try:
            x = Image.open((config.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png').resolve(strict=True))
            x = Image.open((config.script_directory / 'Images/Dummy/SONG_JK_DUMMY.png').resolve(strict=True))
            x = Image.open((config.script_directory / 'Images/Dummy/SONG_LOGO_DUMMY.png').resolve(strict=True))
            x = Image.open((config.script_directory / 'Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png').resolve(strict=True))

            x = Image.open((config.script_directory / 'Images/MM UI - Song Select/Backdrop.png').resolve(strict=True))
            x = Image.open((config.script_directory / 'Images/MM UI - Song Select/Song Selector.png').resolve(strict=True))
            x = Image.open((config.script_directory / 'Images/MM UI - Song Select/Middle Layer.png').resolve(strict=True))
            x = Image.open((config.script_directory / 'Images/MM UI - Song Select/Top Layer.png').resolve(strict=True))

            x = Image.open((config.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png').resolve(strict=True))
            x = Image.open((config.script_directory / 'Images/MM UI - Results Screen/Middle Layer.png').resolve(strict=True))
            x = Image.open((config.script_directory / 'Images/MM UI - Results Screen/Top Layer.png').resolve(strict=True))

            x = Image.open((config.script_directory / 'Images/FT UI - Song Select/Base.png').resolve(strict=True))
            x = Image.open((config.script_directory / 'Images/FT UI - Song Select/Middle Layer.png').resolve(strict=True))
            x = Image.open((config.script_directory / 'Images/FT UI - Song Select/Top Layer.png').resolve(strict=True))

            x = Image.open((config.script_directory / 'Images/FT UI - Results Screen/Base.png').resolve(strict=True))
            x = Image.open((config.script_directory / 'Images/FT UI - Results Screen/Middle Layer.png').resolve(strict=True))
            x = Image.open((config.script_directory / 'Images/FT UI - Results Screen/Top Layer.png').resolve(strict=True))
        except:
            msgbox("Images are missing")
            quit("Images are missing")

    def set_window_size(self) -> str:
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width_percent = 30.25
        height_percent = 50
        self.width = (screen_width * width_percent) // 100
        self.height = (screen_height * height_percent) // 100

        return f"{self.width}x{self.height}+{screen_width // 2 - self.width // 2}+{screen_height // 2 - self.height // 2}"
    def get_scene(self,ui_scene):
       return CTkImage(SceneComposer.compose_scene(ui_scene),size=self.image_size)

    def load_background_button_callback(self):
        try:
            background = Image.open(openFile(title="Open background image", filter="*.png *.jpg")).convert('RGBA')
        except:
            print("Background image wasn't chosen")
        else:
            SceneComposer.scaled_background = ImageOps.scale(background, (1.5))
            self.draw_image_grid()

    def load_jacket_button_callback(self):
        try:
            SceneComposer.jacket = Image.open(openFile(title="Open jacket image", filter="*.png *.jpg")).convert('RGBA')
        except:
            print("Jacket image wasn't chosen")
        else:
            self.draw_image_grid()

    def load_logo_button_callback(self):
        try:
            SceneComposer.logo = Image.open(openFile(title="Open logo image", filter="*.png *.jpg")).convert('RGBA')
        except:
            print("Logo image wasn't chosen")
        else:
            self.draw_image_grid()

    def load_thumbnail_button_callback(self):
        try:
            SceneComposer.thumbnail = Image.open(openFile(title="Open thumbnail image", filter="*.png *.jpg")).convert('RGBA')
        except:
            print("Thumbnail image wasn't chosen")
        else:
            self.draw_image_grid()

    def copy_to_clipboard_button_callback(self):
        composite = Image.new('RGBA', (3840, 2160), (0, 0, 0, 0))
        composite.alpha_composite(SceneComposer.compose_scene("mm_song_selector"), (0, 0))
        composite.alpha_composite(SceneComposer.compose_scene("mm_result"), (1920, 0))
        composite.alpha_composite(SceneComposer.compose_scene("ft_song_selector"), (0, 1080))
        composite.alpha_composite(SceneComposer.compose_scene("ft_result"), (1920, 1080))
        pixels = composite.tobytes()
        copy_image(pixels, composite.width, composite.height)
        self.button_click_feedback(self.copy_to_clipboard_button,"green")

    def button_click_feedback(self,button,color_on_press):
        fg_color = button.cget("fg_color")
        hover_color = button.cget("hover_color")
        button.configure(fg_color=color_on_press,hover_color=color_on_press)
        self.update()
        button.after(600,button.configure(fg_color=fg_color,hover_color=hover_color))

class SceneComposer:
    def compose_scene(self,ui_screen):
        self.prepare_scene(ui_screen)
        composite = Image.new('RGBA' ,(1920,1080))
        iteration=0
        for layer in self.grab_layers(ui_screen):
            composite.alpha_composite(layer,self.anchor_points[iteration])
            iteration=iteration+1
        return composite

    def prepare_scene(self,ui_screen):
        match ui_screen:
            case "mm_song_selector":
                # Anchor points and tweaks
                self.mm_song_selector_jacket_anchor_point = (1284, 130)
                mm_song_selector_jacket_angle = -7
                self.rotated_jacket = self.jacket.rotate(mm_song_selector_jacket_angle, Resampling.BILINEAR, expand=True)

                self.mm_song_selector_logo_anchor_point = (825, 537)
                mm_song_selector_logo_scale = 0.8
                self.scaled_logo = ImageOps.scale(self.logo, mm_song_selector_logo_scale)

                mm_song_selector_thumbnail_size = (160, 76)
                mm_song_selector_selected_thumbnail_size = (202, 98)
                self.resized_thumbnail = self.thumbnail.resize(mm_song_selector_thumbnail_size)
                self.resized_selected_thumbnail = self.thumbnail.resize(mm_song_selector_selected_thumbnail_size)

                self.mm_song_selector_thumbnail_1_anchor_point = (-98, -24)
                self.mm_song_selector_thumbnail_2_anchor_point = (-66, 90)
                self.mm_song_selector_thumbnail_3_anchor_point = (-34, 204)
                self.mm_song_selector_selected_thumbnail_anchor_point = (-8, 332)
                self.mm_song_selector_thumbnail_4_anchor_point = (44, 476)
                self.mm_song_selector_thumbnail_5_anchor_point = (108, 704)
                self.mm_song_selector_thumbnail_6_anchor_point = (140, 818)
                self.mm_song_selector_thumbnail_7_anchor_point = (168, 943)

                # Load images needed
                self.backdrop = Image.open(config.script_directory / 'Images/MM UI - Song Select/Backdrop.png').convert('RGBA')
                self.song_selector = Image.open(config.script_directory / 'Images/MM UI - Song Select/Song Selector.png').convert('RGBA')
                self.middle_layer = Image.open(config.script_directory / 'Images/MM UI - Song Select/Middle Layer.png').convert('RGBA')
                self.top_layer = Image.open(config.script_directory / 'Images/MM UI - Song Select/Top Layer.png').convert('RGBA')
            case "mm_result":
                # Anchor points and tweaks
                self.mm_result_jacket_anchor_point = (108, 387)
                mm_result_jacket_angle = -7
                mm_result_jacket_scale = (0.9)
                scaled_jacket = ImageOps.scale(self.jacket, mm_result_jacket_scale)
                self.rotated_jacket = scaled_jacket.rotate(mm_result_jacket_angle, Resampling.BILINEAR, expand=True)

                self.mm_result_logo_anchor_point = (67, 784)
                mm_result_logo_scale = (0.7)
                self.scaled_logo = ImageOps.scale(self.logo, mm_result_logo_scale)

                # Load images needed
                self.backdrop = ImageOps.scale(Image.open((config.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png')), 1.5)
                self.middle_layer = Image.open((config.script_directory / 'Images/MM UI - Results Screen/Middle Layer.png'))
                self.top_layer = Image.open((config.script_directory / 'Images/MM UI - Results Screen/Top Layer.png'))

            case "ft_song_selector":
                # Anchor points and tweaks
                self.ft_song_selector_jacket_anchor_point = (1331, 205)
                ft_song_selector_jacket_scale = (0.97)
                ft_song_selector_jacket_angle = 5
                scaled_jacket = ImageOps.scale(self.jacket, ft_song_selector_jacket_scale)
                self.rotated_jacket = scaled_jacket.rotate(ft_song_selector_jacket_angle, Resampling.BILINEAR, expand=True)

                self.ft_song_selector_logo_anchor_point = (803, 515)
                ft_song_selector_logo_scale = (0.9)
                self.scaled_logo = ImageOps.scale(self.logo, ft_song_selector_logo_scale)

                # Load images needed
                self.backdrop = Image.open((config.script_directory / 'Images/FT UI - Song Select/Base.png'))
                self.middle_layer = Image.open((config.script_directory / 'Images/FT UI - Song Select/Middle Layer.png'))
                self.top_layer = Image.open((config.script_directory / 'Images/FT UI - Song Select/Top Layer.png'))

            case "ft_result":
                # Anchor points and tweaks
                self.ft_result_jacket_anchor_point = (164, 303)
                ft_result_jacket_angle = 5
                self.rotated_jacket = self.jacket.rotate(ft_result_jacket_angle, Resampling.BILINEAR, expand=True)

                self.ft_result_logo_anchor_point = (134, 663)
                ft_result_logo_scale = (0.75)
                self.scaled_logo = ImageOps.scale(self.logo, ft_result_logo_scale)

                self.backdrop = Image.open((config.script_directory / 'Images/FT UI - Results Screen/Base.png'))
                self.middle_layer = Image.open((config.script_directory / 'Images/FT UI - Results Screen/Middle Layer.png'))
                self.top_layer = Image.open((config.script_directory / 'Images/FT UI - Results Screen/Top Layer.png'))

        pass
    def grab_layers(self,ui_screen):
        match ui_screen:
            case "mm_song_selector":
                self.anchor_points = (
                    (0,0),
                    (0,0),
                    self.mm_song_selector_jacket_anchor_point,
                    (0,0),
                    self.mm_song_selector_logo_anchor_point,
                    (0,0),
                    self.mm_song_selector_thumbnail_1_anchor_point,
                    self.mm_song_selector_thumbnail_2_anchor_point,
                    self.mm_song_selector_thumbnail_3_anchor_point,
                    self.mm_song_selector_selected_thumbnail_anchor_point,
                    self.mm_song_selector_thumbnail_4_anchor_point,
                    self.mm_song_selector_thumbnail_5_anchor_point,
                    self.mm_song_selector_thumbnail_6_anchor_point,
                    self.mm_song_selector_thumbnail_7_anchor_point,
                    (0,0)

                )
                return (
                    self.backdrop,
                    self.scaled_background,
                    self.rotated_jacket,
                    self.middle_layer,
                    self.scaled_logo,
                    self.song_selector,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.resized_selected_thumbnail,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.top_layer
                )
            case "mm_result":
                self.anchor_points = (
                    (0,0),
                    (0,0),
                    (0,0),
                    self.mm_result_jacket_anchor_point,
                    self.mm_result_logo_anchor_point,
                    (0,0)
                )
                return (
                    self.backdrop,
                    self.scaled_background,
                    self.middle_layer,
                    self.rotated_jacket,
                    self.scaled_logo,
                    self.top_layer
                )
            case "ft_song_selector":
                self.anchor_points = (
                    (0,0),
                    (0,0),
                    (0,0),
                    self.ft_song_selector_jacket_anchor_point,
                    self.ft_song_selector_logo_anchor_point,
                    (0,0)
                )
                return (
                    self.backdrop,
                    self.scaled_background,
                    self.middle_layer,
                    self.rotated_jacket,
                    self.scaled_logo,
                    self.top_layer
                )
            case "ft_result":
                self.anchor_points = (
                    (0,0),
                    (0,0),
                    self.ft_result_jacket_anchor_point,
                    self.ft_result_logo_anchor_point,
                    (0,0)
                )
                return (
                    self.backdrop,
                    self.middle_layer,
                    self.rotated_jacket,
                    self.scaled_logo,
                    self.top_layer
                )

config = Configurable()
SceneComposer = SceneComposer()
app = App()

app.mainloop()