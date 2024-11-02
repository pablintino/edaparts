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
import pathlib
from dataclasses import dataclass
from enum import Enum


class StorableLibraryResourceType(Enum):
    FOOTPRINT = "footprint"
    SYMBOL = "symbol"


class CadType(Enum):
    ALTIUM = "altium"
    KICAD = "kicad"


class StorageStatus(Enum):
    NOT_STORED = "NOT_STORED"
    STORING = "STORING"
    STORED = "STORED"
    STORAGE_FAILED = "STORAGE_FAILED"


@dataclass(frozen=True)
class StorableObjectRequest:
    filename: pathlib.Path
    path: str
    file_type: StorableLibraryResourceType
    cad_type: CadType
    reference: str = None
    description: str = None


@dataclass(frozen=True)
class StorableObjectDataUpdateRequest:
    model_id: int
    filename: pathlib.Path
    file_type: StorableLibraryResourceType
    reference: str = None


@dataclass(frozen=True)
class StorableTask:
    model_id: int
    filename: pathlib.Path
    path: str
    file_type: StorableLibraryResourceType
    cad_type: CadType
    reference: str
