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


from pydantic import BaseModel, Field
from sqlalchemy import inspect
from typing_extensions import Annotated

from edaparts.dtos.components import (
    ComponentCreateRequestDtoUnionAlias,
    ComponentUpdateRequestDtoUnionAlias,
    ComponentQueryDtoUnionAlias,
    CapacitorCeramicQueryDto,
    CapacitorElectrolyticQueryDto,
    CapacitorTantalumQueryDto,
    ConnectorPcbQueryDto,
    CrystalOscillatorQueryDto,
    DiodeRectifierQueryDto,
    DiodeTvsQueryDto,
    DiodeZenerQueryDto,
    DiscreteLogicQueryDto,
    FerriteBeadQueryDto,
    FusePPTCQueryDto,
    ResistorQueryDto,
)
from edaparts.models.components import (
    ComponentModelType,
    CapacitorCeramicModel,
    CapacitorElectrolyticModel,
    CapacitorTantalumModel,
    ConnectorPcbModel,
    CrystalOscillatorModel,
    DiodeRectifierModel,
    DiodeTVSModel,
    DiodeZenerModel,
    DiscreteLogicModel,
    FerriteBeadModel,
    FusePPTCModel,
    ResistorModel,
)


# Generic DTO aliases
class ComponentCreateRequestDto(BaseModel):
    component: ComponentCreateRequestDtoUnionAlias = Field(..., discriminator="type")


class ComponentUpdateRequestDto(BaseModel):
    component: ComponentUpdateRequestDtoUnionAlias = Field(..., discriminator="type")


ComponentSpecificQueryDto = Annotated[
    ComponentQueryDtoUnionAlias, Field(discriminator="type")
]

_model_to_query_dto = {
    CapacitorCeramicModel: CapacitorCeramicQueryDto,
    CapacitorElectrolyticModel: CapacitorElectrolyticQueryDto,
    CapacitorTantalumModel: CapacitorTantalumQueryDto,
    ConnectorPcbModel: ConnectorPcbQueryDto,
    CrystalOscillatorModel: CrystalOscillatorQueryDto,
    DiodeRectifierModel: DiodeRectifierQueryDto,
    DiodeTVSModel: DiodeTvsQueryDto,
    DiodeZenerModel: DiodeZenerQueryDto,
    DiscreteLogicModel: DiscreteLogicQueryDto,
    FerriteBeadModel: FerriteBeadQueryDto,
    FusePPTCModel: FusePPTCQueryDto,
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
