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
from edaparts.models.components import DiscreteLogicModel


class DiscreteLogicBaseDto(ComponentCommonBaseFields):
    component_type: Literal["discrete_logic"]
    logic_family: str | None = Field(default=None, max_length=30)
    logic_type: str | None = Field(default=None, max_length=30)
    number_of_bits: str | None = Field(default=None, max_length=30)
    propagation_delay: str | None = Field(default=None, max_length=30)
    supply_voltage_max: str | None = Field(default=None, max_length=30)
    supply_voltage_min: str | None = Field(default=None, max_length=30)
    logic_function: str | None = Field(default=None, max_length=100)

    def to_model(self) -> DiscreteLogicModel:
        return self._fill_model(DiscreteLogicModel())

    @staticmethod
    def model_type() -> typing.Type:
        return DiscreteLogicModel


class DiscreteLogicQueryDto(DiscreteLogicBaseDto, ComponentQueryRequestBaseDto):
    pass


class DiscreteLogicCreateRequestDto(
    DiscreteLogicBaseDto, ComponentCreateRequestBaseDto
):
    pass


class DiscreteLogicUpdateRequestDto(
    DiscreteLogicBaseDto, ComponentUpdateRequestBaseDto
):
    pass
