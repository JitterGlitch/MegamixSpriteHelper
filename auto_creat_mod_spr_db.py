import zlib
from pathlib import Path
from pprint import pprint
import hashlib
from io import BytesIO
from diva_lib.hash import CalculateStr

'''
def get_hash(string):
    obj = hashlib.shake_256()
    obj.update(string.encode("utf-8"))
    result=int(obj.hexdigest(4),16)
    return result
'''


def get_hash(string):
    return CalculateStr(string)


class farc_format:
    AFT = b"FArC"
    AFT_RAW = b"FArc"
    Gzip = b"\x00\x00\x00\x10"


class Manager:
    def __init__(self):
        self.sprinfo_list = list()
        self.spr_list = list()
        self.sprinfo_id_dict = {}
        self.sprinfo_file_name_dict = {}
        self.pvtmb = None

    def read_db(self, _file_path):
        with open(_file_path, "rb") as f:
            info_len = f.read(16)
            SpriteSetInfo_list = {"len": int.from_bytes(info_len[0:4], "little"),
                                  "start": int.from_bytes(info_len[4:8], "little"),
                                  }
            Sprites_list = {"len": int.from_bytes(info_len[8:12], "little"),
                            "start": int.from_bytes(info_len[12:16], "little"),
                            }
            for i in range(SpriteSetInfo_list["len"]):
                f.seek(SpriteSetInfo_list["start"] + i * 16)
                self.add_spr(SpriteSetInfo(f.read(16), f))
                if SpriteSetInfo.max_info_id < self.sprinfo_list[-1].info_id:
                    SpriteSetInfo.max_info_id = self.sprinfo_list[-1].info_id

            for i in range(Sprites_list["len"]):
                f.seek(Sprites_list["start"] + i * 12)
                self.add_spr(Sprites(f.read(12), f))

    def write_db(self, _file_path):
        len_sprinfo = len(self.sprinfo_list)
        len_spr = len(self.spr_list)
        sprinfo_start = 16
        spr_start = len_sprinfo * 16 + sprinfo_start
        spr_no_data_lenght = 16 - ((len_spr * 12) % 16)
        str_start = spr_start + (len_spr * 12) + spr_no_data_lenght

        with open(_file_path, "wb+") as f:
            # write head info
            f.write(len_sprinfo.to_bytes(4, byteorder="little"))
            f.write(sprinfo_start.to_bytes(4, byteorder="little"))
            f.write(len_spr.to_bytes(4, byteorder="little"))
            f.write(spr_start.to_bytes(4, byteorder="little"))
            max_len = len(self.sprinfo_list)
            for i in range(len(self.sprinfo_list)):
                process = i / max_len
                process = str(process * 100)[:5]
                sprinfo = self.sprinfo_list[i]
                #print(f"\rCreat new mod_spr_db:{process}%", end="")
                # write sprinfo
                # write id
                f.seek(sprinfo_start)
                f.write(sprinfo.id.to_bytes(4, byteorder="little"))
                # write str start point
                f.write(str_start.to_bytes(4, byteorder="little"))
                # write file str start point
                file_str_start = len(sprinfo.info_str) + str_start + 1
                f.write(file_str_start.to_bytes(4, byteorder="little"))
                # wrile info id
                f.write(sprinfo.info_id.to_bytes(4, byteorder="little"))

                sprinfo_start += 16

                # write str
                f.seek(str_start)
                f.write(sprinfo.info_str.encode("UTF-8"))
                f.write(b"\x00")
                f.write(sprinfo.file_str.encode("UTF-8"))

                str_start = f.tell() + 1
                # write Sprites and Textures
                temp_list = sprinfo.Sprites_list + sprinfo.Textures_list
                if len(temp_list) > 0:
                    for k in temp_list:
                        f.seek(spr_start)
                        f.write(k.id.to_bytes(4, byteorder="little"))
                        # write str start point
                        f.write(str_start.to_bytes(4, byteorder="little"))
                        # wrile index
                        f.write(k.index.to_bytes(2, byteorder="little"))
                        # wrile info id
                        info_id = k.info_id
                        if not k.is_spr:
                            # \x00\x00 mean spr
                            # \x00\x10 mean tex
                            info_id += 4096
                        f.write(info_id.to_bytes(2, byteorder="little"))

                        spr_start += 12

                        f.seek(str_start)
                        f.write(k.info_str.encode("UTF-8"))

                        str_start = f.tell() + 1
            file_size = f.tell()
            #print("\rCreat new mod_spr_db:100.00%")
            #print("Done!")
            f.write(b"\x00" * (16 - (file_size % 16)))

    def add_spr(self, data):
        #print(f"add {data.info_str}")
        if type(data) == SpriteSetInfo:
            self.sprinfo_list.append(data)
            self.sprinfo_id_dict[self.sprinfo_list[-1].info_id] = self.sprinfo_list[-1]
            self.sprinfo_file_name_dict[self.sprinfo_list[-1].file_str] = self.sprinfo_list[-1].info_id
            if (self.pvtmb == None and self.sprinfo_list[-1].info_str == "SPR_SEL_PVTMB"):
                self.pvtmb = self.sprinfo_list[-1]

        elif type(data) == Sprites:
            self.spr_list.append(data)
            self.sprinfo_id_dict[data.info_id].add_spr(self.spr_list[-1])

        else:
            raise ValueError("Error Dataļ¼", data)

    def check_index(self):
        check_list = []
        for i in self.sprinfo_list:
            #print(f"\r\ncheck {i.info_str} index......", end="")
            check = i.check_index()
            check_list += check
        #print("\nDone!")
        if len(check_list) > 0:
            pass
            #pprint(f"Crash Error Index:\n{check_list}")
        else:
            pass
            #print("No Crash Error")

    def check_id(self):

        #print("\nCheck sprinfo id")
        id_list = []
        same_id_list = []
        for i in self.sprinfo_list:
            #print(f"\rcheck {i.info_str} id......", end="")
            id_list.append(i.id)
            if id_list.count(i.id) > 1 and same_id_list.count(i.id) == 0:
                same_id_list.append(i.id)
        #print("Done!")
        if len(same_id_list) > 0:
            #pprint(f"Same ID:\n{same_id_list}")
            pass
        else:
            pass
            #print("No Same ID")

        #print("\nCheck Spr ID")
        id_list = []
        same_id_list = []
        for i in self.spr_list:
            #print(f"\rcheck {i.info_str} id......", end="")
            id_list.append(i.id)
            if id_list.count(i.id) > 1 and same_id_list.count(i.id) == 0:
                same_id_list.append(i.id)
        #print("Done!")
        if len(same_id_list) > 0:
            #pprint(f"Same ID:\n{same_id_list}")
            pass
        else:
            #print("No Same ID")
            pass

    def have_sprinfo(self, _file_name=None):
        return self.sprinfo_file_name_dict.get(_file_name)

    def Remove_Sprites(self, data):
        _Sprite_Info = self.sprinfo_id_dict[data.info_id]
        if type(data) == SpriteSetInfo:
            for i in range(len(_Sprite_Info.Sprites_list)):
                self.Remove_Sprites(_Sprite_Info.Sprites_list[0])
            for i in range(len(_Sprite_Info.Textures_list)):
                self.Remove_Sprites(_Sprite_Info.Textures_list[0])
        elif type(data) == Sprites:
            if data.is_spr:
                _Sprite_Info.Sprites_list.remove(data)
            else:
                _Sprite_Info.Textures_list.remove(data)
            self.spr_list.remove(data)


