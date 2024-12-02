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

    def fill_common_fields[T](self, model: T):
        for k, v in vars(self).items():
            if k in inspect(type(model)).attrs.keys():
                setattr(model, k, v)
        if hasattr(model, "__tablename__"):
            model.type = model.__tablename__

    @staticmethod
    def model_type() -> typing.Type:
        raise NotImplementedError()


class ComponentProtectedBaseFields:
    mpn: str = Field(max_length=100)
    manufacturer: str = Field(max_length=100)


class ComponentCommentBaseFields:
    comment: str | ComponentCommentToolFields | None = Field(default=None)

    def fill_model_comments[T](self, model: T):
        if isinstance(self.comment, str):
            model.comment_altium = self.comment
            model.comment_kicad = self.comment
        elif isinstance(self.comment, ComponentCommentToolFields):
            model.comment_altium = self.comment.altium
            model.comment_kicad = self.comment.kicad

    def fill_dto_comments(self, model: ComponentModel):
        self.comment = ComponentCommentToolFields.from_model(model)


class ComponentGeneratedBaseFields:
    id: int
    created_on: datetime
    updated_on: datetime


class ComponentCreateRequestBaseDto(
    ComponentCommonBaseFields,
    ComponentProtectedBaseFields,
    ComponentCommentBaseFields,
    BaseModel,
):
    def to_model[T](self) -> T:
        model = self.model_type()()
        self.fill_common_fields(model)
        self.fill_model_comments(model)
        return model


class ComponentUpdateRequestBaseDto(
    ComponentCommonBaseFields, ComponentCommentBaseFields, BaseModel
):
    def to_model[T](self) -> T:
        model = self.model_type()()
        self.fill_common_fields(model)
        self.fill_model_comments(model)
        return model


class ComponentQueryRequestBaseDto(
    ComponentCommonBaseFields,
    ComponentProtectedBaseFields,
    ComponentGeneratedBaseFields,
    ComponentCommentBaseFields,
    BaseModel,
):
    def fill_dto(self, model: ComponentModel) -> "ComponentQueryRequestBaseDto":
        self.fill_dto_comments(model)
        return self
