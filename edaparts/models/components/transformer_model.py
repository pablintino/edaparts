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

from sqlalchemy import Column, String, ForeignKey
from edaparts.models.components.component_model import ComponentModel


class TransformerModel(ComponentModel):
    __tablename__ = 'transformer'
    __id_prefix__ = 'TFRM'

    # Primary key
    id = Column(ForeignKey("component.id"), primary_key=True)

    # Specific properties of a transformer
    number_of_windings = Column(String(30))
    primary_dc_resistance = Column(String(30))
    secondary_dc_resistance = Column(String(30))
    tertiary_dc_resistance = Column(String(30))
    leakage_inductance = Column(String(30))
    primary_inductance = Column(String(30))
    secondary_current_rating = Column(String(30))
    tertiary_current_rating = Column(String(30))
    primary_voltage_rating = Column(String(30))
    secondary_voltage_rating = Column(String(30))
    tertiary_voltage_rating = Column(String(30))
    nps_turns_ratio = Column(String(30))
    npt_turns_ratio = Column(String(30))

    # Tells the ORM the type of a specific component by the distinguish column
    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
    }
