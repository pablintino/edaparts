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
from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import inspect

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
