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
from edaparts.models.components import SwitchPushButtonModel


class SwitchPushButtonBaseDto(ComponentCommonBaseFields):
    type: Literal["switch_push_button"]
    function: str | None = Field(default=None, max_length=50)
    dc_voltage_rating: str | None = Field(default=None, max_length=30)
    ac_voltage_rating: str | None = Field(default=None, max_length=30)
    current_rating: str | None = Field(default=None, max_length=30)
    circuit_type: str | None = Field(default=None, max_length=50)

    def to_model(self) -> SwitchPushButtonModel:
        return self._fill_model(SwitchPushButtonModel())

    @staticmethod
    def model_type() -> typing.Type:
        return SwitchPushButtonModel


class SwitchPushButtonQueryDto(SwitchPushButtonBaseDto, ComponentQueryRequestBaseDto):
    pass


class SwitchPushButtonCreateRequestDto(
    SwitchPushButtonBaseDto, ComponentCreateRequestBaseDto
):
    pass


class SwitchPushButtonUpdateRequestDto(
    SwitchPushButtonBaseDto, ComponentUpdateRequestBaseDto
):
    pass
