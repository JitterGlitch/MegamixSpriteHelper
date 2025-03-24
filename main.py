from pathlib import Path

from filedialpy import openFile
from customtkinter import CTkButton, CTkImage, CTkLabel, CTk, CTkFrame
from PIL import Image, ImageOps
from PIL.Image import Resampling
from copykitten import copy_image


class App(CTk):
    def __init__(self):
        super().__init__()

        self.title("Megamix Sprite Helper")
        self.geometry(self.set_window_size())
        self.resizable(False,False)
        self.script_directory = Path.cwd()
        self.image_size = (self.width * 0.83, self.height * 0.5)
        CTkFrame(self,fg_color="transparent").grid(row=0,column=2,padx=55,pady=10, sticky="nsw")

        #Set default images for images used
        self.scaled_background = ImageOps.scale(Image.open((self.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png')), (1.5)).convert('RGBA')
        self.jacket = Image.open((self.script_directory / 'Images/Dummy/SONG_JK_DUMMY.png')).convert('RGBA')
        self.logo = Image.open((self.script_directory / 'Images/Dummy/SONG_LOGO_DUMMY.png')).convert('RGBA')
        self.thumbnail = Image.open((self.script_directory / 'Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png')).convert('RGBA')

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

    def set_window_size(self) -> str:
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width_percent = 30.25
        height_percent = 50
        self.width = (screen_width * width_percent) // 100
        self.height = (screen_height * height_percent) // 100

        return f"{self.width}x{self.height}+{screen_width // 2 - self.width // 2}+{screen_height // 2 - self.height // 2}"

    def compose_mm_song_selector(self):
        #Anchor points and tweaks
        mm_song_selector_jacket_anchor_point = (1284,130)
        mm_song_selector_jacket_angle = -7
        jacket = self.jacket.rotate(mm_song_selector_jacket_angle, Resampling.BILINEAR, expand=True)

        mm_song_selector_logo_anchor_point = (825,537)
        mm_song_selector_logo_scale = 0.8
        scaled_logo = ImageOps.scale(self.logo, mm_song_selector_logo_scale)

        mm_song_selector_thumbnail_size = (160,76)
        mm_song_selector_selected_thumbnail_size = (202, 98)
        resized_thumbnail = self.thumbnail.resize(mm_song_selector_thumbnail_size)
        resized_selected_thumbnail = self.thumbnail.resize(mm_song_selector_selected_thumbnail_size)

        mm_song_selector_thumbnail_1_anchor_point = (-98,-24)
        mm_song_selector_thumbnail_2_anchor_point = (-66,90)
        mm_song_selector_thumbnail_3_anchor_point = (-34,204)
        mm_song_selector_selected_thumbnail_anchor_point = (-8, 332)
        mm_song_selector_thumbnail_4_anchor_point = (44,476)
        mm_song_selector_thumbnail_5_anchor_point = (108,704)
        mm_song_selector_thumbnail_6_anchor_point = (140,818)
        mm_song_selector_thumbnail_7_anchor_point = (168,943)

        #Load images needed
        song_selector = Image.open((self.script_directory / 'Images/MM UI - Song Select/Song Selector.png'))
        middle_layer = Image.open((self.script_directory / 'Images/MM UI - Song Select/Middle Layer.png'))
        top_layer = Image.open((self.script_directory / 'Images/MM UI - Song Select/Top Layer.png'))

        composite = Image.new('RGBA' ,(1920,1080))
        composite.alpha_composite(self.scaled_background)
        composite.alpha_composite(jacket,mm_song_selector_jacket_anchor_point)
        composite.alpha_composite(middle_layer)
        composite.alpha_composite(scaled_logo,mm_song_selector_logo_anchor_point)
        composite.alpha_composite(song_selector)

        composite.alpha_composite(resized_thumbnail, mm_song_selector_thumbnail_1_anchor_point)
        composite.alpha_composite(resized_thumbnail, mm_song_selector_thumbnail_2_anchor_point)
        composite.alpha_composite(resized_thumbnail, mm_song_selector_thumbnail_3_anchor_point)
        composite.alpha_composite(resized_selected_thumbnail, mm_song_selector_selected_thumbnail_anchor_point)
        composite.alpha_composite(resized_thumbnail, mm_song_selector_thumbnail_4_anchor_point)
        composite.alpha_composite(resized_thumbnail, mm_song_selector_thumbnail_5_anchor_point)
        composite.alpha_composite(resized_thumbnail, mm_song_selector_thumbnail_6_anchor_point)
        composite.alpha_composite(resized_thumbnail, mm_song_selector_thumbnail_7_anchor_point)

        composite.alpha_composite(top_layer)
        self.mm_song_selector_combined_image = composite
        composed_image = CTkImage(self.mm_song_selector_combined_image, size=self.image_size)
        return composed_image

    def compose_mm_result(self):
        #Anchor points and tweaks
        mm_result_logo_anchor_point = (67,784)
        mm_result_logo_scale = (0.7)
        scaled_logo = ImageOps.scale(self.logo, mm_result_logo_scale)

        mm_result_jacket_anchor_point = (108, 387)
        mm_result_jacket_angle = -7
        mm_result_jacket_scale = (0.9)
        scaled_jacket = ImageOps.scale(self.jacket, mm_result_jacket_scale)
        rotated_jacket = scaled_jacket.rotate(mm_result_jacket_angle, Resampling.BILINEAR, expand=True)

        #Load images needed
        backdrop = ImageOps.scale(Image.open((self.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png')),1.5)
        middle_layer = Image.open((self.script_directory / 'Images/MM UI - Results Screen/Middle Layer.png'))
        top_layer = Image.open((self.script_directory / 'Images/MM UI - Results Screen/Top Layer.png'))

        composite = Image.new('RGBA', (1920, 1080))
        composite.alpha_composite(backdrop)
        composite.alpha_composite(self.scaled_background)
        composite.alpha_composite(middle_layer)
        composite.alpha_composite(rotated_jacket,mm_result_jacket_anchor_point)
        composite.alpha_composite(scaled_logo,mm_result_logo_anchor_point)
        composite.alpha_composite(top_layer)
        self.mm_result_combined_image = composite
        composed_image = CTkImage(self.mm_result_combined_image, size=self.image_size)
        return composed_image

    def compose_ft_song_selector(self):
        #Anchor points and tweaks
        ft_song_selector_jacket_anchor_point = (1331, 205)
        ft_song_selector_jacket_scale = (0.97)
        ft_song_selector_jacket_angle = 5
        scaled_jacket = ImageOps.scale(self.jacket, ft_song_selector_jacket_scale)
        rotated_jacket = scaled_jacket.rotate(ft_song_selector_jacket_angle, Resampling.BILINEAR, expand=True)

        ft_song_selector_logo_anchor_point = (803, 515)
        ft_song_selector_logo_scale = (0.9)
        scaled_logo = ImageOps.scale(self.logo, ft_song_selector_logo_scale)

        #Load images needed
        backdrop = Image.open((self.script_directory / 'Images/FT UI - Song Select/Base.png'))
        middle_layer = Image.open((self.script_directory / 'Images/FT UI - Song Select/Middle Layer.png'))
        top_layer = Image.open((self.script_directory / 'Images/FT UI - Song Select/Top Layer.png'))

        composite = Image.new('RGBA', (1920, 1080))
        composite.alpha_composite(backdrop)
        composite.alpha_composite(self.scaled_background)
        composite.alpha_composite(middle_layer)
        composite.alpha_composite(rotated_jacket, ft_song_selector_jacket_anchor_point)
        composite.alpha_composite(scaled_logo, ft_song_selector_logo_anchor_point)
        composite.alpha_composite(top_layer)
        self.ft_song_selector_combined_image = composite
        composed_image = CTkImage(self.ft_song_selector_combined_image, size=self.image_size)
        return composed_image

    def compose_ft_result(self):
        #Anchor points and tweaks
        ft_result_jacket_anchor_point = (164, 303)
        ft_result_jacket_angle = 5

        ft_result_logo_anchor_point = (134, 663)
        ft_result_logo_scale = (0.75)
        scaled_logo = ImageOps.scale(self.logo, ft_result_logo_scale)

        backdrop = Image.open((self.script_directory / 'Images/FT UI - Results Screen/Base.png'))
        middle_layer = Image.open((self.script_directory / 'Images/FT UI - Results Screen/Middle Layer.png'))
        top_layer = Image.open((self.script_directory / 'Images/FT UI - Results Screen/Top Layer.png'))
        rotated_jacket = self.jacket.rotate(ft_result_jacket_angle,Resampling.BILINEAR, expand=True)

        composite = Image.new('RGBA', (1920, 1080))
        composite.alpha_composite(backdrop)
        composite.alpha_composite(middle_layer)
        composite.alpha_composite(rotated_jacket, ft_result_jacket_anchor_point)
        composite.alpha_composite(scaled_logo, ft_result_logo_anchor_point)
        composite.alpha_composite(top_layer)
        self.ft_result_combined_image = composite
        composed_image = CTkImage(self.ft_result_combined_image, size=self.image_size)
        return composed_image

    def draw_image_grid(self):
        self.mm_song_selector_preview = CTkLabel(self, image=self.compose_mm_song_selector(), text="")
        self.ft_song_selector_preview = CTkLabel(self, image=self.compose_ft_song_selector(), text="")
        self.mm_result_preview = CTkLabel(self, image=self.compose_mm_result(), text="")
        self.ft_result_preview = CTkLabel(self, image=self.compose_ft_result(), text="")

        self.mm_song_selector_preview.grid(row=0, column=0, padx=0, pady=0, sticky="wn")
        self.ft_song_selector_preview.grid(row=0, column=1, padx=0, pady=0, sticky="ne")
        self.mm_result_preview.grid(row=1, column=0, padx=0, pady=0, sticky="wn")
        self.ft_result_preview.grid(row=1, column=1, padx=0, pady=0, sticky="wn")

    def load_background_button_callback(self):
        background = Image.open(openFile(title="Open background image", filter="*.png *.jpg")).convert('RGBA')
        self.scaled_background = ImageOps.scale(background, (1.5))
        self.draw_image_grid()

    def load_jacket_button_callback(self):
        self.jacket = Image.open(openFile(title="Open jacket image", filter="*.png *.jpg")).convert('RGBA')
        self.draw_image_grid()

    def load_logo_button_callback(self):
        self.logo = Image.open(openFile(title="Open logo image", filter="*.png *.jpg")).convert('RGBA')
        self.draw_image_grid()

    def load_thumbnail_button_callback(self):
        self.thumbnail = Image.open(openFile(title="Open thumbnail image", filter="*.png *.jpg")).convert('RGBA')
        self.draw_image_grid()

    def copy_to_clipboard_button_callback(self):
        composite = Image.new('RGBA', (3840, 2160), (0, 0, 0, 0))
        composite.alpha_composite(self.mm_song_selector_combined_image, (0, 0))
        composite.alpha_composite(self.ft_song_selector_combined_image, (1920, 0))
        composite.alpha_composite(self.mm_result_combined_image, (0, 1080))
        composite.alpha_composite(self.ft_result_combined_image, (1920, 1080))
        pixels = composite.tobytes()
        copy_image(pixels, composite.width, composite.height)
        self.button_click_feedback(self.copy_to_clipboard_button,"green")

    def button_click_feedback(self,button,color_on_press):
        fg_color = button.cget("fg_color")
        hover_color = button.cget("hover_color")
        button.configure(fg_color=color_on_press,hover_color=color_on_press)
        self.update()
        button.after(600,button.configure(fg_color=fg_color,hover_color=hover_color))



app = App()
app.mainloop()