#
# MIT License
#
# Copyright (c) 2020 Pablo Rodriguez Nava, @pablintino
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#


import struct
from enum import Enum
import olefile
import logging

from edaparts.utils.helpers import CaseInsensitiveDict

__logger = logging.getLogger(__name__)


class PcbComponent:

    def __init__(self, name, pad_count, height, description):
        self.name = name
        self.pad_count = pad_count
        self.height = height
        self.description = description

    def __repr__(self):
        return '%s(%r)' % (self.__class__, self.__dict__)


class SchComponent:

    def __init__(self, lib_reference, part_count, description):
        self.name = lib_reference
        self.part_count = part_count
        self.description = description

    def __repr__(self):
        return '%s(%r)' % (self.__class__, self.__dict__)


class LibType(Enum):
    SCH = "Schematic"
    PCB = "PCB"


class Library:

    def __init__(self, lib_type, parts):
        self.lib_type = lib_type
        self.parts = parts
        self.count = len(parts)

    def __repr__(self):
        return '%s(%r)' % (self.__class__, self.__dict__)

    def get_part_names(self):
        return list(self.parts.keys())

    def part_exists(self, name):
        return name in self.parts.keys()


def parse_key_value_string(s):
    properties = s.decode('utf-8').strip('|').split('|')
    result = CaseInsensitiveDict()

    for prop in properties:
        x = prop.split('=')
        key = x[0]
        if len(x) > 1:
            value = x[1]
        else:
            value = ""
        result[key] = value

    return result


def get_u32(buffer):
    (word,) = struct.unpack('<I', buffer[:4])
    return word


def read_stream(oleobj, path):
    f = oleobj.openstream(path)
    c = True
    buffer = bytes()
    while c:
        c = f.read(1)
        if c:
            buffer += c
    f.close()
    return buffer


def get_symbols_data(olebj):
    parts = {}
    for part in olebj.listdir(streams=True, storages=False):
        if part[0] not in ['FileHeader', 'Storage', 'SectionKeys', 'FileVersionInfo'] + list(parts.keys()) and len(part) == 2:
            # Part streams not used
            data_path = f'{part[0]}/Data'
            buffer = read_stream(olebj, data_path)

            # Properties
            length = get_u32(buffer[:4])
            props = parse_key_value_string(buffer[4:4 + length])
            parts[part[0]] = props
    return parts


def get_toc_data(buffer):
    # first four bytes are total string length
    # last byte is 0x00
    footprints = []
    if get_u32(buffer) + 4 == len(buffer):
        buffer = buffer[4:-1]
        entries = buffer.replace(b'\x0D\x0A', str.encode('\n')).strip().split(str.encode('\n'))
        for entry in entries:
            footprints.append(parse_key_value_string(entry))
    else:
        __logger.warning('Cannot read TOC data from lib. Buffer length mismatch')
    return footprints


def parse_olefile_library(byte_data):
    lib_parts = {}
    with olefile.OleFileIO(byte_data) as ole:
        # Figure out what kind of file it is
        if ole.exists("FileHeader"):
            fh = ole.openstream("FileHeader")
            contents = fh.read()
            fh.close()

            if b"PCB" in contents and b"Binary Library" in contents:
                buffer = read_stream(ole, 'Library/ComponentParamsTOC/Data')
                parts = get_toc_data(buffer)
                for part in parts:
                    name = part.get('Name', None)
                    lib_parts[name] = PcbComponent(name=name,
                                                   description=part.get('Description', None),
                                                   pad_count=part.get('Pad Count', None),
                                                   height=part.get('Height', None),
                                                   )

                lib = Library(LibType.PCB, lib_parts)

            elif b"Schematic Library" in contents:
                for part_k, part_v in get_symbols_data(ole).items():
                    lib_parts[part_k] = SchComponent(
                        lib_reference=part_v.get('LibReference', None),
                        description=part_v.get('ComponentDescription', None),
                        part_count=part_v.get('PartCount', None),
                    )

                lib = Library(LibType.SCH, lib_parts)
            else:
                __logger.warning('Non supported library type')
    if lib:
        part_list = ', '.join(lib.get_part_names())
        __logger.debug(f'Library parsed parts: {part_list}')
    return lib
