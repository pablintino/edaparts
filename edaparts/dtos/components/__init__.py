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

from edaparts.dtos.components.capacitor_ceramic_dtos import (
    CapacitorCeramicCreateRequestDto,
    CapacitorCeramicUpdateRequestDto,
    CapacitorCeramicQueryDto,
)
from edaparts.dtos.components.capacitor_electrolytic_dtos import (
    CapacitorElectrolyticCreateRequestDto,
    CapacitorElectrolyticUpdateRequestDto,
    CapacitorElectrolyticQueryDto,
)
from edaparts.dtos.components.capacitor_tantalum_dtos import (
    CapacitorTantalumCreateRequestDto,
    CapacitorTantalumUpdateRequestDto,
    CapacitorTantalumQueryDto,
)
from edaparts.dtos.components.connector_pcb_dtos import (
    ConnectorPcbCreateRequestDto,
    ConnectorPcbUpdateRequestDto,
    ConnectorPcbQueryDto,
)
from edaparts.dtos.components.crystal_oscillator_dtos import (
    CrystalOscillatorCreateRequestDto,
    CrystalOscillatorUpdateRequestDto,
    CrystalOscillatorQueryDto,
)
from edaparts.dtos.components.diode_rectifier_dtos import (
    DiodeRectifierCreateRequestDto,
    DiodeRectifierUpdateRequestDto,
    DiodeRectifierQueryDto,
)
from edaparts.dtos.components.diode_tvs_dtos import (
    DiodeTvsCreateRequestDto,
    DiodeTvsUpdateRequestDto,
    DiodeTvsQueryDto,
)
from edaparts.dtos.components.diode_zener_dtos import (
    DiodeZenerCreateRequestDto,
    DiodeZenerUpdateRequestDto,
    DiodeZenerQueryDto,
)
from edaparts.dtos.components.discrete_logic_dtos import (
    DiscreteLogicCreateRequestDto,
    DiscreteLogicUpdateRequestDto,
    DiscreteLogicQueryDto,
)
from edaparts.dtos.components.ferrite_bead_dtos import (
    FerriteBeadCreateRequestDto,
    FerriteBeadUpdateRequestDto,
    FerriteBeadQueryDto,
)
from edaparts.dtos.components.fuse_pptc_dtos import (
    FusePPTCCreateRequestDto,
    FusePPTCUpdateRequestDto,
    FusePPTCQueryDto,
)
from edaparts.dtos.components.resistor_dtos import (
    ResistorCreateRequestDto,
    ResistorUpdateRequestDto,
    ResistorQueryDto,
)


ComponentCreateRequestDtoUnionAlias = typing.Union[
    CapacitorCeramicCreateRequestDto,
    CapacitorElectrolyticCreateRequestDto,
    CapacitorTantalumCreateRequestDto,
    ConnectorPcbCreateRequestDto,
    CrystalOscillatorCreateRequestDto,
    DiodeRectifierCreateRequestDto,
    DiodeTvsCreateRequestDto,
    DiodeZenerCreateRequestDto,
    DiscreteLogicCreateRequestDto,
    FerriteBeadCreateRequestDto,
    FusePPTCCreateRequestDto,
    ResistorCreateRequestDto,
]

ComponentUpdateRequestDtoUnionAlias = typing.Union[
    CapacitorCeramicUpdateRequestDto,
    CapacitorElectrolyticUpdateRequestDto,
    CapacitorTantalumUpdateRequestDto,
    ConnectorPcbUpdateRequestDto,
    CrystalOscillatorUpdateRequestDto,
    DiodeRectifierUpdateRequestDto,
    DiodeTvsUpdateRequestDto,
    DiodeZenerUpdateRequestDto,
    DiscreteLogicUpdateRequestDto,
    FerriteBeadUpdateRequestDto,
    FusePPTCUpdateRequestDto,
    ResistorUpdateRequestDto,
]

ComponentQueryDtoUnionAlias = typing.Union[
    CapacitorCeramicQueryDto,
    CapacitorElectrolyticQueryDto,
    CapacitorTantalumQueryDto,
    ConnectorPcbQueryDto,
    CrystalOscillatorQueryDto,
    DiodeRectifierQueryDto,
    DiodeTvsQueryDto,
    DiodeZenerQueryDto,
    DiscreteLogicQueryDto,
    FerriteBeadQueryDto,
    FusePPTCQueryDto,
    ResistorQueryDto,
]
