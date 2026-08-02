from enum import Enum

import kkdlib

class Compression(Enum):
    BC7 = "BC7"
    ATI2 = "YCbCr"
    DXT5 = "DXT5"
    RGBA = "Uncompressed"

    def __str__(self):
        return f"{self.value}"

    def to_kkdlib_format(self):
        match self:
            case Compression.ATI2:
               return kkdlib.txp.Format.BC5
            case Compression.DXT5:
                return kkdlib.txp.Format.BC3
            case Compression.BC7:
                return kkdlib.txp.Format.BC7
            case Compression.RGBA:
                return kkdlib.txp.Format.RGBA8


class FarcCreator:
    def create_jk_bg_logo_farc(self,song_id,jk_bg_texture,logo_texture,output_location,compression:Compression,pv_back_texture=None,ex_bg_jk_texture=None,ex_logo_included=False):
        texture_count = 1
        txp = kkdlib.txp.Set()
        logo_list = []
        names = [f"SH Texture #{texture_count}"]
        if compression is Compression.ATI2:
            txp.add_file(kkdlib.txp.Texture.encode_ycbcr(jk_bg_texture.width,jk_bg_texture.height,jk_bg_texture.tobytes()))
        else:
            txp.add_file(kkdlib.txp.Texture.py_from_rgba(jk_bg_texture.width,jk_bg_texture.height,jk_bg_texture.tobytes(),compression.to_kkdlib_format()))

        background = kkdlib.spr.Info()
        background.texid = texture_count - 1
        background.resolution_mode = kkdlib.spr.ResolutionMode.FHD
        background.px = 2
        background.py = 2
        background.width = 1280
        background.height = 720

        jacket = kkdlib.spr.Info()
        jacket.texid = texture_count - 1
        jacket.resolution_mode = kkdlib.spr.ResolutionMode.FHD
        jacket.px = 1286
        jacket.py = 2
        jacket.width = 502
        jacket.height = 502

        if ex_bg_jk_texture is not None:
            texture_count = texture_count + 1
            names.append(f"SH Texture #{texture_count}")
            if compression is Compression.ATI2:
                txp.add_file(kkdlib.txp.Texture.encode_ycbcr(ex_bg_jk_texture.width, ex_bg_jk_texture.height, ex_bg_jk_texture.tobytes()))
            else:
                txp.add_file(kkdlib.txp.Texture.py_from_rgba(ex_bg_jk_texture.width, ex_bg_jk_texture.height, ex_bg_jk_texture.tobytes(), compression.to_kkdlib_format()))

            ex_background = kkdlib.spr.Info()
            ex_background.texid = texture_count - 1
            ex_background.resolution_mode = kkdlib.spr.ResolutionMode.FHD
            ex_background.px = 2
            ex_background.py = 2
            ex_background.width = 1280
            ex_background.height = 720

            ex_jacket = kkdlib.spr.Info()
            ex_jacket.texid = texture_count - 1
            ex_jacket.resolution_mode = kkdlib.spr.ResolutionMode.FHD
            ex_jacket.px = 1286
            ex_jacket.py = 2
            ex_jacket.width = 502
            ex_jacket.height = 502

        if len(logo_texture) > 0:


            texture_count = texture_count + 1
            names.append(f"SH Texture #{texture_count}")
            if compression is Compression.ATI2:
                txp.add_file(kkdlib.txp.Texture.encode_ycbcr(logo_texture[0].width, logo_texture[0].height, logo_texture[0].tobytes()))
            else:
                txp.add_file(kkdlib.txp.Texture.py_from_rgba(logo_texture[0].width, logo_texture[0].height, logo_texture[0].tobytes(), compression.to_kkdlib_format()))

            default_prefix_seen = False
            for logo_info in logo_texture[1]:

                logo = kkdlib.spr.Info()
                logo.texid = texture_count - 1
                logo.resolution_mode = kkdlib.spr.ResolutionMode.FHD
                logo.px = logo_info[1][0]
                logo.py = logo_info[1][1]
                logo.width = 870
                logo.height = 330

                logo_list.append((logo,logo_info[0]))
                if logo_info[0] == "":
                    default_prefix_seen = True

            if not default_prefix_seen:
                logo = kkdlib.spr.Info()
                logo.texid = 0
                logo.resolution_mode = kkdlib.spr.ResolutionMode.FHD
                logo.px = 2
                logo.py = 2
                logo.width = 0
                logo.height = 0

                logo_list.append((logo, ""))


        else:
            #Adding empty sprite as logo so game doesn't display placeholder
            logo = kkdlib.spr.Info()
            logo.texid = 0
            logo.resolution_mode = kkdlib.spr.ResolutionMode.FHD
            logo.px = 2
            logo.py = 2
            logo.width = 0
            logo.height = 0

            logo_list.append((logo,""))

        if pv_back_texture is not None:

            texture_count = texture_count + 1
            names.append(f"SH Texture #{texture_count}")
            if compression is Compression.ATI2:
                txp.add_file(kkdlib.txp.Texture.encode_ycbcr(pv_back_texture.width, pv_back_texture.height, pv_back_texture.tobytes()))
            else:
                txp.add_file(kkdlib.txp.Texture.py_from_rgba(pv_back_texture.width, pv_back_texture.height, pv_back_texture.tobytes(), compression.to_kkdlib_format()))

            pv_back = kkdlib.spr.Info()
            pv_back.texid = texture_count - 1
            pv_back.resolution_mode = kkdlib.spr.ResolutionMode.FHD
            pv_back.px = 2
            pv_back.py = 2
            pv_back.width = 1920
            pv_back.height = 1080

        spr = kkdlib.spr.Set()

        spr.set_txp(txp, names)
        spr.ready = True
        spr.add_spr(background, str("SONG_BG" + song_id))
        spr.add_spr(jacket, str("SONG_JK" + song_id))

        if ex_bg_jk_texture is not None:
            spr.add_spr(ex_background, str("SONG_BG" + song_id + "_EX"))
            spr.add_spr(ex_jacket, str("SONG_JK" + song_id + "_EX"))


        for logo in logo_list:
            spr.add_spr(logo[0], str("SONG_LOGO" + song_id + logo[1]))

        if pv_back_texture is not None:
            spr.add_spr(pv_back, str("IMAGE"))

        farc = kkdlib.farc.Farc()
        farc.add_file_data("spr_sel_pv"+song_id+".bin", spr.to_buf())
        farc.write(output_location+'/spr_sel_pv'+song_id+'.farc', False, False)

    def create_thumbnail_farc(self,thumb_data,thumbnail_texture,output_location,mod_name,compression:Compression):
        txp = kkdlib.txp.Set()
        if compression is Compression.ATI2:
            txp.add_file(kkdlib.txp.Texture.encode_ycbcr(thumbnail_texture.width,thumbnail_texture.height,thumbnail_texture.tobytes()))
        else:
            txp.add_file(kkdlib.txp.Texture.py_from_rgba(thumbnail_texture.width,thumbnail_texture.height,thumbnail_texture.tobytes(),compression.to_kkdlib_format()))

        spr = kkdlib.spr.Set()
        spr.set_txp(txp, ["SH Texture #1"])
        spr.ready = True

        for thumb in thumb_data:
            #[id,(x,y)]
            thumbnail = kkdlib.spr.Info()
            thumbnail.texid = 0
            thumbnail.resolution_mode = kkdlib.spr.ResolutionMode.FHD
            thumbnail.px = thumb[1][0]
            thumbnail.py = thumb[1][1]
            thumbnail.width = 128
            thumbnail.height = 64

            spr.add_spr(thumbnail, thumb[0])

        farc = kkdlib.farc.Farc()
        farc.add_file_data("spr_sel_pvtmb_"+mod_name+".bin", spr.to_buf())
        farc.write(output_location + '/spr_sel_pvtmb_' + mod_name + '.farc', False, False)