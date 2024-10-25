#
# MIT License
#
# Copyright (c) 2020 Pablo Rodriguez Nava, @pablintino
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
from typing import Optional, Annotated

from pydantic import BaseModel, Field

from edaparts.dtos.components_dtos import ComponentSpecificQueryDto
from edaparts.models.internal.internal_inventory_models import (
    MassStockMovement,
    SingleStockMovement,
)
from edaparts.models.inventory.inventory_category_model import InventoryCategoryModel
from edaparts.models.inventory.inventory_item_model import InventoryItemModel
from edaparts.models.inventory.inventory_item_property import InventoryItemPropertyModel
from edaparts.models.inventory.inventory_location import InventoryLocationModel


class InventoryItemCreateRequestDto(BaseModel):
    mpn: str = Field(max_length=100)
    manufacturer: str = Field(max_length=100)
    name: str = Field(max_length=100)
    description: str = Field(max_length=100)
    last_buy_price: typing.Optional[float] = Field(default=None)

    @staticmethod
    def to_model(data):
        return InventoryItemModel(
            mpn=data.mpn,
            manufacturer=data.manufacturer,
            name=data.name,
            description=data.description,
            last_buy_price=data.last_buy_price,
        )


class InventoryItemQueryDto(InventoryItemCreateRequestDto):
    id: int
    dici: str = Field(max_length=70)
    component: ComponentSpecificQueryDto | None

    @staticmethod
    def from_model(data, component_dto: ComponentSpecificQueryDto = None):
        return InventoryItemQueryDto(
            id=data.id,
            mpn=data.mpn,
            manufacturer=data.manufacturer,
            name=data.name,
            description=data.description,
            last_buy_price=data.last_buy_price,
            dici=data.dici,
            component=component_dto,
        )


class InventoryItemsQueryDto(BaseModel):
    page_size: int
    page_number: int
    total_elements: int
    elements: list[InventoryItemQueryDto]


class InventoryLocationCreateDto(BaseModel):
    name: str
    description: Optional[str] = None


class InventoryLocationQueryDto(BaseModel):
    id: int
    dici: str
    name: str
    description: Optional[str] = None

    @staticmethod
    def from_model(data: InventoryLocationModel):
        return InventoryLocationQueryDto(
            id=data.id, name=data.name, dici=data.dici, description=data.description
        )


class InventoryLocationsQueryDto(BaseModel):
    page_size: int
    page_number: int
    total_elements: int
    elements: list[InventoryLocationQueryDto]


class InventoryItemLocationRelationDto:

    def __init__(self, location_ids):
        self.location_ids = location_ids

    @staticmethod
    def from_model(location_ids):
        return InventoryItemLocationRelationDto(location_ids=location_ids)


class InventoryItemLocationStockDto:

    def __init__(
        self,
        id=None,
        actual_stock=None,
        stock_min_level=None,
        stock_notify_min_level=None,
    ):
        self.id = id
        self.actual_stock = actual_stock
        self.stock_min_level = stock_min_level
        self.stock_notify_min_level = stock_notify_min_level

    @staticmethod
    def from_model(data):
        return InventoryItemLocationStockDto(
            id=data.id,
            actual_stock=data.actual_stock,
            stock_min_level=data.stock_min_level,
            stock_notify_min_level=data.stock_notify_min_level,
        )


class InventorySingleStockMovementDto:
    def __init__(
        self,
        quantity,
        location_dici=None,
        location_id=None,
        item_dici=None,
        item_id=None,
    ):
        self.location_dici = location_dici
        self.location_id = location_id
        self.item_id = item_id
        self.item_dici = item_dici
        self.quantity = quantity

    @staticmethod
    def to_model(data):
        return SingleStockMovement(
            item_dici=data.item_dici,
            item_id=data.item_id,
            location_id=data.location_id,
            location_dici=data.location_dici,
            quantity=data.quantity,
        )


class InventoryMassStockMovementDto:
    def __init__(self, reason, comment=None, movements=None):
        self.reason = reason
        self.comment = comment
        self.movements = movements

    @staticmethod
    def to_model(data):
        return MassStockMovement(
            reason=data.reason,
            comment=data.comment,
            movements=[
                InventorySingleStockMovementDto.to_model(ent) for ent in data.movements
            ],
        )


class InventoryItemStockStatusDto:
    def __init__(self, stock_level, item_dici, location_dici):
        self.stock_level = stock_level
        self.item_dici = item_dici
        self.location_dici = location_dici

    @staticmethod
    def from_model(data):
        return InventoryItemStockStatusDto(
            stock_level=data.stock_level,
            item_dici=data.item_dici,
            location_dici=data.location_dici,
        )


class InventoryMassStockMovementResultDto:

    def __init__(self, stock_levels):
        self.stock_levels = stock_levels

    @staticmethod
    def from_model(data):
        return InventoryMassStockMovementResultDto(
            stock_levels=[
                InventoryItemStockStatusDto.from_model(ent) for ent in data.stock_levels
            ]
        )


class InventoryItemPropertyCreateRequestDto(BaseModel):
    name: str = Field(max_length=100)
    value: Annotated[str, Field(max_length=100)] | int | float

    @staticmethod
    def to_model(
        data: "InventoryItemPropertyCreateRequestDto",
    ) -> InventoryItemPropertyModel:
        model = InventoryItemPropertyModel(property_name=data.name)
        model.set_value(data.value)
        return model


class InventoryItemPropertyQueryDto(InventoryItemPropertyCreateRequestDto):
    id: int

    @staticmethod
    def from_model(
        data: InventoryItemPropertyModel,
    ) -> "InventoryItemPropertyQueryDto":
        return InventoryItemPropertyQueryDto(
            id=data.id, name=data.property_name, value=data.get_value()
        )


class InventoryItemPropertyUpdateDto(BaseModel):
    value: Annotated[str, Field(max_length=100)] | int | float


class InventoryCategoryCreateUpdateRequestDto(BaseModel):
    name: str = Field(max_length=100)
    description: str | None = Field(max_length=100, default=None)


class InventoryCategoryQueryDto(InventoryCategoryCreateUpdateRequestDto):
    id: int
    parent_id: Optional[int]

    @staticmethod
    def from_model(data: InventoryCategoryModel) -> "InventoryCategoryQueryDto":
        return InventoryCategoryQueryDto(
            id=data.id,
            name=data.name,
            description=data.description,
            parent_id=data.parent_id,
        )


class InventoryCategoriesQueryDto(BaseModel):
    page_size: int
    page_number: int
    total_elements: int
    elements: list[InventoryCategoryQueryDto]


class InventoryCategoryReferenceCreationUpdateDto(BaseModel):
    category_id: int
