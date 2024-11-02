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


from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from edaparts.services.database import Base


class InventoryItemLocationStockModel(Base):
    __tablename__ = "inventory_item_location_stock"

    id = Column(Integer, primary_key=True)
    actual_stock = Column(Float, nullable=False)  # todo: name typo
    stock_min_level = Column(Float)
    stock_notify_min_level = Column(Float)

    # relationships
    location_id = Column(Integer, ForeignKey("inventory_location.id"), nullable=False)
    location = relationship(
        "InventoryLocationModel", back_populates="stock_items", lazy="select"
    )

    item_id = Column(Integer, ForeignKey("inventory_item.id"), nullable=False)
    item = relationship(
        "InventoryItemModel", back_populates="stock_items", lazy="select"
    )

    stock_movements = relationship(
        "InventoryItemLocationStockMovementModel",
        back_populates="stock_item",
        cascade="delete",
    )
