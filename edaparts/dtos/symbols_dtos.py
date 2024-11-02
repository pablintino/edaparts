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
import typing

from pydantic import BaseModel

from edaparts.dtos.libraries_dtos import LibraryTypeEnum, StorageStatusEnum
from edaparts.models import LibraryReference


class SymbolQueryDto(BaseModel):
    id: int
    path: str
    reference: str
    cad_type: LibraryTypeEnum
    storage_status: StorageStatusEnum
    storage_error: typing.Optional[str] = None
    description: typing.Optional[str] = None
    alias: typing.Optional[str] = None

    @staticmethod
    def from_model(data: LibraryReference) -> "SymbolQueryDto":
        return SymbolQueryDto(
            id=data.id,
            path=data.path,
            reference=data.reference,
            cad_type=LibraryTypeEnum.from_model(data.cad_type),
            storage_status=StorageStatusEnum.from_model(data.storage_status),
            storage_error=data.storage_error,
            description=data.description,
            alias=data.alias,
        )


class SymbolListResultDto(BaseModel):
    page_size: int
    page_number: int
    total_elements: int
    elements: list[SymbolQueryDto]
