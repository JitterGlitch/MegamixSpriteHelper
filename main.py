from tkinter.filedialog import askopenfilename

import customtkinter
import filedialpy
from pathlib import Path
from PIL import Image, ImageOps
from PIL.Image import Resampling
import copykitten


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Megamix Sprite Helper")
        self.geometry("1880x720")
        #self.grid_columnconfigure(3, weight=0)
        #self.grid_rowconfigure((0, 3), weight=1)
        self.script_directory = Path.cwd()
        self.image_size = (1920/3, 1080/3)
        #Set default images for images used
        self.background = Image.open((self.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png')).convert('RGBA')
        self.jacket = Image.open((self.script_directory / 'Images/Dummy/SONG_JK_DUMMY.png')).convert('RGBA')
        self.logo = Image.open((self.script_directory / 'Images/Dummy/SONG_LOGO_DUMMY.png')).convert('RGBA')
        self.image2 = customtkinter.CTkImage(self.background, size= self.image_size)
        self.thumbnail = Image.open((self.script_directory / 'Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png')).convert('RGBA')

        self.draw_image_grid()

        load_background_button = customtkinter.CTkButton(self, text="Load Background", command=self.load_background_button_callback)
        load_background_button.grid(row=0, column=3, padx=10, pady=10, sticky="wn")

        load_thumbnail_button = customtkinter.CTkButton(self, text="Load Thumbnail", command=self.load_thumbnail_button_callback)
        load_thumbnail_button.grid(row=0, column=3, padx=10, pady=50, sticky="wn")

        load_logo_button = customtkinter.CTkButton(self, text="Load Logo", command=self.load_logo_button_callback)
        load_logo_button.grid(row=0, column=3, padx=160, pady=10, sticky="wn")

        load_jacket_button = customtkinter.CTkButton(self, text="Load Jacket",command=self.load_jacket_button_callback)
        load_jacket_button.grid(row=0, column=3, padx=310, pady=10, sticky="wn")

        copy_to_clipboard_button = customtkinter.CTkButton(self, text="Copy to clipboard",command=self.copy_to_clipboard_button_callback)
        copy_to_clipboard_button.grid(row=0, column=3, padx=460, pady=10, sticky="wn")

    def compose_mm_songselector(self):
        #Load & Prepare images needed
        backdrop = Image.open((self.script_directory / 'Images/MM UI - Song Select/Backdrop.png'))
        jacket = self.jacket.rotate(-7,Resampling.BILINEAR,expand=True)
        song_selector = Image.open((self.script_directory / 'Images/MM UI - Song Select/Song Selector.png'))
        middle_layer = Image.open((self.script_directory / 'Images/MM UI - Song Select/Middle Layer.png'))
        scaled_logo = ImageOps.scale(self.logo,(0.8))
        top_layer = Image.open((self.script_directory / 'Images/MM UI - Song Select/Top Layer.png'))

        #Stretch thumbnail to size
        resized_thumbnail = self.thumbnail.resize((160,76))
        resized_thumbnail_selected = self.thumbnail.resize((202, 98))
        #Stretch 720p background to 1080p to match game's behaviour
        scaled_background = ImageOps.scale(self.background,(1.5))


        composite = Image.new('RGBA' ,(1920,1080), (0,0,0,0))
        composite.alpha_composite(backdrop,(0,0))
        composite.alpha_composite(scaled_background,(0,0))
        composite.alpha_composite(jacket,(1284,130))
        composite.alpha_composite(middle_layer)
        composite.alpha_composite(scaled_logo,(825,537))
        composite.alpha_composite(song_selector, (0, 0))

        composite.alpha_composite(resized_thumbnail, (206-38,943))
        composite.alpha_composite(resized_thumbnail,(140,818))
        composite.alpha_composite(resized_thumbnail, (146-38,706-2))
        composite.alpha_composite(resized_thumbnail, (82-38,478-2))
        composite.alpha_composite(resized_thumbnail, (-34,204))
        composite.alpha_composite(resized_thumbnail, (-66,90))
        composite.alpha_composite(resized_thumbnail, (-98,-24))

        composite.alpha_composite(resized_thumbnail_selected, (-8, 332))



        composite.alpha_composite(top_layer,(0,0))
        self.mm_song_selector_combined_image = composite
        composed_image = customtkinter.CTkImage(self.mm_song_selector_combined_image, size=self.image_size)
        return composed_image

    def compose_mm_result(self):
        backdrop = ImageOps.scale(Image.open((self.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png')),1.5)

        middle_layer = Image.open((self.script_directory / 'Images/MM UI - Results Screen/Middle Layer.png'))
        scaled_logo = ImageOps.scale(self.logo, (0.7))
        top_layer = Image.open((self.script_directory / 'Images/MM UI - Results Screen/Top Layer.png'))

        #Rotate and scale jacket
        scaled_jacket = ImageOps.scale(self.jacket,(0.9))
        jacket = scaled_jacket.rotate(-7, Resampling.BILINEAR, expand=True)

        # Stretch 720p background to 1080p to match game's behaviour
        scaled_background = ImageOps.scale(self.background, (1.5))

        composite = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        composite.alpha_composite(backdrop, (0, 0))
        composite.alpha_composite(scaled_background, (0, 0))
        composite.alpha_composite(middle_layer)
        composite.alpha_composite(jacket,(136-28,413-26)) # Need to make sure coords are accurate
        composite.alpha_composite(scaled_logo,(40+27,750+34)) #34 down , 27 right
        composite.alpha_composite(top_layer, (0, 0))
        self.mm_result_combined_image = composite
        composed_image = customtkinter.CTkImage(self.mm_result_combined_image, size=self.image_size)
        return composed_image

    def compose_ft_song_selector(self):
        #Logo scaled at 90%
        backdrop = Image.open((self.script_directory / 'Images/FT UI - Song Select/Base.png'))
        middle_layer = Image.open((self.script_directory / 'Images/FT UI - Song Select/Middle Layer.png'))
        top_layer = Image.open((self.script_directory / 'Images/FT UI - Song Select/Top Layer.png'))

        scaled_jacket = ImageOps.scale(self.jacket,(0.97))
        jacket = scaled_jacket.rotate(5,Resampling.BILINEAR, expand=True)

        scaled_logo = ImageOps.scale(self.logo,(0.9))
        scaled_background = ImageOps.scale(self.background, (1.5))

        composite = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        composite.alpha_composite(backdrop, (0, 0))
        composite.alpha_composite(scaled_background, (0, 0))
        composite.alpha_composite(middle_layer)
        composite.alpha_composite(jacket, (1309+22, 205))
        composite.alpha_composite(scaled_logo, (803, 550-35))
        composite.alpha_composite(top_layer, (0, 0))
        self.ft_song_selector_combined_image = composite
        composed_image = customtkinter.CTkImage(self.ft_song_selector_combined_image, size=self.image_size)
        return composed_image

    def compose_ft_result(self):
        #Logo scaled at 90%
        backdrop = Image.open((self.script_directory / 'Images/FT UI - Results Screen/Base.png'))
        middle_layer = Image.open((self.script_directory / 'Images/FT UI - Results Screen/Middle Layer.png'))
        top_layer = Image.open((self.script_directory / 'Images/FT UI - Results Screen/Top Layer.png'))

        scaled_jacket = ImageOps.scale(self.jacket,(1))
        jacket = scaled_jacket.rotate(5,Resampling.BILINEAR, expand=True)

        scaled_logo = ImageOps.scale(self.logo,(0.75))

        composite = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        composite.alpha_composite(backdrop, (0, 0))
        composite.alpha_composite(middle_layer)
        composite.alpha_composite(jacket, (164, 303))
        composite.alpha_composite(scaled_logo, (150-16, 700-37))
        composite.alpha_composite(top_layer, (0, 0))
        self.ft_result_combined_image = composite
        composed_image = customtkinter.CTkImage(self.ft_result_combined_image, size=self.image_size)
        return composed_image

    def draw_image_grid(self):
        self.mm_song_selector_preview = customtkinter.CTkLabel(self, image=self.compose_mm_songselector(), text="")
        self.ft_song_selector_preview = customtkinter.CTkLabel(self, image=self.compose_ft_song_selector(), text="")
        self.mm_result_preview = customtkinter.CTkLabel(self, image=self.compose_mm_result(), text="")
        self.ft_result_preview = customtkinter.CTkLabel(self, image=self.compose_ft_result(), text="")

        self.mm_song_selector_preview.grid(row=0, column=0, padx=0, pady=(0, 0), sticky="s")
        self.ft_song_selector_preview.grid(row=0, column=1, padx=0, pady=(0, 0), sticky="e")
        self.mm_result_preview.grid(row=1, column=0, padx=0, pady=(0, 0), sticky="n")
        self.ft_result_preview.grid(row=1, column=1, padx=0, pady=(0, 0), sticky="e")

    def load_background_button_callback(self):
        self.background = Image.open(filedialpy.openFile(title="Open background image", filter="*.png *.jpg")).convert('RGBA')
        self.draw_image_grid()

    def load_jacket_button_callback(self):
        self.jacket = Image.open(filedialpy.openFile(title="Open jacket image", filter="*.png *.jpg")).convert('RGBA')
        self.draw_image_grid()

    def load_logo_button_callback(self):
        self.logo = Image.open(filedialpy.openFile(title="Open logo image", filter="*.png *.jpg")).convert('RGBA')
        self.draw_image_grid()

    def load_thumbnail_button_callback(self):
        self.thumbnail = Image.open(filedialpy.openFile(title="Open thumbnail image", filter="*.png *.jpg")).convert('RGBA')
        self.draw_image_grid()

    def copy_to_clipboard_button_callback(self):
        composite = Image.new('RGBA', (3840, 2160), (0, 0, 0, 0))
        composite.alpha_composite(self.mm_song_selector_combined_image, (0, 0))
        composite.alpha_composite(self.ft_song_selector_combined_image, (1920, 0))
        composite.alpha_composite(self.mm_result_combined_image, (0, 1080))
        composite.alpha_composite(self.ft_result_combined_image, (1920, 1080))
        pixels = composite.tobytes()
        copykitten.copy_image(pixels, composite.width, composite.height)



app = App()
app.mainloop()
