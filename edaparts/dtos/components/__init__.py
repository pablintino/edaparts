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

from edaparts.dtos.components.amplifier_dtos import (
    AmplifierCreateRequestDto,
    AmplifierUpdateRequestDto,
    AmplifierQueryDto,
)
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
from edaparts.dtos.components.inductor_choke_dtos import (
    InductorChokeCreateRequestDto,
    InductorChokeUpdateRequestDto,
    InductorChokeQueryDto,
)
from edaparts.dtos.components.led_indicator_dtos import (
    LedIndicatorCreateRequestDto,
    LedIndicatorUpdateRequestDto,
    LedIndicatorQueryDto,
)
from edaparts.dtos.components.memory_dtos import (
    MemoryCreateRequestDto,
    MemoryUpdateRequestDto,
    MemoryQueryDto,
)
from edaparts.dtos.components.microcontroller_dtos import (
    MicrocontrollerCreateRequestDto,
    MicrocontrollerUpdateRequestDto,
    MicrocontrollerQueryDto,
)
from edaparts.dtos.components.opamp_dtos import (
    OpAmpCreateRequestDto,
    OpAmpUpdateRequestDto,
    OpAmpQueryDto,
)
from edaparts.dtos.components.optocoupler_digital_dtos import (
    OptocouplerDigitalCreateRequestDto,
    OptocouplerDigitalUpdateRequestDto,
    OptocouplerDigitalQueryDto,
)
from edaparts.dtos.components.optocoupler_linear_dtos import (
    OptocouplerLinearCreateRequestDto,
    OptocouplerLinearUpdateRequestDto,
    OptocouplerLinearQueryDto,
)
from edaparts.dtos.components.oscillator_oscillator_dtos import (
    OscillatorOscillatorCreateRequestDto,
    OscillatorOscillatorUpdateRequestDto,
    OscillatorOscillatorQueryDto,
)
from edaparts.dtos.components.potentiometer_dtos import (
    PotentiometerCreateRequestDto,
    PotentiometerUpdateRequestDto,
    PotentiometerQueryDto,
)
from edaparts.dtos.components.power_inductor_dtos import (
    PowerInductorCreateRequestDto,
    PowerInductorUpdateRequestDto,
    PowerInductorQueryDto,
)
from edaparts.dtos.components.power_management_efuse_hotswap_dtos import (
    PowerManagementEFuseHotSwapCreateRequestDto,
    PowerManagementEFuseHotSwapUpdateRequestDto,
    PowerManagementEFuseHotSwapQueryDto,
)
from edaparts.dtos.components.resistor_dtos import (
    ResistorCreateRequestDto,
    ResistorUpdateRequestDto,
    ResistorQueryDto,
)
from edaparts.dtos.components.switch_pushbutton_dtos import (
    SwitchPushButtonCreateRequestDto,
    SwitchPushButtonUpdateRequestDto,
    SwitchPushButtonQueryDto,
)
from edaparts.dtos.components.transceiver_dtos import (
    TransceiverCreateRequestDto,
    TransceiverUpdateRequestDto,
    TransceiverQueryDto,
)
from edaparts.dtos.components.transduder_dtos import (
    TransducerCreateRequestDto,
    TransducerUpdateRequestDto,
    TransducerQueryDto,
)
from edaparts.dtos.components.transformer_dtos import (
    TransformerCreateRequestDto,
    TransformerUpdateRequestDto,
    TransformerQueryDto,
)
from edaparts.dtos.components.transistor_array_mosfet_dtos import (
    TransistorArrayMosfetCreateRequestDto,
    TransistorArrayMosfetUpdateRequestDto,
    TransistorArrayMosfetQueryDto,
)
from edaparts.dtos.components.transistor_bjt_dtos import (
    TransistorBjtCreateRequestDto,
    TransistorBjtUpdateRequestDto,
    TransistorBjtQueryDto,
)
from edaparts.dtos.components.transistor_mosfet_dtos import (
    TransistorMosfetCreateRequestDto,
    TransistorMosfetUpdateRequestDto,
    TransistorMosfetQueryDto,
)
from edaparts.dtos.components.triac_dtos import (
    TriacCreateRequestDto,
    TriacUpdateRequestDto,
    TriacQueryDto,
)
from edaparts.dtos.components.voltage_regulator_dcdc_dtos import (
    VoltageRegulatorDCDCCreateRequestDto,
    VoltageRegulatorDCDCUpdateRequestDto,
    VoltageRegulatorDCDCQueryDto,
)
from edaparts.dtos.components.voltage_regulator_linear_dtos import (
    VoltageRegulatorLinearCreateRequestDto,
    VoltageRegulatorLinearUpdateRequestDto,
    VoltageRegulatorLinearQueryDto,
)


