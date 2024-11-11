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

from pydantic import Field

from edaparts.dtos.components.common_dtos import (
    ComponentCommonBaseFields,
    ComponentQueryRequestBaseDto,
    ComponentCreateRequestBaseDto,
    ComponentUpdateRequestBaseDto,
)
from edaparts.models.components import TransistorMosfetModel


class TransistorMosfetBaseDto(ComponentCommonBaseFields):
    component_type: Literal["transistor_mosfet"]
    rds_on: str | None = Field(default=None, max_length=30)
    vgs_max: str | None = Field(default=None, max_length=30)
    vgs_th: str | None = Field(default=None, max_length=30)
    vds_max: str | None = Field(default=None, max_length=30)
    ids_max: str | None = Field(default=None, max_length=30)
    power_max: str | None = Field(default=None, max_length=30)
    channel_type: str | None = Field(default=None, max_length=30)

    def to_model(self) -> TransistorMosfetModel:
        return self._fill_model(TransistorMosfetModel())

    @staticmethod
    def model_type() -> typing.Type:
        return TransistorMosfetModel


class TransistorMosfetQueryDto(TransistorMosfetBaseDto, ComponentQueryRequestBaseDto):
    pass


class TransistorMosfetCreateRequestDto(
    TransistorMosfetBaseDto, ComponentCreateRequestBaseDto
):
    pass


class TransistorMosfetUpdateRequestDto(
    TransistorMosfetBaseDto, ComponentUpdateRequestBaseDto
):
    pass