class SpriteSetInfo:
    max_info_id = -1

    def __init__(self, data, file=None):
        self.Sprites_list = list()
        self.Textures_list = list()
        self.spr_dict = {}
        if type(data) == type(dict()):
            self.id = data["id"]
            self.info_str = data["info_str"]
            self.file_str = data["file_str"]
            self.info_id = data["info_id"]
        elif file != None:
            self.id = self.to_int(data[:4])
            self.info_str = self.get_str(file, self.to_int(data[4:8]))
            self.file_str = self.get_str(file, self.to_int(data[8:12]))
            self.info_id = self.to_int(data[12:16])

    def get_str(self, file, start):
        file.seek(start)
        get_str = ""
        get_char = ""
        while get_char != b"\x00":
            if get_char != "":
                get_str += get_char.decode("utf-8")
            get_char = file.read(1)
        return get_str

    def to_int(self, int_byte):
        return int.from_bytes(int_byte, "little")

    def add_spr(self, data):
        if data.is_spr == True:
            data.index = len(self.Sprites_list)
            self.Sprites_list.append(data)
        else:
            data.index = len(self.Textures_list)
            self.Textures_list.append(data)

    def check_index(self):
        wrong_list = []
        for i in self.Textures_list:
            if i.index >= len(self.Sprites_list):
                wrong_list.append(i)
        for i in self.Sprites_list:
            if i.index >= len(self.Sprites_list):
                wrong_list.append(i.info_str)
        return wrong_list


