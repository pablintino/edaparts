#
# MIT License
#
# Copyright (c) 2024 Pablo Rodriguez Nava, @pablintino
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


import logging
import pathlib
import struct
from dataclasses import dataclass

from kiutils.footprint import Footprint
from kiutils.symbol import SymbolLib
from kiutils.utils import sexpr
from olefile import olefile

from edaparts.models.internal.internal_models import CadType
from edaparts.services.exceptions import ApiError
from edaparts.utils.helpers import CaseInsensitiveDict
from edaparts.models.internal.internal_models import StorableLibraryResourceType

__logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FootprintModel:
    name: str
    description: str = None


@dataclass(frozen=True)
class SymbolModel:
    name: str
    description: str = None


@dataclass(frozen=True)
class Library:
    cad_type: CadType
    models: dict[str, FootprintModel | SymbolModel]
    library_type: StorableLibraryResourceType

    def is_present(self, name: str) -> bool:
        return name in self.models

    @property
    def count(self) -> int:
        return len(self.models)


def _parse_kicad_lib(path: pathlib.Path) -> dict[str, FootprintModel | SymbolModel]:
    models: dict[str, FootprintModel | SymbolModel] = {}
    parse_paths = path.glob("*.kicad_mod") if path.is_dir() else [path]
    try:
        for model_path in parse_paths:
            parsed_expression = sexpr.parse_sexp(model_path.read_text(encoding="utf-8"))
            if (
                parsed_expression is None
                or (not isinstance(parsed_expression, list))
                or len(parsed_expression) == 0
            ):
                raise ApiError(f"Cannot fetch the library type for {model_path}")
            lib_type = parsed_expression[0]
            if lib_type == "kicad_symbol_lib":
                for parsed_symbol in SymbolLib().from_sexpr(parsed_expression).symbols:
                    description_property = next(
                        (
                            prop
                            for prop in parsed_symbol.properties
                            if prop.key == "Description"
                        ),
                        None,
                    )
                    lib_model = SymbolModel(
                        name=parsed_symbol.entryName,
                        description=(
                            description_property.value if description_property else None
                        ),
                    )
                    models[lib_model.name] = lib_model

            elif lib_type == "footprint":
                footprint_model = Footprint().from_sexpr(parsed_expression)
                lib_model = FootprintModel(
                    name=footprint_model.entryName,
                    description=footprint_model.description,
                )
                models[lib_model.name] = lib_model
            else:
                raise ApiError(f"Unrecognized/unsupported KiCAD model type {lib_type}")
    except (IOError, UnicodeDecodeError) as err:
        raise ApiError(
            f"Cannot read KiCad lib {path}", http_code=400, details=str(err)
        ) from err

    return models


def _parse_key_value_string(s):
    properties = s.decode("utf-8").strip("|").split("|")
    result = CaseInsensitiveDict()

    for prop in properties:
        x = prop.split("=")
        key = x[0]
        if len(x) > 1:
            value = x[1]
        else:
            value = ""
        result[key] = value

    return result


def _get_u32(buffer):
    (word,) = struct.unpack("<I", buffer[:4])
    return word


def _read_stream(oleobj, path):
    f = oleobj.openstream(path)
    c = True
    buffer = bytes()
    while c:
        c = f.read(1)
        if c:
            buffer += c
    f.close()
    return buffer


def _get_symbols_data(olebj):
    parts = {}
    for part in olebj.listdir(streams=True, storages=False):
        if (
            part[0]
            not in ["FileHeader", "Storage", "SectionKeys", "FileVersionInfo"]
            + list(parts.keys())
            and len(part) == 2
        ):
            # Part streams not used
            data_path = f"{part[0]}/Data"
            buffer = _read_stream(olebj, data_path)

            # Properties
            length = _get_u32(buffer[:4])
            props = _parse_key_value_string(buffer[4 : 4 + length])
            parts[part[0]] = props
    return parts


def _get_toc_data(buffer):
    # first four bytes are total string length
    # last byte is 0x00
    footprints = []
    if _get_u32(buffer) + 4 == len(buffer):
        buffer = buffer[4:-1]
        entries = (
            buffer.replace(b"\x0D\x0A", str.encode("\n"))
            .strip()
            .split(str.encode("\n"))
        )
        for entry in entries:
            footprints.append(_parse_key_value_string(entry))
    else:
        __logger.warning("Cannot read TOC data from lib. Buffer length mismatch")
    return footprints


def _parse_olefile_library(byte_data) -> dict[str, FootprintModel | SymbolModel]:
    lib_parts = {}
    with olefile.OleFileIO(byte_data) as ole:
        # Figure out what kind of file it is
        if ole.exists("FileHeader"):
            fh = ole.openstream("FileHeader")
            contents = fh.read()
            fh.close()

            if b"PCB" in contents and b"Binary Library" in contents:
                buffer = _read_stream(ole, "Library/ComponentParamsTOC/Data")
                parts = _get_toc_data(buffer)
                for part in parts:
                    name = part.get("Name", None)
                    lib_parts[name] = FootprintModel(
                        name=name,
                        description=part.get("Description", None),
                    )
            elif b"Schematic Library" in contents:
                for part_k, part_v in _get_symbols_data(ole).items():
                    lib_parts[part_k] = SymbolModel(
                        name=part_k,
                        description=part_v.get("ComponentDescription", None),
                    )
            else:
                __logger.warning("Non supported library type")

    return lib_parts


def parse_file(path: pathlib.Path, cad_type: CadType) -> Library:
    if cad_type == CadType.KICAD:
        models = _parse_kicad_lib(path)
    elif cad_type == CadType.ALTIUM:
        models = _parse_olefile_library(path)
    else:
        raise ApiError(f"Unsupported cad_type {cad_type}")

    if not models:
        raise ApiError("The given KiCAD file is empty", http_code=400)

    return Library(
        cad_type=cad_type,
        models=models,
        library_type=(
            StorableLibraryResourceType.FOOTPRINT
            if isinstance(next(iter(models.values())), FootprintModel)
            else StorableLibraryResourceType.SYMBOL
        ),
    )
