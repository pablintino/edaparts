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
from typing import Literal

from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import inspect
from typing_extensions import Annotated

from edaparts.models.components import ComponentModelType
from edaparts.models.components.capacitor_ceramic_model import CapacitorCeramicModel
from edaparts.models.components.capacitor_electrolytic_model import (
    CapacitorElectrolyticModel,
)
from edaparts.models.components.capacitor_tantalum_model import CapacitorTantalumModel
from edaparts.models.components.resistor_model import ResistorModel
from edaparts.models.components.component_model import ComponentModel


class ComponentCommentToolFields(BaseModel):
    kicad: str | None = Field(default=None, max_length=100)
    altium: str | None = Field(default=None, max_length=100)

    @staticmethod
    def from_model(model: ComponentModel) -> "ComponentCommentToolFields":
        return ComponentCommentToolFields(
            kicad=model.comment_kicad, altium=model.comment_altium
        )


class ComponentCommonBaseFields:
    value: str | None = Field(default=None, max_length=100)
    package: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=100)
    is_through_hole: bool | None = Field(default=None)
    operating_temperature_min: str | None = Field(default=None, max_length=30)
    operating_temperature_max: str | None = Field(default=None, max_length=30)

    def _fill_model[T](self, model: T):
        for k, v in vars(self).items():
            if k in inspect(type(model)).attrs.keys():
                setattr(model, k, v)
        return model


class ComponentProtectedBaseFields:
    mpn: str = Field(max_length=100)
    manufacturer: str = Field(max_length=100)


class ComponentGeneratedBaseFields:
    id: int
    created_on: datetime
    updated_on: datetime


class ComponentCreateRequestBaseDto(
    ComponentCommonBaseFields, ComponentProtectedBaseFields, BaseModel
):
    comment: str | ComponentCommentToolFields | None = Field(default=None)

    def _fill_model[T](self, model: T) -> T:
        super()._fill_model(model)
        if isinstance(self.comment, str):
            model.comment_altium = self.comment
            model.comment_kicad = self.comment
        elif isinstance(self.comment, ComponentCommentToolFields):
            model.comment_altium = self.comment.altium
            model.comment_kicad = self.comment.kicad
        return model


class ComponentUpdateRequestBaseDto(ComponentCommonBaseFields, BaseModel):
    pass


class ComponentQueryRequestBaseDto(
    ComponentCommonBaseFields,
    ComponentProtectedBaseFields,
    ComponentGeneratedBaseFields,
    BaseModel,
):
    comment: ComponentCommentToolFields | None = Field(default=None)

    def _fill_dto[T](self, model: ComponentModel) -> T:
        self.comment = ComponentCommentToolFields.from_model(model)
        return self


# Resistor DTOs
class ResistorBaseFieldsDto(BaseModel):
    type: Literal["resistor"]
    power_max: str | None = Field(default=None, max_length=30)
    tolerance: str | None = Field(default=None, max_length=30)

    def to_model(self) -> ResistorModel:
        return self._fill_model(ResistorModel())


class ResistorQueryDto(ResistorBaseFieldsDto, ComponentQueryRequestBaseDto):
    pass


class ResistorCreateRequestDto(ResistorBaseFieldsDto, ComponentCreateRequestBaseDto):
    pass


class ResistorUpdateRequestDto(ResistorBaseFieldsDto, ComponentUpdateRequestBaseDto):
    pass


# Ceramic Capacitors DTOs
class CapacitorCeramicBaseDto(ComponentCommonBaseFields):
    type: Literal["capacitor_ceramic"]
    tolerance: str | None = Field(default=None, max_length=30)
    voltage: str | None = Field(default=None, max_length=30)
    composition: str | None = Field(default=None, max_length=30)

    def to_model(self) -> CapacitorCeramicModel:
        return self._fill_model(CapacitorCeramicModel())


class CapacitorCeramicQueryDto(CapacitorCeramicBaseDto, ComponentQueryRequestBaseDto):
    pass


class CapacitorCeramicCreateRequestDto(
    CapacitorCeramicBaseDto, ComponentCreateRequestBaseDto
):
    pass