class Sprites:
    def __init__(self, data, file=None):
        if type(data) == type(dict()):
            self.id = data["id"]
            self.info_str = data["info_str"]
            self.index = data["index"]
            self.is_spr = data["is_spr"]
            self.info_id = data["info_id"]
        elif file != None:
            self.id = self.to_int(data[:4])
            self.info_str = self.get_str(file, self.to_int(data[4:8]))
            self.index = int.from_bytes(data[8:10], "little")
            self.get_info_id(data[10:12])

    def get_str(self, file, start):
        file.seek(start)
        get_str = ""
        get_char = ""
        while get_char != b"\x00":
            if get_char != "":
                get_str += get_char.decode("utf-8")
            get_char = file.read(1)
        return get_str

    def to_int(self, int_byte):
        return int.from_bytes(int_byte, "little")

    def get_info_id(self, data):
        check = data[1]
        if check >= 16:
            self.is_spr = False
            check -= 16
        else:
            self.is_spr = True
        self.info_id = data[0] + (check * 256)


class add_farc_to_Manager:
    def __init__(self, _farc, _Manager):
        #print(f"\n*Start add {_farc.name} to mod_spr_db*")
        self.Manager = _Manager
        self.farc_file = BytesIO(_farc.data)
        self.farc_name = _farc.name
        info_id = self.creat_sprsetinfo()
        spr_list = self.get_info("spr")
        tex_list = self.get_info("tex")
        self.creat_sprinfo(spr_list, _is_spr=True, _info_id=info_id)
        self.creat_sprinfo(tex_list, _is_spr=False, _info_id=info_id)

    def get_info(self, _type=None):
        _file = self.farc_file
        if _type == None:
            return
        if _type == "tex":
            head_start = 8
        if _type == "spr":
            head_start = 12
        _file.seek(head_start)
        _len = int.from_bytes(_file.read(4), byteorder="little")
        _file.seek(head_start + 12)
        list_start_point = int.from_bytes(_file.read(4), byteorder="little")
        return self.get_str_list(_len, list_start_point)

    def get_str_list(self, _len, _start_point):
        _file = self.farc_file
        _file.seek(_start_point)
        list_start_point = []
        for i in range(_len):
            list_start_point.append(int.from_bytes(_file.read(4), byteorder="little"))
        str_list = []
        for point in list_start_point:
            _file.seek(point)
            get_str = ""
            get_char = ""
            while get_char != b"\x00":
                if get_char != "":
                    get_str += get_char.decode("utf-8")
                get_char = _file.read(1)
            str_list.append(get_str)
        return str_list

    def creat_sprsetinfo(self):
        if self.Manager.have_sprinfo(self.farc_name) == None:
            head_str = self.farc_name[:-4].upper()
            SpriteSetInfo.max_info_id += 1
            info_id = SpriteSetInfo.max_info_id
            sprsetinfo_dict = {"id": 0,
                               "info_str": head_str,
                               "file_str": self.farc_name,
                               "info_id": info_id
                               }
            sprsetinfo_dict["id"] = get_hash(head_str) if (head_str != "SPR_SEL_PVTMB") else 4527
            print(head_str)
            self.Manager.add_spr(SpriteSetInfo(sprsetinfo_dict))

        else:
            #print(f"\n**Try to add {self.farc_name} but it's already have,it's will be rewrite**\n")
            info_id = self.Manager.have_sprinfo(self.farc_name)
            self.Manager.Remove_Sprites(self.Manager.sprinfo_id_dict[info_id])
        return info_id

    def creat_sprinfo(self, head_str_list, _is_spr=True, _info_id=SpriteSetInfo.max_info_id):
        sprinfo_dict = {"id": 0,
                        "info_str": 0,
                        "index": 0,
                        "is_spr": _is_spr,
                        "info_id": 0}
        for i in range(len(head_str_list)):
            if head_str_list[i] == "":
                head_str = f"{self.farc_name[:-4]}_sprite_null_{i}" if _is_spr else f"{self.farc_name[:-4].upper()}_texture_null_{i}"
            elif "SPR_SEL_PVTMB" in self.farc_name[:-4].upper():
                head_str = f"SPR_SEL_PVTMB_{head_str_list[i]}" if _is_spr else f"{self.farc_name[0:3]}TEX{self.farc_name[3:-4]}_{head_str_list[i]}"
            else:
                head_str = f"{self.farc_name[:-4]}_{head_str_list[i]}" if _is_spr else f"{self.farc_name[0:3]}TEX{self.farc_name[3:-4]}_{head_str_list[i]}"
            sprinfo_dict["info_str"] = head_str.upper()
            sprinfo_dict["index"] = i
            sprinfo_dict["id"] = get_hash(head_str.upper())
            sprinfo_dict["info_id"] = _info_id
            self.Manager.add_spr(Sprites(sprinfo_dict))


