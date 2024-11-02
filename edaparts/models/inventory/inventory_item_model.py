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


from sqlalchemy import Column, Integer, String, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship

from edaparts.models.inventory.inventory_identificable_item_model import (
    InventoryIdentificableItemModel,
)


class InventoryItemModel(InventoryIdentificableItemModel):
    __tablename__ = "inventory_item"
    id = Column(Integer, primary_key=True)
    mpn = Column(String(100), nullable=False, index=True)
    manufacturer = Column(String(100), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(100))
    last_buy_price = Column(Float)
    dici = Column(String(70), nullable=False, index=True)

    # relationships
    component_id = Column(Integer, ForeignKey("component.id"))
    component = relationship(
        "ComponentModel", back_populates="inventory_item", lazy="select"
    )
    category_id = Column(Integer, ForeignKey("inventory_category.id"))
    category = relationship(
        "InventoryCategoryModel", back_populates="category_items", lazy="select"
    )
    stock_items = relationship(
        "InventoryItemLocationStockModel", back_populates="item", lazy="select"
    )
    item_properties = relationship(
        "InventoryItemPropertyModel", back_populates="item", lazy="select"
    )

    # Set a constraint that enforces Part Number - Manufacturer uniqueness for Iventory Item
    __table_args__ = (
        UniqueConstraint("mpn", "manufacturer", name="_mpn_manufacturer_item_uc"),
    )
