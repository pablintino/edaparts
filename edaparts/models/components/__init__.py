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
from edaparts.models.components.amplifier_model import AmplifierModel
from edaparts.models.components.capacitor_ceramic_model import CapacitorCeramicModel
from edaparts.models.components.capacitor_electrolytic_model import (
    CapacitorElectrolyticModel,
)
from edaparts.models.components.capacitor_tantalum_model import CapacitorTantalumModel
from edaparts.models.components.connector_pcb_model import ConnectorPcbModel
from edaparts.models.components.crystal_oscillator_model import CrystalOscillatorModel
from edaparts.models.components.diode_rectifier_model import DiodeRectifierModel
from edaparts.models.components.diode_tvs_model import DiodeTVSModel
from edaparts.models.components.diode_zener_model import DiodeZenerModel
from edaparts.models.components.discrete_logic_model import DiscreteLogicModel
from edaparts.models.components.ferrite_bead_model import FerriteBeadModel
from edaparts.models.components.fuse_pptc_model import FusePPTCModel
from edaparts.models.components.inductor_choke_model import InductorChokeModel
from edaparts.models.components.led_indicator import LedIndicatorModel
from edaparts.models.components.memory_model import MemoryModel
from edaparts.models.components.microcontroller_model import MicrocontrollerModel
from edaparts.models.components.opamp_model import OpAmpModel
from edaparts.models.components.optocoupler_digital_model import OptocouplerDigitalModel
from edaparts.models.components.optocoupler_linear_model import OptocouplerLinearModel
from edaparts.models.components.potentiometer_model import PotentiometerModel
from edaparts.models.components.power_inductor_model import PowerInductorModel
from edaparts.models.components.power_management_efuse_hotswap_model import (
    PowerManagementEFuseHotSwapModel,
)
from edaparts.models.components.resistor_model import ResistorModel
from edaparts.models.components.switch_pushbutton_model import SwitchPushButtonModel
from edaparts.models.components.switch_switch_model import SwitchSwitchModel
from edaparts.models.components.transceiver_model import TransceiverModel
from edaparts.models.components.transducer_model import TransducerModel
from edaparts.models.components.transformer_model import TransformerModel
from edaparts.models.components.transistor_array_mosfet_model import (
    TransistorArrayMosfetModel,
)
from edaparts.models.components.transistor_bjt_model import TransistorBjtModel
from edaparts.models.components.transistor_mosfet_model import TransistorMosfetModel
from edaparts.models.components.triac_model import TriacModel
from edaparts.models.components.voltage_regulator_dcdc_model import (
    VoltageRegulatorDCDCModel,
)
from edaparts.models.components.voltage_regulator_linear_model import (
    VoltageRegulatorLinearModel,
)
from edaparts.models.components.oscillator_oscillator_model import (
    OscillatorOscillatorModel,
)

ComponentModelType = (
    AmplifierModel
    | CapacitorCeramicModel
    | CapacitorElectrolyticModel
    | CapacitorTantalumModel
    | ConnectorPcbModel
    | CrystalOscillatorModel
    | DiodeRectifierModel
    | DiodeTVSModel
    | DiodeZenerModel
    | DiscreteLogicModel
    | FerriteBeadModel
    | FusePPTCModel
    | InductorChokeModel
    | LedIndicatorModel
    | MemoryModel
    | MicrocontrollerModel
    | OpAmpModel
    | OptocouplerDigitalModel
    | OptocouplerLinearModel
    | OscillatorOscillatorModel
    | PotentiometerModel
    | PowerInductorModel
    | PowerManagementEFuseHotSwapModel
    | ResistorModel
    | SwitchPushButtonModel
    | SwitchSwitchModel
    | TransceiverModel
    | TransducerModel
    | TransformerModel
    | TransistorArrayMosfetModel
    | TransistorBjtModel
    | TransistorMosfetModel
    | TriacModel
    | VoltageRegulatorDCDCModel
    | VoltageRegulatorLinearModel
)
