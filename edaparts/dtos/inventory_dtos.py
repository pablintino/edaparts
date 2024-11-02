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
from typing import Optional, Annotated

from pydantic import BaseModel, Field

from edaparts.dtos.components_dtos import ComponentSpecificQueryDto
from edaparts.models.internal.internal_inventory_models import (
    MassStockMovement,
    SingleStockMovement,
    InventoryItemStockStatus,
)
from edaparts.models.inventory.inventory_category_model import InventoryCategoryModel
from edaparts.models.inventory.inventory_item_model import InventoryItemModel
from edaparts.models.inventory.inventory_item_property import InventoryItemPropertyModel
from edaparts.models.inventory.inventory_location import InventoryLocationModel
from edaparts.models.inventory.inventory_item_location_stock import (
    InventoryItemLocationStockModel,
)


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


class InventoryItemLocationReferenceDto(BaseModel):
    location_ids: list[int | str]


class InventoryItemLocationStockUpdateResourceDto(BaseModel):
    stock_min_level: Optional[float] = None
    stock_notify_min_level: Optional[float] = None


class InventoryItemLocationStockQueryDto(InventoryItemLocationStockUpdateResourceDto):
    id: int
    actual_stock: float

    @staticmethod
    def from_model(
        data: InventoryItemLocationStockModel,
    ) -> "InventoryItemLocationStockQueryDto":
        return InventoryItemLocationStockQueryDto(
            id=data.id,
            actual_stock=data.actual_stock,
            stock_min_level=data.stock_min_level,
            stock_notify_min_level=data.stock_notify_min_level,
        )


class InventorySingleStockMovementRequestDto(BaseModel):
    quantity: float
    location_id: str | int
    item_id: str | int

    @staticmethod
    def to_model(data: "InventorySingleStockMovementRequestDto") -> SingleStockMovement:
        return SingleStockMovement(
            item_identifier=data.item_id,
            location_identifier=data.location_id,
            quantity=data.quantity,
        )


class InventoryMassStockMovementDto(BaseModel):
    reason: str
    movements: list[InventorySingleStockMovementRequestDto]

    @staticmethod
    def to_model(data: "InventoryMassStockMovementDto") -> MassStockMovement:
        return MassStockMovement(
            reason=data.reason,
            movements=[
                InventorySingleStockMovementRequestDto.to_model(ent)
                for ent in data.movements
            ],
        )


class InventoryItemStockStatusQueryDto(BaseModel):
    stock_level: float
    item_dici: str
    location_dici: str

    @staticmethod
    def from_model(
        data: InventoryItemStockStatus,
    ) -> "InventoryItemStockStatusQueryDto":
        return InventoryItemStockStatusQueryDto(
            stock_level=data.stock_level,
            item_dici=data.item_dici,
            location_dici=data.location_dici,
        )


class InventoryMassStockMovementQueryDto(BaseModel):
    stock_levels: list[InventoryItemStockStatusQueryDto]

    @staticmethod
    def from_model(
        data: list[InventoryItemStockStatus],
    ) -> "InventoryMassStockMovementQueryDto":
        return InventoryMassStockMovementQueryDto(
            stock_levels=[
                InventoryItemStockStatusQueryDto.from_model(ent) for ent in data
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
