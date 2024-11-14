import typing

from pydantic import BaseModel

from edaparts.models.components.component_model import ComponentModel
from edaparts.models.internal.kicad_models import KiCadPart, KiCadPartProperty


class EndpointsQueryDto(BaseModel):
    categories: str
    parts: str

    @staticmethod
    def build(categories=None, parts=None) -> "EndpointsQueryDto":
        return EndpointsQueryDto(categories=categories or "", parts=parts or "")


class CategoryQueryDto(BaseModel):
    id: str
    name: str


class CategoryPartQueryDto(BaseModel):
    id: str
    name: str
    description: typing.Optional[str]

    @staticmethod
    def from_model(data: ComponentModel) -> "CategoryPartQueryDto":
        return CategoryPartQueryDto(
            id=str(data.id),
            name=data.mpn,
            description=data.description,
        )


class PartFieldQueryDto(BaseModel):
    value: str
    visible: str

    @staticmethod
    def from_model(data: KiCadPartProperty) -> "PartFieldQueryDto":
        return PartFieldQueryDto(
            value=data.value, visible="True" if data.visible else "False"
        )


class PartQueryDto(BaseModel):
    id: str
    name: str
    symbolIdStr: str
    fields: typing.Dict[str, PartFieldQueryDto]

    @staticmethod
    def from_model(data: KiCadPart) -> "PartQueryDto":
        return PartQueryDto(
            id=str(data.id),
            name=data.name,
            symbolIdStr=data.symbolIdStr,
            fields={k: PartFieldQueryDto.from_model(v) for k, v in data.fields.items()},
        )


CategoriesQueryDto = typing.List[CategoryQueryDto]
CategoryPartsQueryDto = typing.List[CategoryPartQueryDto]
