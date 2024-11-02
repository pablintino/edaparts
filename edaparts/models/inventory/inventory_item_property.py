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

from edaparts.services.database import Base


class InventoryItemPropertyModel(Base):
    __tablename__ = "inventory_item_property"
    id = Column(Integer, primary_key=True)
    property_name = Column(String(100), index=True)
    property_s_value = Column(String(100))
    property_i_value = Column(Integer)
    property_f_value = Column(Float)

    # relationships
    item_id = Column(Integer, ForeignKey('inventory_item.id'))
    item = relationship("InventoryItemModel", back_populates="item_properties")

    # Set a constraint that enforces Item - Property Name
    __table_args__ = (UniqueConstraint('item_id', 'property_name', name='_item_prop_uc'),
                      )

    def get_value(self):
        if self.property_i_value:
            return self.property_i_value
        elif self.property_f_value:
            return self.property_f_value
        elif self.property_s_value:
            return self.property_s_value

    def set_value(self, value):
        # Ensure that only one column is written. Only one value type is allowed
        if type(value) is int:
            self.property_s_value = None
            self.property_i_value = value
            self.property_f_value = None
        elif type(value) is float:
            self.property_s_value = None
            self.property_i_value = None
            self.property_f_value = value
        elif type(value) is str or (value is None):
            self.property_s_value = value if type(value) is str else str(value)
            self.property_i_value = None
            self.property_f_value = None
        else:
            self.property_s_value = None
            self.property_i_value = None
            self.property_f_value = None