ComponentCreateRequestDtoUnionAlias = (
    AmplifierCreateRequestDto
    | CapacitorCeramicCreateRequestDto
    | CapacitorElectrolyticCreateRequestDto
    | CapacitorTantalumCreateRequestDto
    | ConnectorPcbCreateRequestDto
    | CrystalOscillatorCreateRequestDto
    | DiodeRectifierCreateRequestDto
    | DiodeTvsCreateRequestDto
    | DiodeZenerCreateRequestDto
    | DiscreteLogicCreateRequestDto
    | FerriteBeadCreateRequestDto
    | FusePPTCCreateRequestDto
    | InductorChokeCreateRequestDto
    | LedIndicatorCreateRequestDto
    | MemoryCreateRequestDto
    | MicrocontrollerCreateRequestDto
    | OpAmpCreateRequestDto
    | OptocouplerDigitalCreateRequestDto
    | OptocouplerLinearCreateRequestDto
    | OscillatorOscillatorCreateRequestDto
    | PotentiometerCreateRequestDto
    | PowerInductorCreateRequestDto
    | PowerManagementEFuseHotSwapCreateRequestDto
    | ResistorCreateRequestDto
    | SwitchPushButtonCreateRequestDto
    | TransceiverCreateRequestDto
    | TransformerCreateRequestDto
    | TransistorArrayMosfetCreateRequestDto
    | TransistorBjtCreateRequestDto
    | TransistorMosfetCreateRequestDto
    | TriacCreateRequestDto
    | TransducerCreateRequestDto
    | VoltageRegulatorDCDCCreateRequestDto
    | VoltageRegulatorLinearCreateRequestDto
)

ComponentUpdateRequestDtoUnionAlias = (
    AmplifierUpdateRequestDto
    | CapacitorCeramicUpdateRequestDto
    | CapacitorElectrolyticUpdateRequestDto
    | CapacitorTantalumUpdateRequestDto
    | ConnectorPcbUpdateRequestDto
    | CrystalOscillatorUpdateRequestDto
    | DiodeRectifierUpdateRequestDto
    | DiodeTvsUpdateRequestDto
    | DiodeZenerUpdateRequestDto
    | DiscreteLogicUpdateRequestDto
    | FerriteBeadUpdateRequestDto
    | FusePPTCUpdateRequestDto
    | InductorChokeUpdateRequestDto
    | LedIndicatorUpdateRequestDto
    | MemoryUpdateRequestDto
    | MicrocontrollerUpdateRequestDto
    | OpAmpUpdateRequestDto
    | OptocouplerDigitalUpdateRequestDto
    | OptocouplerLinearUpdateRequestDto
    | OscillatorOscillatorUpdateRequestDto
    | PotentiometerUpdateRequestDto
    | PowerInductorUpdateRequestDto
    | PowerManagementEFuseHotSwapUpdateRequestDto
    | ResistorUpdateRequestDto
    | SwitchPushButtonUpdateRequestDto
    | TransceiverUpdateRequestDto
    | TransformerUpdateRequestDto
    | TransistorArrayMosfetUpdateRequestDto
    | TransistorBjtUpdateRequestDto
    | TransistorMosfetUpdateRequestDto
    | TriacUpdateRequestDto
    | TransducerUpdateRequestDto
    | VoltageRegulatorDCDCUpdateRequestDto
    | VoltageRegulatorLinearUpdateRequestDto
)

ComponentQueryDtoUnionAlias = (
    AmplifierQueryDto
    | CapacitorCeramicQueryDto
    | CapacitorElectrolyticQueryDto
    | CapacitorTantalumQueryDto
    | ConnectorPcbQueryDto
    | CrystalOscillatorQueryDto
    | DiodeRectifierQueryDto
    | DiodeTvsQueryDto
    | DiodeZenerQueryDto
    | DiscreteLogicQueryDto
    | FerriteBeadQueryDto
    | FusePPTCQueryDto
    | InductorChokeQueryDto
    | LedIndicatorQueryDto
    | MemoryQueryDto
    | MicrocontrollerQueryDto
    | OpAmpQueryDto
    | OptocouplerDigitalQueryDto
    | OptocouplerLinearQueryDto
    | OscillatorOscillatorQueryDto
    | PotentiometerQueryDto
    | PowerInductorQueryDto
    | PowerManagementEFuseHotSwapQueryDto
    | ResistorQueryDto
    | SwitchPushButtonQueryDto
    | TransceiverQueryDto
    | TransformerQueryDto
    | TransistorArrayMosfetQueryDto
    | TransistorBjtQueryDto
    | TransistorMosfetQueryDto
    | TriacQueryDto
    | TransducerQueryDto
    | VoltageRegulatorDCDCQueryDto
    | VoltageRegulatorLinearQueryDto
)