class CapacitorCeramicUpdateRequestDto(
    CapacitorCeramicBaseDto, ComponentUpdateRequestBaseDto
):
    pass


# Electrolytic Capacitors DTOs
class CapacitorElectrolyticBaseDto(ComponentCommonBaseFields):
    type: Literal["capacitor_electrolytic"]
    tolerance: str | None = Field(default=None, max_length=30)
    voltage: str | None = Field(default=None, max_length=30)
    material: str | None = Field(default=None, max_length=30)
    polarised: bool | None = Field(default=None)
    esr: str | None = Field(default=None, max_length=30)
    lifetime_temperature: str | None = Field(default=None, max_length=30)

    def to_model(self) -> CapacitorElectrolyticModel:
        return self._fill_model(CapacitorElectrolyticModel())


class CapacitorElectrolyticQueryDto(
    CapacitorElectrolyticBaseDto, ComponentQueryRequestBaseDto
):
    pass


class CapacitorElectrolyticCreateRequestDto(
    CapacitorElectrolyticBaseDto, ComponentCreateRequestBaseDto
):
    pass


class CapacitorElectrolyticUpdateRequestDto(
    CapacitorElectrolyticBaseDto, ComponentUpdateRequestBaseDto
):
    pass


# Tantalum Capacitors DTOs
class CapacitorTantalumBaseDto(ComponentCommonBaseFields):
    type: Literal["capacitor_tantalum"]
    tolerance: str | None = Field(default=None, max_length=30)
    voltage: str | None = Field(default=None, max_length=30)
    esr: str | None = Field(default=None, max_length=30)
    lifetime_temperature: str | None = Field(default=None, max_length=30)

    def to_model(self) -> CapacitorTantalumModel:
        return self._fill_model(CapacitorTantalumModel())


class CapacitorTantalumQueryDto(CapacitorTantalumBaseDto, ComponentQueryRequestBaseDto):
    pass


class CapacitorTantalumCreateRequestDto(
    CapacitorTantalumBaseDto, ComponentCreateRequestBaseDto
):
    pass


class CapacitorTantalumUpdateRequestDto(
    CapacitorTantalumBaseDto, ComponentUpdateRequestBaseDto
):
    pass


# Generic DTO aliases
class ComponentCreateRequestDto(BaseModel):
    component: typing.Union[
        CapacitorCeramicCreateRequestDto,
        CapacitorElectrolyticCreateRequestDto,
        CapacitorTantalumCreateRequestDto,
        ResistorCreateRequestDto,
    ] = Field(..., discriminator="type")


class ComponentUpdateRequestDto(BaseModel):
    component: typing.Union[
        CapacitorCeramicUpdateRequestDto,
        CapacitorElectrolyticUpdateRequestDto,
        CapacitorTantalumUpdateRequestDto,
        ResistorUpdateRequestDto,
    ] = Field(..., discriminator="type")


ComponentQueryDtoUnionAlias = (
    CapacitorCeramicQueryDto
    | CapacitorElectrolyticQueryDto
    | CapacitorTantalumQueryDto
    | ResistorQueryDto
)

ComponentSpecificQueryDto = Annotated[
    ComponentQueryDtoUnionAlias, Field(discriminator="type")
]

_model_to_query_dto = {
    CapacitorCeramicModel: CapacitorCeramicQueryDto,
    CapacitorElectrolyticModel: CapacitorElectrolyticQueryDto,
    CapacitorTantalumModel: CapacitorTantalumQueryDto,
    ResistorModel: ResistorQueryDto,
}


def map_component_model_to_query_dto(
    model: ComponentModelType,
) -> ComponentSpecificQueryDto:
    dto_t = _model_to_query_dto[type(model)]
    dto_data = {
        c.key: getattr(model, c.key)
        for c in inspect(model).mapper.column_attrs
        if c.key in dto_t.model_fields
    }
    mapped_dto = dto_t(**dto_data)
    return mapped_dto._fill_dto(model)


# todo: try to use a generic schema for list operations
class ComponentsListResultDto(BaseModel):
    page_size: int
    page_number: int
    total_elements: int
    elements: list[ComponentSpecificQueryDto]
