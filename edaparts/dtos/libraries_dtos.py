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


import typing
from enum import Enum

from pydantic import BaseModel, model_validator

from edaparts.models import FootprintReference, LibraryReference
from edaparts.models.internal.internal_models import (
    CadType,
    StorageStatus,
    StorableObjectCreateReuseRequest,
    StorableLibraryResourceType,
    StorableObjectUpdateRequest,
)


class LibraryTypeEnum(Enum):
    ALTIUM = "altium"
    KICAD = "kicad"

    @staticmethod
    def to_model(data: "LibraryTypeEnum") -> CadType:
        if data == LibraryTypeEnum.ALTIUM:
            return CadType.ALTIUM
        if data == LibraryTypeEnum.KICAD:
            return CadType.KICAD
        raise ValueError(data)

    @staticmethod
    def from_model(data: CadType) -> "LibraryTypeEnum":
        if data == CadType.ALTIUM:
            return LibraryTypeEnum.ALTIUM
        if data == CadType.KICAD:
            return LibraryTypeEnum.KICAD
        raise ValueError(data)


class StorageStatusEnum(Enum):
    NOT_STORED = "NOT_STORED"
    STORING = "STORING"
    STORED = "STORED"
    STORAGE_FAILED = "STORAGE_FAILED"

    @staticmethod
    def to_model(data: "StorageStatusEnum") -> StorageStatus:
        if data == StorageStatusEnum.NOT_STORED:
            return StorageStatus.NOT_STORED
        if data == StorageStatusEnum.STORING:
            return StorageStatus.STORING
        if data == StorageStatusEnum.STORED:
            return StorageStatus.STORED
        if data == StorageStatusEnum.STORAGE_FAILED:
            return StorageStatus.STORAGE_FAILED
        raise ValueError(data)

    @staticmethod
    def from_model(data: StorageStatus) -> "StorageStatusEnum":
        if data == StorageStatus.NOT_STORED:
            return StorageStatusEnum.NOT_STORED
        if data == StorageStatus.STORING:
            return StorageStatusEnum.STORING
        if data == StorageStatus.STORED:
            return StorageStatusEnum.STORED
        if data == StorageStatus.STORAGE_FAILED:
            return StorageStatusEnum.STORAGE_FAILED
        raise ValueError(data)


class BaseLibraryQueryDto(BaseModel):
    id: int
    path: str
    reference: str
    cad_type: LibraryTypeEnum
    storage_status: StorageStatusEnum
    storage_error: typing.Optional[str] = None
    description: typing.Optional[str] = None
    alias: typing.Optional[str] = None

    @staticmethod
    def from_model[
        T
    ](model_type: typing.Type[T], data: LibraryReference | FootprintReference) -> T:
        return model_type(
            id=data.id,
            path=data.path,
            reference=data.reference,
            cad_type=LibraryTypeEnum.from_model(data.cad_type),
            storage_status=StorageStatusEnum.from_model(data.storage_status),
            storage_error=data.storage_error,
            description=data.description,
            alias=data.alias,
        )


class CommonObjectFromExistingCreateDto(BaseModel):
    path: str
    reference: str
    cad_type: LibraryTypeEnum
    description: typing.Optional[str] = None

    def to_model(
        self, file_type: StorableLibraryResourceType
    ) -> StorableObjectCreateReuseRequest:
        return StorableObjectCreateReuseRequest(
            path=self.path,
            reference=self.reference,
            description=self.description,
            cad_type=LibraryTypeEnum.to_model(self.cad_type),
            file_type=file_type,
        )


class CommonObjectUpdateDto(BaseModel):
    cad_type: typing.Optional[LibraryTypeEnum] = None
    reference: typing.Optional[str] = None
    description: typing.Optional[str] = None

    def to_model(
        self, file_type: StorableLibraryResourceType
    ) -> StorableObjectUpdateRequest:
        return StorableObjectUpdateRequest(
            reference=self.reference,
            description=self.description,
            cad_type=LibraryTypeEnum.to_model(self.cad_type) if self.cad_type else None,
            file_type=file_type,
        )

    @model_validator(mode="after")
    def cad_type_present_if_ref(self):
        if self.reference and not self.cad_type:
            raise ValueError("if 'reference' is given 'cad_type' is mandatory")
        return self
