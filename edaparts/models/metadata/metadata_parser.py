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


from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty

from edaparts.services.database import Base
from edaparts.models import ModelDescriptor
from edaparts.services.exceptions import GenericIntenalApiError
from edaparts.utils.helpers import BraceMessage


class MetadataParser:

    @staticmethod
    def __get_all_alquemy_models():
        return [
            cls
            for cls in Base.registry._class_registry.values()
            if isinstance(cls, type) and issubclass(cls, Base)
        ]

    @staticmethod
    def model_exists_by_name(model_name):
        return any(
            cls.__tablename__ == model_name
            for cls in MetadataParser.__get_all_alquemy_models()
        )

    @staticmethod
    def __get_model_from_alquemy(name, raise_ex=True):
        if not name:
            raise GenericIntenalApiError("SQLAlchemy model name cannot be empty")

        models = [
            cls
            for cls in MetadataParser.__get_all_alquemy_models()
            if cls.__tablename__ == name
        ]
        if (not MetadataParser.model_exists_by_name(name)) and raise_ex:
            raise GenericIntenalApiError(
                BraceMessage(
                    "SQLAlquemy model parse has failed cause model {0} cannot be found",
                    name,
                )
            )
        return models[0]

    @staticmethod
    def __get_alquemy_model_metadata(model):
        mapper = inspect(model)
        descriptor = ModelDescriptor(model.__name__)
        for attr in mapper.attrs:
            if type(attr) is ColumnProperty:
                descriptor.add_field(
                    attr.key,
                    attr.expression.unique
                    or attr.expression.primary_key
                    or attr.expression.nullable is False,
                    attr.expression.primary_key,
                    attr.expression.type.python_type,
                )
        return descriptor

    def __init__(self):
        self.mappers = {}

    def get_model_by_name(self, model_name):
        if model_name in self.mappers:
            model = self.mappers.get(model_name)
        else:
            model = MetadataParser.__get_model_from_alquemy(model_name)
            self.mappers[model_name] = model

        return model

    def get_model_children_by_parent_name(self, parent_name):
        parent_mapper = inspect(self.get_model_by_name(parent_name))
        children_mappers = {
            k: v
            for k, v in parent_mapper.polymorphic_map.items()
            if parent_mapper.polymorphic_map[k].polymorphic_identity
            != parent_mapper.polymorphic_identity
        }.values()
        return [mapper.entity for mapper in children_mappers]

    def get_model_metadata_by_name(self, model_name):
        return MetadataParser.__get_alquemy_model_metadata(
            self.get_model_by_name(model_name)
        )

    @staticmethod
    def get_model_metadata_by_model(model):
        if not issubclass(model, Base):
            raise GenericIntenalApiError("The given model is not a SQLAlquemy one")

        return MetadataParser.__get_alquemy_model_metadata(model)

    def get_model_children_by_parent_model(self, model):
        if not issubclass(model, Base):
            raise GenericIntenalApiError("The given model is not a SQLAlquemy one")

        return self.get_model_children_by_parent_name(model.__tablename__)


metadata_parser = MetadataParser()
