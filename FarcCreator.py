from enum import Enum, auto

import kkdlib

class Compression(Enum):
    ATI2 = "YCbCr"
    DXT5 = "DXT5"
    BC7 = "BC7"
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
                return kkdlib.txp.Format.RGBA


class FarcCreator:
    def create_jk_bg_logo_farc(self,song_id,jk_bg_texture,logo_texture,output_location,compression:Compression):

        txp = kkdlib.txp.Set()
        names = ["SH Texture #1"]
        if compression is Compression.ATI2:
            txp.add_file(kkdlib.txp.Texture.py_ycbcr_from_rgba_gpu(jk_bg_texture.width,jk_bg_texture.height,jk_bg_texture.tobytes()))
        else:
            txp.add_file(kkdlib.txp.Texture.py_from_rgba_gpu(jk_bg_texture.width,jk_bg_texture.height,jk_bg_texture.tobytes(),compression.to_kkdlib_format()))

        background = kkdlib.spr.Info()
        background.texid = 0
        background.resolution_mode = kkdlib.spr.ResolutionMode.FHD
        background.px = 2
        background.py = 2
        background.width = 1280
        background.height = 720

        jacket = kkdlib.spr.Info()
        jacket.texid = 0
        jacket.resolution_mode = kkdlib.spr.ResolutionMode.FHD
        jacket.px = 1286
        jacket.py = 2
        jacket.width = 502
        jacket.height = 502

        spr = kkdlib.spr.Set()


        if logo_texture is not None:
            names.append("SH Texture #2")
            if compression is Compression.ATI2:
                txp.add_file(kkdlib.txp.Texture.py_ycbcr_from_rgba_gpu(logo_texture.width,logo_texture.height,logo_texture.tobytes()))
            else:
                txp.add_file(kkdlib.txp.Texture.py_from_rgba_gpu(logo_texture.width,logo_texture.height,logo_texture.tobytes(),compression.to_kkdlib_format()))

            logo = kkdlib.spr.Info()
            logo.texid = 1
            logo.resolution_mode = kkdlib.spr.ResolutionMode.FHD
            logo.px = 2
            logo.py = 2
            logo.width = 870
            logo.height = 330



        spr.set_txp(txp, names)
        spr.ready = True
        spr.add_spr(background, str("SONG_BG" + song_id))
        spr.add_spr(jacket, str("SONG_JK" + song_id))
        if logo_texture is not None:
            spr.add_spr(logo, str("SONG_LOGO" + song_id))

        farc = kkdlib.farc.Farc()
        farc.add_file_data("spr_sel_pv"+song_id+".bin", spr.to_buf())
        farc.write(output_location+'/spr_sel_pv'+song_id+'.farc', False, False)

    def create_thumbnail_farc(self,thumb_data,thumbnail_texture,output_location,mod_name,compression:Compression):
        txp = kkdlib.txp.Set()
        if compression is Compression.ATI2:
            txp.add_file(kkdlib.txp.Texture.py_ycbcr_from_rgba_gpu(thumbnail_texture.width,thumbnail_texture.height,thumbnail_texture.tobytes()))
        else:
            txp.add_file(kkdlib.txp.Texture.py_from_rgba_gpu(thumbnail_texture.width,thumbnail_texture.height,thumbnail_texture.tobytes(),compression.to_kkdlib_format()))

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