class read_farc:

    def __init__(self, file_path):
        with open(file_path, "rb") as f:
            format = self.check_format(f)
            f.seek(4)
            lenght = int.from_bytes(f.read(4), byteorder="big")
            f.seek(12)
            if format == farc_format.AFT:
                file_info = self.get_file_list(f, lenght)
                file_info["SizeComp"] = self.fix_file_size(f, int.from_bytes(f.read(4), byteorder="big"), file_info["start_point"])
                file_info["Size"] = int.from_bytes(f.read(4), byteorder="big")
                file_info["data"] = self.unpack_farc(file_info, f)
            elif format == farc_format.AFT_RAW:
                file_info = self.get_file_list(f, lenght)
                file_info["Size"] = int.from_bytes(f.read(4), byteorder="big")
                f.seek(file_info["start_point"])
                file_info["data"] = f.read(file_info["Size"])
            else:
                raise TypeError("unsupport format")
        self.data = file_info["data"]
        self.name = file_info["name"]

    def check_format(self, farc_file):
        format = farc_file.read(4)
        if format in (farc_format.AFT, farc_format.AFT_RAW):
            return format
        else:
            raise NotImplementedError("Only Support AFT Format")

    def get_file_list(self, _info_data, lenght):
        _info_data.seek(12)
        start_point = 12
        file_list = []
        while start_point < lenght:
            file_name, start_point = self.get_file_info(_info_data, start_point)
            _info_data.seek(start_point)
            file_start_point = int.from_bytes(_info_data.read(4), byteorder="big")
            file_list.append({"name": file_name,
                              "start_point": file_start_point
                              })
            start_point = _info_data.tell()

        if len(file_list) > 1:
            raise NotImplementedError("Multi File are not support")
        return file_list[0]

    def get_file_info(self, _data, start_point):
        _data.seek(start_point)
        get_str = ""
        get_char = ""
        while get_char != b"\x00":
            if get_char != "":
                get_str += get_char.decode("utf-8")
            get_char = _data.read(1)
        end_point = _data.tell()
        return get_str, end_point

    def fix_file_size(self, _file, _SizeComp, _offset):
        _file.seek(0, 2)
        real_size = _file.tell() - _offset
        return min(_SizeComp, real_size)

    def unpack_farc(self, _file_info, _file):
        _file.seek(_file_info["start_point"])
        data = _file.read(_file_info["SizeComp"])
        return zlib.decompress(data, wbits=16 + zlib.MAX_WBITS, bufsize=_file_info["Size"])